import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import os 

API_URL = st.secrets.get(
    "API_URL",
    "http://127.0.0.1:8000"
)

st.set_page_config(
    page_title="GroundTruth AI",
    layout="wide"
)

st.title("🧠 GroundTruth AI")
st.caption("LLM Evaluation & Benchmarking Platform")


# Upload Dataset
st.header("📤 Step 1: Upload Benchmark Dataset")

with st.container(border=True):
    uploaded_file = st.file_uploader(
        "Upload a CSV file with columns: question, expected_answer",
        type=["csv"]
    )

    if uploaded_file is not None and st.button("Upload Dataset"):
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "text/csv"
            )
        }

        response = requests.post(
            f"{API_URL}/datasets/upload",
            files=files
        )

        result = response.json()

        if result.get("success"):
            st.success("Dataset uploaded successfully.")
            st.write(f"**Dataset:** {result['name']}")
            st.write(f"**Rows:** {result['rows']}")
        else:
            st.error(result.get("error", "Upload failed."))


# Select Dataset
st.header("📚 Step 2: Select Dataset")

with st.container(border=True):
    response = requests.get(f"{API_URL}/datasets")
    result = response.json()

    if result.get("success") and result["datasets"]:
        datasets = result["datasets"]

        dataset_options = {
            f"{dataset['name']} ({dataset['rows']} questions)": dataset
            for dataset in datasets
        }

        selected_dataset_label = st.selectbox(
            "Choose a dataset",
            list(dataset_options.keys())
        )

        selected_dataset = dataset_options[selected_dataset_label]

        st.session_state["dataset_id"] = selected_dataset["dataset_id"]
        st.session_state["dataset_name"] = selected_dataset["name"]
        st.session_state["dataset_rows"] = selected_dataset["rows"]

        col1, col2, col3 = st.columns(3)
        col1.metric("Dataset", selected_dataset["name"])
        col2.metric("Questions", selected_dataset["rows"])
        col3.metric("Dataset ID", selected_dataset["dataset_id"])

    else:
        st.warning("No datasets uploaded yet.")


# Select Model & Run Experiment
st.header("🚀 Step 3: Run Benchmark")

with st.container(border=True):
    model_options = {
        "Gemini 2.5 Flash": "gemini-2.5-flash",
        "GPT-4o Mini": "openai",
        "Claude Haiku 4.5": "claude"
    }

    selected_model_label = st.selectbox(
        "Choose a model",
        list(model_options.keys())
    )

    selected_model = model_options[selected_model_label]

    if "dataset_id" in st.session_state:
        st.write(f"Selected dataset: **{st.session_state['dataset_name']}**")
        st.write(f"Selected model: **{selected_model_label}**")

        if st.button("Run Benchmark", type="primary"):
            try:
                with st.spinner(
                    f"Running and evaluating {selected_model_label}..."
                ):
                    # 1. Run the selected model
                    run_response = requests.post(
                        f"{API_URL}/experiments/run/"
                        f"{st.session_state['dataset_id']}/"
                        f"{selected_model}",
                        timeout=180
                    )

                    if run_response.status_code != 200:
                        st.error(
                            f"Experiment failed: "
                            f"{run_response.status_code}"
                        )
                        st.text(run_response.text)
                        st.stop()

                    run_result = run_response.json()

                    if not run_result.get("success"):
                        st.error(
                            run_result.get(
                                "error",
                                "Experiment failed."
                            )
                        )
                        st.stop()

                    experiment_id = run_result["experiment_id"]

                    # 2. Evaluate the generated responses
                    evaluation_response = requests.post(
                        f"{API_URL}/experiments/evaluate/"
                        f"{experiment_id}",
                        timeout=180
                    )

                    if evaluation_response.status_code != 200:
                        st.error(
                            f"Evaluation failed: "
                            f"{evaluation_response.status_code}"
                        )
                        st.text(evaluation_response.text)
                        st.stop()

                    evaluation_result = evaluation_response.json()

                    if not evaluation_result.get("success"):
                        st.error(
                            evaluation_result.get(
                                "error",
                                "Evaluation failed."
                            )
                        )
                        st.stop()

                    # 3. Store results in Streamlit session
                    st.session_state["experiment_id"] = experiment_id
                    st.session_state["experiment_model"] = (
                        selected_model_label
                    )
                    st.session_state["metrics"] = evaluation_result

                    st.success("Benchmark completed successfully.")

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Experiment ID",
                        experiment_id
                    )

                    col2.metric(
                        "Model",
                        selected_model_label
                    )

                    col3.metric(
                        "Questions Evaluated",
                        run_result["questions_evaluated"]
                    )

            except requests.exceptions.Timeout:
                st.error(
                    "The benchmark took too long. "
                    "Please try again."
                )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Unable to connect to the backend API."
                )

            except ValueError:
                st.error(
                    "The backend returned an invalid response."
                )

    else:
        st.info("Please select a dataset first.")


