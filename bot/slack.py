import os

from dotenv import load_dotenv


from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from agent.analyze import analyze_alert
from agent.models import AlertRequest
load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.command("/oncall")
def handle_oncall(ack, say, command):
    ack()  # Acknowledge the command immediately
    alert = command["text"]
    say(f"Analyzing alert: {alert}...")
    parts = alert.split(" on ")
    name = parts[0].strip() # "HighMemoryUsage"
    service = parts[1].strip() if len(parts) > 1 else "unknown"  # "payments-api"
    request = AlertRequest(
        name=name,
        service=service,
        environment="unknown"
    )
    result = analyze_alert(request)
    say(result)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
