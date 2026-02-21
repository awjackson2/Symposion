---
layout: default
title: Architecture
---

# Symposion Architecture

A collaborative, role-based multi-agent framework designed for complex task decomposition and orchestrated execution.

## Subpages

- [Intent Taxonomy](intent-taxonomy.md) — Semantic message purposes and coordination protocol
- [Action Pipelines](action-pipelines.md) — GitHub Actions CI/CD workflows for testing and deployment

---

## 1. Overview

Symposion is a **message-driven architecture** where autonomous agents with distinct roles collaborate to achieve user-defined goals. Each agent is responsible for a specific phase of the goal lifecycle, from interpretation through execution to quality assurance and reporting.

### Core Philosophy
- **Separation of Concerns**: Each agent has a well-defined responsibility
- **Message-Driven**: Agents communicate asynchronously via a central message bus
- **Protocol Enforcement**: All communication follows a strict intent taxonomy and message schema
- **Quality Gates**: Critical outputs (artifacts) pass through a validation agent before finalization

---

## 2. System Architecture

### High-Level Flow

```
User Goal
    ↓
[HERM] Goal Interpreter
    ↓
[DAED] Architect/Planner
    ↓
[ATHEN] Researcher
    ↓
[HEPH] Builder/Executor
    ↓
[NEM] Quality Auditor (Nemesis Gate)
    ↓
[CLIO] Narrator
    ↓
Human Output
```

### Core Components

#### 2.1 Message Bus (`core/messaging.py`)
- **Responsibility**: In-memory message queue and dispatch
- **Features**:
  - FIFO message queue
  - JSONL logging of all messages for audit trails
  - Batch drain operations for efficient processing
- **v0 Implementation**: Single-process in-memory queue

#### 2.2 Orchestrator (`core/orchestrator.py`)
- **Responsibility**: Routes messages, enforces protocol, manages task lifecycle
- **Key Functions**:
  - Message validation against intent taxonomy
  - Agent registry lookup and message delivery
  - Task state tracking (active/completed)
  - Nemesis gate enforcement (hard-coded rule: HEPH artifacts → NEM)
  - Strict protocol mode for development/testing
  - Max step limit to prevent infinite loops
- **Task Completion**: Marked only after FINAL_REPORT reaches HUMAN

#### 2.3 Agent Registry (`core/registry.py`)
- **Responsibility**: Central agent catalog and lookup
- **Pattern**: Protocol-based agent discovery
- **Error Handling**: Raises KeyError for unknown agents

#### 2.4 Logging System (`utils/logging.py`)
- **Format**: JSONL (JSON Lines) for structured, queryable logs
- **Events Tracked**:
  - Message enqueued/routed
  - Protocol violations
  - Task completion
  - Message drops and state transitions

---

## 3. Agent Roles

### HERM (Interpreter)
**Goal**: Parse human intent into structured requirements
- **Input**: User goal (natural language)
- **Output**: Structured goal with OBJECTIVE, SCOPE, CONSTRAINTS, SUCCESS_CRITERIA, ASSUMPTIONS
- **Intent**: NEW_GOAL → STRUCTURED_GOAL
- **Next Agent**: DAED

### DAED (Architect)
**Goal**: Decompose structured goals into actionable tasks
- **Input**: Structured goal
- **Output**: Task plan with execution order and dependencies
- **Intent**: STRUCTURED_GOAL → BUILD_TASK (or research requests)
- **Next Agent**: ATHEN (for research) or HEPH (for direct tasks)

### ATHEN (Researcher)
**Goal**: Gather context and information
- **Input**: Research request
- **Output**: Context brief with findings
- **Intent**: RESEARCH_REQUEST → CONTEXT_BRIEF
- **Next Agent**: HEPH or DAED (for iterative planning)

### HEPH (Builder)
**Goal**: Produce tangible artifacts
- **Input**: Build tasks, context, requirements
- **Output**: Code, documentation, structured outputs, artifacts
- **Intent**: BUILD_TASK → ARTIFACT_BUILT
- **Next Agent**: NEM (via Nemesis gate enforcement)
- **Note**: All ARTIFACT_BUILT messages are intercepted and routed to NEM for validation

