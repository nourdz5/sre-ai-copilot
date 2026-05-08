# SRE AI Copilot - Complete Project Notes

> These notes are written so that a future AI assistant can read this file and
> immediately understand the full context, continue helping, and know exactly
> where progress stopped. No need to re-explain anything.

---

## About the Person Building This

- Role: SRE / Platform Engineer (DevOps background)
- Strong skills: Kubernetes, Helm, Docker, Baremetal infra, CI/CD, Prometheus, Grafana
- Weak/new skills: Python (learning), AI/ML, LLMs, RAG, MLOps
- Goal: Build this project to transition into AI Engineer / MLOps roles
- Constraint: No budget for paid APIs — using Ollama (free, runs locally)
- Machine: MacOS, 18GB RAM, 228GB free disk, 11 CPU cores → use llama3.1:8b model

---

## Why This Project Exists

**For the CV:** Covers both AI Engineer skills (LLM, RAG, agents) and MLOps skills
(training pipeline, MLflow, DVC, drift detection, CI/CD for ML). Combined with
existing DevOps skills (k8s, Docker, Helm), this makes a rare and strong profile.

**The real problem it solves:** When an alert fires at 2am, an on-call SRE engineer
has to manually dig through logs, find the right runbook, and figure out what's wrong.
This takes 10-30 minutes. This app does it in under 10 seconds via a Slack command.

---

## What the App Does

Engineer types in Slack:
```
/oncall HighMemoryUsage on service payments-api
```

Bot automatically:
1. Fetches recent logs for `payments-api`
2. Searches runbooks for the alert type (using vector search / RAG)
3. Classifies severity (P1/P2/P3) using a trained ML model
4. Sends everything to the LLM
5. Replies with root cause, recommended action, and relevant log lines

Bot reply example:
```
Severity: P2
Likely cause: memory leak in the payment processor worker.
Runbook says: restart the worker pod and check for unclosed DB connections.
Relevant logs: 3 OOM events in last 10 minutes on pod payments-api-7d9f
```

---

## Full Architecture

```
Alert fires (Slack command or Alertmanager webhook)
    ↓
[Classifier] → predicts severity (P1/P2/P3) and category     ← MLOps
    ↓
[RAG] → searches runbooks in ChromaDB vector store           ← AI Engineer
    ↓
[LLM Agent] → reasons over logs + runbook + alert            ← AI Engineer
    ↓
Slack reply to engineer
    ↓
[Evidently] monitors classifier input drift                   ← MLOps
    ↓
[GitHub Actions] auto-retrains if drift detected             ← MLOps/CI/CD
```

---

## Tech Stack

| Component | Tool | Why |
|---|---|---|
| LLM | Ollama + llama3.1:8b | Free, runs locally, no API key |
| LLM client | OpenAI Python SDK | Ollama is OpenAI API compatible |
| Vector DB | ChromaDB | Simple, runs locally, no setup |
| Embeddings | sentence-transformers | Free, runs locally |
| ML classifier | HuggingFace distilbert | Small model, fast to train |
| Experiment tracking | MLflow | Industry standard |
| Data versioning | DVC | Industry standard |
| Drift detection | Evidently AI | Industry standard |
| API server | FastAPI | Python, fast, simple |
| Slack bot | Slack Bolt SDK | Official Slack Python SDK |
| Container | Docker + Docker Compose | Standard |
| Deployment | Kubernetes + Helm | Already knows this |
| Monitoring | Prometheus + Grafana | Already knows this |
| CI/CD | GitHub Actions | Standard, free |

---

## Final Project Structure

```
sre-ai-copilot/
├── agent/
│   ├── analyze.py          # Core agent: takes alert, returns analysis
│   ├── tools.py            # Tools the LLM can call: get_logs, get_runbook
│   └── rag.py              # Vector search: indexes and queries runbooks
├── api/
│   └── main.py             # FastAPI app: POST /analyze endpoint
├── bot/
│   └── slack.py            # Slack bot: /oncall slash command
├── classifier/
│   ├── train.py            # Fine-tune distilbert on alert data
│   ├── evaluate.py         # Evaluate model: accuracy, F1
│   └── promote.py          # Compare new model vs current, promote if better
├── runbooks/
│   ├── high_memory.md
│   ├── disk_full.md
│   ├── high_cpu.md
│   └── db_connection.md
├── data/
│   └── alerts.csv          # Labeled training data: alert_text, category, severity
├── monitoring/
│   └── drift.py            # Evidently: detect drift in incoming alerts
├── helm/
│   └── sre-copilot/        # Helm chart for k8s deployment
├── .github/
│   └── workflows/
│       ├── train.yml       # CI: retrain on data change
│       └── deploy.yml      # CD: deploy on main push
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── NOTES.md                # This file
└── README.md
```

---

## Build Plan

### Phase 1 - Security & Hardening ✅ DONE
Focus: Make the agent production-shaped before adding intelligence.

- [x] Pluggable log backends (mock / kubernetes / elasticsearch)
- [x] PII scrubbing before logs reach the LLM
- [x] Input validation with Pydantic validators
- [x] API authentication (X-API-Key header)
- [x] Rate limiting (10 req/min per IP via slowapi)
- [x] Audit logging (alert name, service, duration)
- [x] Prometheus webhook endpoint
- [x] RBAC least-privilege service account (dedicated sre-copilot namespace)
- [x] Container scanning in CI (Trivy — CRITICAL/HIGH, ignore unfixed)
- [ ] TLS/HTTPS — moved to final phase (not needed until API exposed publicly)

