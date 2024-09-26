import uvicorn

from fastapi import FastAPI
from app.routers.routers import main_api_router

app = FastAPI(
    title="Library"
)

app.include_router(main_api_router)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
