from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"

class Alert(BaseModel):
    id: str
    timestamp: datetime
    source_device: str
    alert_type: str
    message: str
    details: Optional[Dict[str, Any]] = None

class Incident(BaseModel):
    id: str
    alerts: List[Alert]
    primary_type: str
    severity: Severity
    status: IncidentStatus
    priority_score: int
    summary: str
    recommended_action: str
    runbook_citation: str
    human_escalation: bool = False
    escalation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class TriageRequest(BaseModel):
    alerts: List[Alert]

class TriageResponse(BaseModel):
    incidents: List[Incident]
    noise_alerts: List[str]
    total_alerts: int
    incidents_created: int
