import os
import json
import time
from agent.models import AlertRequest
from openai import OpenAI
from agent.tools import TOOLS, run_tool, get_logs, get_runbook
from agent.judge import judge_analysis
from agent.memory import store_incident, get_similar_incidents

max_retries = 3

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

    # check memory for similar past incidents
    past_incidents = get_similar_incidents(alert_text)
    past_context = ""
    if past_incidents:
        past_context = "\n\nPast similar incidents:\n"
        for inc in past_incidents:
            past_context += f"- [{inc['timestamp']}] {inc['alert']} (severity: {inc['severity']}): {inc['analysis'][:200]}...\n"

    messages = [
        {
            "role": "system",
            "content": os.environ.get("SYSTEM_PROMPT", "You are an SRE assistant. Use the available tools to fetch logs and runbooks, then analyze the alert.")
        },
        {
            "role": "user",
            "content": f"Alert: {alert_text}\n\nInvestigate and explain what is happening and what should be done.{past_context}"
        }
    ]

    # agentic loop — runs until LLM stops calling tools
    for attempt in range(max_retries):
        try:
            for _ in range(10):  # max 10 tool calls to prevent infinite loop
                response = client.chat.completions.create(
                    model=os.environ.get("LLM_MODEL", "llama3.1:8b"),
                    messages=messages,
                    tools=TOOLS,
                    timeout=30
                )

                message = response.choices[0].message

                # LLM is done — no more tool calls, return final answer
                if not message.tool_calls:
                    # small models sometimes ignore tool calling and answer directly
                    # if the answer looks like a tool call description, fall back to pre-fetching
                    if message.content and "get_logs" not in message.content and "get_runbook" not in message.content:
                        logs = get_logs(request.service)
                        verdict = judge_analysis(alert_text, logs, message.content)
                        store_incident(alert_text, severity, message.content, verdict["verdict"])
                        verdict_line = f"Judge: {verdict['verdict'].upper()} (confidence: {verdict['confidence']}) — {verdict['reason']}"
                        return f"Severity: {severity}\n\n{message.content}\n\n---\n{verdict_line}"

                    # fallback — model didn't use tool calls properly, pre-fetch everything
                    logs = get_logs(request.service)
                    runbook = get_runbook(alert_text)
                    messages.append({
                        "role": "user",
                        "content": f"Here is the data you need:\n\nLogs:\n{logs}\n\nRunbook:\n{runbook}\n\nNow provide your analysis."
                    })
                    continue

                # LLM wants to call a tool — execute it and feed result back
                messages.append(message)

                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_input = json.loads(tool_call.function.arguments)
                    tool_result = run_tool(tool_name, tool_input)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })

            return f"Severity: {severity}\n\nAgent reached max tool calls without a final answer."

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return f"Severity: {severity}\n\nLLM unavailable after {max_retries} attempts: {str(e)}"


if __name__ == "__main__":
    request = AlertRequest(
        name="HighMemoryUsage",
        service="payments-api",
        environment="production"
    )
    print(analyze_alert(request))
