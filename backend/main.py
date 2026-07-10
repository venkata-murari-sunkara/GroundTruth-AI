import os
import shutil

from fastapi import FastAPI, UploadFile, File

from backend.dataset_service import save_dataset, get_all_datasets
from backend.model_runner import ask_gemini
from backend.experiment_service import run_experiment
from backend.evaluation_service import evaluate_experiment, get_experiment_results, get_leaderboard
from backend.model_runner import run_model


app = FastAPI(title= "GroundTruth AI")


@app.get("/")
def root():
    return {
        "message": "Welcome to GroundTruth AI"
    }

@app.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".csv"):
            return {
                "success": False,
                "error": "Only CSV files are supported."
            }

        os.makedirs("uploads", exist_ok=True)

        file_path = os.path.join("uploads", file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        dataset = save_dataset(file_path, file.filename)

        return {
            "success": True,
            **dataset
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
@app.get("/datasets")
def list_datasets():
    return {
        "success": True,
        "datasets": get_all_datasets()
    }

@app.get("/ask")
def test_model():
    result = ask_gemini("What is captial of france?")

    return result

@app.post("/experiments/run/{dataset_id}/{model_name}")
def run_model_experiment(dataset_id: int, model_name: str):
    return run_experiment(dataset_id, model_name)

@app.post("/experiments/evaluate/{experiment_id}")
def evaluate(experiment_id: int):
    return evaluate_experiment(experiment_id)

@app.get("/experiments/{experiment_id}/results")
def experiment_results(experiment_id: int):
    return get_experiment_results(experiment_id) 


@app.get("/test-model/{model_name}")
def test_model(model_name: str):
    try:
        return run_model(
            question= "What is the capital of France?",
            model_name= model_name
        )
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
@app.get("/leaderboard")
def leaderboard():
    return get_leaderboard()