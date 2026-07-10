import pandas as pd

RequiredColumns = {"question", "expected_answer"}


def load_and_validate_dataset(file_path: str):
    df = pd.read_csv(file_path)

    df.columns = [col.strip().lower() for col in df.columns]

    missing_columns = RequiredColumns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Dataset must contain columns: {RequiredColumns}. Missing: {missing_columns}"
        )

    df = df[["question", "expected_answer"]]

    df = df.dropna(subset=["question", "expected_answer"])

    if df.empty:
        raise ValueError("Dataset contains no valid question-answer rows.")

    return df