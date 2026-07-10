from backend.database import SessionLocal
from backend.models import ModelResponse, EvaluationMetric, Experiment
from backend.evaluator import calculate_exact_match, calculate_semantic_score


def evaluate_experiment(experiment_id: int):
    with SessionLocal() as session:
        responses = (
            session.query(ModelResponse)
            .filter(ModelResponse.experiment_id == experiment_id)
            .all()
        )

        if not responses:
            return {
                "success": False,
                "error": "No responses found for this experiment."
            }

        total_exact_matches = 0
        total_semantic_score = 0
        total_overall_score = 0

        for response in responses:
            expected_answer = response.question.expected_answer
            generated_answer = response.generated_answer

            exact_match = calculate_exact_match(
                expected_answer,
                generated_answer
            )

            semantic_score = calculate_semantic_score(
                expected_answer,
                generated_answer
            )

            overall_score = round((exact_match + semantic_score) / 2, 2)

            metric = (
                session.query(EvaluationMetric)
                .filter(EvaluationMetric.response_id == response.id)
                .first()
            )

            if metric:
                metric.exact_match = exact_match
                metric.semantic_score = semantic_score
                metric.overall_score = overall_score
            else:
                metric = EvaluationMetric(
                    response_id= response.id,
                    exact_match= exact_match,
                    semantic_score= semantic_score,
                    overall_score= overall_score
                )
                session.add(metric)

            total_exact_matches += exact_match
            total_semantic_score += semantic_score
            total_overall_score += overall_score


        session.commit()

        total_responses = len(responses)

        return {
            "success": True,
            "experiment_id": experiment_id,
            "responses_evaluated": total_responses,
            "exact_match_accuracy": round(total_exact_matches / total_responses, 2),
            "average_semantic_score": round(total_semantic_score / total_responses, 2),
            "average_overall_score": round(total_overall_score / total_responses, 2)
        }
    
def get_experiment_results(experiment_id: int):
    with SessionLocal() as session:
        responses = (
            session.query(ModelResponse)
            .filter(ModelResponse.experiment_id == experiment_id)
            .all()
        )

        if not responses:
            return {
                "success": False,
                "error": "No results found for this experiment."
            }

        results = []

        for response in responses:
            metric = response.metrics

            results.append({
                "question": response.question.question,
                "expected_answer": response.question.expected_answer,
                "generated_answer": response.generated_answer,
                "latency_seconds": response.latency_seconds,
                "exact_match": metric.exact_match if metric else None,
                "semantic_score": metric.semantic_score if metric else None,
                "overall_score": metric.overall_score if metric else None
            })

        return {
            "success": True,
            "experiment_id": experiment_id,
            "results": results
        }
    
def get_leaderboard():
    with SessionLocal() as session:
        experiments = session.query(Experiment).all()

        model_groups = {}

        for experiment in experiments:
            responses = (
                session.query(ModelResponse)
                .filter(ModelResponse.experiment_id == experiment.id)
                .all()
            )

            if not responses:
                continue

            metrics = [
                response.metrics
                for response in responses
                if response.metrics is not None
            ]

            if not metrics:
                continue

            model_name = experiment.model_name

            if model_name not in model_groups:
                model_groups[model_name] = {
                    "model_name": model_name,
                    "exact_matches": [],
                    "semantic_scores": [],
                    "overall_scores": [],
                    "latencies": [],
                    "costs": [],
                    "experiment_count": 0
                }

            model_groups[model_name]["experiment_count"] += 1

            model_groups[model_name]["exact_matches"].extend(
                [metric.exact_match for metric in metrics]
            )

            model_groups[model_name]["semantic_scores"].extend(
                [metric.semantic_score or 0 for metric in metrics]
            )

            model_groups[model_name]["overall_scores"].extend(
                [metric.overall_score or 0 for metric in metrics]
            )

            model_groups[model_name]["latencies"].extend(
                [response.latency_seconds for response in responses]
            )

            model_groups[model_name]["costs"].extend(
                [response.estimated_cost or 0 for response in responses]
            )

        leaderboard = []

        display_names = {
            "gemini-2.5-flash": "Gemini 2.5 Flash",
            "openai": "GPT-4o Mini",
            "claude": "Claude Haiku 4.5"
        }

        for model_name, values in model_groups.items():
            accuracy = (
                sum(values["exact_matches"])
                / len(values["exact_matches"])
            )

            semantic_score = (
                sum(values["semantic_scores"])
                / len(values["semantic_scores"])
            )

            overall_score = (
                sum(values["overall_scores"])
                / len(values["overall_scores"])
            )

            avg_latency = (
                sum(values["latencies"])
                / len(values["latencies"])
            )

            total_cost = sum(values["costs"])

            average_experiment_cost = (
                total_cost / values["experiment_count"]
                if values["experiment_count"] > 0
                else 0
            )

            leaderboard.append({
                "model_name": display_names.get(
                    model_name,
                    model_name
                ),
                "accuracy": round(accuracy, 2),
                "semantic_score": round(semantic_score, 2),
                "overall_score": round(overall_score, 2),
                "average_latency": round(avg_latency, 2),
                "estimated_cost": f"${average_experiment_cost:.6f}"
            })

        leaderboard = sorted(
            leaderboard,
            key=lambda item: (
                -item["overall_score"],
                -item["accuracy"],
                item["average_latency"]
            )
        )

        return {
            "success": True,
            "leaderboard": leaderboard
        }