import os
from agent.models import AlertRequest

from openai import OpenAI
from agent.tools import get_logs, get_runbook

try:
    from classifier.predict import classify_alert
except ImportError:
    def classify_alert(alert):
        return "P2"

client = OpenAI(
    base_url=os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/v1/",
    api_key="ollama",
)

def analyze_alert(request):
    alert_text = f"{request.name} on {request.service}"
    severity = classify_alert(alert_text)

    # Pre-fetch data ourselves instead of relying on the LLM to call tools
    logs = get_logs(request.service)
    runbook = get_runbook(alert_text)
    content= os.environ.get("SYSTEM_PROMPT", "You are an SRE assistant. Analyze the alert using the logs and runbook provided.")
    messages = [
        {
            "role": "system",
            "content": content
        },
        {
            "role": "user",
            "content": f"Alert: {alert_text}\n\nLogs:\n{logs}\n\nRunbook:\n{runbook}"
        }
    ]

    response = client.chat.completions.create(
        model=os.environ.get("LLM_MODEL", "llama3.1:8b"),
        messages=messages
    )

    #return response.choices[0].message.content
    return f"Severity: {severity}\n\n{response.choices[0].message.content}"


if __name__ == "__main__":
    request = AlertRequest(
        name="HighMemoryUsage",
        service="payments-api",
        environment="production"
    )
    print(analyze_alert(request))
