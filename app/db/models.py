from datetime import datetime
from typing import Annotated
from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import Column, Integer, String, Text, CheckConstraint, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, declarative_base
from sqlalchemy import func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# from app.db.database import Base
from app.config import MAX_DATA, MIN_DATA

# annotation
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

class Book(Base):
    __tablename__ = 'books'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String, nullable=False, unique=True)
    author = Column(String)
    publication_year = Column(Integer, nullable=False)
    genre = Column(ARRAY(String), nullable=False)
    description = Column(Text)
    cover_image = Column(String)
    price = Column(Integer, nullable=True)
    archived = Column(Boolean, nullable=False, default=False)

    history: Mapped['PriceHistory'] = relationship(back_populates='book', cascade='all, delete-orphan',
                                                   single_parent=True)

    __table_args__ = (
        CheckConstraint(f'publication_year >= {MIN_DATA}', name='min_publication_year_error'),
        CheckConstraint(f'publication_year <= {MAX_DATA}', name='max_publication_year_error'),
        CheckConstraint('price >= 0', name='price must be positive')

    )


class PriceHistory(Base):
    __tablename__ = 'price_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    book_id = Column(UUID, ForeignKey('books.id'), nullable=False)
    price = Column(Integer, nullable=False)

    book: Mapped['Book'] = relationship(back_populates='history')

    __table_args__ = (
        CheckConstraint('price >= 0', name='positive_price'),
    )
