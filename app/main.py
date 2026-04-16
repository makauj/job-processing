# main entry into the application
from fastapi import FastAPI

from app.api.routes import router
from app.db.base import Base
from app.db.session import engine
from app.models import jobs, users  # noqa: F401

app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(router)
