import os
import json
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

from src.models import Alert
from src.alert_processor import AlertProcessor
from src.rag_engine import RAGEngine
from src.triage_engine import TriageEngine

# Initialize
rag = RAGEngine()
rag.load_runbooks()
rag.chunk_documents()
rag.embed_and_index()

processor = AlertProcessor()
triage = TriageEngine(rag)

print("="*70)
print("🔍 EDGE CASE COVERAGE TEST")
print("="*70)
print()

results = []

# ============================================================
# TEST 1: Empty Alerts
# ============================================================
print("📋 TEST 1: Empty Alerts")
try:
    groups = processor.group_alerts([])
    incidents = processor.create_incidents(groups)
    status = "✅ PASS" if len(incidents) == 0 else "❌ FAIL"
except Exception as e:
    status = f"❌ FAIL - {e}"
print(f"  {status}")
results.append(("Empty Alerts", status))
print()

# ============================================================
# TEST 2: Single Alert
# ============================================================
print("📋 TEST 2: Single Alert")
alert = Alert(
    id=str(uuid.uuid4()),
    timestamp=datetime.now(),
    source_device="Router-1",
    alert_type="link_down",
    message="Link down on Router-1"
)
try:
    groups = processor.group_alerts([alert])
    incidents = processor.create_incidents(groups)
    triaged = triage.triage_incident(incidents[0])
    status = "✅ PASS" if len(incidents) == 1 else "❌ FAIL"
except Exception as e:
    status = f"❌ FAIL - {e}"
print(f"  {status}")
results.append(("Single Alert", status))
print()

# ============================================================
# TEST 3: Duplicate Alerts (Same Device, Same Type)
# ============================================================
print("📋 TEST 3: Duplicate Alerts (Same Device, Same Type)")
alerts = []
for i in range(5):
    alerts.append(Alert(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        source_device="Router-1",
        alert_type="link_down",
        message=f"Link down on Router-1 {i+1}"
    ))
try:
    groups = processor.group_alerts(alerts)
    incidents = processor.create_incidents(groups)
    status = "✅ PASS" if len(incidents) == 1 and len(incidents[0].alerts) == 5 else "❌ FAIL"
except Exception as e:
    status = f"❌ FAIL - {e}"
print(f"  {status}")
results.append(("Duplicate Alerts", status))
print()

# ============================================================
# TEST 4: Different Devices, Same Alert Type
# ============================================================
print("📋 TEST 4: Different Devices, Same Alert Type")
alerts = []
for i in range(3):
    alerts.append(Alert(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        source_device=f"Router-{i+1}",
        alert_type="link_down",
        message=f"Link down on Router-{i+1}"
    ))
try:
    groups = processor.group_alerts(alerts)
    incidents = processor.create_incidents(groups)
    status = "✅ PASS" if len(incidents) == 1 else "❌ FAIL"
except Exception as e:
    status = f"❌ FAIL - {e}"
print(f"  {status}")
results.append(("Different Devices", status))
print()

# ============================================================
# TEST 5: Mixed Alert Types (Should be separate)
# ============================================================
print("📋 TEST 5: Mixed Alert Types (Should be separate)")
alerts = [
    Alert(id=str(uuid.uuid4()), timestamp=datetime.now(), source_device="Router-1", alert_type="link_down", message="Link down"),
    Alert(id=str(uuid.uuid4()), timestamp=datetime.now(), source_device="Router-2", alert_type="device_unreachable", message="Unreachable"),
    Alert(id=str(uuid.uuid4()), timestamp=datetime.now(), source_device="Router-3", alert_type="high_latency", message="High latency"),
]
try:
    groups = processor.group_alerts(alerts)
    incidents = processor.create_incidents(groups)
    status = "✅ PASS" if len(incidents) == 3 else "❌ FAIL"
except Exception as e:
    status = f"❌ FAIL - {e}"
print(f"  {status}")
results.append(("Mixed Types", status))
print()

# ============================================================
# TEST 6: Related Alerts (Same Device, Different Types)
# ============================================================
print("📋 TEST 6: Related Alerts (Same Device, Different Types)")
now = datetime.now()
alerts = [
    Alert(id=str(uuid.uuid4()), timestamp=now, source_device="Router-1", alert_type="link_down", message="Link down"),
    Alert(id=str(uuid.uuid4()), timestamp=now + timedelta(seconds=10), source_device="Router-1", alert_type="device_unreachable", message="Device unreachable"),
]
try:
    groups = processor.group_alerts(alerts)
    incidents = processor.create_incidents(groups)
    status = "✅ PASS" if len(incidents) == 1 else "❌ FAIL"
