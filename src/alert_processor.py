from datetime import datetime, timedelta
from typing import List, Set
import uuid
from src.models import Alert, Incident

class AlertProcessor:
    def __init__(self, time_window_seconds: int = 60):
        self.time_window = timedelta(seconds=time_window_seconds)
    
    def group_alerts(self, alerts: List[Alert]) -> List[List[Alert]]:
        if not alerts:
            return []
        
        sorted_alerts = sorted(alerts, key=lambda x: x.timestamp)
        groups = []
        used = set()
        
        for i, alert in enumerate(sorted_alerts):
            if i in used:
                continue
            
            group = [alert]
            used.add(i)
            
            for j, other in enumerate(sorted_alerts):
                if j in used:
                    continue
                
                if self._are_related(alert, other):
                    group.append(other)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_related(self, a: Alert, b: Alert) -> bool:
        # Different devices with different types -> NOT related
        if a.source_device != b.source_device and a.alert_type != b.alert_type:
            return False
        
        # Same device -> related
        if a.source_device == b.source_device:
            return True
        
        # Same alert type -> related
        if a.alert_type == b.alert_type:
            return True
        
        # Time window + same device or same type
        time_diff = abs((a.timestamp - b.timestamp).total_seconds())
        if time_diff <= self.time_window.total_seconds():
            if a.source_device == b.source_device or a.alert_type == b.alert_type:
                return True
        
        # Message mentions same device
        a_device = self._extract_device_from_message(a.message)
        b_device = self._extract_device_from_message(b.message)
        if a_device and b_device and a_device == b_device:
            return True
        
        return False
    
    def _extract_device_from_message(self, message: str) -> str:
        import re
        patterns = [
            r'([A-Za-z]+[-_][0-9]+)',
            r'([A-Za-z]+[0-9]+)',
            r'(\d+\.\d+\.\d+\.\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        return ""
    
    def identify_primary_type(self, alerts: List[Alert]) -> str:
        type_counts = {}
        for alert in alerts:
            type_counts[alert.alert_type] = type_counts.get(alert.alert_type, 0) + 1
        max_count = max(type_counts.values())
        for alert_type, count in type_counts.items():
            if count == max_count:
                return alert_type
        return alerts[0].alert_type if alerts else "unknown"
    
    def create_incidents(self, alert_groups: List[List[Alert]]) -> List[Incident]:
        incidents = []
        for group in alert_groups:
            if not group:
                continue
            sorted_group = sorted(group, key=lambda x: x.timestamp)
            primary_type = self.identify_primary_type(sorted_group)
            incident = Incident(
                id=str(uuid.uuid4()),
                alerts=sorted_group,
                primary_type=primary_type,
                severity=self._determine_severity(sorted_group),
                status="OPEN",
                priority_score=self._calculate_priority(sorted_group),
                summary=f"{len(sorted_group)} alerts related to {primary_type}",
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
            if len(alerts) >= 3:
                return "CRITICAL"
            return "HIGH"
        if "high_latency" in alert_types:
            if len(alerts) >= 5:
                return "HIGH"
            return "MEDIUM"
        if "auth_failure" in alert_types:
            if len(alerts) >= 10:
                return "HIGH"
            return "LOW"
        return "MEDIUM"
    
    def _calculate_priority(self, alerts: List[Alert]) -> int:
        score = min(len(alerts), 5)
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
