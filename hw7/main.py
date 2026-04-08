from fastapi import FastAPI

from .db import Base, engine
from .routers import auth, items

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CRUD + Auth Homework")

app.include_router(auth.router)
app.include_router(items.router)


@app.get("/")
def root():
    return {"message": "API is running"}