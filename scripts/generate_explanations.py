import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Draw header and footer on all pages except the cover page (page 1)
        if self._pageNumber > 1:
            self.saveState()
            
            # Draw elegant top header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1A365D"))
            self.drawString(54, 750, "COBANE: THE GRAND ARCHITECTURE EXPLORATION")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#718096"))
            self.drawRightString(612 - 54, 750, "A Feynmanesque Technical Guide")
            
            # Header separator line
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.75)
            self.line(54, 742, 612 - 54, 742)
            
            # Footer separator line
            self.line(54, 60, 612 - 54, 60)
            
            # Footer text
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#718096"))
            self.drawString(54, 45, "Confidential - System Architecture Documentation")
            
            # Page number
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(612 - 54, 45, page_text)
            
            self.restoreState()

def build_pdf():
    # Setup document template with 0.75 inch margins (54 points)
    # The flowables will stay between y=72 and y=720, avoiding the header (y=742) and footer (y=60)
    pdf_dir = os.path.abspath("explanation files")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, "explanations.pdf")
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom unique styles to prevent overlap and look extremely premium
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=colors.HexColor('#1A365D'),
        alignment=1,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#4A5568'),
        alignment=1,
        spaceAfter=40
    )
    
    metadata_style = ParagraphStyle(
        'CoverMetadata',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        alignment=1,
        spaceAfter=6
    )
    
    chapter_title_style = ParagraphStyle(
        'ChapterTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#1A365D'),
        spaceBefore=10,
        spaceAfter=15
    )
    
    heading_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'FeynmanBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=8
    )
    
    code_style = ParagraphStyle(
        'FeynmanCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1A202C'),
        backColor=colors.HexColor('#EDF2F7'),
        borderPadding=5,
        spaceBefore=6,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'FeynmanBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    story = []

    # ==================== PAGE 1: COVER PAGE ====================
    story.append(Spacer(1, 100))
    story.append(Paragraph("THE QUANTUM DYNAMICS OF CLEAN CODE", title_style))
    story.append(Paragraph("A Feynmanesque Technical Guide to the Architecture, Internals, and Operation of the Cobane AI-Powered Code Review System", subtitle_style))
    story.append(Spacer(1, 120))
    
    # Elegant central visual divider line
    d_table = Table([[""]], colWidths=[200], rowHeights=[2])
    d_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 1.5, colors.HexColor('#1A365D')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    story.append(d_table)
    story.append(Spacer(1, 120))
    
    story.append(Paragraph("Author: Richard P. Feynman (Channeled by Antigravity)", metadata_style))
    story.append(Paragraph("Affiliation: Google DeepMind Advanced Agentic Coding Division", metadata_style))
    story.append(Paragraph("Version: 1.0.0 (Production Release)", metadata_style))
    story.append(Paragraph("Date: July 2026", metadata_style))
    story.append(PageBreak())

    # ==================== PAGE 2: PHILOSOPHY & TOC ====================
    story.append(Paragraph("The Philosophy of Code Quality: A Prelude", chapter_title_style))
    story.append(Paragraph(
        "You see, when we write code, we aren't just giving instructions to a machine. We are constructing a little universe "
        "of logic—a lattice of rules and conditions. In physics, when you build a crystal lattice, if one atom is misaligned, "
        "or if there's a foreign element where it shouldn't be, the whole structure becomes brittle. It can fracture under "
        "the slightest external stress. That's exactly what happens to software when code quality degrades! One bad variable scope, "
        "one unhandled connection pool leak, or one hardcoded secret, and the entire system collapses under load.",
        body_style
    ))
    story.append(Paragraph(
        "Cobane was created to solve this. It's a platform that combines the mathematical rigor of static analysis (the laws of "
        "mechanics) with the intuitive flexibility of Large Language Models (the creative adaptation). Over the next fifteen "
        "chapters, we will pull off the covers, look under the hood, and watch how energy—in our case, requests and files—flows "
        "through this machine. We will explore how it starts at the HTTP network level, hits the database, registers in memory, "
        "interacts with subprocesses, communicates with remote LLMs, and projects itself back onto a beautiful React user interface.",
        body_style
    ))
    story.append(Paragraph("Structure of the Exploration:", heading_style))
    story.append(Paragraph("• <b>Page 3</b>: Chapter 1: The Anatomy of a Request (FastAPI Routing)", bullet_style))
    story.append(Paragraph("• <b>Page 4</b>: Chapter 2: The Core Database Schema & Graceful Fallback", bullet_style))
    story.append(Paragraph("• <b>Page 5</b>: Chapter 3: Authentication and Security Scaffolding", bullet_style))
    story.append(Paragraph("• <b>Page 6</b>: Chapter 4: Static Analysis Foundations (Complexity Theory)", bullet_style))
    story.append(Paragraph("• <b>Page 7</b>: Chapter 5: The Adapters Registry Pattern", bullet_style))
    story.append(Paragraph("• <b>Page 8</b>: Chapter 6: The Static Analysis Orchestrator", bullet_style))
    story.append(Paragraph("• <b>Page 9</b>: Chapter 7: Large Language Model Integration Strategy", bullet_style))
    story.append(Paragraph("• <b>Page 10</b>: Chapter 8: The AI Context Orchestration Flow", bullet_style))
    story.append(Paragraph("• <b>Page 11</b>: Chapter 9: The Review Service and Lifecycle", bullet_style))
    story.append(Paragraph("• <b>Page 12</b>: Chapter 10: Reports and PDF Exporter Mechanics", bullet_style))
    story.append(Paragraph("• <b>Page 13</b>: Chapter 11: The Frontend User Experience Architecture", bullet_style))
    story.append(Paragraph("• <b>Page 14</b>: Chapter 12: Interactive Frontend Components", bullet_style))
    story.append(Paragraph("• <b>Page 15</b>: Chapter 13: CI/CD Workflows and Integration Tests", bullet_style))
    story.append(Paragraph("• <b>Page 16</b>: Chapter 14: Production Deployment on Render Platforms", bullet_style))
    story.append(Paragraph("• <b>Page 17</b>: Epilogue: The Physics of Clean Code", bullet_style))
    story.append(PageBreak())

    # ==================== PAGE 3: REQUEST ANATOMY ====================
    story.append(Paragraph("Chapter 1: The Anatomy of a Request", chapter_title_style))
    story.append(Paragraph(
        "Let's trace what happens when someone clicks a button on the screen. A packet of energy (an HTTP POST or GET request) "
        "flies across the network and hits our backend. In Cobane, the gatekeeper of this backend is FastAPI, which sits at the "
        "front door. Think of FastAPI as an extremely efficient postmaster. It doesn't waste time opening every letter himself; "
        "instead, he checks the envelope, reads the address, validates the format of the contents, and immediately routes it to "
        "the right clerk.",
        body_style
    ))
    story.append(Paragraph(
        "This all starts in <code>backend/app/main.py</code>. When the server launches, FastAPI sets up a system startup and "
        "shutdown lifecycle hook called a <i>lifespan</i> context manager. This lifespan executes critical initialization tasks, "
        "such as checking if the database is ready and running baseline seeding. Once initialized, the routing table is mounted. "
        "Our routing structure is organized under <code>backend/app/api/v1/</code>, where specialized sub-routers handle "
        "authentication (<code>auth.py</code>), project management (<code>projects.py</code>), review triggers (<code>reviews.py</code>), "
        "diagnostics (<code>health.py</code>), and AI interactions (<code>ai.py</code>).",
        body_style
    ))
    story.append(Paragraph("The Lifespan Logic Hook:", heading_style))
    story.append(Paragraph(
        "@asynccontextmanager<br/>"
        "async def lifespan(_app: FastAPI):<br/>"
        "    app_logger.info(\"Initializing Cobane API runtime...\")<br/>"
        "    async with engine.begin() as conn:<br/>"
        "        await conn.run_sync(Base.metadata.create_all)<br/>"
        "    yield",
        code_style
    ))
    story.append(Paragraph(
        "By enforcing schema generation inside the lifespan block, Cobane guarantees that the database tables are perfectly "
        "aligned with our models before a single request is processed. If the main database fails to reply or isn't formatted, "
        "the initialization catches the exception, logs it, and continues so that fallback procedures can kick in.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== PAGE 4: DATABASE SCHEMA ====================
    story.append(Paragraph("Chapter 2: The Core Database Schema & Graceful Fallback", chapter_title_style))
    story.append(Paragraph(
        "If you want to know how a system remembers things, you look at its schema. In Cobane, we use SQLAlchemy to build an "
        "object-relational mapping (ORM) layer. We have six primary particles (models) that interact in our system's gravity field: "
        "Users, UserProfiles, UserPreferences, Projects, UploadedSources, and Reviews. Each model maps directly to a table in the database, "
        "connected by foreign keys that represent relational bonds.",
        body_style
    ))
    story.append(Paragraph(
        "But what happens if the database isn't there? In many corporate or cloud systems, the primary database (like PostgreSQL) "
        "might be temporarily offline or unreachable due to a network hitch. Most applications would just throw up their hands, scream, "
        "and crash. Not Cobane. Cobane implements a dynamic fallback to a local SQLite file (<code>test.db</code>).",
        body_style
    ))
    story.append(Paragraph(
        "When the application boots, the configuration loader in <code>backend/app/core/config.py</code> reads the connection "
        "string. If the configured URL is a remote PostgreSQL endpoint, it performs a dual-stage check. First, it attempts a fast "
        "TCP socket connection with a 2-second timeout. If that succeeds, it runs a real connection test in an isolated thread "
        "to verify query execution. If either of these steps fail, it intercepts the crash, reinitializes the engine to use a local "
        "sqlite file, creates the tables on-the-fly, and seeds default records so that the server remains fully operational.",
        body_style
    ))
    story.append(Paragraph("Fallback Algorithm Workflow:", heading_style))
    story.append(Paragraph(
        "def parse_database_url(cls, v) -> str:<br/>"
        "    # Probes PostgreSQL connectivity<br/>"
        "    if not cls._is_db_reachable(v):<br/>"
        "        # Fallback to local SQLite file<br/>"
        "        return \"sqlite+aiosqlite:///test.db\"<br/>"
        "    return v",
        code_style
    ))
    story.append(Paragraph(
        "This dynamic database steering means that even if a database server experiences a catastrophic crash, the Cobane API "
        "continues to accept file uploads, run local static checks, and handle reviews, storing everything locally until recovery is triggered.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== PAGE 5: AUTHENTICATION ====================
    story.append(Paragraph("Chapter 3: Authentication and Security Scaffolding", chapter_title_style))
    story.append(Paragraph(
        "How does the system know that you are who you say you are? We use a digital passport system called JWT (JSON Web Tokens). "
        "When a user signs up (handled by <code>backend/app/services/auth_service.py</code>), we take their password and run it through "
        "a one-way hashing function called Bcrypt. In physics, one-way processes are like mixing cream into coffee; it's easy to mix, "
        "but near impossible to separate them back out. Hashing works the same way: we get a secure, salted string, and we store "
        "only that hash in the database. We never keep the raw password in memory.",
        body_style
    ))
    story.append(Paragraph(
        "When a user logs in, we verify the password, and if correct, we issue an access token and a refresh token. The access token "
        "is signed using a symmetric encryption key (like HMAC-SHA256). Every subsequent request from the client includes this token "
        "in the HTTP Authorization header. Our API endpoints use FastAPI dependencies to intercept the request, decode the token, "
        "validate the expiration timestamp, and extract the user's role.",
        body_style
    ))
    story.append(Paragraph("Scope Validation Rules:", heading_style))
    story.append(Paragraph(
        "• <b>Superuser Access</b>: Admins bypass all ownership filters. They can view, edit, or delete any project and review in the database.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Owner Enforcement</b>: Regular users can only access resources where the project's <code>owner_id</code> matches their own user ID.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Refresh Cycle</b>: Access tokens expire in 30 minutes, requiring clients to hit the refresh endpoint with their long-lived refresh token.",
        bullet_style
    ))
    story.append(Paragraph(
        "This security model prevents cross-tenant data leaks and ensures that all static reviews and code snippets remain private "
        "to the project owner, keeping proprietary source code secure.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== PAGE 6: STATIC ANALYSIS ====================
    story.append(Paragraph("Chapter 4: Static Analysis Foundations", chapter_title_style))
    story.append(Paragraph(
        "Let's talk about static analysis. What is it really? It's the act of analyzing a program's structure without actually "
        "running it. Imagine you're checking a bridge. You could drive a massive 50-ton truck across it to see if it collapses "
        "(that's dynamic testing). Or, you could take a blueprint, calculate the load tolerances, check the angles of the steel girders, "
        "and determine if it's safe mathematically (that's static analysis). Static analysis looks at code as a text document and "
        "abstract syntax tree (AST) to find structural anomalies.",
        body_style
    ))
    story.append(Paragraph(
        "In Cobane, we measure three critical properties of code: syntax/style compliance, security weaknesses, and structural complexity. "
        "We use three open-source engines to perform these checks: Pylint, Bandit, and Radon. Each of these tools measures a different "
        "dimension of code quality.",
        body_style
    ))
    story.append(Paragraph(
        "Radon, for instance, calculates <i>Cyclomatic Complexity</i>. This is a mathematical measure of the number of linearly independent "
        "paths through a program's source code. If a function has lots of nested <code>if</code> statements, loops, and conditional branches, "
        "the cyclomatic complexity ($V(G)$) increases: $V(G) = E - V + 2P$, where $E$ is the number of edges, $V$ is the number of vertices, "
        "and $P$ is the number of connected components in the control flow graph. High complexity means more paths, which means more places "
        "for bugs to hide, and lower maintainability.",
        body_style
    ))
    story.append(Paragraph("Complexity Rating Scale:", heading_style))
    story.append(Paragraph("• <b>Class A (1 to 5)</b>: Low complexity. Easy to read, verify, and write unit tests for.", bullet_style))
    story.append(Paragraph("• <b>Class B (6 to 10)</b>: Moderate complexity. Standard application logic, clean and manageable.", bullet_style))
    story.append(Paragraph("• <b>Class C (11 to 20)</b>: High complexity. Needs refactoring. Testing requires many independent paths.", bullet_style))
    story.append(Paragraph("• <b>Class D-F (21+)</b>: Severe complexity. Extremely difficult to maintain, likely containing bugs.", bullet_style))
    story.append(PageBreak())

    # ==================== PAGE 7: ADAPTERS REGISTRY ====================
    story.append(Paragraph("Chapter 5: The Adapters Registry Pattern", chapter_title_style))
    story.append(Paragraph(
        "Now, how do we write code that manages these static analysis tools? If we wrote custom code for Pylint, custom code for Bandit, "
        "and custom code for Radon all mixed together, our system would become a tangled ball of yarn. In software design, we use "
        "the <i>Adapter Pattern</i>. We define a common, clean contract (interface) that every analyzer must follow. This interface is defined "
        "in <code>backend/app/services/static_analysis_engine/interface.py</code>.",
        body_style
    ))
    story.append(Paragraph(
        "Every adapter (like <code>PylintAdapter</code>, <code>BanditAdapter</code>, and <code>RadonAdapter</code>) inherits from this interface. "
        "They implement three standard behaviors: <code>validate()</code> (checks if the file is supported), <code>run_sync()</code> "
        "(executes the tool and gathers raw output), and <code>normalize()</code> (converts the tool's raw output into a standard "
        "format our system understands).",
        body_style
    ))
    story.append(Paragraph(
        "We also use a <i>Registry</i> pattern. This is a central catalog (like a directory) where all active adapters are registered. "
        "When the system needs to run a scan, it queries the registry for all registered tools, iterates through them, and runs each "
        "one. This makes the system incredibly extensible: if we want to add a JavaScript or C++ linter tomorrow, we just write an adapter, "
        "register it, and the orchestrator immediately supports it without modifying a single line of execution logic!",
        body_style
    ))
    story.append(Paragraph("The Severity Mapping Layer:", heading_style))
    story.append(Paragraph(
        "Each tool has its own vocabulary for severity. Pylint says 'convention' or 'warning', Bandit says 'HIGH' or 'LOW', "
        "and Radon calculates letter grades. The <code>SeverityMapper</code> class acts as a translator, mapping these disparate values "
        "into a standardized set of labels: <code>critical</code>, <code>high</code>, <code>medium</code>, <code>low</code>, or <code>info</code>.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== PAGE 8: ORCHESTRATION ====================
    story.append(Paragraph("Chapter 6: The Static Analysis Orchestration", chapter_title_style))
    story.append(Paragraph(
        "Once we have adapters, how do we run them? The orchestrator is the engine that drives the execution. "
        "In <code>backend/app/services/static_analysis_engine/orchestrator.py</code>, we have the <code>StaticAnalysisOrchestrator</code>. "
        "It is responsible for checking if a file is empty or too large (using limits configured in <code>config.py</code>), and then "
        "triggering the registered adapters.",
        body_style
    ))
    story.append(Paragraph(
        "There are two paths of execution: synchronous and asynchronous. For small scripts or quick user-triggered actions, the "
        "orchestrator can run everything synchronously. But for larger projects or background tasks, blocking the main thread while "
        "waiting for shell commands to finish would slow the API to a crawl. Therefore, we use Python's <code>asyncio</code> "
        "to run the subprocesses concurrently in the background.",
        body_style
    ))
    story.append(Paragraph("Subprocess Execution Code:", heading_style))
    story.append(Paragraph(
        "process = await asyncio.create_subprocess_exec(<br/>"
        "    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE<br/>"
        ")<br/>"
        "stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)",
        code_style
    ))
    story.append(Paragraph(
        "This asynchronous subprocess execution is a key architectural feature. It launches external binaries (like the <code>pylint</code> "
        "or <code>bandit</code> executables) in separate processes managed by the operating system kernel. The Python main process does "
        "not block; it yields control to the event loop, allowing the API to handle other user requests while the OS runs the "
        "linters. If a subprocess hangs (for instance, if an analyzer gets stuck in an infinite loop parsing a malformed file), the "
        "orchestrator intercepts it after a 15-second timeout, kills the process, and returns a clean timeout error message.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== PAGE 9: LLM INTEGRATION ====================
    story.append(Paragraph("Chapter 7: Large Language Model Integration Strategy", chapter_title_style))
    story.append(Paragraph(
        "Static analysis is fantastic at checking rules—indentation, syntax, known CVEs. But static analysis is blind to intent. "
        "It doesn't understand <i>what</i> the code is trying to achieve. It can tell you if a function's variable is unused, but it "
        "cannot tell you if your logic for calculating interest rates has a structural flaw. To bridge this gap, Cobane "
        "integrates with Large Language Models.",
        body_style
    ))
    story.append(Paragraph(
        "This integration lives in <code>backend/app/services/ai/</code>. The architecture is designed around two key goals: "
        "robustness and reliability. The LLM connection is config-driven. The <code>settings</code> object loads parameters like "
        "<code>AI_PROVIDER</code> (e.g. OpenAI), the base endpoint URL, the model name, and the API key. Since connecting to remote API "
        "services over the internet is inherently unreliable due to network congestion or rate limits, the integration includes "
        "a robust retry-on-failure loop with exponential backoff.",
        body_style
    ))
    story.append(Paragraph("Integration Design Patterns:", heading_style))
    story.append(Paragraph(
        "• <b>Mock Fallback</b>: If the API key is not configured, or if the remote model is unreachable, the system automatically "
        "steers the request to a mock generator. This prevents the application from throwing errors during local development or offline environments.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Token Management</b>: The system includes a token manager that estimates prompt lengths. If a source file is too large "
        "to fit into the model's context window, it flags it rather than letting the API request fail due to context overflow.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>JSON Contracts</b>: To integrate LLM suggestions back into our database, the system requests structured JSON responses "
        "from the model, mapping findings to specific lines, categories, and severity levels.",
        bullet_style
    ))
    story.append(PageBreak())

    # ==================== PAGE 10: CONTEXT ASSEMBLY ====================
    story.append(Paragraph("Chapter 8: The AI Context Orchestration Flow", chapter_title_style))
    story.append(Paragraph(
        "An LLM is only as smart as the context you feed it. If you just send 'review my code' without any information, you get back "
        "generic advice. To provide actionable, line-specific feedback, Cobane constructs a rich context payload. When a user chats "
        "about a project or triggers a review, the chatbot endpoint in <code>backend/app/api/v1/ai.py</code> dynamically compiles three "
        "data streams into a single system prompt.",
        body_style
    ))
    story.append(Paragraph(
        "First, it retrieves the actual source code of the files in the project. Second, it pulls the exact findings detected by our "
        "local static checkers (Pylint and Bandit), including the file paths and line numbers. Third, it appends the user's active editor "
        "selection (if they highlighted a specific block of code) and their conversational history.",
        body_style
    ))
    story.append(Paragraph("System Prompt Assembly Formula:", heading_style))
    story.append(Paragraph(
        "system_prompt = (<br/>"
        "    \"You are Cobane Chatbot, an expert AI engineer...\\n\\n\"<br/>"
        "    f\"Code context:\\n{code_context}\\n\"<br/>"
        "    f\"{selected_code_context}\\n\"<br/>"
        "    f\"{findings_context}\\n\"<br/>"
        "    \"Guidelines:...\"<br/>"
        ")",
        code_style
    ))
    story.append(Paragraph(
        "By merging static analysis results directly into the system prompt, we save the LLM from having to re-calculate simple syntax "
        "issues. Instead, the model can focus its intelligence on high-level concerns: checking if the code matches the user's instructions, "
        "suggesting architectural improvements, or explaining complex logic. This hybrid approach saves API costs, reduces model latency, "
        "and delivers highly specific, line-anchored recommendations.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== PAGE 11: REVIEW LIFECYCLE ====================
    story.append(Paragraph("Chapter 9: The Review Service and Lifecycle", chapter_title_style))
    story.append(Paragraph(
        "Now let's look at how all these pieces are coordinated. This coordination is the responsibility of the "
        "<code>ReviewService</code> in <code>backend/app/services/review_service.py</code>. The lifecycle of a code review is a sequence "
        "of steps that transition a review run from a request to a saved report.",
        body_style
    ))
    story.append(Paragraph(
        "When a user triggers a review, we create a <code>Review</code> record in the database with a status of 'pending'. This immediately "
        "tells the system that a job is in progress. The service then calls the static analysis orchestrator to analyze the source code on disk. "
        "Once the static analysis is complete, the service parses the findings, extracts metrics (like cyclomatic complexity and loc), "
        "and saves them as <code>ReviewFinding</code> and <code>ReviewMetrics</code> records in the database.",
        body_style
    ))
    story.append(Paragraph("Review Job Flow:", heading_style))
    story.append(Paragraph(
        "1. Create Review DB record (status = pending)<br/>"
        "2. Run Static Analysis Orchestrator (Pylint, Bandit, Radon)<br/>"
        "3. Parse raw static findings and write to DB<br/>"
        "4. Call LLM for AI-based logic and safety reviews<br/>"
        "5. Merge AI and static findings into a final checklist<br/>"
        "6. Save aggregated metrics, calculate stats, mark review as completed",
        code_style
    ))
    story.append(Paragraph(
        "After writing the static analysis findings, the service triggers the LLM review. Once the LLM returns its response, the findings "
        "are parsed, categorized, and added to the review. Finally, the service updates the main project statistics—calculating the "
        "aggregate Pylint score across files, counting total issues, and updating the project's health dashboard. The review status is "
        "then updated to 'completed', and the client is notified.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== PAGE 12: REPORTS GENERATION ====================
    story.append(Paragraph("Chapter 10: Reports and PDF Exporter Mechanics", chapter_title_style))
    story.append(Paragraph(
        "A code review is only useful if you can share it. Cobane provides a report export service. When a user requests an export, "
        "the <code>reports.py</code> API router manages the request. Rather than keeping massive pre-generated PDFs in storage (which "
        "would occupy disk space), the system generates reports on-the-fly and caches them for quick access.",
        body_style
    ))
    story.append(Paragraph(
        "When a user clicks 'Download Report', the server checks if the PDF file exists at the configured path. If not, it initiates a "
        "generation sequence. It queries the database for all findings linked to the review, assembles the project metadata, and generates "
        "a clean PDF document containing the review summary, linting scores, maintainability metrics, and actionable code recommendations.",
        body_style
    ))
    story.append(Paragraph("Download Security Architecture:", heading_style))
    story.append(Paragraph(
        "• <b>Token Authentication</b>: Standard API requests use the <code>Authorization: Bearer</code> header. However, browser file "
        "downloads (like image tags or iframe sources) cannot easily append custom headers. To secure these, we use a query parameter token scheme.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Isolated Session Validation</b>: The download endpoint decodes the token from the query parameter (<code>?token=...</code>), "
        "validates the signature and expiration, and extracts the user context to ensure they own the project before streaming the file.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Streaming Response</b>: Once validated, the server uses a FastAPI <code>FileResponse</code> to stream the PDF bytes to the "
        "browser with a content disposition header, triggering a secure download.",
        bullet_style
    ))
    story.append(PageBreak())

    # ==================== PAGE 13: FRONTEND ARCHITECTURE ====================
    story.append(Paragraph("Chapter 11: The Frontend User Experience Architecture", chapter_title_style))
    story.append(Paragraph(
        "Now let's cross the bridge and explore the frontend. The user interface of Cobane is built as a modern Single Page "
        "Application (SPA) using React and TypeScript. In physics, we know that light travels fast, but humans perceive latency "
        "in milliseconds. A slow interface makes the entire application feel laggy, regardless of how fast the backend is. "
        "Cobane's frontend is optimized for responsiveness, structured under <code>frontend/src/</code>.",
        body_style
    ))
    story.append(Paragraph(
        "The application routing is managed by React Router. When the app loads in <code>main.tsx</code>, it hooks into the DOM. "
        "The main <code>App.tsx</code> file handles routing, defining pages like <code>Landing.tsx</code>, <code>Dashboard.tsx</code>, "
        "<code>Projects.tsx</code>, <code>ProjectDetail.tsx</code>, <code>ReviewDetail.tsx</code>, and <code>Settings.tsx</code>. "
        "Styles are managed using a custom, high-fidelity Vanilla CSS design system.",
        body_style
    ))
    story.append(Paragraph("Core CSS Variables Design System:", heading_style))
    story.append(Paragraph(
        ":root {<br/>"
        "  --primary-color: #1A365D; /* Sleek Dark Blue */<br/>"
        "  --secondary-color: #2B6CB0; /* Vibrant Accent Blue */<br/>"
        "  --background-dark: #0F172A; /* Slate Gray for Dark Mode */<br/>"
        "  --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);<br/>"
        "}",
        code_style
    ))
    story.append(Paragraph(
        "By avoiding complex runtime CSS frameworks, the application loads instantly. The design uses modern web aesthetics: "
        "glassmorphism overlays, subtle transitions, color-coded health indicators (green, yellow, red), and dynamic sidebar menus "
        "that provide immediate feedback to user actions.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== PAGE 14: INTERACTIVE FRONTEND ====================
    story.append(Paragraph("Chapter 12: Interactive Frontend Components", chapter_title_style))
    story.append(Paragraph(
        "Cobane is highly interactive. Its three most complex UI components are the <code>MonacoWrapper</code>, the "
        "<code>UploadZone</code>, and the <code>Chatbot</code>. Each component is modularly separated in <code>components/</code>.",
        body_style
    ))
    story.append(Paragraph(
        "The Monaco Editor Wrapper (<code>MonacoWrapper.tsx</code>) hosts Microsoft's Monaco Editor inside a React component. "
        "It provides syntax highlighting, automatic line numbers, and custom read-only toggles. It intercepts cursor select events, "
        "allowing users to highlight a block of code and send it to the chatbot context.",
        body_style
    ))
    story.append(Paragraph(
        "The <code>UploadZone</code> component handles drag-and-drop file imports, managing file size limits and extension checks "
        "in the browser. The <code>Chatbot</code> component (found in <code>components/common/Chatbot.tsx</code>) manages the chat stream. "
        "It communicates with our backend AI routes, handles typing indicators, and renders markdown and code blocks returned by the model.",
        body_style
    ))
    story.append(Paragraph("Chat Event Handling Protocol:", heading_style))
    story.append(Paragraph(
        "1. Capture user text input in state<br/>"
        "2. Read highlighted editor context from Monaco state<br/>"
        "3. Construct payload including conversation history<br/>"
        "4. Dispatch async request to /api/v1/ai/chat<br/>"
        "5. Receive response, update state, and render markdown response block",
        code_style
    ))
    story.append(Paragraph(
        "The chatbot uses local state to render conversation streams, keeping the conversation fluid. It also includes automatic "
        "scroll locks that keep the chat window anchored to the latest response during generation.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== PAGE 15: CI/CD WORKFLOWS ====================
    story.append(Paragraph("Chapter 13: CI/CD Workflows and Integration Tests", chapter_title_style))
    story.append(Paragraph(
        "A system is only as stable as its tests. In Cobane, we ensure that every code change is validated before it hits main. "
        "We do this using GitHub Actions. Our pipelines are defined in <code>.github/workflows/</code>, containing two automated check jobs: "
        "<code>lint.yml</code> and <code>test.yml</code>.",
        body_style
    ))
    story.append(Paragraph(
        "The linting pipeline (<code>lint.yml</code>) runs on every push and pull request. It spins up an isolated Ubuntu container, "
        "installs python 3.12, caches dependencies to speed up subsequent runs, and runs flake8 to scan for syntax errors, "
        "and black to check code formatting. If a developer pushes code that is poorly formatted, the build fails and shows "
        "a red cross on the repository.",
        body_style
    ))
    story.append(Paragraph(
        "The testing pipeline (<code>test.yml</code>) runs our comprehensive integration suite. It launches a PostgreSQL database service "
        "in a docker container, sets up the python environment, installs the required packages, and runs pytest. It checks endpoints, "
        "validates authentication flows, confirms project upload handlers, and checks static analysis adapters.",
        body_style
    ))
    story.append(Paragraph("Testing Suite Commands:", heading_style))
    story.append(Paragraph(
        "- Setup: <code>pip install -r backend/requirements.txt pytest pytest-asyncio</code><br/>"
        "- Run: <code>python -m pytest --cov=app tests/ --cov-report=xml</code><br/>"
        "- Coverage: Uploads findings to Codecov for visibility.",
        code_style
    ))
    story.append(Paragraph(
        "This continuous integration ensures that code changes are fully validated. It verifies that routing handlers, database "
        "models, and analysis engines remain functional with every commit.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== PAGE 16: DEPLOYMENT ====================
    story.append(Paragraph("Chapter 14: Production Deployment on Render Platforms", chapter_title_style))
    story.append(Paragraph(
        "Once the tests pass and the linter is happy, how do we deploy this system? We use a platform called Render. "
        "Render reads our configuration from <code>render.yaml</code>, which acts as a blueprint for the server infrastructure.",
        body_style
    ))
    story.append(Paragraph(
        "The <code>render.yaml</code> file defines a multi-service structure: a web service for the FastAPI backend and a static site "
        "service for the React frontend. The web service configures build commands, sets up the start command (running uvicorn), "
        "and links to a managed PostgreSQL database. Environment variables like <code>DATABASE_URL</code> and <code>JWT_SECRET_KEY</code> "
        "are loaded from environment settings or secrets vaults.",
        body_style
    ))
    story.append(Paragraph(
        "To make deployment instant, Render supports Webhook-based rebuilds. When the master pipeline completes successfully on GitHub, "
        "it triggers a webhook URL. Render receives this webhook, fetches the latest code commit, rebuilds the docker images, and deploys "
        "the new release without downtime. In production, we also configure static file routing: the FastAPI backend serves static assets "
        "from the <code>dist/</code> folder if they exist, allowing the entire application to run from a single container if necessary.",
        body_style
    ))
    story.append(Paragraph("Production Service Definition Blueprint:", heading_style))
    story.append(Paragraph(
        "services:<br/>"
        "  - type: web<br/>"
        "    name: cobane-api<br/>"
        "    env: python<br/>"
        "    buildCommand: pip install -r requirements.txt<br/>"
        "    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT",
        code_style
    ))
    story.append(Paragraph(
        "This architecture allows the system to scale easily: you can run the entire platform on a single lightweight VPS or "
        "split it across scaled containers behind a load balancer as request volume grows.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== PAGE 17: EPILOGUE ====================
    story.append(Paragraph("Epilogue: The Physics of Clean Code", chapter_title_style))
    story.append(Paragraph(
        "We've looked at the routing tables, database schemas, static analysis engines, AI context builders, and frontend components. "
        "But let's step back for a second. What's the core takeaway here? In physics, there is a concept called <i>entropy</i>. "
        "It's a measure of disorder, and the Second Law of Thermodynamics tells us that in any closed system, entropy always increases. "
        "A system naturally slides from order to chaos unless you put energy into it to keep it structured.",
        body_style
    ))
    story.append(Paragraph(
        "Software codebases are subject to the same law of entropy. We call it 'code smell' or 'technical debt'. Left alone, a clean "
        "codebase naturally becomes messy, complex, and fragile. Developers add shortcuts, hardcode values, or write overly "
        "complex loops. The only way to combat code entropy is to continuously inject energy in the form of code reviews, "
        "formatting checks, and structural testing. Cobane automate this injection of energy.",
        body_style
    ))
    story.append(Paragraph(
        "By enforcing styling checks, measuring cyclomatic complexity, scanning for security issues, and leveraging LLMs to explain "
        "and refactor code, Cobane acts as an anti-entropy shield for software. It keeps codebases simple, elegant, and maintainable. "
        "Because at the end of the day, the best code is not the cleverest or the most complex—it's the simplest code that solves the "
        "problem. As we say in physics, nature always finds the path of least resistance. Our code should do the same.",
        body_style
    ))
    story.append(Spacer(1, 30))
    
    # Elegant ending block
    e_table = Table([[""]], colWidths=[200], rowHeights=[1])
    e_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#718096')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    story.append(e_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("End of Exploration - Cobane Engineering Group", metadata_style))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF Generation complete: explanations.pdf created in 'explanation files' directory.")

if __name__ == "__main__":
    build_pdf()
