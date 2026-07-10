# 🧠 GroundTruth AI

> A production-style LLM benchmarking platform for evaluating and comparing multiple Large Language Models on custom benchmark datasets.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)

---

## 🌐 Live Demo

* **Frontend (Streamlit App):** [Try it here](your-streamlit-url)
* **Backend API (Swagger Docs):** [View API docs](https://groundtruth-ai.onrender.com)

> ⚠️ Note: The backend is hosted on Render's free tier and may take 30–60 seconds to wake up if it has been inactive. Please be patient on first load.

---

## 📌 Overview

GroundTruth AI is an end-to-end evaluation platform that benchmarks multiple Large Language Models (LLMs) side-by-side on custom datasets — automating what would otherwise be manual response comparison.

The platform runs the same benchmark against multiple providers in parallel, scores each response, tracks cost and latency, and surfaces results in an interactive leaderboard.

Currently supported models:

- Gemini 2.5 Flash
- GPT-4o Mini
- Claude Haiku 4.5

---

## 🚀 Features

### 📤 Upload Benchmark Dataset

Upload a custom benchmark CSV containing:

| question | expected_answer |
|-----------|-----------------|
| ... | ... |

### 🤖 Multi-Model Evaluation

Run the same benchmark simultaneously against Gemini, GPT, and Claude — no sequential waiting, no manual copy-pasting between provider consoles.

### 📊 Automatic Evaluation

Each response is scored using:

- Exact Match Accuracy
- Semantic Similarity (LLM-judged)
- Overall Score
- Average Latency

### 💰 Cost Tracking

Estimated inference cost is calculated per experiment, enabling direct performance-vs-cost comparison across providers.

### 🏆 Model Leaderboard

Models are automatically ranked by Overall Score, Accuracy, Semantic Score, Latency, and Estimated Cost — giving a single view of which model wins on which dimension.

### 📈 Interactive Dashboard

Visualizations built with Plotly:

- Semantic Score by Question
- Response Latency Comparison
- Exact Match Distribution

### 📥 Export Results

Download full benchmark results as CSV for offline analysis.

---

## 🏗️ System Architecture

![Architecture Diagram](assets/GroundTruth_AI_Architecture.png)

---

## 📸 Application Demo

### Dashboard

![Dashboard](assets/ui_1.png)

---

### Leaderboard

![Leaderboard](assets/ui_2.png)

---

### Performance Analytics

![Analytics](assets/ui_3.png)

---

### Detailed Results

![Results](assets/ui_4.png)

---

## 🛠 Tech Stack

**Backend:** FastAPI, SQLAlchemy, PostgreSQL, Pydantic

**Frontend:** Streamlit, Plotly, Pandas

**LLM Providers:** Google Gemini API, OpenAI API, Anthropic Claude API

**Database:** PostgreSQL

---

## 📂 Project Structure

```text
GroundTruth-AI/
├── assets
├── backend/
│   ├── config.py
│   ├── create_tables.py
│   ├── database.py
│   ├── dataset_loader.py
│   ├── dataset_service.py
│   ├── evaluation_service.py
│   ├── evaluator.py
│   ├── experiment_service.py
│   ├── main.py
│   ├── model_runner.py
│   ├── models.py
├── data/                        # Benchmark datasets
├── frontend/
│   ├── app.py
│   └── uploads/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/venkata-murari-sunkara/groundtruth-ai.git
cd groundtruth-ai
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY= your_openai_key
GEMINI_API_KEY= your_gemini_key
ANTHROPIC_API_KEY= your_claude_key
DATABASE_URL= postgresql://username:password@localhost/groundtruth
```

### 5. Run Backend

```bash
uvicorn backend.main:app --reload
```

Backend URL: `http://127.0.0.1:8000`

### 6. Run Frontend

```bash
streamlit run frontend/app.py
```

Frontend URL: `http://localhost:8501`

---

## 📊 Evaluation Metrics

**Exact Match** — Checks whether the generated answer exactly matches the expected answer.

**Semantic Similarity** — Uses an LLM judge to score semantic alignment between the expected and generated answer, on a 0 (incorrect) to 1 (perfect match) scale.

**Overall Score** — Overall Score = (Exact Match + Semantic Score) / 2

**Latency** — Average response time per question, per model.

**Estimated Cost** — Inference cost calculated from each provider's token pricing.

---

## 📈 Leaderboard Ranking

Models are ranked primarily by:

1. Overall Score — (Exact Match + Semantic Score) / 2
2. Accuracy — used as a tiebreaker
3. Lower Latency — used as a tiebreaker

Cost and full latency data remain visible in the dashboard for deeper analysis even though they don't affect the primary ranking — this keeps the leaderboard focused on correctness while still surfacing performance-vs-cost tradeoffs for anyone who wants to dig deeper.

---

## 🧠 Engineering Decisions & Tradeoffs

* **Parallel evaluation over sequential:** All three providers are queried concurrently for each benchmark question rather than sequentially, reducing total benchmark runtime and giving latency numbers that reflect real-world simultaneous usage rather than artificially inflated sequential wait times.

* **LLM-as-a-judge for semantic scoring:** Exact match alone is too rigid for evaluating natural language answers — two correct answers can be worded completely differently. Using an LLM judge for semantic similarity captures correctness that exact match misses, at the cost of introducing judge-model variance as a tradeoff.

* **PostgreSQL over SQLite:** Chosen to support concurrent writes during parallel multi-model evaluation runs and to allow the results store to scale toward experiment history tracking in future iterations.

* **Cost estimation over live billing APIs:** Each provider's real-time billing API has different latency and access requirements. Estimating cost from published token pricing keeps the evaluation loop fast and provider-agnostic, at the cost of small deviations from actual billed amounts.

---

## 🚧 Challenges Solved

* **Multi-provider API integration:** Built a unified evaluation pipeline that integrates Gemini, GPT-4o Mini, and Claude through a common interface despite differences in SDKs, authentication, response formats, and error handling. This keeps the benchmarking workflow provider-agnostic and easy to extend with additional models.

* **Judge-model consistency:** Using an LLM as a semantic judge introduces its own variance between runs. Structured the judge prompt with explicit scoring criteria and a fixed 0–1 scale to reduce inconsistency across repeated evaluations.

* **Fair latency comparison:** Running requests sequentially would have inflated later providers' apparent latency due to queuing effects. Parallelizing requests ensures each provider's latency reflects its own real response time, not artifacts of test ordering.

---

## 🎯 Key Concepts Demonstrated

- LLM Evaluation & Benchmarking
- Multi-Provider AI Integration (OpenAI, Gemini, Anthropic)
- LLM-as-a-Judge Scoring
- Concurrent/Async API Orchestration
- FastAPI REST API Design
- PostgreSQL Data Modeling
- Cost & Latency Analysis
- Interactive Data Visualization (Plotly)
- Production-Style AI System Architecture

---

## 🔮 Future Improvements

- RAG-specific evaluation (Faithfulness, Citation Grounding)
- Hallucination detection
- Prompt versioning and A/B comparison
- BLEU / ROUGE metrics
- Experiment history and tracking
- User authentication
- Docker support
- Batch benchmarking
- PDF export
- Public REST API

---

## 👨‍💻 Author

**Venkata Murari**

- GitHub: [venkata-murari-sunkara](https://github.com/venkata-murari-sunkara)
- LinkedIn: [venkata-murari](https://www.linkedin.com/in/venkata-murari/)