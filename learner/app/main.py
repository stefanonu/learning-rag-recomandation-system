from fastapi import FastAPI
from app.api.routes import router as api_router
from app.db.base import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(api_router)