### NEM (Judge)
**Goal**: Quality assurance and goal alignment validation
- **Input**: Artifacts from HEPH
- **Evaluation Criteria**:
  - Goal alignment
  - Completeness
  - Quality standards
  - Logical correctness
- **Output**:
  - REVISION_REQUEST (with feedback) → back to HEPH
  - APPROVED_OUTPUT → to CLIO
- **Intent**: ARTIFACT_BUILT → REVISION_REQUEST or APPROVED_OUTPUT
- **Nemesis Gate**: Hard-coded orchestrator rule ensures HEPH outputs cannot bypass NEM

### CLIO (Narrator)
**Goal**: Synthesize and report final results
- **Input**: Approved outputs and task summary
- **Output**: Human-readable final report
- **Intent**: APPROVED_OUTPUT → FINAL_REPORT
- **Next Agent**: HUMAN

---

## 4. Message Protocol

### Message Schema (`models.py`)

```python
@dataclass(frozen=True)
class Message:
    sender: str              # Agent name (HERM, DAED, ATHEN, HEPH, NEM, CLIO)
    recipient: str           # Target agent or HUMAN
    task_id: str            # Unique task identifier (format: TASK-{uuid})
    intent: str             # Message type (see Intent enum)
    content: str            # Payload (message body)
    goal_reference: str     # Original user goal description
    urgency: Urgency        # LOW | NORMAL | HIGH | CRITICAL
    timestamp: float        # Unix timestamp (auto-populated)
    meta: Dict[str, Any]    # Optional metadata (revised flag, source_intent, etc.)
```

### Intent Taxonomy (`protocol/intent.py`)

| Intent | Sender | Recipient | Purpose |
|--------|--------|-----------|---------|
| NEW_GOAL | HUMAN | HERM | Initial goal submission |
| STRUCTURED_GOAL | HERM | DAED | Parsed goal template |
| RESEARCH_REQUEST | DAED | ATHEN | Information gathering request |
| CONTEXT_BRIEF | ATHEN | HEPH/DAED | Research findings |
| BUILD_TASK | DAED | HEPH | Build instructions |
| ARTIFACT_BUILT | HEPH | NEM | Deliverable (intercepted by Nemesis gate) |
| REVISION_REQUEST | NEM | HEPH | Feedback and change request |
| APPROVED_OUTPUT | NEM | CLIO | Validated deliverable |
| FINAL_REPORT | CLIO | HUMAN | Human-readable summary |

### Message Validation (`protocol/validate.py`)
- Enforces required fields (sender, recipient, task_id, intent, content, goal_reference, urgency, timestamp)
- Validates intent against taxonomy
- Raises `ProtocolViolation` on invalid messages
- Strict mode (`SYMPOSION_STRICT_PROTOCOL` env var) raises exceptions; permissive mode logs and continues

---

## 5. Orchestration & Lifecycle

### Execution Model

1. **Bootstrap** (`orchestrator.bootstrap(first_message)`)
   - Enqueue initial message from HUMAN to HERM

2. **Process Loop** (`orchestrator.run(max_steps)`)
   - Per iteration:
     - Drain message queue (batch processing)
     - For each message:
       - Check if task is completed (skip if yes, except FINAL_REPORT)
       - Validate message protocol
       - Route to recipient agent
       - **Apply Nemesis Gate**: If sender=HEPH and intent=ARTIFACT_BUILT, force recipient=NEM
       - Collect agent responses
       - Mark task complete (if FINAL_REPORT reaches HUMAN)
   - Stop when queue empty or max steps reached

3. **Task State Management**
   - `task_state`: Active task metadata
   - `completed_tasks`: Tasks marked done after FINAL_REPORT delivery
   - Prevents reprocessing of messages for completed tasks

### Nemesis Gate (Hard-Coded Rule)

**Rule**: No HEPH artifact reaches CLIO without NEM approval

