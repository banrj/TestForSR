from typing import List
from uuid import UUID
from app.dto.price_history import PriceHistoryShow

from app.db.cruds import price_history as history_cruds


async def show_history_book(book_id: UUID, lim: int, offset: int) -> List[PriceHistoryShow]:
    return await history_cruds.get_history_book(book_id=book_id, lim=lim, offset=offset)