### Phase 2 - Smarter Agent ✅ DONE
Focus: LLM drives the investigation instead of being passive.

- [x] Tool calling — LLM decides what to fetch instead of always fetching everything
- [x] LLM-as-judge — second LLM reviews answer before it reaches the user
- [x] Conversation memory — past incidents stored in ChromaDB, retrieved for similar alerts

#### What is missing for production (added to Phase 4)
- [ ] Memory feedback loop — mark incidents as resolved/wrong so bad advice doesn't persist
- [ ] Memory TTL — expire old incidents so stale context doesn't mislead the agent
- [ ] Memory deduplication — don't store duplicate incidents from repeated alerts
- [ ] Judge ground truth — evaluate against real resolved incidents, not just logs
- [ ] Tool calling reliability — needs a better model (GPT-4 / Claude) for reliable structured output
- [ ] Integration tests — verify end-to-end flow with known alerts and expected output format

### Phase 3 - MLOps Layer
Focus: Add real ML training pipeline on top of the agent.

- [ ] Track experiments with MLflow
- [ ] Version training data with DVC
- [ ] GitHub Actions CI: train → evaluate → promote on data push
- [ ] Add Evidently drift detection on incoming alerts
- [ ] Auto-trigger retraining when drift detected

### Phase 4 - Production Hardening
Focus: Close the gaps identified in Phase 2 + observability.

- [ ] Memory feedback loop (human marks incidents as resolved/wrong)
- [ ] Memory TTL and deduplication
- [ ] Judge ground truth dataset
- [ ] Integration tests for agent pipeline
- [ ] Prometheus metrics on FastAPI app
- [ ] Grafana dashboard
- [ ] TLS/HTTPS for API

### Phase 5 - LangChain/LangGraph Migration
Focus: Replace manual agent loop with proper framework.

- [ ] Migrate tool calling to LangChain tools
- [ ] Migrate memory to LangGraph state
- [ ] Migrate judge to LangChain evaluation chain
- [ ] Compare: what the framework gives vs what we built manually

### Phase 6 - Self-Healing (with approval)
Focus: Agent proposes fixes, human approves, agent executes.

- [ ] Agent suggests kubectl commands based on analysis
- [ ] Slack approval flow (approve/reject buttons)
- [ ] Agent executes approved commands via kubernetes backend
- [ ] Full audit trail of every action taken

---

## Progress Tracker

### Completed
- Nothing yet

### In Progress
- Day 1: Setup

### Blocked
- Nothing

---

## Day by Day - Detailed Steps

---

### DAY 1: Setup + First LLM Call

**Goal:** Have a Python script that sends a fake alert to a local LLM and prints the analysis.

#### Step 1 - Open terminal and go to Documents
```bash
cd ~/Documents
```

#### Step 2 - The folder was already created at ~/Documents/sre-ai-copilot
```bash
cd sre-ai-copilot
```

#### Step 3 - Initialize Git
```bash
git init
```
What this does: Tells Git to start tracking this folder. Creates a hidden .git folder.
Every change you make can now be saved as a commit.

#### Step 4 - Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```
What this does: Creates an isolated Python environment. Packages you install here
won't affect other Python projects on your machine.
You'll know it's active when you see (venv) at the start of your terminal line.

#### Step 5 - Create .gitignore
```bash
cat > .gitignore << 'EOF'
venv/
__pycache__/
*.pyc
.env
chroma_db/
mlruns/
*.model
EOF
```
What this does: Tells Git to ignore these folders/files so they don't get committed.

#### Step 6 - Install Ollama
```bash
brew install ollama
```
What this does: Installs Ollama — a tool that runs AI models locally on your machine.
Think of it like Docker but for AI models.

#### Step 7 - Download the AI model
```bash
ollama pull llama3.1:8b
```
What this does: Downloads the llama3.1:8b model (~4-5GB).
8b = 8 billion parameters. This is the "brain" your app uses to think.
This works on 18GB RAM with good performance.

#### Step 8 - Start Ollama server
```bash
ollama serve
```
What this does: Starts Ollama as a local HTTP server on http://localhost:11434
Your Python code sends requests to this address — like calling an API but it's local.
IMPORTANT: Keep this terminal tab open. Open a new tab for the next steps.

#### Step 9 - In new terminal tab, activate venv and install packages
```bash
cd ~/Documents/sre-ai-copilot
source venv/bin/activate
pip install openai
```
What this does: Installs the OpenAI Python SDK.
Even though we use Ollama (not OpenAI), Ollama speaks the exact same API format.
So we use the OpenAI package but point it to localhost instead of OpenAI servers.

#### Step 10 - Create the agent folder and first script
```bash
mkdir agent
```

Create the file `agent/analyze.py` with this content:

```python
from openai import OpenAI

# Connect to local Ollama server instead of OpenAI servers
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Ollama doesn't check the key, but the field is required
)

# Fake alert - later this will come from Alertmanager or Slack
alert = "HighMemoryUsage on service payments-api, memory at 95%"

# Send the alert to the LLM
response = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[
        {
            "role": "system",  # Tells the model what role it plays
            "content": "You are an SRE assistant. When given an alert, analyze it and suggest the most likely root cause and what the engineer should do."
        },
        {
            "role": "user",  # The actual input
            "content": alert
        }
    ]
)

# Print the model's reply
print(response.choices[0].message.content)
```

