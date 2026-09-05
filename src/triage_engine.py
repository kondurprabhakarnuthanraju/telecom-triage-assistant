from datetime import datetime
from typing import Dict
from src.models import Incident
from src.rag_engine import RAGEngine
import google.generativeai as genai

class TriageEngine:
    def __init__(self, rag_engine: RAGEngine):
        self.rag = rag_engine
    
    def triage_incident(self, incident: Incident) -> Incident:
        # List of known alert types that should have runbooks
        known_types = ["link_down", "device_unreachable", "high_latency", "auth_failure", 
                       "cpu_high", "memory_high", "interface_error", "bgp_down"]
        
        # UNKNOWN TYPES - ALWAYS ESCALATE IMMEDIATELY
        if incident.primary_type not in known_types:
            incident.human_escalation = True
            incident.escalation_reason = f"Unknown alert type '{incident.primary_type}' - automatically escalated to human"
            incident.recommended_action = f"🚨 ESCALATED TO HUMAN: Unknown alert type '{incident.primary_type}' detected.\n\nAlert Details:\n- Type: {incident.primary_type}\n- Device: {incident.alerts[0].source_device if incident.alerts else 'Unknown'}\n- Message: {incident.alerts[0].message if incident.alerts else 'No message'}\n\nPlease investigate this unknown alert type manually."
            incident.runbook_citation = "No runbook found"
            incident.status = "ESCALATED"
            incident.updated_at = datetime.now()
            return incident
        
        # For KNOWN types, try to find runbook
        description = f"{incident.primary_type}: {incident.summary}"
        result = self.rag.get_relevant_runbook(incident.primary_type, description)
        
        if result.get("found", False) and result.get("confidence", 0) > 0.2:
            incident.recommended_action = self._generate_recommendation(incident, result.get("content", ""))
            incident.runbook_citation = result.get("citation", "No citation")
            incident.human_escalation = False
        else:
            # No runbook found for known type - escalate
            incident.human_escalation = True
            incident.escalation_reason = f"No runbook found for '{incident.primary_type}'"
            incident.recommended_action = f"🚨 ESCALATED TO HUMAN: No runbook found for '{incident.primary_type}'. Please investigate."
            incident.runbook_citation = "No runbook found"
        
        incident.status = "INVESTIGATING"
        incident.updated_at = datetime.now()
        return incident
    
    def _generate_recommendation(self, incident: Incident, runbook_content: str) -> str:
        prompt = f"""
You are a network operations triage assistant.

## Incident Details
- Type: {incident.primary_type}
- Alerts: {len(incident.alerts)} related alerts
- Severity: {incident.severity}
- Summary: {incident.summary}

## Runbook Reference
{runbook_content}

## Task
Based on the runbook above, provide a specific, actionable recommendation.
Format as:
1. **Immediate Action**: What to do right now
2. **Root Cause Investigation**: What to check
3. **Escalation Criteria**: When to escalate
"""
        models_to_try = [
            'models/gemini-3.5-flash-lite',
            'models/gemini-2.5-flash-lite',
            'models/gemini-flash-lite-latest',
        ]
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception:
                continue
        return f"""
1. **Immediate Action**: Check the {incident.primary_type} issue on {incident.alerts[0].source_device if incident.alerts else 'affected device'}
2. **Root Cause Investigation**: Verify device status, check connectivity, review logs
3. **Escalation Criteria**: Escalate if issue persists after 10 minutes
"""
