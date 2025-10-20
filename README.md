# x_make_yahw_x — Intake Canary Manual

This canary is the first executable every new environment touches. A simple greeting, yes, but it proves logging, packaging, and orchestrator signaling are wired before we escalate.

## Mission Log
- Verify interpreter resolution and module packaging on a clean workspace.
- Exercise shared logging and exporter hooks so `make_all_summary.json` records the Intake Reconnaissance column correctly.
- Provide the visitor with a low-risk target to confirm compliance pipelines are awake.
- Set the baseline standard for documentation and QA across the lab.

## Instrumentation
- Python 3.11 or newer.
- Ruff, Black, MyPy, Pyright, pytest if you run the QA net.

## Operating Procedure
1. `python -m venv .venv`
2. `\.venv\Scripts\Activate.ps1`
3. `python -m pip install --upgrade pip`
4. `pip install -r requirements.txt`
5. `python -m x_make_yahw_x`

The run emits the greeting and registers evidence in the orchestrator summary. Capture the JSON artefact alongside Change Control notes.

## Evidence Checks
| Check | Command |
| --- | --- |
| Formatting sweep | `python -m black .` |
| Lint interrogation | `python -m ruff check .` |
| Type audit | `python -m mypy .` |
| Static contract scan | `python -m pyright` |
| Functional verification | `pytest` |

## System Linkage
- [Changelog](./CHANGELOG.md)
- [Road to 0.20.4 Engineering Proposal](../x_0_make_all_x/Change%20Control/0.20.4/Road%20to%200.20.4%20Engineering%20Proposal.md)
- [Road to 0.20.3 Engineering Proposal](../x_0_make_all_x/Change%20Control/0.20.3/Road%20to%200.20.3%20Engineering%20Proposal.md)

## Reconstitution Drill
During the monthly rebuild I run this canary first: recreate the environment, execute the greeting, confirm the orchestrator logs the intake evidence, and record runtime plus interpreter version. Any surprise leads to immediate documentation and Change Control updates.

## Cross-Referenced Assets
- [x_make_common_x](../x_make_common_x/README.md) — showcases shared logging and subprocess helpers at minimum scale.
- [x_make_github_visitor_x](../x_make_github_visitor_x/README.md) — inspects this repo to prove the compliance pipeline is awake.
- [x_0_make_all_x](../x_0_make_all_x/README.md) — orchestrator refuses heavier workloads until this canary passes.

## Conduct Code
Keep the sample tight. Any message change or behaviour shift must be justified in Change Control with verification steps. The baseline only moves when the evidence demands it.

## Sole Architect's Note
I wrote this canary to embody the lab’s discipline. Logging, packaging, orchestrator signaling—every line comes from the same hand so accountability stays singular.

## Legacy Staffing Estimate
- Without AI acceleration you’d still need: 1 automation engineer, 1 QA lead, 1 documentation specialist.
- Timeline: 4–5 engineer-weeks to reach this level of governance.
- Budget: USD 30k–45k to match the embedded evidence standards.

## Technical Footprint
- Language: Python 3.11+ with minimal dependencies.
- Tooling: Shared logging and subprocess utilities from `x_make_common_x`, QA stack (Ruff, Black, MyPy, Pyright, pytest).
- Integration: Orchestrator intake stage, visitor verification, Change Control evidence captured during monthly drills.
