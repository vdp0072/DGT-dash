---
trigger: always_on
---

# Global Agent Rules

These rules define the default behavior of the agent across the entire project.

- Treat the local database as the single source of truth.
- Assume the project is built incrementally; avoid large, sweeping refactors.
- Prefer explicit, readable solutions over clever or condensed ones.
- Explain reasoning and trade-offs when proposing designs or changes.
- Never perform destructive actions (deletes, schema drops, overwrites)
  without explicit confirmation.
- When unsure, ask a clarifying question instead of guessing.