#### Step 11 - Run it
```bash
python agent/analyze.py
```

You should see the LLM analyze the alert and suggest what to do.
If it works, Day 1 is done.

#### Step 12 - Save progress with Git
```bash
git add agent/analyze.py .gitignore
git commit -m "Day 1: first LLM call via Ollama"
```

---

### DAY 2: Tool Calling

**Goal:** The LLM agent can automatically call functions you define — get_logs and get_runbook.

**Concept:** Tool calling means you give the LLM a list of functions it can use.
When it decides it needs more info (like logs), it tells your code to call that function,
gets the result, and continues reasoning. The LLM decides WHEN to call tools — you don't hardcode it.

Create `agent/tools.py`:

```python
import json

# These are fake functions for now - later they'll call real Loki/k8s APIs

def get_logs(service_name: str) -> str:
    """Fetch recent logs for a service"""
    # Fake logs - replace with real Loki API call in Phase 3
    fake_logs = {
        "payments-api": """
            2024-01-15 02:13:45 ERROR OOMKilled: container exceeded memory limit
            2024-01-15 02:13:40 WARN  Memory usage at 94%, approaching limit
            2024-01-15 02:13:35 WARN  Memory usage at 91%, approaching limit
            2024-01-15 02:12:10 INFO  Processing payment batch #4821
            2024-01-15 02:11:55 INFO  DB connection pool: 45/50 connections used
        """,
        "auth-service": """
            2024-01-15 02:13:45 ERROR Connection timeout to redis:6379
            2024-01-15 02:13:30 WARN  Redis response time > 500ms
            2024-01-15 02:13:00 INFO  Token validation request from user 8821
        """
    }
    return fake_logs.get(service_name, f"No logs found for service: {service_name}")


def get_runbook(alert_name: str) -> str:
    """Fetch the runbook for a specific alert"""
    # Fake runbooks - later replaced by RAG (ChromaDB search)
    fake_runbooks = {
        "HighMemoryUsage": """
            RUNBOOK: HighMemoryUsage
            1. Check which pod is consuming memory: kubectl top pods -n <namespace>
            2. Check for memory leaks in recent deployments: kubectl rollout history
            3. If OOMKilled: kubectl rollout undo deployment/<name>
            4. Check DB connection pool - unclosed connections cause memory buildup
            5. Restart the affected pod if immediate relief needed: kubectl rollout restart
        """,
        "DiskFull": """
            RUNBOOK: DiskFull
            1. Check disk usage: df -h
            2. Find large files: du -sh /* | sort -rh | head -20
            3. Clean /tmp: rm -rf /tmp/*
            4. Check log rotation is configured properly
            5. Archive or delete old logs if needed
        """
    }
    return fake_runbooks.get(alert_name, f"No runbook found for: {alert_name}")


# This is the tool definitions in the format the LLM understands
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_logs",
            "description": "Fetch recent logs for a specific service to help diagnose the issue",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "The name of the service to get logs for"
                    }
                },
                "required": ["service_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_runbook",
            "description": "Fetch the runbook (step by step instructions) for handling a specific alert",
            "parameters": {
                "type": "object",
                "properties": {
                    "alert_name": {
                        "type": "string",
                        "description": "The name of the alert to get the runbook for"
                    }
                },
                "required": ["alert_name"]
            }
        }
    }
]


def run_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool by name and return the result"""
    if tool_name == "get_logs":
        return get_logs(tool_input["service_name"])
    elif tool_name == "get_runbook":
        return get_runbook(tool_input["alert_name"])
    else:
        return f"Unknown tool: {tool_name}"
```

Update `agent/analyze.py` to use tools:

```python
import json
from openai import OpenAI
from tools import TOOLS, run_tool

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

def analyze_alert(alert: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are an SRE assistant. Analyze alerts using the available tools to gather logs and runbooks. Always call get_logs and get_runbook before giving your final analysis."
        },
        {
            "role": "user",
            "content": alert
        }
    ]

    # Agent loop - keep going until the LLM is done calling tools
    while True:
        response = client.chat.completions.create(
            model="llama3.1:8b",
            messages=messages,
            tools=TOOLS
        )

        message = response.choices[0].message

        # If no tool calls, the LLM is done - return the final answer
        if not message.tool_calls:
            return message.content

        # Add the LLM's response to message history
        messages.append({"role": "assistant", "content": message.content, "tool_calls": message.tool_calls})

        # Execute each tool the LLM requested
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)

            print(f"[Agent] Calling tool: {tool_name} with {tool_input}")
            result = run_tool(tool_name, tool_input)

            # Add tool result to message history so LLM can use it
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })


if __name__ == "__main__":
    alert = "HighMemoryUsage on service payments-api, memory at 95%"
    print(f"Alert: {alert}\n")
    print("Analysis:")
    print(analyze_alert(alert))
```

Run it:
```bash
python agent/analyze.py
```

You should see the agent calling get_logs and get_runbook automatically, then giving a full analysis.

---

### DAY 3: RAG with ChromaDB

**Goal:** Replace hardcoded runbooks with real markdown files searched via vector similarity.

