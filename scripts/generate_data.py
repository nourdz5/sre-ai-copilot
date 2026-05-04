import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI

client = OpenAI(
    base_url=os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/v1/",
    api_key="ollama",
)

ALERT_TYPES = [
    "HighCPU", "DiskFull", "PodCrashLooping",
    "HighLatency", "DatabaseDown", "ConnectionTimeout",
    "OOMKilled", "NodeNotReady", "ServiceUnavailable",
    "HighMemoryUsage", "NetworkPartition", "CertificateExpiring",
    "ReplicaSetDown", "PersistentVolumeError", "IngressDown",
    "RedisDown", "KafkaLag", "ElasticsearchDown",
    "SlowQuery", "HighErrorRate"
]

def generate_runbook(alert_name):
    print(f"Generating runbook for {alert_name}...")
    response = client.chat.completions.create(
        model=os.environ.get("LLM_MODEL", "llama3.1:8b"),
        messages=[
            {
                "role": "system",
                "content": "You are a senior SRE. Write detailed runbooks in markdown format."
            },
            {
                "role": "user",
                "content": f"""Write a detailed SRE runbook for alert: {alert_name}

                Include these sections:
                ## Description
                ## Likely Causes
                ## Steps to Diagnose
                ## Steps to Fix
                ## Escalate if

                Use kubectl commands where relevant. Be specific and practical."""
            }
        ],
        timeout=60
    )
    return response.choices[0].message.content


def generate_training_data(n=100):
    print(f"Generating {n} training examples...")
    response = client.chat.completions.create(
        model=os.environ.get("LLM_MODEL", "llama3.1:8b"),
        messages=[
            {
                "role": "system",
                "content": "You generate realistic labeled alert data for ML training. Output only CSV rows, no headers, no explanation."
            },
            {
                "role": "user",
                "content": f"""Generate {n} realistic alert text examples with labels.

                Format: "alert text",LABEL

                Labels:
                - P1 = critical, system down or data loss risk
                - P2 = degraded performance, impacting users
                - P3 = warning, not yet impacting users

                Examples:
                "Database connection pool exhausted on payments-api, 0 connections available",P1
                "High CPU usage on auth-service at 85% for 10 minutes",P2
                "Disk usage at 72% on logging server",P3

                Generate {n} diverse examples across different services and alert types."""
            }
        ],
        timeout=120
    )
    return response.choices[0].message.content


def save_runbook(alert_name, content):
    path = f"runbooks/{alert_name.lower()}.md"
    with open(path, "w") as f:
        f.write(f"# {alert_name}\n\n{content}")
    print(f"Saved {path}")


def save_training_data(csv_content):
    lines = csv_content.strip().split("\n")
    valid_lines = []
    for line in lines:
        line = line.strip()
        if line and ("P1" in line or "P2" in line or "P3" in line):
            valid_lines.append(line)

    with open("data/alerts.csv", "a") as f:
        for line in valid_lines:
            f.write(line + "\n")

    print(f"Added {len(valid_lines)} training examples to data/alerts.csv")


if __name__ == "__main__":
    # Generate runbooks
    for alert in ALERT_TYPES:
        content = generate_runbook(alert)
        save_runbook(alert, content)

    # Generate training data in batches of 100
    print("\nGenerating training data...")
    for batch in range(10):  # 10 batches × 100 = 1000 examples
        print(f"Batch {batch + 1}/10...")
        csv_content = generate_training_data(100)
        save_training_data(csv_content)

    print("\nDone! Now run:")
    print("  python agent/rag.py        # re-index runbooks")
    print("  python classifier/train.py # retrain classifier")