```python
if out_msg.sender == "HEPH" and out_msg.intent in (Intent.ARTIFACT_BUILT.value, "ARTIFACT"):
    if out_msg.recipient != "NEM":
        # Force redirect to NEM
        out_msg.recipient = "NEM"
```

**Purpose**: Ensures quality control and prevents unvalidated outputs from propagating.

---

## 6. Data Flow & Collaboration Patterns

### Linear Flow (Simple Tasks)
```
NEW_GOAL
  ↓ (HERM)
STRUCTURED_GOAL
  ↓ (DAED)
BUILD_TASK
  ↓ (HEPH)
ARTIFACT_BUILT → [NEM Gate] → ARTIFACT_BUILT
  ↓ (NEM)
APPROVED_OUTPUT
  ↓ (CLIO)
FINAL_REPORT
```

### Iterative Flow (With Research & Revisions)
```
NEW_GOAL
  ↓ (HERM)
STRUCTURED_GOAL
  ↓ (DAED)
RESEARCH_REQUEST
  ↓ (ATHEN)
CONTEXT_BRIEF
  ↓ (DAED or HEPH)
BUILD_TASK
  ↓ (HEPH)
ARTIFACT_BUILT → [NEM Gate]
  ↓ (NEM - No. 1 pass: REVISION_REQUEST)
  ↓ (HEPH - Revise)
ARTIFACT_BUILT → [NEM Gate]
  ↓ (NEM - No. 2 pass: APPROVED_OUTPUT)
  ↓ (CLIO)
FINAL_REPORT
```

---

## 7. Technical Stack

### Current Implementation (v0)
- **Language**: Python 3.9+
- **Concurrency**: Single-process, synchronous message dispatch
- **Persistence**: JSONL logging to `examples/out/demo_log.jsonl`
- **Dependencies**: None (minimal prototype)

### Key Files
```
symposion/
├── models.py                    # Message and data structures
├── core/
│   ├── messaging.py            # Message bus
│   ├── orchestrator.py         # Main orchestration engine
│   ├── registry.py             # Agent registry
│   └── __init__.py
├── agents/
│   ├── base.py                 # Base agent class
│   ├── herm.py, daed.py, ..   # Agent implementations
│   └── __init__.py
├── protocol/
│   ├── intent.py               # Intent enum
│   ├── taxonomy.py             # Intent taxonomy
│   ├── validate.py             # Protocol validation
│   └── __init__.py
└── utils/
    ├── logging.py              # JSONL logger
    ├── ids.py                  # ID generation
    └── __init__.py
```

---

## 8. Extension Points

### Adding New Agents
1. Create new file in `symposion/agents/{name}.py`
2. Implement agent class with `name` attribute and `handle(msg: Message) -> List[Message]` method
3. Register in orchestrator setup (see `scripts/run_demo.py`)

### Custom Intents
1. Add to `protocol/intent.py` enum
2. Update protocol validator if new validation logic needed
3. Update agent handlers to recognize new intents

### Advanced Features (v1+)
- Persistent state storage
- Microservices architecture
- Tool/API integration
- LLM-backed agent implementations
- Distributed message bus (async message queue)
- Per-agent metrics and telemetry

---

## 9. Design Patterns

### Message Handler Pattern
```python
def handle(self, msg: Message) -> List[Message]:
    # Validate, process, return zero or more messages
    # Each output message routes to next agent
    # Recipient determines message flow
```

### Nemesis Gate Pattern
- Orchestrator applies hard-coded business rule
- Prevents agents from bypassing quality gates
- Extensible for additional rules in future versions

### Task Tracking Pattern
- task_id propagates through all messages in single goal execution
- completed_tasks set prevents reprocessing and loops
- goal_reference maintained for traceability

---

## 10. Future Direction

**Beta Phase** will introduce:
- FastAPI microservices for each agent
- Persistent message queue (Redis/Kafka)
- Distributed task coordination
- Multi-machine deployment
- Async message handling
- Agent-specific tool integration

---
