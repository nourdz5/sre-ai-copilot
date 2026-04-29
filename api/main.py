import os 
from fastapi import FastAPI, Header, HTTPException, Depends
from agent.models import AlertRequest
from agent.analyze import analyze_alert
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI()
Instrumentator().instrument(app).expose(app)


def verify_api_key(x_api_key: str = Header(...)):
    expected = os.environ.get("API_KEY")
    if not expected:
        return  # no API_KEY set, skip auth (development mode)
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")
@app.post("/analyze")
def analyze(request: AlertRequest, api_key: str = Depends(verify_api_key)):
    result = analyze_alert(request)
    return {"analysis": result}

@app.get("/health")
def health():
    return {"status": "ok"}