# Evaluation Summary
if "metrics" in st.session_state:
    st.header("🏆 Evaluation Summary")

    metrics = st.session_state["metrics"]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Exact Match Accuracy",
        f"{metrics['exact_match_accuracy'] * 100:.0f}%"
    )

    col2.metric(
        "Average Semantic Score",
        f"{metrics['average_semantic_score']:.2f}"
    )

    col3.metric(
        "Average Overall Score",
        f"{metrics['average_overall_score']:.2f}"
    )


# Leaderboard
st.header("🏆 Leaderboard")

leaderboard_response = requests.get(f"{API_URL}/leaderboard")

if leaderboard_response.status_code == 200:
    leaderboard_result = leaderboard_response.json()

    if leaderboard_result.get("success") and leaderboard_result["leaderboard"]:
        leaderboard_df = pd.DataFrame(leaderboard_result["leaderboard"])

        leaderboard_df = leaderboard_df.rename(
            columns={
                "model_name": "Model",
                "accuracy": "Accuracy",
                "semantic_score": "Semantic Score",
                "overall_score": "Evaluation Score",
                "average_latency": "Avg Latency (s)",
                "estimated_cost": "Estimated Cost"
            }
        )

        leaderboard_df["Accuracy"] = leaderboard_df["Accuracy"].apply(
            lambda value: f"{value * 100:.0f}%"
        )

        leaderboard_df["Semantic Score"] = leaderboard_df[
            "Semantic Score"
        ].apply(lambda value: f"{value:.2f}")

        leaderboard_df["Evaluation Score"] = leaderboard_df[
            "Evaluation Score"
        ].apply(lambda value: f"{value:.2f}")

        leaderboard_df["Avg Latency (s)"] = leaderboard_df[
            "Avg Latency (s)"
        ].apply(lambda value: f"{value:.2f} s")

        rank_icons = ["1", "2", "3"]

        leaderboard_df.insert(0, "Rank",
            [
                rank_icons[index] if index < 3 else str(index + 1)
                for index in range(len(leaderboard_df))
            ]
        )

        st.dataframe(
            leaderboard_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No evaluated experiments available yet.")
else:
    st.error(f"Backend error: {leaderboard_response.status_code}")
    st.text(leaderboard_response.text)


# Detailed Results + Charts
if "experiment_id" in st.session_state:
    response = requests.get(
        f"{API_URL}/experiments/{st.session_state['experiment_id']}/results"
    )

    if response.status_code != 200:
        st.error(f"Backend error: {response.status_code}")
        st.text(response.text)
    else:
        result = response.json()

        if result.get("success"):
            raw_df = pd.DataFrame(result["results"])

            if not raw_df.empty:
                raw_df["Question ID"] = [f"Q{i+1}" for i in range(len(raw_df))]

                display_df = raw_df.rename(
                    columns={
                        "question": "Question",
                        "expected_answer": "Expected Answer",
                        "generated_answer": "Generated Answer",
                        "latency_seconds": "Latency (s)",
                        "exact_match": "Exact Match",
                        "semantic_score": "Semantic Score",
                        "overall_score": "Overall Score"
                    }
                )

                st.header("📈 Performance Charts")

                col1, col2 = st.columns(2)

                with col1:
                    fig = px.bar(
                        raw_df,
                        x="Question ID",
                        y="semantic_score",
                        hover_data=["question"],
                        title="Semantic Score by Question"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    fig = px.bar(
                        raw_df,
                        x="Question ID",
                        y="latency_seconds",
                        hover_data=["question"],
                        title="Latency by Question"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                exact_counts = (
                    raw_df["exact_match"]
                    .map({1: "Correct", 0: "Incorrect"})
                    .value_counts()
                    .rename_axis("Result")
                    .reset_index(name="Count")
                )

                fig = px.bar(
                    exact_counts,
                    x="Result",
                    y="Count",
                    title="Exact Match Distribution"
                )

                st.plotly_chart(fig, use_container_width=True)

                st.header("📋 Detailed Results")

                st.dataframe(
                    display_df[
                        [
                            "Question ID",
                            "Question",
                            "Expected Answer",
                            "Generated Answer",
                            "Latency (s)",
                            "Exact Match",
                            "Semantic Score",
                            "Overall Score"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )

                csv = display_df.to_csv(index=False)

                st.download_button(
                    label="⬇️ Download Results as CSV",
                    data=csv,
                    file_name="groundtruth_ai_results.csv",
                    mime="text/csv"
                )

        else:
            st.error(result.get("error", "Unable to fetch experiment results."))