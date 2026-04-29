from pydantic import BaseModel
from typing import Optional

class AlertRequest(BaseModel):
    name: str
    service: str
    environment: str
    namespace: Optional[str] = None
    cluster: Optional[str] = None
    timestamp: Optional[str] = None
