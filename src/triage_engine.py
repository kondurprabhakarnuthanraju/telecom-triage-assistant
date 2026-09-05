from datetime import datetime
from typing import Dict
from src.models import Incident
from src.rag_engine import RAGEngine
import google.generativeai as genai

class TriageEngine:
    def __init__(self, rag_engine: RAGEngine):
        self.rag = rag_engine
    
    def triage_incident(self, incident: Incident) -> Incident:
        description = f"{incident.primary_type}: {incident.summary}"
        result = self.rag.get_relevant_runbook(incident.primary_type, description)
        
        if result["found"]:
            incident.recommended_action = self._generate_recommendation(incident, result["content"])
            incident.runbook_citation = result["citation"]
            incident.human_escalation = False
        else:
            incident.human_escalation = True
            incident.escalation_reason = result["reason"]
            incident.recommended_action = "ESCALATE TO HUMAN - No matching runbook found"
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
        
        # Use the latest working model
        try:
            model = genai.GenerativeModel('models/gemini-3.8-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback to another model
            try:
                model = genai.GenerativeModel('models/gemini-3.7-flash')
                response = model.generate_content(prompt)
                return response.text
            except Exception as e2:
                # Final fallback
                return f"""
1. **Immediate Action**: Check the {incident.primary_type} issue on {incident.alerts[0].source_device if incident.alerts else 'affected device'}

2. **Root Cause Investigation**: Verify device status, check connectivity, review logs

3. **Escalation Criteria**: Escalate if issue persists after 10 minutes or if multiple devices affected

⚠️ Note: This is a fallback recommendation. Please check the runbook manually.
"""