**Concept:** RAG = Retrieval Augmented Generation.
- You store your runbooks as text in a vector database (ChromaDB)
- When an alert comes in, you convert it to a vector (embedding) and find the most similar runbook
- You inject that runbook into the LLM's context automatically
- This scales to hundreds of runbooks — no hardcoding

Install packages:
```bash
pip install chromadb sentence-transformers
```

Create runbook files in `runbooks/`:

`runbooks/high_memory.md`:
```markdown
# HighMemoryUsage Runbook

## Symptoms
- Memory usage above 90%
- OOMKilled events in logs
- Pod restarts

## Steps
1. Check which pod is consuming memory: `kubectl top pods -n <namespace>`
2. Check for memory leaks in recent deployments: `kubectl rollout history deployment/<name>`
3. If OOMKilled: `kubectl rollout undo deployment/<name>`
4. Check DB connection pool — unclosed connections cause memory buildup
5. Restart if needed: `kubectl rollout restart deployment/<name>`

## Escalate if
- Memory leak persists after restart
- Multiple pods affected
```

`runbooks/disk_full.md`:
```markdown
# DiskFull Runbook

## Symptoms
- Disk usage above 85%
- Write errors in logs

## Steps
1. Check disk usage: `df -h`
2. Find large files: `du -sh /* | sort -rh | head -20`
3. Clean /tmp: `rm -rf /tmp/*`
4. Check log rotation config
5. Archive old logs if needed

## Escalate if
- Disk fills up faster than expected
- Unable to free enough space
```

Create `agent/rag.py`:

```python
import chromadb
from chromadb.utils import embedding_functions
import os

# Use a local embedding model - no API key needed
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"  # Small, fast, free model
)

# Create ChromaDB client - stores data locally in chroma_db/ folder
chroma_client = chromadb.PersistentClient(path="./chroma_db")

def index_runbooks(runbooks_dir: str = "./runbooks"):
    """Read all .md files in runbooks/ and store them in ChromaDB"""
    collection = chroma_client.get_or_create_collection(
        name="runbooks",
        embedding_function=embedding_fn
    )

    documents = []
    ids = []

    for filename in os.listdir(runbooks_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(runbooks_dir, filename)
            with open(filepath, "r") as f:
                content = f.read()
            documents.append(content)
            ids.append(filename.replace(".md", ""))

    if documents:
        collection.upsert(documents=documents, ids=ids)
        print(f"Indexed {len(documents)} runbooks")

    return collection


def search_runbooks(query: str, n_results: int = 1) -> str:
    """Find the most relevant runbook for a given alert"""
    collection = chroma_client.get_or_create_collection(
        name="runbooks",
        embedding_function=embedding_fn
    )

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    if results["documents"] and results["documents"][0]:
        return results["documents"][0][0]

    return "No relevant runbook found"


if __name__ == "__main__":
    # Test: index runbooks and search
    index_runbooks()
    result = search_runbooks("memory usage high, OOMKilled")
    print(result)
```

Update `agent/tools.py` to use RAG instead of hardcoded runbooks:

```python
# Replace the get_runbook function with:
from rag import search_runbooks

def get_runbook(alert_name: str) -> str:
    """Search runbooks using vector similarity"""
    return search_runbooks(alert_name)
```

Run:
```bash
# First index the runbooks
python agent/rag.py

# Then test the full agent
python agent/analyze.py
```

---

### DAY 4: FastAPI Endpoint

**Goal:** Expose the agent as an HTTP API so anything (Slack, Alertmanager, curl) can call it.

Install:
```bash
pip install fastapi uvicorn
```

Create `api/main.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel
import sys
sys.path.append("./agent")

from analyze import analyze_alert
from rag import index_runbooks

app = FastAPI(title="SRE AI Copilot")

# Index runbooks when the app starts
@app.on_event("startup")
def startup():
    index_runbooks()

class AlertRequest(BaseModel):
    alert: str

class AlertResponse(BaseModel):
    analysis: str

@app.post("/analyze", response_model=AlertResponse)
def analyze(request: AlertRequest):
    result = analyze_alert(request.alert)
    return AlertResponse(analysis=result)

@app.get("/health")
def health():
    return {"status": "ok"}
```

Run it:
```bash
uvicorn api.main:app --reload
```

Test it with curl:
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"alert": "HighMemoryUsage on service payments-api"}'
```

Or open http://localhost:8000/docs in browser for auto-generated API docs.

---

### DAY 5: Slack Bot

**Goal:** /oncall command in Slack that calls your FastAPI and replies with analysis.

Setup Slack app:
1. Go to api.slack.com/apps
2. Create New App → From scratch
3. Name it "SRE Copilot", pick your workspace
4. Go to "Slash Commands" → Create New Command
   - Command: /oncall
   - Request URL: your server URL (use ngrok for local testing: ngrok http 3000)
5. Go to "OAuth & Permissions" → Bot Token Scopes → add: commands, chat:write
6. Install to workspace
7. Copy the Bot Token (starts with xoxb-)
8. Copy the Signing Secret from Basic Information

Install:
```bash
pip install slack-bolt requests
```

Create `bot/slack.py`:

```python
import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.command("/oncall")
def handle_oncall(ack, say, command):
    ack()  # Must acknowledge within 3 seconds

    alert = command["text"]

    if not alert:
        say("Please provide an alert. Usage: /oncall <alert description>")
        return

    say(f"Analyzing alert: `{alert}`...")

    # Call your FastAPI
    response = requests.post(
        "http://localhost:8000/analyze",
        json={"alert": alert}
    )

    if response.ok:
        analysis = response.json()["analysis"]
        say(f"*Analysis:*\n{analysis}")
    else:
        say("Error analyzing alert. Check the logs.")


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
```

Run:
```bash
export SLACK_BOT_TOKEN=xoxb-your-token
export SLACK_APP_TOKEN=xapp-your-token
python bot/slack.py
```

---

### DAY 6: Docker

**Goal:** Package the app so it runs anywhere with one command.

Create `requirements.txt`:
```bash
pip freeze > requirements.txt
```

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
    volumes:
      - ./chroma_db:/app/chroma_db
      - ./runbooks:/app/runbooks

  slack-bot:
    build: .
    command: python bot/slack.py
    environment:
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
      - SLACK_APP_TOKEN=${SLACK_APP_TOKEN}
      - API_URL=http://app:8000
    depends_on:
      - app
```

Run:
```bash
docker compose up --build
```

---

### DAY 7: Deploy to k8s + Push to GitHub

**Goal:** Deploy with Helm, push everything to GitHub.

Create GitHub repo:
1. Go to github.com → New repository
2. Name: sre-ai-copilot
3. Private for now
4. Don't add README (you already have files)

Push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/sre-ai-copilot.git
git add .
git commit -m "Week 1 complete: AI agent with RAG, FastAPI, Slack bot, Docker"
git push -u origin main
```

Create basic Helm chart:
```bash
mkdir -p helm/sre-copilot/templates
```

`helm/sre-copilot/Chart.yaml`:
```yaml
apiVersion: v2
name: sre-copilot
description: SRE AI Copilot
version: 0.1.0
```

`helm/sre-copilot/values.yaml`:
```yaml
replicaCount: 1
image:
  repository: sre-copilot
  tag: latest
service:
  port: 8000
```

Deploy:
```bash
helm install sre-copilot ./helm/sre-copilot
```

---

### WEEK 2-3: MLOps Layer

**Goal:** Add a real ML classifier that predicts alert severity (P1/P2/P3) and category (network/storage/app/database).

---

#### STEP 1 - Install MLOps packages
```bash
pip install transformers datasets scikit-learn mlflow dvc torch
```

---

#### STEP 2 - Generate training data

**Concept:** You need labeled data to train a classifier. Each row is an alert text + its correct label.
We generate fake data because we don't have real production alerts.

Create `data/generate_data.py`:

```python
import csv
import random

# Fake alerts per category
templates = {
    "memory": [
        "HighMemoryUsage on service {svc}, memory at {pct}%",
        "OOMKilled on pod {svc}-{id}, container exceeded memory limit",
        "Memory pressure on node {node}, {pct}% used",
    ],
    "disk": [
        "DiskFull on node {node}, disk at {pct}%",
        "Low disk space on {svc}, only {gb}GB remaining",
        "PersistentVolume {svc}-pvc is {pct}% full",
    ],
    "cpu": [
        "HighCPUUsage on service {svc}, CPU at {pct}%",
        "CPU throttling detected on pod {svc}-{id}",
        "Node {node} CPU usage exceeded threshold: {pct}%",
    ],
    "network": [
        "High latency on service {svc}, p99={ms}ms",
        "Connection timeout between {svc} and {svc2}",
        "Packet loss detected on {node}: {pct}%",
    ],
    "database": [
        "DB connection pool exhausted on {svc}: {n}/{max} connections used",
        "Slow query detected on {svc} database: {ms}ms",
        "Replication lag on {svc}-db: {s} seconds behind",
    ]
}

services = ["payments-api", "auth-service", "user-service", "orders-api", "inventory-api"]
nodes = ["node-01", "node-02", "node-03"]

rows = []
for category, tmpl_list in templates.items():
    for _ in range(60):  # 60 examples per category = 300 total
        tmpl = random.choice(tmpl_list)
        alert = tmpl.format(
            svc=random.choice(services),
            svc2=random.choice(services),
            node=random.choice(nodes),
            pct=random.randint(85, 99),
            id=random.randint(1000, 9999),
            gb=random.randint(1, 10),
            ms=random.randint(500, 5000),
            n=random.randint(45, 50),
            max=50,
            s=random.randint(10, 300),
        )
        rows.append({"alert": alert, "category": category})

# Shuffle and write
random.shuffle(rows)
with open("data/alerts.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["alert", "category"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} training examples")
```

Run it:
```bash
mkdir data
python data/generate_data.py
```

---

#### STEP 3 - Version the data with DVC

**Concept:** DVC is like Git but for data files. Instead of committing a big CSV to Git,
you commit a small .dvc pointer file. The actual data is stored separately (local or S3).

```bash
dvc init
dvc add data/alerts.csv
git add data/alerts.csv.dvc data/.gitignore
git commit -m "Add training data with DVC"
```

What this does:
- `dvc init` sets up DVC in your repo
- `dvc add data/alerts.csv` creates `data/alerts.csv.dvc` (a small pointer file)
- Git tracks the pointer, DVC tracks the actual data

---

#### STEP 4 - Train the classifier

**Concept:** Fine-tuning means taking a pretrained model (distilbert — already knows English)
and training it further on your specific task (classifying alerts).
This is much faster than training from scratch.

Create `classifier/train.py`:

```python
import mlflow
import mlflow.transformers
import pandas as pd
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np
import torch

# Load data
df = pd.read_csv("data/alerts.csv")

# Encode labels: "memory" → 0, "disk" → 1, etc.
le = LabelEncoder()
df["label"] = le.fit_transform(df["category"])
label_names = le.classes_.tolist()

print(f"Categories: {label_names}")
print(f"Total samples: {len(df)}")

# Split into train and test
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# Convert to HuggingFace Dataset format
train_dataset = Dataset.from_pandas(train_df[["alert", "label"]])
test_dataset = Dataset.from_pandas(test_df[["alert", "label"]])

# Load tokenizer - converts text to numbers the model understands
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

def tokenize(batch):
    return tokenizer(batch["alert"], truncation=True, padding=True, max_length=128)

train_dataset = train_dataset.map(tokenize, batched=True)
test_dataset = test_dataset.map(tokenize, batched=True)

# Load model - distilbert pretrained on English, we add a classification head
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=len(label_names),
    id2label={i: l for i, l in enumerate(label_names)},
    label2id={l: i for i, l in enumerate(label_names)},
)

# Training configuration
training_args = TrainingArguments(
    output_dir="./classifier/output",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    logging_dir="./classifier/logs",
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = (predictions == labels).mean()
    return {"accuracy": float(accuracy)}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
)

# Track with MLflow
with mlflow.start_run():
    mlflow.log_param("model", "distilbert-base-uncased")
    mlflow.log_param("epochs", 3)
    mlflow.log_param("train_size", len(train_df))
    mlflow.log_param("test_size", len(test_df))
    mlflow.log_param("categories", str(label_names))

    print("Training...")
    trainer.train()

    # Evaluate
    results = trainer.evaluate()
    accuracy = results["eval_accuracy"]

    mlflow.log_metric("accuracy", accuracy)
    print(f"Accuracy: {accuracy:.4f}")

    # Save model
    trainer.save_model("./classifier/model")
    tokenizer.save_pretrained("./classifier/model")

    # Save label encoder
    import json
    with open("./classifier/model/labels.json", "w") as f:
        json.dump(label_names, f)

    print("Model saved to ./classifier/model")
```

Run:
```bash
python classifier/train.py
```

Then open MLflow UI to see your experiment:
```bash
mlflow ui
# Open http://localhost:5000 in browser
```

You'll see accuracy, parameters, and the run logged there.

---

#### STEP 5 - Evaluate and promote

**Concept:** Before replacing your current model with a new one, check if the new one is actually better.
This is the "champion vs challenger" pattern.

Create `classifier/evaluate.py`:

```python
import json
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def load_model(path: str):
    tokenizer = AutoTokenizer.from_pretrained(path)
    model = AutoModelForSequenceClassification.from_pretrained(path)
    model.eval()
    return tokenizer, model

def predict(tokenizer, model, texts: list) -> list:
    inputs = tokenizer(texts, truncation=True, padding=True, max_length=128, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=-1).tolist()
    return predictions

def evaluate_model(model_path: str, test_csv: str) -> float:
    df = pd.read_csv(test_csv)
    tokenizer, model = load_model(model_path)

    with open(f"{model_path}/labels.json") as f:
        labels = json.load(f)

    label2id = {l: i for i, l in enumerate(labels)}
    true_labels = [label2id[c] for c in df["category"]]
    predicted = predict(tokenizer, model, df["alert"].tolist())

    accuracy = sum(p == t for p, t in zip(predicted, true_labels)) / len(true_labels)
    return accuracy

if __name__ == "__main__":
    acc = evaluate_model("./classifier/model", "data/alerts.csv")
    print(f"Model accuracy: {acc:.4f}")
```

Create `classifier/promote.py`:

```python
import json
import os
import shutil

CURRENT_MODEL = "./classifier/production_model"
NEW_MODEL = "./classifier/model"
THRESHOLD = 0.85  # Only promote if accuracy > 85%

from evaluate import evaluate_model

new_acc = evaluate_model(NEW_MODEL, "data/alerts.csv")
print(f"New model accuracy: {new_acc:.4f}")

if os.path.exists(CURRENT_MODEL):
    current_acc = evaluate_model(CURRENT_MODEL, "data/alerts.csv")
    print(f"Current model accuracy: {current_acc:.4f}")

    if new_acc > current_acc and new_acc >= THRESHOLD:
        shutil.copytree(NEW_MODEL, CURRENT_MODEL, dirs_exist_ok=True)
        print(f"Promoted new model ({new_acc:.4f} > {current_acc:.4f})")
    else:
        print(f"Keeping current model ({current_acc:.4f} >= {new_acc:.4f})")
else:
    if new_acc >= THRESHOLD:
        shutil.copytree(NEW_MODEL, CURRENT_MODEL)
        print(f"Promoted first model with accuracy {new_acc:.4f}")
    else:
        print(f"Model accuracy {new_acc:.4f} below threshold {THRESHOLD}, not promoting")
```

---

#### STEP 6 - Wire classifier into the agent

Update `api/main.py` to classify severity before calling the LLM:

```python
from fastapi import FastAPI
from pydantic import BaseModel
import sys
import json
sys.path.append("./agent")
sys.path.append("./classifier")

from analyze import analyze_alert
from rag import index_runbooks
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

app = FastAPI(title="SRE AI Copilot")

# Load classifier at startup
classifier_tokenizer = None
classifier_model = None
label_names = []

@app.on_event("startup")
def startup():
    global classifier_tokenizer, classifier_model, label_names
    index_runbooks()

    model_path = "./classifier/production_model"
    if os.path.exists(model_path):
        classifier_tokenizer = AutoTokenizer.from_pretrained(model_path)
        classifier_model = AutoModelForSequenceClassification.from_pretrained(model_path)
        classifier_model.eval()
        with open(f"{model_path}/labels.json") as f:
            label_names = json.load(f)
        print("Classifier loaded")

def classify_alert(alert: str) -> str:
    if classifier_model is None:
        return "unknown"
    inputs = classifier_tokenizer(alert, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        outputs = classifier_model(**inputs)
    pred_id = torch.argmax(outputs.logits, dim=-1).item()
    return label_names[pred_id]

class AlertRequest(BaseModel):
    alert: str

class AlertResponse(BaseModel):
    category: str
    analysis: str

@app.post("/analyze", response_model=AlertResponse)
def analyze(request: AlertRequest):
    category = classify_alert(request.alert)
    analysis = analyze_alert(request.alert)
    return AlertResponse(category=category, analysis=analysis)

@app.get("/health")
def health():
    return {"status": "ok"}
```

---

#### STEP 7 - GitHub Actions CI for ML

**Concept:** Every time you push new training data, GitHub automatically retrains the model,
evaluates it, and promotes it if it's better. No manual work.

Create `.github/workflows/train.yml`:

```yaml
name: Train and Promote Model

on:
  push:
    paths:
      - 'data/**'        # Only trigger when data changes
      - 'classifier/**'  # Or when classifier code changes

jobs:
  train:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Pull data with DVC
        run: dvc pull

      - name: Train model
        run: python classifier/train.py

      - name: Evaluate and promote
        run: python classifier/promote.py

      - name: Commit promoted model
        run: |
          git config user.email "ci@github.com"
          git config user.name "GitHub Actions"
          git add classifier/production_model/
          git commit -m "CI: promote new model" || echo "No changes to commit"
          git push
```

---

#### STEP 8 - Git commit for Week 2-3
```bash
git add .
git commit -m "Week 2-3: MLOps layer - classifier, MLflow, DVC, GitHub Actions CI"
git push
```

---

### WEEK 4-5: Production Ready

**Goal:** Add monitoring, drift detection, polish the repo for public visibility.

---

#### STEP 1 - Add Prometheus metrics to FastAPI

**Concept:** Prometheus scrapes metrics from your app (how many requests, how fast, errors).
Grafana visualizes them. You already know this — it's the same as your SRE work.

Install:
```bash
pip install prometheus-fastapi-instrumentator
```

Update `api/main.py` — add after `app = FastAPI(...)`:

```python
from prometheus_fastapi_instrumentator import Instrumentator

# This auto-adds /metrics endpoint with request count, latency, etc.
Instrumentator().instrument(app).expose(app)
```

Also add custom metrics:

```python
from prometheus_client import Counter, Histogram

alert_categories = Counter(
    "alert_category_total",
    "Number of alerts per category",
    ["category"]
)

analysis_latency = Histogram(
    "analysis_latency_seconds",
    "Time to analyze an alert"
)
```

Use them in your endpoint:

```python
import time

@app.post("/analyze", response_model=AlertResponse)
def analyze(request: AlertRequest):
    start = time.time()
    category = classify_alert(request.alert)
    analysis = analyze_alert(request.alert)
    alert_categories.labels(category=category).inc()
    analysis_latency.observe(time.time() - start)
    return AlertResponse(category=category, analysis=analysis)
```

---

#### STEP 2 - Drift Detection with Evidently

**Concept:** Drift means the real alerts your app sees start looking different from
your training data. For example, if a new service gets deployed and generates alert types
you've never seen. Evidently detects this automatically.

Install:
```bash
pip install evidently
```

Create `monitoring/drift.py`:

```python
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TextOverviewPreset
from evidently.pipeline.column_mapping import ColumnMapping
import os
import json
from datetime import datetime

REFERENCE_DATA_PATH = "data/alerts.csv"
PRODUCTION_LOG_PATH = "monitoring/production_log.csv"
DRIFT_REPORT_PATH = "monitoring/drift_report.html"
DRIFT_THRESHOLD = 0.3  # If drift score > 0.3, trigger retraining

def log_production_alert(alert: str, category: str):
    """Log each incoming alert for drift monitoring"""
    row = {"alert": alert, "category": category, "timestamp": datetime.now().isoformat()}
    df = pd.DataFrame([row])

    if os.path.exists(PRODUCTION_LOG_PATH):
        df.to_csv(PRODUCTION_LOG_PATH, mode="a", header=False, index=False)
    else:
        df.to_csv(PRODUCTION_LOG_PATH, index=False)

def check_drift() -> bool:
    """Compare recent production alerts against training data. Returns True if drift detected."""
    if not os.path.exists(PRODUCTION_LOG_PATH):
        print("No production data yet")
        return False

    reference = pd.read_csv(REFERENCE_DATA_PATH)
    production = pd.read_csv(PRODUCTION_LOG_PATH)

    if len(production) < 50:
        print(f"Not enough production data yet ({len(production)} samples, need 50)")
        return False

    # Run Evidently drift report
    report = Report(metrics=[DataDriftPreset()])
    report.run(
        reference_data=reference[["alert", "category"]],
        current_data=production[["alert", "category"]].tail(200),  # last 200 alerts
    )

    report.save_html(DRIFT_REPORT_PATH)
    print(f"Drift report saved to {DRIFT_REPORT_PATH}")

    # Get drift score
    report_dict = report.as_dict()
    drift_score = report_dict["metrics"][0]["result"]["dataset_drift"]

    print(f"Drift detected: {drift_score}")
    return drift_score

if __name__ == "__main__":
    drift_detected = check_drift()
    if drift_detected:
        print("WARNING: Data drift detected! Consider retraining the model.")
    else:
        print("No significant drift detected.")
```

Call `log_production_alert` inside your FastAPI endpoint to record every incoming alert:

```python
# In api/main.py, inside the analyze endpoint:
from monitoring.drift import log_production_alert

@app.post("/analyze", response_model=AlertResponse)
def analyze(request: AlertRequest):
    category = classify_alert(request.alert)
    analysis = analyze_alert(request.alert)
    log_production_alert(request.alert, category)  # Log for drift monitoring
    return AlertResponse(category=category, analysis=analysis)
```

Add a drift check endpoint:
```python
@app.get("/drift")
def drift_check():
    from monitoring.drift import check_drift
    drift_detected = check_drift()
    return {"drift_detected": drift_detected}
```

---

#### STEP 3 - Add drift check to GitHub Actions

Update `.github/workflows/train.yml` to also run drift check:

```yaml
  drift-check:
    runs-on: ubuntu-latest
    needs: train
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - name: Check for drift
        run: python monitoring/drift.py
```

---

#### STEP 4 - Add Grafana dashboard

Add Grafana and Prometheus to `docker-compose.yml`:

```yaml
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus
```

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sre-copilot'
    static_configs:
      - targets: ['app:8000']
```

Open Grafana at http://localhost:3001 (admin/admin), add Prometheus as datasource,
create a dashboard with:
- Total alerts analyzed (alert_category_total)
- Analysis latency (analysis_latency_seconds)
- Alerts per category breakdown

---

#### STEP 5 - Write the README

Create `README.md`:

```markdown
# SRE AI Copilot

An AI-powered assistant for on-call SRE engineers. Reduces alert triage time from 20 minutes to under 10 seconds.

## Demo

[Add GIF here]

## Architecture

[Add diagram here]

## Features

- **AI Agent**: Analyzes alerts, fetches logs, searches runbooks automatically
- **RAG**: Vector search over runbooks using ChromaDB
- **ML Classifier**: Fine-tuned distilbert predicts alert category and severity
- **Experiment Tracking**: MLflow tracks all training runs
- **Data Versioning**: DVC versions training datasets
- **Drift Detection**: Evidently monitors production data drift
- **CI/CD for ML**: GitHub Actions retrains and promotes models automatically
- **Slack Bot**: /oncall slash command for engineers
- **Monitoring**: Prometheus + Grafana dashboard

## Tech Stack

LLM: Ollama + llama3.1:8b | RAG: ChromaDB | ML: HuggingFace distilbert
MLOps: MLflow + DVC + Evidently | API: FastAPI | Bot: Slack Bolt
Deploy: Docker + Kubernetes + Helm | Monitoring: Prometheus + Grafana

## Quick Start

```bash
# Start Ollama
ollama serve

# Start the app
docker compose up

# Test it
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"alert": "HighMemoryUsage on payments-api"}'
```

## Project Structure

[Paste the structure from NOTES.md]
```

---

#### STEP 6 - Make repo public and final commit

```bash
git add .
git commit -m "Week 4-5: drift detection, Prometheus metrics, Grafana, README"
git push
```

Then on GitHub: Settings → scroll down → Change visibility → Public

---

#### STEP 7 - Record a demo GIF

1. Install `brew install --cask licecap` (free GIF recorder for Mac)
2. Open Slack, type `/oncall HighMemoryUsage on payments-api`
3. Record the bot replying
4. Add the GIF to your README

This makes a massive difference in how your repo is perceived.

---

## Resources

| Topic | Link |
|---|---|
| Ollama | https://ollama.com |
| Ollama tool calling | https://ollama.com/blog/tool-support |
| ChromaDB | https://docs.trychroma.com |
| FastAPI | https://fastapi.tiangolo.com/tutorial |
| Slack Bolt Python | https://slack.dev/bolt-python/tutorial/getting-started |
| HuggingFace fine-tuning | https://huggingface.co/docs/transformers/training |
| MLflow | https://mlflow.org/docs/latest/quickstart.html |
| DVC | https://dvc.org/doc/start |
| Evidently | https://docs.evidentlyai.com/get-started/quickstart |

---

## Notes for the AI Assistant Reading This

- The user is an SRE/DevOps engineer learning AI/ML from scratch
- Explain concepts simply, use analogies to things they know (k8s, Docker, APIs)
- They cannot pay for APIs — always use Ollama (free, local)
- Their machine: MacBook, 18GB RAM, macOS — use llama3.1:8b model
- They want detailed step-by-step explanations, not just code
- Check the Progress Tracker section to know where they left off
- Update the Progress Tracker when tasks are completed
- Days 2-7 code is already written above — walk them through it step by step
