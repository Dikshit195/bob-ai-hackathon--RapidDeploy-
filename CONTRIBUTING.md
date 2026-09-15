# Contributing & Submission Guide — RapidDeploy

This file documents how the RapidDeploy submission was assembled and what each part of
the repository contains. It also serves as a reference for anyone who wants to run,
review, or build on the project.

---

## Repository

| Field | Value |
|---|---|
| **Repo name** | `bob-ai-hackathon--RapidDeploy-` |
| **Team** | RapidDeploy |
| **Track** | Open |
| **Lead** | Patel Dikshit — 26mca115@gmail.com |
| **Visibility** | Public |

Clone the repository:

```bash
git clone https://github.com/ibm-hackathon/bob-ai-hackathon--RapidDeploy-.git
cd bob-ai-hackathon--RapidDeploy-
```

---

## Submission File Checklist

### `submission.yaml` ✅
All required fields are filled in — team details, problem statement, solution summary,
key features, tech stack, and artifact paths.
See [`submission.yaml`](submission.yaml).

### `README.md` ✅
All placeholder text has been replaced with real project content — team info, problem
statement, solution, key features, tech stack, repo structure, how-to-run steps, known
limitations, and what we're most proud of.
See [`README.md`](README.md).

### `docs/` ✅
All four documentation files are complete:

| File | Contents |
|---|---|
| [`docs/problem-statement.md`](docs/problem-statement.md) | The supply chain / cold-chain monitoring problem |
| [`docs/solution-overview.md`](docs/solution-overview.md) | How RapidDeploy solves it |
| [`docs/architecture.md`](docs/architecture.md) | System architecture and component diagram |
| [`docs/setup-guide.md`](docs/setup-guide.md) | Step-by-step instructions to run the project locally |

### Source Code ✅
The entire backend lives in [`main.py`](main.py) at the repo root.
The entire frontend lives in [`static/index.html`](static/index.html).

> **Note:** The `src/` folder contains [`src/README.md`](src/README.md) (code map) and
> [`src/.env.example`](src/.env.example) (environment variable template). No `.env` file
> with real secrets is committed — it is in `.gitignore`.

### `demo/` ✅
| File | Status |
|---|---|
| [`demo/demo-video-link.txt`](demo/demo-video-link.txt) | Real video URL |
| [`demo/live-demo-url.txt`](demo/live-demo-url.txt) | Live demo URL (or "NOT DEPLOYED") |
| [`demo/screenshots/`](demo/screenshots/) | Per-tab HTML screenshots of the running app |

### `presentation/` ✅
Slide deck is at [`presentation/RapidDeploy.pptx`](presentation/RapidDeploy.pptx).

---

## How to Run

Full instructions: [`docs/setup-guide.md`](docs/setup-guide.md)

**Quick start:**

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# 2. Install dependencies (no build step needed)
pip install fastapi uvicorn[standard] pydantic

# 3. Start the server
uvicorn main:app --reload
```

Open **`http://localhost:8000`** — no `.env` file or external services required.

**Run the test suite:**

```bash
pip install pytest httpx
pytest test_main.py -v        # 10 tests, all should pass in ~0.5 s
```

---

## Submission Checklist

- [x] `submission.yaml` — all required fields filled
- [x] `README.md` — no `[placeholder]` text remaining
- [x] `docs/setup-guide.md` — step-by-step run instructions verified
- [x] Source code committed (`main.py` + `static/index.html`) — no `node_modules`, no `.env`
- [x] `demo/demo-video-link.txt` — real video URL present
- [x] `demo/screenshots/` — per-tab screenshots of the running application
- [x] `presentation/RapidDeploy.pptx` — slide deck present
- [x] GitHub Actions **✅ Validate Submission** is green
- [x] Repository is **Public**
- [x] Entry form submitted before the deadline

---
