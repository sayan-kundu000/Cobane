from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User, UserProfile, UserPreference
from app.models.project import Project, UploadedSource
from app.models.review import Review, ReviewFinding, ReviewMetrics, Report
from app.core.security import hash_password
from app.core.logging import database_logger


async def seed_database(db: AsyncSession) -> None:
    """Seeds the relational database with initial bootstrap profiles and demo configurations."""
    database_logger.info("Starting database seeding process...")

    # 1. Check if demo user already exists
    result = await db.execute(select(User).filter(User.username == "admin"))
    existing_user = result.scalars().first()

    if existing_user:
        database_logger.info("Demo account 'admin' already registered. Skipping seeding.")
        return

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

    # 4. Seed Demo Project
    demo_project = Project(
        name="demo-python-app",
        description="A sample Python app containing syntax warnings, complexities, and security risks.",
        owner_id=admin.id,
    )
    db.add(demo_project)
    await db.flush()

    # 5. Seed Uploaded Source File
    source_file = UploadedSource(
        project_id=demo_project.id,
        filename="utils.py",
        file_path="uploads/processed/demo_utils.py",
        file_size=1024,
        language="python",
        sha256_hash="d577273ff885c3f84dadb8578bb41399573b1a0f68a5c2d0f4d8e82ef45b5c90",
        status="processed",
    )
    db.add(source_file)
    await db.flush()

    # 6. Seed Sample Review Report
    demo_review = Review(
        project_id=demo_project.id,
        uploaded_source_id=source_file.id,
        status="completed",
        pylint_score=7.8,
        radon_mi_score=85.0,
        bandit_issues_count=1,
        ai_review_completed=True,
    )
    db.add(demo_review)
    await db.flush()

    # 7. Seed Review Findings (Pylint, Bandit, AI advice)
    pylint_finding = ReviewFinding(
        review_id=demo_review.id,
        file_path="utils.py",
        line_number=12,
        severity="warning",
        category="style",
        message="Unused argument 'connection_string' (unused-argument)",
        code_snippet="def connect(connection_string):",
        suggestion="Remove the unused parameter if not required by parent interfaces.",
        provider="pylint",
    )
    bandit_finding = ReviewFinding(
        review_id=demo_review.id,
        file_path="utils.py",
        line_number=24,
        severity="critical",
        category="security",
        message="Possible hardcoded password string detection.",
        code_snippet="password = 'secretPassword123'",
        suggestion="Load credential fields via env configurations to avoid plaintext checks.",
        provider="bandit",
    )
    ai_finding = ReviewFinding(
        review_id=demo_review.id,
        file_path="utils.py",
        line_number=24,
        severity="warning",
        category="performance",
        message="Avoid calling multiple global connection pools iteratively.",
        code_snippet="for x in range(10): pool.connect()",
        suggestion="Configure a single singleton connection pool outside iterative loops.",
        provider="ai",
    )

    # 8. Seed Complexity Metrics
    metrics = ReviewMetrics(
        review_id=demo_review.id,
        cyclomatic_complexity=4,
        maintainability_index=88.5,
        loc=35,
        functions_count=3,
        classes_count=1,
    )

    # 9. Seed Report Export records
    report = Report(review_id=demo_review.id, format="pdf", file_path="reports/exports/demo-review-report.pdf")

    db.add_all([pylint_finding, bandit_finding, ai_finding, metrics, report])
    await db.commit()
    database_logger.info("Database seeding completed successfully.")
