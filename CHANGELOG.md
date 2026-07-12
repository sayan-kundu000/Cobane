# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-07-12

### Added
- **Core Architecture & Scaffold**: Configured FastAPI base, database repositories, Alembic migrations config, and health checks.
- **REST API Layer (v1)**: Developed authenticated controllers scoped for user profiles, project CRUD, complexity reports downloads, settings configs, and review triggers.
- **AI Code Review Engine**: Built structured orchestrator managing code chunking, token estimation, openai provider integrations, mock fallback configurations, and backoff retries.
- **Static Analysis Engine**: Implemented registry-based execution adapters for Pylint, Bandit, and Radon metrics.
- **Dockerization Assets**: Optimized multi-stage Docker build pipeline running under non-privileged app user credentials.
- **CI/CD Integration Workflows**: Added linting style formats verification, unit testing service pipelines, and Render build webhooks.
- **Render Blueprints Support**: Defined declarative managed app and DB services configurations.
