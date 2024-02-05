from fastapi import FastAPI
import uvicorn
from backend.routes import router as routes_router

app = FastAPI()
app.include_router(routes_router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


def serve():
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
