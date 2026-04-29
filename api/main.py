import os 
from fastapi import FastAPI, Header, HTTPException, Depends, Request
from agent.models import AlertRequest
from agent.analyze import analyze_alert
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI()
Instrumentator().instrument(app).expose(app)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def verify_api_key(x_api_key: str = Header(...)):
    expected = os.environ.get("API_KEY")
    if not expected:
        return  # no API_KEY set, skip auth (development mode)
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")
@app.post("/analyze")
@limiter.limit("10/minute")  # max 10 requests per minute per IP
def analyze(alert: AlertRequest, request: Request , api_key: str = Depends(verify_api_key)):
    result = analyze_alert(alert)
    return {"analysis": result}

@app.get("/health")
def health():
    return {"status": "ok"}