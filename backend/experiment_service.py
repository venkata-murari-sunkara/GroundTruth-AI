from backend.database import SessionLocal
from backend.models import Experiment, ModelResponse, BenchmarkQuestion
from backend.model_runner import run_model


def run_experiment(dataset_id: int, model_name: str):
    with SessionLocal() as session:
        questions = (
            session.query(BenchmarkQuestion)
            .filter(BenchmarkQuestion.dataset_id == dataset_id)
            .all()
        )

        if not questions:
            return {
                "success": False,
                "error": "No questions found for this dataset."
            }

        experiment = Experiment(
            dataset_id=dataset_id,
            model_name=model_name,
            prompt_version="v1"
        )

        session.add(experiment)
        session.commit()
        session.refresh(experiment)

        for question in questions:
            result = run_model(question.question, model_name)

            response = ModelResponse(
                experiment_id=experiment.id,
                question_id=question.id,
                generated_answer=result["answer"],
                latency_seconds=result["latency"],
                token_usage=result.get("token_usage"),
                estimated_cost=result.get("estimated_cost")
            )

            session.add(response)

        session.commit()

        return {
            "success": True,
            "experiment_id": experiment.id,
            "dataset_id": dataset_id,
            "model_name": model_name,
            "questions_evaluated": len(questions)
        }