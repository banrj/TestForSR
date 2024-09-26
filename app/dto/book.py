from uuid import UUID, uuid4
from pydantic import BaseModel, conint, ConfigDict
from typing import List, Any
from app.config import MIN_DATA, MAX_DATA


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""
        populate_by_name = True
        from_attributes = True


class CreateBook(TunedModel):
    title: str
    publication_year: conint(le=MAX_DATA, ge=MIN_DATA)
    genre: List[str]
    author: str | None = None
    description: str | None = None
    cover_image: str | None = None
    price: int | None = 0
    archived: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Example Book",
                "publication_year": 2022,
                "genre": ["fiction", "mystery"],
                "author": "John Doe",
                "description": "An example book description.",
                "cover_image": "https://example.com/cover-image.jpg",
                "archived": False
        }
        }

    def json(self, **kwargs):
        return {
            'title': self.title,
            'publication_year': self.publication_year,
            'genre': self.genre,
            'author': self.author,
            'description': self.description,
            'cover_image': self.cover_image,
            'price': self.price,
            'archived': self.archived

        }


class UpdateBook(TunedModel):
    """ class for patch update"""
    title: str | None = None
    publication_year: conint(le=MAX_DATA, ge=MIN_DATA) | None = None
    genre: List[str] | None = None
    price: int | None = None
    author: str | None = None
    description: str | None = None
    cover_image: str | None = None
    archived: bool = False


class ShowBook(CreateBook):
    id: UUID

    def json(self, **kwargs):
        return {
            'id': str(self.id),
            'title': self.title,
            'publication_year': self.publication_year,
            'genre': self.genre,
            'author': self.author,
            'description': self.description,
            'cover_image': self.cover_image,
            'price': self.price,
            'archived': self.archived
        }


class DeleteBook(TunedModel):
    id: UUID


class SearchBook(DeleteBook):
    pass


class Book(CreateBook):
    id: UUID

    class Config:
        model_config = ConfigDict(from_attributes=True)
        json_schema_extra = {
            "example": {
                "id": uuid4(),
                "title": "Example Book",
                "publication_year": 2022,
                "genre": ["fiction", "mystery"],
                "author": "John Doe",
                "description": "An example book description.",
                "cover_image": "https://example.com/cover-image.jpg"
            }
        }

    def json(self, **kwargs):
        return {
            'id': self.id,
            'title': self.title,
            'publication_year': self.publication_year,
            'genre': self.genre,
            'author': self.author,
            'description': self.description,
            'cover_image': self.cover_image,
            'price': self.price,
            'archived': self.archived
        }


class ValidBook(CreateBook):

    def json(self, **kwargs):
        return {
            'title': self.title,
            'publication_year': self.publication_year,
            'genre': self.genre,
            'author': self.author,
            'description': self.description,
            'cover_image': self.cover_image,
            'price': self.price,
            'error': self.error
        }


class InvalidBook(CreateBook):
    title: Any
    genre: Any
    author: Any
    description: Any
    price: Any
    publication_year: Any
    cover_image: Any
    error: Any

    def json(self, **kwargs):
        return {
            'title': self.title,
            'publication_year': self.publication_year,
            'genre': self.genre,
            'author': self.author,
            'description': self.description,
            'cover_image': self.cover_image,
            'price': self.price,
            'error': self.error
        }
