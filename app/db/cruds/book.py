from typing import List, Text, Dict
from uuid import UUID

from fastapi.responses import Response, JSONResponse
from fastapi import HTTPException

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError, DataError, DBAPIError, SQLAlchemyError

from app.db.models import Book, PriceHistory
from app.dto.book import UpdateBook, InvalidBook, ShowBook
from app.db.database import async_session_maker
from app.config import MIN_DATA, MAX_DATA


async def create_book(
        title: str,
        publication_year: int,
        genre: List[str],
        price: int | None = 0,
        author: str | None = None,
        description: Text | None = None,
        cover_image: str | None = None
) -> Book | Response:
    """
    func for create new book
    """
    async with async_session_maker() as session:
        async with session.begin():
            try:
                print(
                    f"Trying to insert publication_year: {publication_year}, MIN_DATA: {MIN_DATA}, "
                    f"MAX_DATA: {MAX_DATA}")

                new_book = Book(title=title,
                                publication_year=publication_year,
                                genre=genre,
                                author=author,
                                price=price,
                                description=description,
                                cover_image=cover_image)
                session.add(new_book)
                await session.commit()
                await session.flush()
                return new_book
            except (IntegrityError, DataError, TypeError, DBAPIError) as ex:
                await session.rollback()
                invalid_book = InvalidBook(title=title, publication_year=publication_year,
                                           genre=genre, author=author, price=price,
                                           description=description, cover_image=cover_image,
                                           error=f'{str(ex)}').json()
                raise HTTPException(detail={'invalid_book': invalid_book},
                                    status_code=400)
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

            except Exception as ex:
                await session.rollback()
                raise HTTPException(detail={'message': f'Произошла ошибка!: {str(ex)}'},
                                    status_code=500)


async def delete_book(book_id: UUID) -> Response:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = (update(Book).where(Book.id == book_id)
                        .values(archived=True)
                        .returning(Book.id))
                deleted_id = await session.scalar(stmt)

                if deleted_id:
                    await session.commit()
                    return Response(content={
                        'message': f'Книга под №{deleted_id} заархивирована!'},
                        status_code=200)

                await session.rollback()
                raise HTTPException(detail={
                    'message': f'Книги с id {book_id} не существует'},
                    status_code=404)
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

            except Exception as ex:
                await session.rollback()
                raise HTTPException(detail={'message': f'Произошла ошибка!: {str(ex)}'},
                                    status_code=500)


async def get_book(book_id: UUID) -> Book | Response:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                query = select(Book).where(Book.id == book_id)
                row = await session.execute(query)
                book_row = row.fetchone()
                if book_row:
                    return book_row[0]
                raise HTTPException(detail={
                    'message': f'Книги с id {book_id} не существует'},
                    status_code=404)
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
            except Exception as ex:
                raise HTTPException(detail={'message': f'Произошла ошибка!: {str(ex)}'},
                                    status_code=500)


async def update_book(book_id: UUID, update_book: UpdateBook) -> Dict | Response:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                query = select(Book).where(Book.id == book_id)
                row = await session.execute(query)
                book_row = row.fetchone()
                if book_row:
                    cur_book = book_row[0]
                    price_flag = ((update_book.price is not None) and update_book.price != cur_book.price)
                    book_data = update_book.model_dump(exclude_none=True, exclude_unset=True)
                    for key, value in book_data.items():
                        setattr(cur_book, key, value)
                    await session.commit()
                    return {'book': cur_book, 'flag': price_flag}
                raise HTTPException(detail={
                    'message': f'Книги с id {book_id} не существует'},
                    status_code=404)
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
            except Exception as ex:
                await session.rollback()
                raise HTTPException(detail={'message': f'Произошла ошибка!: {str(ex)}'},
                                    status_code=500)


async def get_books(lim: int, offset: int, title: str = None,
                    author: str = None, genres: str = None, price: int = None,
                    description: str = None, genres_neq: str = None
                    ):
    async with async_session_maker() as session:
        async with session.begin():

            try:
                stmt = select(Book.id, Book.title, Book.publication_year,
                              Book.author, Book.genre, Book.description,
                              Book.cover_image, Book.price
                              ).order_by(Book.id).limit(lim).offset(offset)
                if title:
                    stmt = stmt.filter(Book.title == title)
                if price:
                    stmt = stmt.filter(Book.price == price)
                if author:
                    stmt = stmt.filter(Book.author == author)
                if genres:
                    stmt = stmt.filter(Book.genre.contains(genres.split(',')))
                if genres_neq:
                    stmt = stmt.filter(~(Book.genre.contains(genres_neq.split(','))))
                if description:
                    stmt = stmt.filter(Book.description.ilike(f'%{description}%'))

                res = await session.execute(stmt)
                book_row = [ShowBook(**r).json() for r in res.mappings().all()]

                if not book_row:
                    raise HTTPException(detail={'message': f'Нет книги с такими параметрами'},
                                        status_code=404)
                return book_row

            except Exception as ex:
                await session.rollback()
                raise HTTPException(detail={'message': f'Произошла ошибка!: {str(ex)}'},
                                    status_code=500)


async def load_data(load_data):
    async with async_session_maker() as session:
        async with session.begin():

            duplicates = []
            original = []
            try:
                stmt = select(Book.title)
                res = await session.execute(stmt)
                book_row = [r[0] for r in res.fetchall()]
                for data in load_data:
                    if data['title'] not in book_row:
                        book = Book(**data)
                        original.append(book)
                        book_row.append(data['title'])
                    else:
                        duplicates.append(data)

                session.add_all(original)
                await session.commit()

            except Exception as ex:
                await session.rollback()
                raise HTTPException(detail={'message': f'Произошла ошибка!: {str(ex)}'},
                                    status_code=500)
            finally:
                await session.close()

            return {'message': 'Data processed', 'valid_books': original, 'duplicate_books': duplicates}
