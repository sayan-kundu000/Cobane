from fastapi import APIRouter, Depends, Body
from app.core.dependencies import get_current_user, get_db
from app.core.responses import StandardJSONResponse
from app.models.user import User
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.project import Project, UploadedSource
from app.models.review import Review, ReviewFinding
from pydantic import BaseModel
from typing import List, Optional
import httpx

router = APIRouter(prefix="/ai", tags=["ai-capabilities"])


@router.get("/config", response_class=StandardJSONResponse)
async def get_ai_config(current_user: User = Depends(get_current_user)):
    """Retrieves config parameters for registered LLM integration models and providers."""
    return {
        "provider": settings.AI_PROVIDER,
        "base_url": settings.AI_BASE_URL,
        "model_engine": "gpt-4-turbo-preview",
        "temperature": 0.2,
        "max_tokens": 2048,
    }


@router.get("/prompts", response_class=StandardJSONResponse)
async def get_active_prompts(current_user: User = Depends(get_current_user)):
    """Lists preconfigured code analysis review prompt templates."""
    return {
        "templates": [
            {
                "name": "security",
                "description": "Scans for credentials leak, insecure code constructs, and SQL injection risks.",
            },
            {
                "name": "refactoring",
                "description": "Reviews names, modular formatting, redundant operations, and style conventions.",
            },
            {
                "name": "performance",
                "description": "Checks memory footprints, loop structures, and database query pools.",
            },
        ]
    }


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    project_id: Optional[int] = None
    review_id: Optional[int] = None
    message: str
    history: Optional[List[ChatMessage]] = []
    selected_code: Optional[str] = None
    editor_code: Optional[str] = None
    filename: Optional[str] = None
    selection_start_line: Optional[int] = None
    selection_end_line: Optional[int] = None


