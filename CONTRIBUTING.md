# Contributing to Cobane

We welcome contributions of all forms to **Cobane — AI Code Review Assistant**! 

To guarantee code quality, reproducibility, and maintainability, please adhere to the following workflows when proposing additions or bug fixes.

---

## 1. Code Style and Quality Standards

All Python code must comply with:
- **Style Rules**: Checked using `black` formatter. Run `black backend/app` locally before committing.
- **Code Linter**: Checked using `flake8`. Run `flake8 backend` to verify syntax rules.
- **Complexity Guidelines**: Standard CC thresholds must remain below 10 for all methods. Run `radon cc backend/app` to verify.

---

## 2. Development Workflow

1. **Fork & Branch**: Fork this repository to your profile and create a descriptive branch:
   - Features: `feature/your-feature-name`
   - Bug Fixes: `bugfix/issue-id-description`
   - Security: `hotfix/vulnerability-patch`
2. **Commit Conventions**: Use structured prefixes:
   - `feat: Add support for Gitlab webhooks`
   - `fix: Resolve token manager character fallback boundary error`
   - `docs: Update PostgreSQL migration steps`
   - `chore: Upgrade Uvicorn package version`
3. **Write Unit Tests**: Add corresponding tests in `backend/tests/unit/` for any new service layer functions.
4. **Local Verification**: Ensure all tests pass:
   ```bash
   cd backend
   python -m pytest
   ```

---

## 3. Pull Request Submission Checklist

When opening a Pull Request:
- Reference the related Issue number (e.g. `Fixes #42`).
- Fill out the PR Template completely.
- Verify that CI pipelines (lint checks and pytest runs) succeed.
- Request review from **sayan-kundu000** or project maintainers.
