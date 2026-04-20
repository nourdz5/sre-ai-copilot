import sys
sys.path.insert(0, "/Users/nourdziri/Documents/sre-ai-copilot")

from openai import OpenAI
import csv

client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
)

def generate_alerts(severity, count):
    response = client.chat.completions.create(
        model="llama3.1:8b",
        messages=[
            {
                "role": "user",
                "content": f"""Generate {count} realistic SRE alert messages that would be classified as {severity} severity.
{severity} means: {'service is down or data loss' if severity == 'P1' else 'service degraded but running' if severity == 'P2' else 'warning, nothing urgent'}.
Return ONLY the alert messages, one per line, no numbering, no extra text."""
            }
        ]
    )
    lines = response.choices[0].message.content.strip().split("\n")
    return [line.strip().strip('"') for line in lines if line.strip()]

with open("data/alerts.csv", "a", newline="") as f:
    writer = csv.writer(f)
    for severity in ["P1", "P2", "P3"]:
        print(f"Generating {severity} alerts...")
        alerts = generate_alerts(severity, 60)
        for alert in alerts:
            if alert:
                writer.writerow([alert, severity])
        print(f"Done: {len(alerts)} alerts")

print("Finished. Check data/alerts.csv")