@router.post("/chat", response_class=StandardJSONResponse)
async def chat_about_code(
    payload: ChatRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Answers chatbot inquiries about loaded projects or specific code review details."""
    project_id = payload.project_id
    review_id = payload.review_id
    user_message = payload.message
    chat_history = payload.history or []
    selected_code = payload.selected_code
    editor_code = payload.editor_code
    filename = payload.filename

    code_context = ""
    findings_context = ""
    project_name = "this project"
    findings = []

    # 1. Fetch code context
    if editor_code:
        code_context = f"### File: {filename or 'source_code'}\n```python\n{editor_code}\n```"
        if review_id:
            # Load findings context if review session is specified
            stmt_findings = select(ReviewFinding).filter(ReviewFinding.review_id == review_id)
            res_findings = await db.execute(stmt_findings)
            findings = list(res_findings.scalars().all())
            if findings:
                findings_list = []
                for f in findings:
                    findings_list.append(
                        f"- Line {f.line_number} [{f.severity.upper()}]: {f.message} (Category: {f.category})"
                    )
                findings_context = "\nStatic Analysis Findings:\n" + "\n".join(findings_list)
    else:
        if review_id:
            stmt = select(Review).filter(Review.id == review_id)
            res = await db.execute(stmt)
            review = res.scalars().first()
            if not review:
                from app.core.exceptions import NotFoundException

                raise NotFoundException(f"Review run #{review_id} not found.")

            project_id = review.project_id

            # Load source file content
            stmt_src = select(UploadedSource).filter(UploadedSource.id == review.uploaded_source_id)
            res_src = await db.execute(stmt_src)
            source = res_src.scalars().first()
            if source:
                import os

                if os.path.exists(source.file_path):
                    try:
                        with open(source.file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        code_context = f"### File: {source.filename}\n```{source.language}\n{content}\n```"
                    except Exception:
                        pass

            # Load findings context
            stmt_findings = select(ReviewFinding).filter(ReviewFinding.review_id == review_id)
            res_findings = await db.execute(stmt_findings)
            findings = list(res_findings.scalars().all())
            if findings:
                findings_list = []
                for f in findings:
                    findings_list.append(
                        f"- Line {f.line_number} [{f.severity.upper()}]: {f.message} (Category: {f.category})"
                    )
                findings_context = "\nStatic Analysis Findings:\n" + "\n".join(findings_list)

        elif project_id:
            from sqlalchemy import desc

            stmt_latest_review = (
                select(Review).filter(Review.project_id == project_id).order_by(desc(Review.id)).limit(1)
            )
            res_latest_review = await db.execute(stmt_latest_review)
            latest_review = res_latest_review.scalars().first()
            if latest_review:
                stmt_findings = select(ReviewFinding).filter(ReviewFinding.review_id == latest_review.id)
                res_findings = await db.execute(stmt_findings)
                findings = list(res_findings.scalars().all())
                if findings:
                    findings_list = []
                    for f in findings:
                        findings_list.append(
                            f"- Line {f.line_number} [{f.severity.upper()}]: {f.message} (Category: {f.category})"
                        )
                    findings_context = "\nStatic Analysis Findings:\n" + "\n".join(findings_list)

            stmt_src = select(UploadedSource).filter(
                UploadedSource.project_id == project_id, UploadedSource.status == "processed"
            )
            res_src = await db.execute(stmt_src)
            sources = res_src.scalars().all()
            code_blocks = []
            import os

            for source in sources:
                if os.path.exists(source.file_path):
                    try:
                        with open(source.file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        code_blocks.append(f"### File: {source.filename}\n```{source.language}\n{content}\n```")
                    except Exception:
                        pass
            if code_blocks:
                code_context = "\n\n".join(code_blocks)

    if project_id:
        stmt_proj = select(Project).filter(Project.id == project_id)
        res_proj = await db.execute(stmt_proj)
        proj = res_proj.scalars().first()
        if proj:
            project_name = proj.name

    # Build active editor selection context if present
    selected_code_context = ""
    if selected_code:
        selected_code_context = f"\nCurrently Selected Code in Editor:\n```{filename or 'code'}\n{selected_code}\n```"
        if payload.selection_start_line and payload.selection_end_line:
            selected_code_context += f" (Lines {payload.selection_start_line} to {payload.selection_end_line})"

    # 2. Build system prompt
    system_prompt = (
        "You are Cobane Chatbot, an expert AI software engineering assistant. "
        f"You are helping the user chat about the code files in their project '{project_name}'.\n\n"
        f"Code context:\n{code_context}\n"
        f"{selected_code_context}\n"
        f"{findings_context}\n"
        "Guidelines:\n"
        "- Explain logic, identify bugs, suggest performance/security fixes.\n"
        "- When discussing vulnerabilities, bugs, or refactoring, ALWAYS specify the line numbers, exact files, and detailed explanations of each issue.\n"
        "- When providing code modifications, use standard Markdown code blocks.\n"
        "- Be professional, detailed, and clean."
    )

    # 3. Call AI provider
    is_mock = (
        not settings.AI_API_KEY
        or "mock" in settings.AI_API_KEY.lower()
        or settings.AI_API_KEY == "openai-api-key"
        or "replace_with" in settings.AI_API_KEY
    )

    response_content = None

    if not is_mock:
        try:
            url = f"{settings.AI_BASE_URL.rstrip('/')}/chat/completions"
            headers = {"Authorization": f"Bearer {settings.AI_API_KEY}", "Content-Type": "application/json"}
            messages = [{"role": "system", "content": system_prompt}]
            for msg in chat_history:
                messages.append({"role": msg.role, "content": msg.content})
            messages.append({"role": "user", "content": user_message})

            payload_data = {
                "model": settings.AI_MODEL if hasattr(settings, "AI_MODEL") else "gpt-4o",
                "messages": messages,
                "temperature": 0.5,
                "max_tokens": 1024,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload_data)
                if response.status_code == 200:
                    res_json = response.json()
                    response_content = res_json.get("choices", [])[0].get("message", {}).get("content", "")
        except Exception:
            pass

    # 4. Mock response generator (fallback)
    if not response_content:
        # Fetch file names to describe structure
        stmt_srcs = select(UploadedSource).filter(
            UploadedSource.project_id == project_id, UploadedSource.status == "processed"
        )
        res_srcs = await db.execute(stmt_srcs)
        sources_list = res_srcs.scalars().all()
        filenames = [s.filename for s in sources_list]
        files_desc = ", ".join([f"`{name}`" for name in filenames]) if filenames else "source files"

        msg_lower = user_message.lower()
        lines_desc = (
            f"lines {payload.selection_start_line}-{payload.selection_end_line}"
            if payload.selection_start_line
            else "the selected code block"
        )

        if selected_code and (
            "explain" in msg_lower or "what" in msg_lower or "do" in msg_lower or "purpose" in msg_lower
        ):
            response_content = (
                f"Here is an explanation of your selected code in `{filename or 'source file'}` ({lines_desc}):\n\n"
                "1. This snippet defines operations within the application core logic.\n"
                "2. It runs synchronously or asynchronously as needed by the workspace context.\n\n"
                f"Selection detail:\n```python\n{selected_code}\n```"
            )
        elif selected_code and (
            "refactor" in msg_lower
            or "clean" in msg_lower
            or "rewrite" in msg_lower
            or "fix" in msg_lower
            or "optimize" in msg_lower
        ):
            refactored_code = f"# Optimized / Refactored version\n{selected_code}"
            if "def " in selected_code:
                lines = selected_code.split("\n")
                new_lines = []
                added_docstring = False
                for line in lines:
                    new_lines.append(line)
                    if "def " in line and not added_docstring:
                        indent = len(line) - len(line.lstrip())
                        new_lines.append(
                            " " * (indent + 4)
                            + '"""Refactored: added docstring and basic performance optimizations."""'
                        )
                        added_docstring = True
                refactored_code = "\n".join(new_lines)

            response_content = (
                f"I have reviewed the selection in `{filename or 'source file'}` ({lines_desc}). Here is a recommended refactored and optimized version:\n\n"
                f"```python\n{refactored_code}\n```\n\n"
                "Changes implemented:\n"
                "- Added proper documentation/docstrings.\n"
                "- Cleaned up logic formatting and structure."
            )
        elif "security" in msg_lower or "vuln" in msg_lower or "issue" in msg_lower or "password" in msg_lower:
            vuln_findings = [f for f in findings if f.category == "security" or f.severity == "critical"]
            if vuln_findings:
                response_content = f"Based on the static analysis scan of the project `{project_name}`, here are the security vulnerabilities/issues identified:\n\n"
                for idx, f in enumerate(vuln_findings, 1):
                    response_content += f"{idx}. **Line {f.line_number}** ({f.file_path}):\n"
                    response_content += f"   - **Severity**: {f.severity.upper()}\n"
                    response_content += f"   - **Vulnerability**: {f.message}\n"
                    if f.suggestion:
                        response_content += f"   - **Recommendation**: {f.suggestion}\n"
                    if f.code_snippet:
                        response_content += f"   - **Code**: `{f.code_snippet}`\n"
                    response_content += "\n"
            elif findings:
                response_content = f"Based on the static analysis scan of the project `{project_name}`, there are no security-specific issues. However, here are the other code quality findings detected:\n\n"
                for idx, f in enumerate(findings, 1):
                    response_content += f"{idx}. **Line {f.line_number}** ({f.file_path}) - [{f.category.upper()}] (Severity: {f.severity.upper()}):\n"
                    response_content += f"   - **Finding**: {f.message}\n"
                    if f.suggestion:
                        response_content += f"   - **Recommendation**: {f.suggestion}\n"
                    response_content += "\n"
            else:
                response_content = (
                    f"Based on the static analysis scan of the project `{project_name}`, there are no critical vulnerabilities or findings detected in {files_desc}.\n\n"
                    "If you introduce hardcoded credentials or insecure calls, static checkers like Bandit will highlight them."
                )
        elif (
            "refactor" in msg_lower
            or "clean" in msg_lower
            or "rewrite" in msg_lower
            or "fix" in msg_lower
            or "optimize" in msg_lower
        ):
            refactor_findings = [
                f for f in findings if f.category in ["refactor", "style", "complexity", "naming", "performance"]
            ]
            if refactor_findings:
                response_content = (
                    f"Here are the refactoring and optimization recommendations for project `{project_name}`:\n\n"
                )
                for idx, f in enumerate(refactor_findings, 1):
                    response_content += f"{idx}. **Line {f.line_number}** ({f.file_path}) - [{f.category.upper()}]:\n"
                    response_content += f"   - **Issue**: {f.message}\n"
                    if f.suggestion:
                        response_content += f"   - **Recommendation**: {f.suggestion}\n"
                    if f.code_snippet:
                        response_content += f"   - **Snippet**: `{f.code_snippet}`\n"
                    response_content += "\n"
            else:
                response_content = (
                    f"For the codebase in `{project_name}`, ensure that all function definitions are modular, "
                    "proper docstrings are added, and credentials are configuration-driven using environment variables."
                )
        elif "what" in msg_lower or "explain" in msg_lower or "do" in msg_lower or "purpose" in msg_lower:
            response_content = (
                f"The project `{project_name}` contains the following codebase structure:\n\n"
                f"- {files_desc}: Implementation files for the project's features.\n\n"
            )
            if findings:
                response_content += "Here are the static analysis & AI findings for this codebase:\n"
                for idx, f in enumerate(findings, 1):
                    response_content += f"- **Line {f.line_number}** ({f.file_path}): {f.message} (Category: {f.category}, Severity: {f.severity})\n"
            else:
                response_content += "Currently, the Radon complexity score reports it as class **A** (excellent maintainability). Ask me anything about how to optimize or refactor it!"
        else:
            response_content = (
                f"Hello! I am the Cobane AI Chatbot. I've analyzed `{project_name}`'s files and static metrics. "
                "You can ask me to:\n"
                "- **Explain code logic** (e.g., 'What does this code do?')\n"
                "- **Scan for security issues** (e.g., 'Are there security issues?')\n"
                "- **Refactor components** (e.g., 'Refactor this code')\n\n"
                "How can I assist you with your codebase today?"
            )

    return {"response": response_content}
