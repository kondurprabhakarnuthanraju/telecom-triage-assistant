import os
import json
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load .env FIRST
load_dotenv()

# Try both variable names
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: No API key found!")
    print("Please set GEMINI_API_KEY or GOOGLE_API_KEY in .env")
    exit(1)

# Set for Google libraries
os.environ["GOOGLE_API_KEY"] = api_key

print(f"✅ API Key loaded (first 10 chars): {api_key[:10]}...")
print("📌 Generation Model: models/gemini-3.5-flash-lite (Judge's model)")

from src.models import Alert, TriageRequest, TriageResponse
from src.alert_processor import AlertProcessor
from src.rag_engine import RAGEngine
from src.triage_engine import TriageEngine

app = FastAPI(title="Network Incident Triage Assistant")
templates = Jinja2Templates(directory="templates")

print("🚀 Initializing Triage Assistant...")

print("📚 Loading runbooks...")
rag_engine = RAGEngine()
rag_engine.load_runbooks()
rag_engine.chunk_documents()
rag_engine.embed_and_index()

alert_processor = AlertProcessor()
triage_engine = TriageEngine(rag_engine)

print("✅ Triage Assistant ready!")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/triage", response_model=TriageResponse)
async def triage_alerts(request: TriageRequest):
    if not request.alerts:
        raise HTTPException(status_code=400, detail="No alerts provided")
    
    alert_groups = alert_processor.group_alerts(request.alerts)
    incidents = alert_processor.create_incidents(alert_groups)
    
    triaged_incidents = []
    for incident in incidents:
        triaged = triage_engine.triage_incident(incident)
        triaged_incidents.append(triaged)
    
    grouped_alert_ids = set()
    for incident in triaged_incidents:
        for alert in incident.alerts:
            grouped_alert_ids.add(alert.id)
    
    all_alert_ids = {alert.id for alert in request.alerts}
    noise_alerts = list(all_alert_ids - grouped_alert_ids)
    
    return TriageResponse(
        incidents=triaged_incidents,
        noise_alerts=noise_alerts,
        total_alerts=len(request.alerts),
        incidents_created=len(triaged_incidents)
    )

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "runbooks": len(rag_engine.documents)}

@app.post("/api/generate-sample-alerts")
async def generate_sample_alerts():
    base_time = datetime.now()
    sample_alerts = []
    
    for i in range(5):
        sample_alerts.append({
            "id": str(uuid.uuid4()),
            "timestamp": base_time.isoformat(),
            "source_device": f"Router-{i%2+1}",
            "alert_type": "link_down",
            "message": f"Link down on Router-{i%2+1}"
        })
    
    for i in range(3):
        sample_alerts.append({
            "id": str(uuid.uuid4()),
            "timestamp": base_time.isoformat(),
            "source_device": f"Switch-{i%2+3}",
            "alert_type": "device_unreachable",
            "message": f"Device Switch-{i%2+3} unreachable"
        })
    
    for i in range(2):
        sample_alerts.append({
            "id": str(uuid.uuid4()),
            "timestamp": base_time.isoformat(),
            "source_device": f"Router-{i%2+1}",
            "alert_type": "high_latency",
            "message": f"High latency on Router-{i%2+1}: 250ms"
        })
    
    sample_alerts.append({
        "id": str(uuid.uuid4()),
        "timestamp": base_time.isoformat(),
        "source_device": "AAA-Server",
        "alert_type": "auth_failure",
        "message": "Authentication failure for user admin"
    })
    
    return {"alerts": sample_alerts}

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Network Incident Triage Assistant")
    print("📌 Generation Model: models/gemini-3.5-flash-lite (Judge's model)")
    print("📌 Embedding Model: models/gemini-embedding-001")
    print("📌 Port: 8000")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
