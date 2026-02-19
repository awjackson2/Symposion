# Symposion (Starter Prototype)

This is a starter scaffold for **Symposion**, a role-based multi-agent framework.

Roles:
- Herm (Interpreter)
- Daed (Architect)
- Athen (Sage)
- Met (Diplomat)
- Heph (Builder)
- Nem (Judge)
- Clio (Narrator)

## Quickstart (local demo)

```bash
python -m scripts.run_demo
```

Outputs:
- `examples/out/demo_log.jsonl` (message trail)
- terminal prints a FINAL_REPORT message to `HUMAN`

## Message Schema
See `schemas/message.schema.json`.

## Notes
This prototype uses an in-memory message bus and simple placeholder agent logic.
Replace agent internals with LLM calls, tools, and persistence as you iterate.
