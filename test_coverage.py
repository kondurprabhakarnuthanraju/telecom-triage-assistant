import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Import your RAG engine
from src.rag_engine import RAGEngine

# Initialize RAG
rag = RAGEngine()
rag.load_runbooks()
rag.chunk_documents()
rag.embed_and_index()

# Test different alert types
test_alerts = [
    # Basic alert types (should be covered)
    {"type": "link_down", "desc": "Link down on interface Gi0/0/1"},
    {"type": "device_unreachable", "desc": "Device 10.0.0.1 unreachable"},
    {"type": "high_latency", "desc": "High latency on path to 10.0.0.1: 250ms"},
    {"type": "auth_failure", "desc": "Authentication failure for user admin"},
    
    # Variations (should still be covered)
    {"type": "link_flap", "desc": "Interface flapping on Gi0/0/1"},
    {"type": "device_down", "desc": "Router-1 is down"},
    {"type": "latency_spike", "desc": "Latency spike on link to 10.0.0.1"},
    {"type": "login_failed", "desc": "Login failed for user admin"},
    
    # Edge cases (may not be covered)
    {"type": "cpu_high", "desc": "CPU usage at 95% on Router-1"},
    {"type": "memory_high", "desc": "Memory usage at 90% on Switch-1"},
    {"type": "interface_error", "desc": "Interface errors on Gi0/0/1"},
    {"type": "routing_loop", "desc": "Routing loop detected"},
    {"type": "bgp_down", "desc": "BGP neighbor 10.0.0.2 down"},
    {"type": "ospf_down", "desc": "OSPF adjacency down"},
    {"type": "power_failure", "desc": "Power supply failure on Router-1"},
    {"type": "fan_failure", "desc": "Fan failure on Switch-1"},
    {"type": "temperature_high", "desc": "Temperature high on Router-1"},
]

print("="*60)
print("📊 RUNBOOK COVERAGE TEST")
print("="*60)
print()

covered = []
not_covered = []
partial = []

for alert in test_alerts:
    query = f"{alert['type']}: {alert['desc']}"
    result = rag.search(query, top_k=1)
    
    if result:
        # Check if the result is relevant (distance < 1.0 means somewhat similar)
        distance = result[0][1]
        if distance < 0.8:
            covered.append(alert)
            status = "✅ COVERED"
        else:
            partial.append(alert)
            status = "⚠️ PARTIAL"
    else:
        not_covered.append(alert)
        status = "❌ NOT COVERED"
    
    print(f"{status} - {alert['type']}: {alert['desc'][:40]}...")

print()
print("="*60)
print("📊 SUMMARY")
print("="*60)
print(f"✅ Covered: {len(covered)}")
print(f"⚠️ Partial: {len(partial)}")
print(f"❌ Not Covered: {len(not_covered)}")

if not_covered:
    print()
    print("❌ NOT COVERED ALERTS (NEED RUNBOOKS):")
    for alert in not_covered:
        print(f"  - {alert['type']}: {alert['desc']}")

if partial:
    print()
    print("⚠️ PARTIAL COVERAGE (MAY NEED IMPROVEMENT):")
    for alert in partial:
        print(f"  - {alert['type']}: {alert['desc']}")

