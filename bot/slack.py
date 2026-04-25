import os
from dotenv import load_dotenv


from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from agent.analyze import analyze_alert

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.command("/oncall")
def handle_oncall(ack, say, command):
    ack()  # Acknowledge the command immediately
    alert = command["text"]
    say(f"Analyzing alert: {alert}...")
    result = analyze_alert(alert)
    say(result)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