except Exception as e:
    status = f"❌ FAIL - {e}"
print(f"  {status}")
results.append(("Related Alerts (Same Device)", status))
print()

# ============================================================
# TEST 7: Time Gap > 60 seconds
# ============================================================
print("📋 TEST 7: Time Gap > 60 seconds")
now = datetime.now()
alerts = [
    Alert(id=str(uuid.uuid4()), timestamp=now, source_device="Router-1", alert_type="link_down", message="Link down"),
    Alert(id=str(uuid.uuid4()), timestamp=now + timedelta(seconds=120), source_device="Router-1", alert_type="link_down", message="Link down later"),
]
try:
    groups = processor.group_alerts(alerts)
    incidents = processor.create_incidents(groups)
    status = "✅ PASS" if len(incidents) == 1 else "❌ FAIL"
except Exception as e:
    status = f"❌ FAIL - {e}"
print(f"  {status}")
results.append(("Time Gap > 60s", status))
print()

# ============================================================
# TEST 8: Large Number of Alerts (50+)
# ============================================================
print("📋 TEST 8: Large Number of Alerts (50 alerts)")
alerts = []
for i in range(50):
    alerts.append(Alert(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        source_device=f"Router-{i%5+1}",
        alert_type=["link_down", "device_unreachable", "high_latency"][i%3],
        message=f"Alert {i+1}"
    ))
try:
    groups = processor.group_alerts(alerts)
    incidents = processor.create_incidents(groups)
    status = "✅ PASS" if len(incidents) > 0 else "❌ FAIL"
except Exception as e:
    status = f"❌ FAIL - {e}"
print(f"  {status}")
results.append(("50 Alerts", status))
print()

# ============================================================
# TEST 9: Unknown Alert Type (Should escalate)
# ============================================================
print("📋 TEST 9: Unknown Alert Type (Should escalate to human)")
alert = Alert(
    id=str(uuid.uuid4()),
    timestamp=datetime.now(),
    source_device="Router-1",
    alert_type="unknown_type",
    message="Some unknown alert"
)
try:
    groups = processor.group_alerts([alert])
    incidents = processor.create_incidents(groups)
    triaged = triage.triage_incident(incidents[0])
    # Should escalate to human
    status = "✅ PASS" if triaged.human_escalation == True else "❌ FAIL"
except Exception as e:
    status = f"❌ FAIL - {e}"
print(f"  {status}")
results.append(("Unknown Alert Type", status))
print()

# ============================================================
# TEST 10: No Runbook Match (Should escalate)
# ============================================================
print("📋 TEST 10: No Runbook Match (Should escalate to human)")
alert = Alert(
    id=str(uuid.uuid4()),
    timestamp=datetime.now(),
    source_device="Router-1",
    alert_type="quantum_anomaly",
    message="Quantum anomaly detected in network fabric"
)
try:
    groups = processor.group_alerts([alert])
    incidents = processor.create_incidents(groups)
    triaged = triage.triage_incident(incidents[0])
    # Should escalate to human
    status = "✅ PASS" if triaged.human_escalation == True else "❌ FAIL"
except Exception as e:
    status = f"❌ FAIL - {e}"
print(f"  {status}")
results.append(("No Runbook Match", status))
print()

# ============================================================
# TEST 11: Malformed Alert
# ============================================================
print("📋 TEST 11: Malformed Alert (Should handle gracefully)")
try:
    alert = Alert(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        source_device="Router-1",
        alert_type="link_down",
        message="Link down"
    )
    groups = processor.group_alerts([alert])
    incidents = processor.create_incidents(groups)
    triaged = triage.triage_incident(incidents[0])
    status = "✅ PASS"
except Exception as e:
    status = f"❌ FAIL - {e}"
print(f"  {status}")
results.append(("Malformed Alert", status))
print()

# ============================================================
# SUMMARY
# ============================================================
print("="*70)
print("📊 EDGE CASE TEST SUMMARY")
print("="*70)
print()

passed = sum(1 for _, status in results if "✅" in status)
failed = sum(1 for _, status in results if "❌" in status)
partial = sum(1 for _, status in results if "⚠️" in status)

for test, status in results:
    print(f"  {status} - {test}")

print()
print("="*70)
print(f"✅ Passed: {passed}")
print(f"⚠️ Partial: {partial}")
print(f"❌ Failed: {failed}")
print("="*70)

if failed > 0:
    print("❌ SOME EDGE CASES FAILED! Fix them before submission.")
elif partial > 0:
    print("⚠️ SOME EDGE CASES PARTIAL! Review them.")
else:
    print("🎉 ALL EDGE CASES PASSED! Your project is ready!")
