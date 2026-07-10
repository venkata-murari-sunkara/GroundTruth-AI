from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key= True, index= True)
    name = Column(String, nullable= False)
    filename = Column(String, nullable= False)
    row_count = Column(Integer, nullable= False)
    uploaded_at = Column(DateTime, default= datetime.utcnow)

    questions = relationship(
        "BenchmarkQuestion",
        back_populates= "dataset",
        cascade= "all, delete-orphan"
    )

    experiments = relationship(
        "Experiment",
        back_populates= "dataset",
        cascade= "all, delete-orphan"
    )


class BenchmarkQuestion(Base):
    __tablename__ = "benchmark_questions"

    id = Column(Integer, primary_key= True, index= True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable= False)

    question = Column(Text, nullable= False)
    expected_answer = Column(Text, nullable= False)

    dataset = relationship("Dataset", back_populates= "questions")

    responses = relationship(
        "ModelResponse",
        back_populates= "question",
        cascade= "all, delete-orphan"
    )


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key= True, index= True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable= False)

    model_name = Column(String, nullable= False)
    prompt_version = Column(String, default= "v1")
    created_at = Column(DateTime, default= datetime.utcnow)

    dataset = relationship("Dataset", back_populates= "experiments")

    responses = relationship(
        "ModelResponse",
        back_populates= "experiment",
        cascade= "all, delete-orphan"
    )


class ModelResponse(Base):
    __tablename__ = "model_responses"

    id = Column(Integer, primary_key= True, index= True)

    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable= False)
    question_id = Column(Integer, ForeignKey("benchmark_questions.id"), nullable= False)

    generated_answer = Column(Text, nullable= False)
    latency_seconds = Column(Float, nullable= False)
    token_usage = Column(Integer, nullable= True)
    estimated_cost = Column(Float, nullable= True)

    experiment = relationship("Experiment", back_populates= "responses")
    question = relationship("BenchmarkQuestion", back_populates= "responses")

    metrics = relationship(
        "EvaluationMetric",
        back_populates= "response",
        cascade= "all, delete-orphan",
        uselist= False
    )


class EvaluationMetric(Base):
    __tablename__ = "evaluation_metrics"

    id = Column(Integer, primary_key= True, index= True)

    response_id = Column(
        Integer,
        ForeignKey("model_responses.id"),
        unique= True,
        nullable= False
    )

    exact_match = Column(Integer, nullable= False)
    semantic_score = Column(Float, nullable= True)
    faithfulness_score = Column(Float, nullable= True)
    overall_score = Column(Float, nullable= False)

    response = relationship("ModelResponse", back_populates= "metrics")