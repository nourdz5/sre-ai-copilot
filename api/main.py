from fastapi import FastAPI
from pydantic import BaseModel
from agent.analyze import analyze_alert

app = FastAPI()

class AlertRequest(BaseModel):
    alert: str

@app.post("/analyze")
def analyze(request: AlertRequest):
    result = analyze_alert(request.alert)
    return {"analysis": result}
