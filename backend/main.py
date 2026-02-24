from fastapi import FastAPI
from app.auth.router import router as auth_router

app = FastAPI(title="Bytestream Messenger API")

app.include_router(auth_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
