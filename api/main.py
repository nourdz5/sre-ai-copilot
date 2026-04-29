from fastapi import FastAPI
from agent.models import AlertRequest
from agent.analyze import analyze_alert
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.post("/analyze")
def analyze(request: AlertRequest):
    result = analyze_alert(request)
    return {"analysis": result}
