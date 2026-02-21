---
layout: default
title: Architecture
---

# Symposion Architecture

A comprehensive guide to the system design, message protocol, and orchestration model.

## Subpages

- **[Intent Taxonomy](./intent-taxonomy.md)** — Semantic message purposes and coordination protocol
- **[Action Pipelines](./action-pipelines.md)** — GitHub Actions CI/CD workflows for testing and deployment

---

## 1. System Overview

Symposion is a **message-driven orchestration framework** where specialized agents collaborate through asynchronous message passing. The architecture emphasizes:

- **Role Specialization**: Each agent has a distinct responsibility (interpret, plan, research, build, judge, narrate)
- **Protocol Enforcement**: All communication follows explicit intent taxonomy and message schema
- **Quality Gates**: Critical outputs pass through validation before delivery (Nemesis Gate)
- **Auditability**: JSONL logging enables complete message replay and analysis

### Core Execution Model

```
User Goal
    ↓
[HERM] → Interprets goal
    ↓
[DAED] → Plans decomposition
    ↓
[ATHEN] → Gathers context (optional)
    ↓
[HEPH] → Builds artifacts
    ↓
[NEM] ── Validates quality ← (Nemesis Gate)
    ↓
[CLIO] → Reports results
    ↓
Human Output
```

---

## 2. Core Components

### 2.1 Message Bus (`core/messaging.py`)

The central communication channel for all agent messages.

**Responsibilities**:
- Maintain FIFO message queue
- Log all messages to JSONL for audit trail
- Batch drain operations for efficient processing

**Key Methods**:
- `send(msg: Message)` — Enqueue a message
- `drain() -> List[Message]` — Retrieve all queued messages (FIFO)

**Current Implementation (v0)**: Single-process, in-memory queue. Future versions will support distributed queues (Redis, Kafka).

### 2.2 Orchestrator (`core/orchestrator.py`)

The central coordinator that routes messages and enforces system rules.

**Key Responsibilities**:
- Message validation against intent taxonomy
- Agent lookup and message delivery
- Task state management (active/completed)
- Nemesis Gate enforcement (HEPH artifacts → NEM before reaching CLIO)
- Protocol violation handling (strict vs. permissive mode)
- Loop detection (max steps limit)

**Main Method**:
```python
def run(self, max_steps: int = 200) -> None:
    """
    Process message queue until empty or max_steps reached.
    
    1. Drain queue (batch)
    2. For each message:
       - Skip if task already completed (except FINAL_REPORT)
       - Validate protocol
       - Apply Nemesis Gate rules
       - Route to agent.handle()
       - Mark task complete if FINAL_REPORT reached HUMAN
    3. Repeat
    """
```

**Task Lifecycle**:
- `task_state: Dict[str, Dict]` — Metadata for active tasks
- `completed_tasks: set[str]` — Tasks marked complete after FINAL_REPORT delivery
- Prevents infinite loops and reprocessing

### 2.3 Agent Registry (`core/registry.py`)

Central catalog of all agents in the system.

**Pattern**: Uses Python Protocol for agent discovery (duck typing).

```python
class Agent(Protocol):
    name: str
    def handle(self, msg: Message) -> List[Message]: ...

class AgentRegistry:
    def get(self, name: str) -> Agent
```

**Error Handling**: Raises `KeyError` for unknown agents.

### 2.4 Message & Data Models (`models.py`)

**Message Schema**:
```python
@dataclass(frozen=True)
class Message:
    sender: str              # Agent name (HERM, DAED, etc.)
    recipient: str          # Target agent or "HUMAN"
    task_id: str            # Unique task ID (TASK-{uuid})
    intent: str             # Message type (see Intent Taxonomy)
    content: str            # Payload
    goal_reference: str     # Original user goal
    urgency: Urgency        # LOW | NORMAL | HIGH | CRITICAL
    timestamp: float        # Unix timestamp (auto-populated)
    meta: Dict[str, Any]    # Optional metadata
```

**Message Immutability**: `@dataclass(frozen=True)` ensures messages cannot be modified after creation (safe for replay and auditing).

### 2.5 Protocol Validation (`protocol/validate.py`)

Enforces message compliance.

**Validation Rules**:
- All required fields present and non-empty
- Intent is in registered taxonomy
- Sender and recipient are valid agent names
- Task ID follows format `TASK-{uuid}`

**Modes**:
- **Strict**: Raises `ProtocolViolation` exception (development/testing)
- **Permissive**: Logs violation and continues (production fallback)

**Configuration**: `SYMPOSION_STRICT_PROTOCOL` environment variable

### 2.6 Logging System (`utils/logging.py`)

JSONL-based structured logging for auditability.

**Events Logged**:
- `message_enqueued` — Message added to queue
- `message_routed` — Message delivered to agent
- `protocol_violation` — Invalid message detected
- `task_completed` — Task lifecycle finished
- `message_dropped_task_completed` — Stale message rejected

**Output Format**: `examples/out/demo_log.jsonl` (queryable JSON lines)

---

## 3. Agent Framework

### Base Agent Class (`agents/base.py`)

