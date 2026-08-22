import hmac
import hashlib
from typing import Dict, Any, Set
from fastapi import FastAPI, Header, HTTPException, Request
from app.core.config import settings
from app.core.graph import review_pipeline

app = FastAPI(title=settings.PROJECT_NAME)

# In-memory idempotency cache (in production backed by Redis/SQLite)
PROCESSED_DELIVERIES: Set[str] = set()

def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verifies HMAC SHA-256 signature from GitHub Webhooks."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected_sig = hmac.new(
        key=settings.WEBHOOK_SECRET.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_sig}", signature_header)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

@app.post("/api/v1/webhook/github")
async def github_webhook_endpoint(
    request: Request,
    x_github_delivery: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    body_bytes = await request.body()
    
    # 1. Idempotency Check
    if x_github_delivery:
        if x_github_delivery in PROCESSED_DELIVERIES:
            return {"status": "skipped", "reason": "duplicate delivery ID"}
        PROCESSED_DELIVERIES.add(x_github_delivery)

    # 2. Signature Validation
    if settings.ENVIRONMENT == "production":
        if not verify_github_signature(body_bytes, x_hub_signature_256):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    pr_data = payload.get("pull_request", {})
    raw_diff = payload.get("diff", "")
    pr_id = str(pr_data.get("number", "PR-WEBHOOK"))

    # 3. Trigger LangGraph pipeline
    initial_state = {
        "pr_id": pr_id,
        "raw_diff": raw_diff,
        "changed_files": [],
        "static_findings": [],
        "security_findings": [],
        "quality_findings": [],
        "aggregated_findings": [],
        "final_report": None,
        "error": None
    }
    result = review_pipeline.invoke(initial_state)
    return {"status": "success", "report": result["final_report"].model_dump() if result["final_report"] else None}