# Cobane — AI Code Review Assistant

[![Build & Lint Checks](https://github.com/sayan-kundu000/cobane/actions/workflows/lint.yml/badge.svg)](https://github.com/sayan-kundu000/cobane/actions)
[![Pytest Coverage](https://github.com/sayan-kundu000/cobane/actions/workflows/test.yml/badge.svg)](https://github.com/sayan-kundu000/cobane/actions)
[![Deployment Status](https://img.shields.io/badge/Render-Deployed-brightgreen)](https://render.com)
[![Python Version](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Cobane** is a modular, production-ready AI-powered Code Review Assistant. It combines static code analysis (Pylint, Bandit, Radon), language complexity indexing, and generative AI review suggestions to provide comprehensive feedback on submitted codebases.

---

## 🚀 Key Features

* **Advanced REST API**: Unified envelopes standard, whitelisted sorting, advanced search, filtering, and pagination.
* **Modular Static Analysis Engine**: Dynamic registry orchestration of parallel subprocesses:
  * **Pylint**: For style validation and code quality scoring.
  * **Bandit**: For security checks and vulnerability identification.
  * **Radon**: For LOC metrics, Cyclomatic Complexity, and Maintainability Index checks.
* **AI Code Review Engine**: Token-limited chunking, exponential backoff retries, and schema validation.
* **JWT Authentication**: Secure user login, session refreshing, profile configurations, and password hashing.
* **Production Infrastructure-As-Code**: Ready-to-deploy configurations for Docker, Render, and GitHub Actions.

---

## 🛠️ Technology Stack

* **Language**: Python 3.12 / 3.13+
* **Framework**: FastAPI (Asynchronous API layer)
* **ORM & Database**: SQLAlchemy 2.x, Alembic, PostgreSQL, SQLite (for local testing)
* **Analyzers**: Pylint, Bandit, Radon
* **AI Model API**: OpenAI Compatible API (GPT-4o or Mock engine)
* **Deployment**: Docker, Docker Compose, Render

---

## 📁 Repository Structure

```
├── .github/                 # GitHub workflows (CI/CD) and templates
├── backend/                 # FastAPI Backend Codebase
│   ├── app/                 # Application Core Layer
│   │   ├── api/             # API Routers & Controllers
│   │   ├── db/              # Database Repositories & Base ORM Models
│   │   ├── services/        # Business logic services
│   │   │   ├── ai/          # AI Code Review orchestrator subpackage
│   │   │   └── static_analysis_engine/ # Static checker adapters
│   │   └── schemas/         # Pydantic schemas (requests & responses)
│   ├── tests/               # Pytest suite (unit and integration tests)
│   ├── Dockerfile.prod      # Production-ready multi-stage Docker build
│   └── render.yaml          # Render blueprint configuration
├── docs/                    # Architecture and deployment manuals
└── README.md                # Master guide
```

---

## ⚙️ Environment Variables Setup

Create a `.env` file at the root folder or under `backend/` by referencing `.env.example`:

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `DATABASE_URL` | SQLAlchemy Database Connection URI | `sqlite+aiosqlite:///./test.db` |
| `JWT_SECRET_KEY` | JWT signature encryption secret key | *Randomly generated* |
| `JWT_REFRESH_SECRET_KEY` | Refresh token encryption secret key | *Randomly generated* |
| `AI_PROVIDER` | AI provider selector: `openai` or `mock` | `openai` |
| `AI_PROVIDER_API_KEY` | API Key credential for the provider | `mock-key` |
| `AI_MODEL` | Provider model name tag | `gpt-4o` |
| `ALLOWED_ORIGINS` | CORS allowed origins list | `*` |

---

## 💻 Local Development Setup

### 1. Prerequisites
- Python 3.12+
- Docker (optional)

### 2. Manual Installation
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start local server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🐳 Docker Deployment

To build and run the optimized production image locally:

```bash
cd backend
docker build -t cobane-backend -f Dockerfile.prod .
docker run -d -p 8000:8000 --name cobane-app \
  -e DATABASE_URL=sqlite+aiosqlite:///./production.db \
  -e JWT_SECRET_KEY=your-production-jwt-secret-key-must-be-long \
  -e JWT_REFRESH_SECRET_KEY=your-production-refresh-secret-key-must-be-long \
  cobane-backend
```

---

## 🚀 Deployment to Render

This repository includes a `render.yaml` Blueprint file for Render deployments:

1. **Push code** to your repository at GitHub.
2. Go to the **Render Dashboard** and select **Blueprints**.
3. Link your GitHub account and select this repository.
4. Render will read `render.yaml` and spin up:
   - A managed **PostgreSQL** database cluster.
   - An isolated **Web Service** running the `Dockerfile.prod` container configuration.
5. In the Web Service Environment tab, add the environment variable `AI_PROVIDER_API_KEY` containing your OpenAI API Key.

---

## 🧪 Testing

To run the full test suite locally:

```bash
cd backend
python -m pytest
```

---

## 🔒 Security Policy
For security disclosures or vulnerability reporting instructions, refer to our [SECURITY.md](SECURITY.md).

## 📄 License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
