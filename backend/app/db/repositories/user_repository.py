from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.repositories.base_repository import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository[User]):
    """Repository managing User accounts queries with eager profile/preference loads."""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(User, db_session)

    async def get(self, id_val: int) -> Optional[User]:
        """Fetches User account matching integer ID parameters eagerly loading related profile/preferences."""
        result = await self.db.execute(
            select(User)
            .filter(User.id == id_val)
            .options(selectinload(User.profile), selectinload(User.preference))
        )
        return result.scalars().first()

    async def get_by_email(self, email_val: str) -> Optional[User]:
        """Fetches User account matching email parameters with eager relationship loadings."""
        result = await self.db.execute(
            select(User)
            .filter(User.email == email_val)
            .options(selectinload(User.profile), selectinload(User.preference))
        )
        return result.scalars().first()

    async def get_by_username(self, username_val: str) -> Optional[User]:
        """Fetches User account matching username parameters with eager relationship loadings."""
        result = await self.db.execute(
            select(User)
            .filter(User.username == username_val)
            .options(selectinload(User.profile), selectinload(User.preference))
        )
        return result.scalars().first()
