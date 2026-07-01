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
    alert = command["text"].strip()
    
    if not alert:
        say("Usage: `/oncall AlertName on service-name`")
        return
    parts = alert.split(" on ")
    if len(parts) < 2:
        say("Usage: `/oncall AlertName on service-name`")
        return

    name = parts[0].strip()
    service = parts[1].strip()
    request = AlertRequest(
        name=name,
        service=service,
        environment="unknown"
    )

    try:
        say(f"Analyzing alert: {alert}...")
        result = analyze_alert(request)
        say(result["text"])
    except Exception as e:
        say(f"Error analyzing alert: {str(e)}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
