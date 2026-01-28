"""Base repository class with common CRUD operations."""

from typing import TypeVar, Generic, List, Optional, Type, Any
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository providing CRUD operations."""

    def __init__(self, model_class: Type[T], session: Session):
        """Initialize repository.

        Args:
            model_class: SQLAlchemy model class
            session: SQLAlchemy session
        """
        self.model_class = model_class
        self.session = session

    def create(self, **kwargs: Any) -> T:
        """Create and add a new entity.

        Args:
            **kwargs: Entity attributes

        Returns:
            Created entity
        """
        entity = self.model_class(**kwargs)
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Entity or None
        """
        return self.session.query(self.model_class).filter(
            self.model_class.id == entity_id
        ).first()

    def get_all(self, offset: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination.

        Args:
            offset: Offset for pagination
            limit: Limit for pagination

        Returns:
            List of entities
        """
        return self.session.query(self.model_class).offset(offset).limit(limit).all()

    def update(self, entity: T, **kwargs: Any) -> T:
        """Update an entity.

        Args:
            entity: Entity to update
            **kwargs: Attributes to update

        Returns:
            Updated entity
        """
        for key, value in kwargs.items():
            setattr(entity, key, value)
        self.session.flush()
        return entity

    def delete(self, entity: T) -> None:
        """Delete an entity.

        Args:
            entity: Entity to delete
        """
        self.session.delete(entity)
        self.session.flush()

    def delete_by_id(self, entity_id: int) -> bool:
        """Delete entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            True if deleted, False if not found
        """
        entity = self.get_by_id(entity_id)
        if entity:
            self.delete(entity)
            return True
        return False

    def count(self) -> int:
        """Count all entities.

        Returns:
            Total count
        """
        return self.session.query(self.model_class).count()

    def save(self, entity: T) -> T:
        """Add or update entity in session.

        Args:
            entity: Entity to save

        Returns:
            Saved entity
        """
        self.session.add(entity)
        self.session.flush()
        return entity

    def commit(self) -> None:
        """Commit current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        self.session.rollback()
