import sys
sys.path.insert(0, "/Users/nourdziri/Documents/sre-ai-copilot")

import json
from openai import OpenAI
from agent.tools import get_logs, get_runbook
from classifier.predict import classify_alert


from classifier.predict import classify_alert

client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
)

def analyze_alert(alert):
    severity = classify_alert(alert)

    # Pre-fetch data ourselves instead of relying on the LLM to call tools
    logs = get_logs("payments-api")
    runbook = get_runbook(alert)

    messages = [
        {
            "role": "system",
            "content": "You are an SRE assistant. Analyze the alert using the logs and runbook provided."
        },
        {
            "role": "user",
            "content": f"Alert: {alert}\n\nLogs:\n{logs}\n\nRunbook:\n{runbook}"
        }
    ]

    response = client.chat.completions.create(
        model="llama3.1:8b",
        messages=messages
    )

    #return response.choices[0].message.content
    return f"Severity: {severity}\n\n{response.choices[0].message.content}"


if __name__ == "__main__":
    alert = "HighMemoryUsage on service payments-api, memory at 95%"
    print(analyze_alert(alert))