All agents implement a common interface:

```python
class BaseAgent:
    name: str = "AGENT_NAME"
    
    def handle(self, msg: Message) -> List[Message]:
        """
        Process incoming message, return zero or more outgoing messages.
        """
        self._validate(msg)
        self.on_message(msg)  # Hook for logging/metrics
        out = self.process(msg)  # Implement in subclass
        for m in out:
            self._validate(m)
        return out
    
    def process(self, msg: Message) -> List[Message]:
        """Override in subclass to implement agent logic."""
        raise NotImplementedError
    
    def on_message(self, msg: Message) -> None:
        """Override for custom behavior (logging, metrics, etc.)"""
        pass
```

### The 7 Agent Roles

| Role | Agent | Responsibility | Output Intent |
|------|-------|-----------------|----------------|
| 🗣️ Interpreter | **Herm** | Parse user goal into structured form | STRUCTURED_GOAL |
| 📐 Architect | **Daed** | Decompose into tasks and plan execution | BUILD_TASK |
| 🔍 Researcher | **Athen** | Gather context and information | CONTEXT_BRIEF |
| 🤝 Diplomat | **Met** | Resolve conflicts and build consensus | CONSENSUS_DECISION |
| 🔨 Builder | **Heph** | Create artifacts and deliverables | ARTIFACT_BUILT |
| ✅ Judge | **Nem** | Validate quality and enforce standards | APPROVED_OUTPUT or REVISION_REQUEST |
| 📖 Narrator | **Clio** | Synthesize and report final results | FINAL_REPORT |

---

## 4. Message Protocol

See [Intent Taxonomy](./intent-taxonomy.md) for comprehensive message types.

### Intent Categories

**Goal & Intake** — Introduce and structure goals
- `NEW_GOAL`, `CLARIFY_GOAL`, `STRUCTURED_GOAL`

**Planning** — Decompose and plan execution
- `PLAN_REQUEST`, `TASK_DECOMPOSITION`, `REPLAN_REQUEST`

**Research** — Gather and verify information
- `RESEARCH_REQUEST`, `CONTEXT_BRIEF`, `FACT_CHECK`

**Alignment** — Resolve conflicts and build consensus
- `ALIGNMENT_CHECK`, `CONFLICT_NOTICE`, `CONSENSUS_DECISION`

**Execution** — Build and produce artifacts
- `BUILD_TASK`, `ARTIFACT_BUILT`, `EXECUTION_COMPLETE`

**Evaluation** — Assess quality and approve
- `EVALUATE_OUTPUT`, `REVISION_REQUEST`, `APPROVED_OUTPUT`

**Reporting** — Communicate outcomes
- `STATUS_UPDATE`, `FINAL_REPORT`, `EXPLANATION`

**System & Control** — Lifecycle and error handling
- `HEARTBEAT`, `ERROR_NOTICE`, `TASK_BLOCKED`, `TASK_CANCELLED`

---

## 5. Quality Gates: The Nemesis Gate

### Hard-Coded Rule

**All artifacts produced by HEPH must be evaluated by NEM before reaching CLIO.**

This rule is enforced in the orchestrator (not delegable):

```python
# In Orchestrator.run()
if out_msg.sender == "HEPH" and out_msg.intent in (Intent.ARTIFACT_BUILT.value, "ARTIFACT"):
    if out_msg.recipient != "NEM":
        # Force redirect to NEM
        out_msg.recipient = "NEM"
```

### Purpose

1. **Quality Assurance** — Ensures outputs meet standards
2. **Traceability** — Evaluation decisions are logged
3. **Revision Loops** — Failures trigger feedback to Heph for improvement
4. **Prevents Bypassing** — Recipients can't circumvent quality checks

### Example Flow

```
Heph produces ARTIFACT_BUILT
    → Nemesis Gate intercepts
    → Routes to NEM (forced)
    
NEM evaluates:
    ✗ No. 1 pass: REVISION_REQUEST
       → Heph receives feedback
       → Heph produces improved ARTIFACT_BUILT
       → NEM evaluates again
    ✓ No. 2 pass: APPROVED_OUTPUT
       → Clio receives verified output
       → Clio produces FINAL_REPORT
```

---

## 6. Orchestration Lifecycle

### Bootstrap

```python
orchestrator.bootstrap(Message(
    sender="HUMAN",
    recipient="HERM",
    intent="NEW_GOAL",
    content="User's request...",
    ...
))
```

### Processing Loop

```python
orchestrator.run(max_steps=200)
```

**Per Iteration**:
1. **Drain Queue** — Retrieve all queued messages (batch)
2. **Validate** — Check message protocol compliance
3. **Route** — Look up recipient agent in registry
4. **Apply Gates** — Enforce Nemesis Gate and other rules
5. **Deliver** — Call `agent.handle(msg)`
6. **Collect** — Gather output messages
7. **Track** — Mark task complete if FINAL_REPORT → HUMAN
8. **Repeat** — Until queue empty or max steps reached

**Exit Conditions**:
- Queue is empty (all messages processed)
- Max steps exceeded (prevent infinite loops)
- Critical error (orchestrator crash)

