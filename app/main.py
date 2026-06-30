from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers import auth, recipes


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Recipe Box API", lifespan=lifespan)

# Without this, the browser blocks every request from the Next.js dev server
# (localhost:3000) to this API (localhost:8000) — different ports count as
# different "origins" as far as browsers are concerned, even on localhost.
# curl/Postman ignore this entirely, which is why it's easy to miss in testing.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(recipes.router)


@app.get("/")
def root():
    return {"message": "Recipe Box API — see /docs for the interactive API explorer"}
