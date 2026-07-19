from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, desc
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic CRUD repository implementing foundational query patterns for ORM entities."""

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db = db_session

    async def get(self, id_val: int) -> Optional[ModelType]:
        """Fetches a single model instance by integer ID."""
        result = await self.db.execute(select(self.model).filter(self.model.id == id_val))
        return result.scalars().first()

    async def get_by_uuid(self, uuid_val: str) -> Optional[ModelType]:
        """Fetches a single model instance by UUID string reference."""
        # Ensure UUID attribute exists
        if hasattr(self.model, "uuid"):
            result = await self.db.execute(select(self.model).filter(self.model.uuid == uuid_val))
            return result.scalars().first()
        return None

    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Dict[str, Any] = None,
        sort_by: str = "id",
        ascending: bool = True,
    ) -> List[ModelType]:
        """Lists multiple entity records matching generic filters and order settings."""
        query = select(self.model)

        # Apply standard matching filters
        if filters:
            for field, val in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == val)

        # Apply sorting order
        if hasattr(self.model, sort_by):
            sort_attr = getattr(self.model, sort_by)
            query = query.order_by(sort_attr if ascending else desc(sort_attr))
        else:
            query = query.order_by(self.model.id if ascending else desc(self.model.id))

        # Apply pagination offsets
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Saves a new entity database record instance."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Modifies and synchronizes changes over an existing database record."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.flush()
        return db_obj

    async def delete(self, id_val: int) -> bool:
        """Removes a model database record by integer ID. Returns success status."""
        obj = await self.get(id_val)
        if obj:
            await self.db.delete(obj)
            await self.db.flush()
            return True
        return False
