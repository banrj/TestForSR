from uuid import UUID

from fastapi import APIRouter

from app.handlers.price_history import show_history_book

price_history_router = APIRouter()


@price_history_router.get('/{book_id}', tags=['price_history'])
async def show_history(book_id: UUID, lim: int = 10, offset: int = 0):
    return await show_history_book(book_id=book_id, lim=lim, offset=offset)
