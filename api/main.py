import os 
from fastapi import FastAPI, Header, HTTPException, Depends, Request
from agent.models import AlertRequest
from agent.analyze import analyze_alert
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time 
import logging 

logging.basicConfig(
    filename="audit.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)

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
    start = time.time()
    result = analyze_alert(alert)
    duration = round(time.time() - start, 2)
    logging.info(f"alert={alert.name} service={alert.service} env={alert.environment} duration={duration}s")
    return {"analysis": result}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/webhook")
def webhook(payload: dict, request: Request):
    for alert in payload.get("alerts", []):
        labels = alert.get("labels", {})
        alert_request = AlertRequest(
            name=labels.get("alertname", "UnknownAlert"),
            service=labels.get("service", "unknown"),
            environment=labels.get("environment", "production"),
            cluster=labels.get("cluster", None),
            namespace=labels.get("namespace", None)
        )
        result = analyze_alert(alert_request)
        logging.info(f"webhook alert={alert_request.name} service={alert_request.service}")
    return {"status": "received"}