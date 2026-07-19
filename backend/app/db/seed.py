import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User, UserProfile, UserPreference
from app.models.project import Project, UploadedSource
from app.models.review import Review, ReviewFinding, ReviewMetrics, Report
from app.core.security import hash_password
from app.core.logging import database_logger


async def seed_project_if_missing(
    db: AsyncSession,
    owner_id: int,
    name: str,
    description: str,
    filename: str,
    file_path: str,
    code_content: str,
    language: str,
) -> None:
    """Helper function to seed a project and its sample review with findings if missing."""
    # Check if project already exists
    res = await db.execute(select(Project).filter(Project.name == name))
    existing_project = res.scalars().first()
    if existing_project:
        database_logger.info("Project '%s' already exists. Skipping seeding for this project.", name)
        return

    database_logger.info("Seeding project '%s'...", name)

    # 1. Create Project
    project = Project(
        name=name,
        description=description,
        owner_id=owner_id,
    )
    db.add(project)
    await db.flush()

    # 2. Create Uploaded Source File
    source_file = UploadedSource(
        project_id=project.id,
        filename=filename,
        file_path=file_path,
        file_size=len(code_content.encode("utf-8")),
        language=language,
        sha256_hash="d577273ff885c3f84dadb8578bb41399573b1a0f68a5c2d0f4d8e82ef45b5c90",
        status="processed",
    )
    db.add(source_file)
    await db.flush()

    # 3. Create Sample Review
    review = Review(
        project_id=project.id,
        uploaded_source_id=source_file.id,
        status="completed",
        pylint_score=8.2,
        radon_mi_score=88.0,
        bandit_issues_count=0,
        ai_review_completed=True,
    )
    db.add(review)
    await db.flush()

    # 4. Create Review Findings
    findings = []
    if name == "scientific-calculator-project":
        findings.extend(
            [
                ReviewFinding(
                    review_id=review.id,
                    file_path=filename,
                    line_number=32,
                    severity="warning",
                    category="style",
                    message="Highly branched conditional block (too many elif checks). Consider using a dictionary mapping or dispatcher pattern.",
                    code_snippet="def calculate(op, x, y=None):",
                    suggestion="Refactor calculate function to map operation names to functions directly.",
                    provider="pylint",
                ),
                ReviewFinding(
                    review_id=review.id,
                    file_path=filename,
                    line_number=14,
                    severity="medium",
                    category="complexity",
                    message="Consider grouping basic math operations in a class or standard structure.",
                    code_snippet="def divide(x, y):",
                    suggestion="Encapsulate math operators inside a ScientificCalculator engine class.",
                    provider="ai",
                ),
            ]
        )
    elif name == "sudoku-project":
        findings.extend(
            [
                ReviewFinding(
                    review_id=review.id,
                    file_path=filename,
                    line_number=14,
                    severity="warning",
                    category="performance",
                    message="Backtracking depth first search can be slow. Consider caching valid states or using bitmask constraints.",
                    code_snippet="def solve_sudoku(board):",
                    suggestion="Optimize backtracking solver with constraint propagation (e.g. tracking row/col/box sets).",
                    provider="ai",
                ),
                ReviewFinding(
                    review_id=review.id,
                    file_path=filename,
                    line_number=30,
                    severity="info",
                    category="style",
                    message="Consider extracting string concatenation into a join loop or cleaner formatter.",
                    code_snippet="print(str(board[i][j]) + ' ', end='')",
                    suggestion="Use f-string formats or ' '.join() for clearer output loops.",
                    provider="pylint",
                ),
            ]
        )
    else:  # hangman-project
        findings.extend(
            [
                ReviewFinding(
                    review_id=review.id,
                    file_path=filename,
                    line_number=23,
                    severity="warning",
                    category="security",
                    message="Using input() directly without validating character encoding or stripping trailing whitespaces.",
                    code_snippet="guess = input('Guess a letter: ').lower()",
                    suggestion="Sanitize keyboard input elements cleanly to prevent shell escape sequences or format errors.",
                    provider="bandit",
                ),
                ReviewFinding(
                    review_id=review.id,
                    file_path=filename,
                    line_number=1,
                    severity="info",
                    category="style",
                    message="WORDS list contains magic strings hardcoded. Consider loading words list from a separate configuration file.",
                    code_snippet="WORDS = ['python', 'hangman', 'sudoku', ...]",
                    suggestion="Move words dictionary list to a settings file or database resource table.",
                    provider="ai",
                ),
            ]
        )

    # 5. Create Review Metrics
    metrics = ReviewMetrics(
        review_id=review.id,
        cyclomatic_complexity=6,
        maintainability_index=85.0,
        loc=45,
        functions_count=5,
        classes_count=0,
    )

    # 6. Create Report Export
    report = Report(review_id=review.id, format="pdf", file_path=f"reports/exports/{name}-review-report.pdf")

    db.add_all(findings + [metrics, report])
    await db.flush()


