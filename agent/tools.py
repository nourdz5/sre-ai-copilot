from agent.rag import search_runbooks

def get_logs(service_name):
    logs = {
        "payments-api": "ERROR OOMKilled: container exceeded memory limit",
        "auth-service": "ERROR Connection timeout to redis"
    }
    return logs.get(service_name, "No logs found")
    # Placeholder implementation - replace with actual log retrieval logic
    #return f"Logs for {service_name}"

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