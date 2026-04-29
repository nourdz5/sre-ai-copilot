from pydantic import BaseModel, field_validator
from typing import Optional



class AlertRequest(BaseModel):
    name: str
    service: str
    environment: str
    namespace: Optional[str] = None
    cluster: Optional[str] = None
    timestamp: Optional[str] = None
    @field_validator("name", "service", "environment")
    @classmethod
    def validate_field(cls, v):
        if not v.strip():
            raise ValueError("must not be empty")
        if len(v) > 100:
            raise ValueError("too long — max 100 characters")
        return v.strip()
