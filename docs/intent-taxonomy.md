# Intent Taxonomy

An **intent** is the semantic purpose of a message—it defines *why* a message exists and what the recipient is expected to do. Intents drive agent behavior and enable explicit, loggable coordination across the system.

---

## Purpose

Rather than relying on implicit message patterns, Symposion makes intent explicit. This ensures:
- **Clarity** — Each message has an unambiguous purpose
- **Routing** — The orchestrator knows which agent should handle it
- **Logging** — Message trails are interpretable and replayable
- **Extensibility** — New intents can be added as workflows mature

---

## Intent Categories

### 🎯 Goal & Intake Intents

Used to introduce, clarify, and structure goals.

| Intent | Sender | Recipient | Purpose |
|--------|--------|-----------|---------|
| **NEW_GOAL** | Human / System | Herm | Introduce a new goal to be processed |
| **CLARIFY_GOAL** | Herm / Daed | Human | Request clarification about a goal |
| **GOAL_CLARIFICATION** | Human | Herm | Response with clarifications |
| **STRUCTURED_GOAL** | Herm | Daed | Herm's structured interpretation ready for planning |
| **UPDATE_GOAL** | Any | Daed | Modify scope, constraints, or success criteria |

---

### 📋 Planning Intents (Daed)

Used for goal decomposition, planning, and replanning.

| Intent | Sender | Recipient | Purpose |
|--------|--------|-----------|---------|
| **PLAN_REQUEST** | Herm | Daed | Ask Daed to generate a plan |
| **TASK_DECOMPOSITION** | Daed | Daed / Athen | Break a goal into subtasks |
| **PLAN_PROPOSAL** | Daed | Met / Athen | Proposed plan for review or alignment |
| **PLAN_APPROVED** | Met | Daed | Plan accepted for execution |
| **REPLAN_REQUEST** | Nem / Heph | Daed | Trigger replanning due to failure or rejection |

---

### 🔍 Research & Context Intents (Athen)

Used to gather, verify, and communicate knowledge.

| Intent | Sender | Recipient | Purpose |
|--------|--------|-----------|---------|
| **RESEARCH_REQUEST** | Daed / Met | Athen | Request information or context |
| **CONTEXT_BRIEF** | Athen | Daed / Met | Summary of relevant knowledge |
| **FACT_CHECK** | Any | Athen | Request to verify claims |
| **FACT_RESULT** | Athen | Any | Verified or corrected information |

---

### 🤝 Alignment & Negotiation Intents (Met)

Used for conflict resolution and consensus building.

| Intent | Sender | Recipient | Purpose |
|--------|--------|-----------|---------|
| **ALIGNMENT_CHECK** | Daed / Heph | Met | Confirm agents agree on direction |
| **CONFLICT_NOTICE** | Any | Met | Signal disagreement or concern |
| **CONSENSUS_REQUEST** | Daed / Nem | Met | Ask Met to mediate and decide |
| **CONSENSUS_DECISION** | Met | Daed / Heph | Final decision after mediation |
| **ESCALATION_NOTICE** | Any | Human / Met | Human or higher-level escalation |

---

### 🔨 Execution Intents (Heph)

Used to trigger, track, and report on artifact creation.

| Intent | Sender | Recipient | Purpose |
|--------|--------|-----------|---------|
| **BUILD_TASK** | Daed | Heph | Instruction to create something |
| **EXECUTION_START** | Heph | Orchestrator | Signal that building has begun |
| **ARTIFACT_BUILT** | Heph | Nem | Deliverable produced and ready for evaluation |
| **ARTIFACT_UPDATE** | Heph | Nem | Revised deliverable after feedback |
| **EXECUTION_COMPLETE** | Heph | Orchestrator | Task finished (artifact accepted or rejected) |

---

### ✅ Evaluation Intents (Nem)

Used to assess quality, approve, or request revisions.

| Intent | Sender | Recipient | Purpose |
|--------|--------|-----------|---------|
| **EVALUATE_OUTPUT** | Heph | Nem | Request evaluation of an artifact |
| **QUALITY_CHECK** | Nem | Nem | Explicit quality review (internal) |
| **REVISION_REQUEST** | Nem | Heph | Output needs changes |
| **REJECTION_NOTICE** | Nem | Daed / Heph | Output rejected; escalate or replan |
| **APPROVED_OUTPUT** | Nem | Clio | Output accepted and ready for reporting |

---

### 📖 Reporting Intents (Clio)

Used to communicate outcomes and reasoning to humans.

| Intent | Sender | Recipient | Purpose |
|--------|--------|-----------|---------|
| **STATUS_UPDATE** | Any | Clio | Progress report (intermediate) |
| **SUMMARY_REQUEST** | Human | Clio | Ask for a structured summary |
| **FINAL_REPORT** | Clio | Human | Human-readable final result |
| **EXPLANATION** | Clio | Human | Rationale for decisions and recommendations |

---

### 🔧 System & Control Intents

Used for housekeeping, error handling, and lifecycle management.

| Intent | Sender | Recipient | Purpose |
|--------|--------|-----------|---------|
| **HEARTBEAT** | Any | Orchestrator | Agent alive signal (keep-alive) |
| **ERROR_NOTICE** | Any | Orchestrator / Human | Something failed |
| **TASK_BLOCKED** | Any | Orchestrator / Human | Progress cannot continue |
| **TASK_CANCELLED** | Human / Orchestrator | All | Task terminated |
| **TASK_COMPLETE** | Clio | Orchestrator / Human | Task lifecycle finished |
| **LOG_ENTRY** | Any | Logging system | Structured logging message |

---

## Intent Design Principles

### 1. **Specificity**
Each intent has a precise, narrow meaning. Ambiguous messages are avoided.

### 2. **Causality**
Intents imply a response. Not all responses need an explicit return message, but the pathway should be clear.

### 3. **Idempotency**
Idempotent intents (like `APPROVED_OUTPUT`) are safe to replay. Non-idempotent ones (like `BUILD_TASK`) should be carefully isolated.

### 4. **Versioning**
New intents can be added without breaking old ones. Deprecated intents are marked and phased out.

### 5. **Human-Readable**
Intent names use SNAKE_CASE and are semantically obvious (e.g., `REVISION_REQUEST`, not `REV_Q`).

---

## Using Intents in Your Agents

When implementing an agent, check the `intent` field and dispatch accordingly:

```python
def process_message(self, message):
    intent = message.intent
    
    if intent == "PLAN_REQUEST":
        return self.create_plan(message)
    elif intent == "PLAN_APPROVED":
        return self.execute_plan(message)
    elif intent == "REPLAN_REQUEST":
        return self.revise_plan(message)
    else:
        raise UnknownIntentError(f"Unknown intent: {intent}")
```

---

## Extending the Taxonomy

To add a new intent:

1. Define it clearly (purpose, sender, recipient)
2. Add it to the appropriate category above
3. Update agent message handlers
4. Document the response (if any)
5. Add tests for the new intent flow

---

## See Also

- [Architecture Overview](architecture.md)
- [Action Pipelines](action-pipelines.md)
- [Message Schema](../schemas/message.schema.json)
