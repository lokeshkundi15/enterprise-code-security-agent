# 🏛️ Architecture Decision Records (ADR) - Project 2

### 1. Why LangGraph over linear chains?
- **Decision:** Used LangGraph `StateGraph` for multi-agent routing.
- **Reason:** Code review requires fan-out to isolated security/quality agents and deterministic fan-in to an aggregator node, avoiding shared mutable state.

### 2. Why FastMCP Static Tools alongside LLMs?
- **Decision:** Integrated Python AST and regular expression pattern scanners via FastMCP.
- **Reason:** LLMs can miss high-entropy string tokens or simple SQL concatenations. Deterministic AST parsing guarantees 0ms latency detection for known CWE patterns with zero hallucination.

### 3. Why Strict Pydantic Validation?
- **Decision:** Enforced `CodeFinding` and `ReviewReport` Pydantic models.
- **Reason:** Ensures programmatic downstream consumption by CI/CD webhooks and prevents malformed LLM outputs from breaking UI rendering.

### 4. Why Human-in-the-Loop Gatekeeper?
- **Decision:** Autonomous write operations to GitHub PR comments are blocked until approved.
- **Reason:** In enterprise environments, hallucinated security flags cause developer alert fatigue. Human verification ensures high-trust code reviews.