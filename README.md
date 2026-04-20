# SRE AI Copilot

An AI-powered Slack bot that analyzes on-call alerts in under 10 seconds. When an alert fires, the bot automatically fetches logs, searches runbooks, classifies severity, and replies with a root cause analysis.

## Demo

Type in Slack:
```
/oncall HighMemoryUsage on service payments-api
```

Bot replies:
```
Severity: P2
Likely cause: memory leak, OOMKilled event detected.
Runbook says: kubectl rollout undo deployment/payments-api
Relevant logs: ERROR OOMKilled: container exceeded memory limit
```

## Architecture

```
Slack /oncall command
        ↓
Slack Bot (slack-bolt)
        ↓
FastAPI /analyze endpoint
        ↓
┌─────────────────────────────────┐
│  Classifier (distilbert)        │  → predicts severity P1/P2/P3
│  RAG (ChromaDB)                 │  → finds relevant runbook
│  LLM Agent (Ollama llama3.1:8b) │  → generates analysis
└─────────────────────────────────┘
        ↓
Slack reply to engineer
```

## Tech Stack

| Component | Tool |
|---|---|
| LLM | Ollama + llama3.1:8b (local, free) |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers |
| Severity Classifier | HuggingFace distilbert |
| Experiment Tracking | MLflow |
| Data Versioning | DVC |
| Drift Detection | Evidently |
| API | FastAPI |
| Slack Bot | Slack Bolt SDK |
| Metrics | Prometheus + Grafana |
| CI/CD | GitHub Actions |
| Deployment | Docker + Kubernetes/Helm |

## Project Structure

```
sre-ai-copilot/
├── agent/
│   ├── analyze.py      # Core agent: fetches data, calls LLM
│   ├── tools.py        # get_logs, get_runbook functions
│   └── rag.py          # ChromaDB vector search
├── api/
│   └── main.py         # FastAPI POST /analyze endpoint
├── bot/
│   └── slack.py        # Slack bot /oncall slash command
├── classifier/
│   ├── train.py        # Fine-tune distilbert on alert data
│   └── predict.py      # Predict severity for new alerts
├── data/
│   └── alerts.csv      # 280+ labeled training alerts
├── runbooks/
│   ├── high_memory.md
│   └── disk_full.md
├── monitoring/
│   ├── drift.py        # Evidently drift detection
│   └── prometheus.yml  # Prometheus scrape config
├── .github/
│   └── workflows/
│       └── train.yml   # Auto-retrain on data change
└── docker-compose.yml  # API + Bot + Prometheus + Grafana
```

## Setup

### Prerequisites
- Python 3.12
- Ollama installed and running (`ollama serve`)
- llama3.1:8b model pulled (`ollama pull llama3.1:8b`)

### Install

```bash
git clone https://github.com/nourdz5/sre-ai-copilot.git
cd sre-ai-copilot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure

Create a `.env` file:
```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
```

### Run

```bash
# Index runbooks into ChromaDB
python agent/rag.py

# Train the classifier
python classifier/train.py

# Start the API
uvicorn api.main:app --reload

# Start the Slack bot (new terminal)
python bot/slack.py
```

### Run with Docker

```bash
docker-compose up --build
```

## MLOps Pipeline

- **Training data** versioned with DVC (`data/alerts.csv`)
- **Experiments** tracked with MLflow (`mlflow ui`)
- **CI/CD** via GitHub Actions — auto-retrains classifier when training data changes
- **Drift detection** via Evidently — flags when incoming alerts drift from training data

## Why This Project

Built to demonstrate a combined AI Engineer + MLOps skill set:
- **AI Engineer skills**: LLM integration, RAG, vector search, agent design
- **MLOps skills**: model training, experiment tracking, data versioning, drift detection, CI/CD
- **SRE/DevOps skills**: Kubernetes, Helm, Docker, Prometheus, Grafana
