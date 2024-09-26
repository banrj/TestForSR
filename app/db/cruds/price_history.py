from uuid import UUID

from fastapi import HTTPException, Response

from sqlalchemy import delete, select

from app.db.models import PriceHistory
from app.db.database import async_session_maker


async def create_history(book_id: UUID, price: int | None = 0):
    async with async_session_maker() as session:
        async with session.begin():
            try:
                new_history = PriceHistory(book_id=book_id, price=price)
                session.add(new_history)
                await session.commit()
            except Exception as ex:
                await session.rollback()
                raise HTTPException(detail={'message': f'Произошла ошибка!: {str(ex)}'},
                                    status_code=500)


async def delete_history_book(book_id: UUID):
    async with async_session_maker() as session:
        async with session.begin():

            try:
                stmt = (delete(PriceHistory).where(PriceHistory.book_id == book_id).returning(PriceHistory.id))
                deleted_id = await session.scalar(stmt)

                if deleted_id:
                    await session.commit()
                    return Response(content={
                        'message': f'История цен книнги №{deleted_id} удалена!'},
                        status_code=200)

                await session.rollback()
                raise HTTPException(detail={
                    'message': f'История цен книги с id {book_id} не существует!'},
                    status_code=404)
            except Exception as ex:
                await session.rollback()
                raise HTTPException(detail={'message': f'Произошла ошибка!: {str(ex)}'},
                                    status_code=500)


async def get_history_book(book_id: UUID, lim: int, offset: int):
    async with async_session_maker() as session:
        async with session.begin():

            try:
                stmt = select(PriceHistory.id, PriceHistory.book_id,
                              PriceHistory.price, PriceHistory.updated_at
                              ).where(PriceHistory.book_id == book_id
                                      ).order_by(PriceHistory.updated_at).limit(lim).offset(offset)
                res = await session.execute(stmt)
                history_row = [r._asdict() for r in res.fetchall()]
                if not history_row:
                    raise HTTPException(detail={
                        'message': f'История цен книги с id {book_id} не существует!'},
                        status_code=404)
                return history_row
            except Exception as ex:
                await session.rollback()
                raise HTTPException(detail={'message': f'Произошла ошибка!: {str(ex)}'},
                                    status_code=500)


async def create_many_history(books_data):
    async with async_session_maker() as session:
        async with session.begin():

            try:
                print(books_data)
                all_history = []
                for book in books_data:
                    all_history.append(PriceHistory(book_id=book[0], price=book[1]))
                session.add_all(all_history)
                await session.commit()
            except Exception as ex:
                await session.rollback()
                raise HTTPException(detail={'message': f'Произошла ошибка!: {str(ex)}'},
                                    status_code=500)