### Task Completion

A task is marked complete **only after** its FINAL_REPORT message has been routed to HUMAN. This ensures:
- All processing is complete
- Final output has been delivered
- Stale messages for this task are dropped in future iterations

---

## 7. Data Flow Patterns

### Linear Flow (Simple Tasks)

```
NEW_GOAL
  ↓ (Herm)
STRUCTURED_GOAL
  ↓ (Daed)
BUILD_TASK
  ↓ (Heph)
ARTIFACT_BUILT → [Nemesis Gate] → NEM
  ↓ (Nem - approve)
APPROVED_OUTPUT
  ↓ (Clio)
FINAL_REPORT → HUMAN
```

### Iterative Flow (With Research & Revisions)

```
NEW_GOAL
  ↓ (Herm)
STRUCTURED_GOAL
  ↓ (Daed)
├─→ RESEARCH_REQUEST → (Athen)
│     ↓
│   CONTEXT_BRIEF
│     ↓
└─→ → BUILD_TASK → (Heph)
      ↓
    ARTIFACT_BUILT → [Nemesis Gate] → NEM
      ↓ (Nem - revision no. 1)
    REVISION_REQUEST → (Heph)
      ↓
    ARTIFACT_BUILT → [Nemesis Gate] → NEM
      ↓ (Nem - approve)
    APPROVED_OUTPUT → (Clio)
      ↓
    FINAL_REPORT → HUMAN
```

### Conflict Resolution Flow

```
PLAN_PROPOSAL from Daed
  ↓ (Daed → Met)
CONFLICT_NOTICE from Heph (disagrees)
  ↓ (Heph → Met)
CONSENSUS_REQUEST
  ↓ (Met)
Met evaluates and decides...
CONSENSUS_DECISION
  ↓ (Met → Daed/Heph)
Both agents proceed with decision
```

---

## 8. Technical Stack

### Dependencies
- **Python**: 3.9+
- **External**: None (minimal v0 prototype)

### Project Structure

```
symposion/
├── __init__.py
├── models.py                    # Message and data structures
├── core/
│   ├── __init__.py
│   ├── messaging.py            # MessageBus
│   ├── orchestrator.py         # Main orchestrator
│   └── registry.py             # AgentRegistry
├── agents/
│   ├── __init__.py
│   ├── base.py                 # BaseAgent
│   ├── herm.py, daed.py, ...  # Specific agents
│   └── __init__.py
├── protocol/
│   ├── __init__.py
│   ├── intent.py               # Intent enum
│   ├── taxonomy.py             # Intent taxonomy
│   └── validate.py             # Validation logic
└── utils/
    ├── __init__.py
    ├── logging.py              # JsonlLogger
    ├── ids.py                  # ID generation
    └── __init__.py

scripts/
└── run_demo.py                 # Runnable demo

tests/
├── test_protocol_enforcement.py
└── test_schema_smoke.py

examples/
└── out/
    └── demo_log.jsonl          # Output: message trail
```

---

## 9. Extension Points

### Adding a New Agent

1. Create `symposion/agents/newagent.py`
2. Implement agent class with `name` and `handle(msg)` method
3. Register in demo setup (see `scripts/run_demo.py`)

**Template**:
```python
from typing import List
from ..models import Message
from ..protocol.intent import Intent

class NewAgent:
    name = "NEWAGENT"
    
    def handle(self, msg: Message) -> List[Message]:
        if msg.intent == "SOME_INTENT":
            # Process and return responses
            return [Message(...)]
        return []
```

### Adding New Intents

1. Add to `protocol/intent.py` enum
2. Update `protocol/validate.py` if needed
3. Document in [Intent Taxonomy](./intent-taxonomy.md)
4. Update agent handlers

### Adding Custom Orchestration Rules

Extend `orchestrator.run()` to add business logic (like Nemesis Gate).

---

## 10. Design Principles

### 1. **Explicit Over Implicit**
Every message has an explicit intent. Routing decisions are transparent.

### 2. **Immutability**
Messages are frozen dataclasses. Safe for replay and audit.

### 3. **Single Responsibility**
Each agent has one core job. Composition via messaging.

### 4. **Auditability**
Every decision is logged. Complete replay capability.

### 5. **Extensibility**
New agents, intents, and rules don't break existing code.

### 6. **Testability**
In-memory messaging enables deterministic testing.

---

## 11. Future Roadmap

### Beta (v1)
- FastAPI microservices per agent
- Persistent message queues (Redis/Kafka)
- Async message handling
- Distributed task coordination

### v2+
- LLM-backed agent implementations
- Tool/API integration (external knowledge, APIs)
- Multi-machine deployment
- Advanced scheduling and priority queuing

---

## See Also

- **[Intent Taxonomy](./intent-taxonomy.md)** — Complete message protocol reference
- **[Action Pipelines](./action-pipelines.md)** — CI/CD workflows and testing
- **[GitHub Repository](https://github.com/aksel/Symposion)** — Source code
- **[Message Schema](../schemas/message.schema.json)** — JSON schema definition