async def seed_database(db: AsyncSession) -> None:
    """Seeds the relational database with initial bootstrap profiles and calculator/sudoku/hangman project configurations."""
    database_logger.info("Starting database seeding process...")

    # 1. Check if demo user already exists
    result = await db.execute(select(User).filter(User.username == "admin"))
    admin = result.scalars().first()

    if not admin:
        # 2. Seed Default Admin User
        admin = User(
            email="admin@cobane.ai", username="admin", hashed_password=hash_password("admin123"), is_superuser=True
        )
        db.add(admin)
        await db.flush()  # Flushes to retrieve the admin.id

        # 3. Seed Default Admin Profile and Preferences
        profile = UserProfile(
            user_id=admin.id, full_name="Cobane Admin", bio="Default system administrator profile account for Cobane."
        )
        preferences = UserPreference(user_id=admin.id, theme="dark", receiving_notifications=True)
        db.add_all([profile, preferences])
        await db.flush()
    else:
        database_logger.info("Demo account 'admin' already registered. Checking projects...")

    # 4. Seed Scientific Calculator Project
    calc_code = ""
    calc_path = "uploads/processed/scientific_calculator.py"
    if os.path.exists(calc_path):
        with open(calc_path, "r", encoding="utf-8") as f:
            calc_code = f.read()
    await seed_project_if_missing(
        db=db,
        owner_id=admin.id,
        name="scientific-calculator-project",
        description="A simple scientific calculator script supporting basic arithmetic, trigonometric, and logarithmic calculations.",
        filename="scientific_calculator.py",
        file_path=calc_path,
        code_content=calc_code or "# scientific calculator code",
        language="python",
    )

    # 5. Seed Sudoku Solver Project
    sudoku_code = ""
    sudoku_path = "uploads/processed/sudoku_solver.py"
    if os.path.exists(sudoku_path):
        with open(sudoku_path, "r", encoding="utf-8") as f:
            sudoku_code = f.read()
    await seed_project_if_missing(
        db=db,
        owner_id=admin.id,
        name="sudoku-project",
        description="A Sudoku solver workspace implementing validation constraints and depth-first backtracking search algorithm.",
        filename="sudoku_solver.py",
        file_path=sudoku_path,
        code_content=sudoku_code or "# sudoku solver code",
        language="python",
    )

    # 6. Seed Hangman Game Project
    hangman_code = ""
    hangman_path = "uploads/processed/hangman_game.py"
    if os.path.exists(hangman_path):
        with open(hangman_path, "r", encoding="utf-8") as f:
            hangman_code = f.read()
    await seed_project_if_missing(
        db=db,
        owner_id=admin.id,
        name="hangman-project",
        description="A console-based Hangman game containing core random word selection, user input loops, and state checks.",
        filename="hangman_game.py",
        file_path=hangman_path,
        code_content=hangman_code or "# hangman game code",
        language="python",
    )

    await db.commit()
    database_logger.info("Database seeding completed successfully.")
