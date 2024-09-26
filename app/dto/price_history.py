from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class PriceHistoryShow(BaseModel):
    id: UUID
    book_id: int
    price: int
    time: datetime

    model_config = ConfigDict(from_attributes=True)

