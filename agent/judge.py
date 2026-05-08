import os
import json
import time
from openai import OpenAI

client = OpenAI(
    base_url=os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/v1/",
    api_key="ollama",
)

JUDGE_PROMPT = """You are a judge evaluating an SRE assistant's analysis of an alert.

You will be given:
- The original alert
- The logs fetched
- The assistant's analysis

Your job is to evaluate if the analysis is reasonable and useful.

Respond ONLY with a JSON object in this exact format:
{
    "verdict": "pass" or "fail",
    "confidence": a number between 0 and 1,
    "reason": "one sentence explaining your verdict"
}

Rules:
- verdict is "fail" if the analysis directly contradicts what the logs say
- verdict is "fail" if the analysis is completely irrelevant to the alert
- verdict is "fail" if the analysis is vague and provides no actionable steps
- verdict is "pass" if the analysis is relevant and provides reasonable steps, even if they go beyond the runbook
- confidence reflects how certain you are of your verdict
"""

def judge_analysis(alert_text, logs, analysis):
    messages = [
        {
            "role": "system",
            "content": JUDGE_PROMPT
        },
        {
            "role": "user",
            "content": f"""Alert: {alert_text}

Logs:
{logs}

Assistant analysis:
{analysis}

Evaluate the analysis and respond with JSON only."""
        }
    ]

    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=os.environ.get("LLM_MODEL", "llama3.1:8b"),
                messages=messages,
                timeout=30
            )
            content = response.choices[0].message.content

            # extract JSON from response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end != 0:
                verdict = json.loads(content[start:end])
                return verdict

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue

    # if judge fails, return neutral verdict so we don't block the answer
    return {
        "verdict": "unknown",
        "confidence": 0.0,
        "reason": "Judge unavailable"
    }
