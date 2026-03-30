# Week 5 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **Akhmad Daffa Azzikri** \
SUNet ID: **TODO** \
Citations: Utilized Warp AI for agentic development.

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
### Automation A: Warp Drive saved prompts, rules, MCP servers

**Target Tasks:** Task 10 (Test coverage improvements) & Task 7 (Robust error handling)
**Name:** Auto-Test Runner & Debugger

a. Design of each automation, including goals, inputs/outputs, steps
> Created a Warp Rule named "Auto-Test Runner & Debugger" that intercepts any prompt containing "run tests" or "fix tests". The goal is to autonomously execute `pytest`, analyze tracebacks, fix code in the `backend/` folder (with special handling for Windows WinError 32 SQLite teardown issues), write any missing 400/404 test cases, and re-run until 100% of tests pass.

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before:** Manual debugging was required for OS-specific database locking errors (WinError 32 on SQLite teardown), which meant searching StackOverflow and iterating through fixes by hand.
> **After:** The agent autonomously modified `conftest.py` to properly dispose of engines, updated deprecated FastAPI lifespan events in `main.py`, and wrote 4 new test cases. The result was a 7/7 pass rate achieved instantly without manual intervention.

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> High autonomy. The agent had read/write permissions for the `backend/` directory. Supervision was done by reviewing the diffs in the chat panel before accepting each change.

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> N/A

e. How you used the automation (what pain point it resolves or accelerates)
> Eliminates the tedious cycle of manual TDD, debugging boilerplate code, and searching StackOverflow for OS-specific quirks. A single prompt triggers a fully autonomous test-fix-verify loop.



### Automation B: Multi‑agent workflows in Warp 

**Target Task:** Task 4 (Action items filters and bulk complete)

a. Design of each automation, including goals, inputs/outputs, steps
> Simulated parallel development using two autonomous agents in separate Warp tabs to concurrently build a full-stack feature without file conflicts. Tab 1 (Backend Agent) was scoped to `backend/` and tasked with building `GET /action-items?completed=...` and `POST /action-items/bulk-complete` endpoints plus tests. Tab 2 (Frontend Agent) was scoped to `frontend/` and tasked with building UI filter toggles and a bulk complete checkbox table.

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before:** Frontend and backend development were done sequentially — one after the other — by a single developer.
> **After:** Both layers were developed concurrently in parallel, cutting feature delivery time roughly in half.

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> Scoped autonomy. Agent 1 was strictly restricted to `backend/` and Agent 2 to `frontend/`, preventing any cross-directory interference. Supervised by verifying terminal outputs for the backend and inspecting the browser UI for the frontend.

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> **Roles:** Tab 1 (Backend Agent) built the filter and bulk-complete API endpoints with tests. Tab 2 (Frontend Agent) built the filter toggle UI and the checkbox-based bulk complete table.
> **Concurrency Wins:** Zero file clashing or git merge conflicts due to strict directory-level constraints. Backend tests achieved 15/15 passed instantly.
> **Risks/Failures:** The Frontend Agent initially hallucinated and forgot to render the actual checkboxes, making the bulk complete button useless. A managerial prompt revision was required to correct the UI logic.

e. How you used the automation (what pain point it resolves or accelerates)
> Halves feature delivery time and enforces a clean separation of concerns between API and UI development. The directory-scoped constraints act as an automatic guard against merge conflicts.


### (Optional) Automation C: Any Additional Automations

> N/A

