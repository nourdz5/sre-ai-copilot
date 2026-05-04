from agent.rag import search_runbooks
import os
import subprocess
from elasticsearch import Elasticsearch

import re

def scrub_logs(logs):
    # emails
    logs = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', logs)
    # bearer tokens
    logs = re.sub(r'Bearer\s+[a-zA-Z0-9._-]+', '[TOKEN]', logs)
    # API keys (long alphanumeric strings)
    logs = re.sub(r'[a-zA-Z0-9]{32,}', '[REDACTED]', logs)
    # IP addresses
    logs = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', logs)
    # credit cards
    logs = re.sub(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[CARD]', logs)
    return logs


def get_logs_from_mock(service_name):
    logs = {
        "payments-api": "ERROR OOMKilled: container exceeded memory limit",
        "auth-service": "ERROR Connection timeout to redis"
    }
    return logs.get(service_name, "No logs found")


def get_logs_from_kubernetes(service_name):
    namespace = os.environ.get("KUBE_NAMESPACE", "default")
    context = os.environ.get("KUBE_CONTEXT", "minikube")
    result = subprocess.run(
        ["kubectl", "logs", f"deployment/{service_name}",
         "--tail=50", "-n", namespace, "--context", context],
        capture_output=True, text=True
    )
    return result.stdout or "No logs found"

def get_logs_from_elasticsearch(service_name):
    try:
        es = Elasticsearch(
            os.environ.get("ES_HOST", "http://localhost:9200"),
            basic_auth=(
                os.environ.get("ES_USER", ""),
                os.environ.get("ES_PASSWORD", "")
            )
        )
             
        results = es.search(
            index=os.environ.get("ES_INDEX", "logs"),
            query={"match": {"service": service_name}},
            size=50
        )
        hits = results["hits"]["hits"]
        return "\n".join([h["_source"]["message"] for h in hits])
    
    except Exception as e:
        return f"Elasticsearch unavailable: {str(e)}"


def get_logs(service_name):
    backend = os.environ.get("LOG_BACKEND", "mock")
    
    if backend == "elasticsearch":
        logs= get_logs_from_elasticsearch(service_name)
    elif backend == "kubernetes":
        logs=get_logs_from_kubernetes(service_name)
    else:
        logs=get_logs_from_mock(service_name)
        
    return scrub_logs(logs)

# def get_runbook(alert_name):
#     runbooks = {
#         "HighMemoryUsage": "1. Check kubectl top pods\n2. Restart the pod",
#     }
#     return runbooks.get(alert_name, "No runbook found")
def get_runbook(alert_name):
    return search_runbooks(alert_name)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_logs",
            "description": "Fetch recent logs for a specific service",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "The name of the service"
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
            "description": "Fetch the runbook for a specific alert",
            "parameters": {
                "type": "object",
                "properties": {
                    "alert_name": {
                        "type": "string",
                        "description": "The name of the alert"
                    }
                },
                "required": ["alert_name"]
    }
        }
    }
]


def run_tool(tool_name, tool_input):
    if tool_name == "get_logs":
        service_name = tool_input.get("service_name") or list(tool_input.values())[0]
        return get_logs(service_name)
    elif tool_name == "get_runbook":
        alert_name = tool_input.get("alert_name") or list(tool_input.values())[0]
        return get_runbook(alert_name)