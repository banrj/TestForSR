from uuid import UUID

from fastapi import APIRouter, UploadFile

from app.dto.book import CreateBook, ShowBook, DeleteBook, SearchBook, UpdateBook
from app.handlers.book import create_new_book, delete_book, get_current_book, update_current_book, get_list_books, \
    finalize_books, check_file, filter_books

book_router = APIRouter()


@book_router.post('/create', tags=['books'], response_model=ShowBook)
async def create_book(body: CreateBook) -> ShowBook:

    return await create_new_book(body=body)


@book_router.delete('/{book_id}', tags=['books'])
async def delete_book(book_id: UUID):

    return await delete_book(book_id=book_id)


@book_router.get('/{book_id}', tags=['books'])
async def get_book(book_id: UUID):

    return await get_current_book(book_id=book_id)


@book_router.patch('/{book_id}', tags=['books'])
async def update_book(book_id: UUID, body: UpdateBook):

    return await update_current_book(body=body, book_id=book_id)


@book_router.get('/', tags=['books'])
async def get_books(offset: int = 0, lim: int = 10, title: str = None,
                    author: str = None, genres: str = None, price: int = None,
                    description: str = None, genres_neq: str = None,
                    ):
    return await get_list_books(lim=lim, offset=offset, title=title,
                                author=author, genres=genres, genres_neq=genres_neq,
                                description=description, price=price
                                )


@book_router.post("/file/upload-file", tags=['books'])
async def upload_file(file: UploadFile):
    return await finalize_books(file=file, func=check_file)


@book_router.get('/loading/', tags=['books'])
async def load_books():
    return await finalize_books(func=filter_books)
