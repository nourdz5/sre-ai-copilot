import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    for severity in ["P1", "P2", "P3"]: # Generate 60 alerts for each severity level P1, P2, P3 , change to P1 only if you want to focus on critical alerts P1 
        #P1 severity means: service is down or data loss, P2 means service degraded but running, P3 means warning, nothing urgent
        # model generates more P1 but has some imbalance for P3, you can adjust the prompt to generate more P3 if needed to improve its performance on that class
        print(f"Generating {severity} alerts...")
        alerts = generate_alerts(severity, 60)
        for alert in alerts:
            if alert:
                writer.writerow([alert, severity])
        print(f"Done: {len(alerts)} alerts")

print("Finished. Check data/alerts.csv")
