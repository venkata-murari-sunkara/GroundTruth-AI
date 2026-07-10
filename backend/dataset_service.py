import os
from backend.database import SessionLocal
from backend.models import Dataset, BenchmarkQuestion
from backend.dataset_loader import load_and_validate_dataset

def save_dataset(file_path: str, filename: str):
    df = load_and_validate_dataset(file_path)
    dataset_name = os.path.splitext(filename)[0]

    with SessionLocal() as session:
        try:
            dataset = Dataset(
                name= dataset_name,
                filename= filename,
                row_count= len(df)
            )

            session.add(dataset)
            session.commit()
            session.refresh(dataset)

            questions = [
                BenchmarkQuestion(
                    dataset_id= dataset.id,
                    question= row["question"],
                    expected_answer= row["expected_answer"]
                )
                for row in df.to_dict(orient="records")
            ]

            session.add_all(questions)
            session.commit()

            return {
                "dataset_id": dataset.id,
                "name": dataset.name,
                "filename": dataset.filename,
                "rows": dataset.row_count
            }

        except Exception:
            session.rollback()
            raise

def get_all_datasets():
    with SessionLocal() as session:
        datasets = session.query(Dataset).all()

        return [
            {
                "dataset_id": dataset.id,
                "name": dataset.name,
                "filename": dataset.filename,
                "rows": dataset.row_count,
                "uploaded_at": dataset.uploaded_at
            }
            for dataset in datasets
        ]
    
def get_questions_by_dataset(dataset_id: int):
    with SessionLocal() as session:
        questions = (
            session.query(BenchmarkQuestion)
            .filter(BenchmarkQuestion.dataset_id == dataset_id)
            .all()
        )

        return [
            {
                "question_id": question.id,
                "question": question.question,
                "expected_answer": question.expected_answer
            }
            for question in questions
        ]