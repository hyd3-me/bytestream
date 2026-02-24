from fastapi import FastAPI

app = FastAPI(title="Bytestream Messenger API")

@app.get("/health")
async def health_check():
    return {"status": "ok"}