from datetime import datetime, timedelta
from typing import List, Set
import uuid
from src.models import Alert, Incident

class AlertProcessor:
    def __init__(self, time_window_seconds: int = 60):
        self.time_window = timedelta(seconds=time_window_seconds)
    
    def group_alerts(self, alerts: List[Alert]) -> List[List[Alert]]:
        groups = []
        used = set()
        
        for i, alert in enumerate(alerts):
            if i in used:
                continue
            
            group = [alert]
            used.add(i)
            
            for j, other in enumerate(alerts):
                if j in used:
                    continue
                
                if self._are_related(alert, other):
                    group.append(other)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_related(self, a: Alert, b: Alert) -> bool:
        if a.source_device == b.source_device:
            return True
        if a.alert_type == b.alert_type:
            return True
        if abs((a.timestamp - b.timestamp).total_seconds()) < self.time_window.total_seconds():
            return True
        if self._extract_device(a.message) == self._extract_device(b.message):
            return True
        return False
    
    def _extract_device(self, message: str) -> str:
        words = message.split()
        for word in words:
            if '.' in word or '-' in word:
                if len(word) > 5:
                    return word
        return ""
    
    def identify_primary_type(self, alerts: List[Alert]) -> str:
        type_counts = {}
        for alert in alerts:
            type_counts[alert.alert_type] = type_counts.get(alert.alert_type, 0) + 1
        return max(type_counts, key=type_counts.get)
    
    def create_incidents(self, alert_groups: List[List[Alert]]) -> List[Incident]:
        incidents = []
        
        for group in alert_groups:
            primary_type = self.identify_primary_type(group)
            
            incident = Incident(
                id=str(uuid.uuid4()),
                alerts=group,
                primary_type=primary_type,
                severity=self._determine_severity(group),
                status="OPEN",
                priority_score=self._calculate_priority(group),
                summary=f"{len(group)} alerts related to {primary_type}",
                recommended_action="",
                runbook_citation="",
                human_escalation=False,
                escalation_reason=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            incidents.append(incident)
        
        return incidents
    
    def _determine_severity(self, alerts: List[Alert]) -> str:
        alert_types = [a.alert_type for a in alerts]
        
        if "link_down" in alert_types or "device_unreachable" in alert_types:
            if len(alerts) > 3:
                return "CRITICAL"
            return "HIGH"
        
        if "high_latency" in alert_types:
            if len(alerts) > 5:
                return "HIGH"
            return "MEDIUM"
        
        if "auth_failure" in alert_types:
            if len(alerts) > 10:
                return "HIGH"
            return "LOW"
        
        return "MEDIUM"
    
    def _calculate_priority(self, alerts: List[Alert]) -> int:
        score = 0
        score += min(len(alerts), 5)
        
        critical_types = {"link_down", "device_unreachable"}
        high_types = {"high_latency", "auth_failure"}
        
        for alert in alerts:
            if alert.alert_type in critical_types:
                score += 3
                break
            elif alert.alert_type in high_types:
                score += 1
        
        devices = set(a.source_device for a in alerts)
        if len(devices) > 2:
            score += 2
        
        return min(score, 10)
