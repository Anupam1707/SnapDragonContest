"""
GuardianEdge FastAPI Server and Interactive SOC (Security Operations Center) Dashboard.
Serves REST APIs for live DLP scanning, redaction, telemetry, and web UI.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os

from guardian_edge.detector import detector
from guardian_edge.redactor import redactor
from guardian_edge.screen_guard import screen_guard
from guardian_edge.policy_engine import policy_engine, audit_vault
from guardian_edge.npu_engine import npu_engine
from benchmarks.benchmark_suite import run_comparative_benchmark

app = FastAPI(
    title="GuardianEdge - Snapdragon® X Hexagon NPU DLP",
    description="Real-Time On-Device DLP and Threat Neutralization Engine",
    version="1.0.0"
)

# Static files directory
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

class ScanRequest(BaseModel):
    text: str
    mask_style: Optional[str] = "SYNTHETIC_LABEL"
    source: Optional[str] = "clipboard"

class PolicyUpdateRequest(BaseModel):
    category: str
    action: str

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>GuardianEdge Dashboard Initializing...</h1>")

@app.get("/api/telemetry")
async def get_telemetry():
    """Return Snapdragon X NPU hardware status and active execution metrics."""
    npu_info = npu_engine.get_hardware_telemetry()
    vault_metrics = audit_vault.get_metrics_summary()
    return {
        "npu": npu_info,
        "vault": vault_metrics,
        "screen_protection_active": screen_guard.active_protection
    }

@app.post("/api/scan")
async def scan_payload(req: ScanRequest):
    """Scan and redact incoming text payload with NPU acceleration."""
    if not req.text:
        return {"status": "EMPTY", "entities": [], "redacted_text": "", "telemetry": {}}

    entities, npu_telemetry = detector.scan_text(req.text)
    redacted_text, count = redactor.redact_text(req.text, entities, mask_style=req.mask_style)

    # Log to local audit vault
    if entities:
        top_entity = entities[0]
        policy = policy_engine.evaluate(top_entity.category)
        audit_vault.log_event(
            category=top_entity.category,
            severity=top_entity.severity,
            action_taken=policy["action"],
            redacted_count=count,
            latency_ms=npu_telemetry["latency_ms"],
            preview=top_entity.value[:16] + "..."
        )

    return {
        "status": "SUCCESS",
        "entities_count": len(entities),
        "entities": [e.to_dict() for e in entities],
        "redacted_text": redacted_text,
        "raw_text": req.text,
        "telemetry": npu_telemetry
    }

@app.post("/api/screen/scan")
async def scan_screen_frame():
    """Simulate real-time screen frame inspection."""
    return screen_guard.analyze_frame_simulation()

@app.get("/api/audit")
async def get_audit_trail():
    """Return local encrypted compliance audit trail."""
    return {
        "events": audit_vault.get_recent_events(limit=25),
        "summary": audit_vault.get_metrics_summary()
    }

@app.get("/api/policies")
async def get_policies():
    """Return active protection policies."""
    return {k: {"category": v.category, "severity": v.severity, "action": v.action, "description": v.description}
            for k, v in policy_engine.policies.items()}

@app.post("/api/policies/update")
async def update_policy(req: PolicyUpdateRequest):
    policy_engine.set_policy(req.category, req.action)
    return {"status": "UPDATED", "category": req.category, "action": req.action}

@app.get("/api/benchmarks")
async def get_benchmarks():
    """Return comparative benchmarks across Snapdragon NPU, CPU, GPU, and Cloud."""
    return run_comparative_benchmark()
