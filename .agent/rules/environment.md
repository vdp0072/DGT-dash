---
trigger: always_on
---

# Python Environment & Dependency Rules

These rules govern how Python environments and dependencies are managed.

- Always use a Python virtual environment (`venv`) for this project.
- Never install Python packages globally.
- Assume Python version is explicitly defined (e.g. python3.10 or python3.11).
- All dependencies must be declared in a `requirements.txt` file.
- When adding a new dependency:
  - Explain why it is needed.
  - Prefer stable, well-maintained libraries.
  - Avoid redundant or overlapping libraries.
- Do not use undeclared dependencies in code examples.
- If multiple dependency groups are needed, recommend separating them
  (e.g. `requirements.txt`, `requirements-dev.txt`).
- Prefer reproducible installs (`pip install -r requirements.txt`).
