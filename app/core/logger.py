import structlog
import uuid
import time
from typing import Dict, Any

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger("CodeReviewAgent")

# Pricing estimations (e.g. Llama-3.3-70B: ~$0.59 / 1M prompt tokens)
COST_PER_PROMPT_TOKEN = 0.59 / 1_000_000
COST_PER_COMPLETION_TOKEN = 0.79 / 1_000_000

def track_inference_telemetry(pr_id: str, agent_name: str, prompt_tokens: int, completion_tokens: int, duration_ms: float):
    """Logs structured FinOps telemetry and token spend for auditability."""
    cost = (prompt_tokens * COST_PER_PROMPT_TOKEN) + (completion_tokens * COST_PER_COMPLETION_TOKEN)
    logger.info(
        "llm_inference_completed",
        request_id=str(uuid.uuid4())[:8],
        pr_id=pr_id,
        agent=agent_name,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        estimated_cost_usd=round(cost, 6),
        duration_ms=round(duration_ms, 2)
    )