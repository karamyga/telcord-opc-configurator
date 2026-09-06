from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from .api.routes import router
from .database import Base, engine

Base.metadata.create_all(engine)
app=FastAPI(title="TELCORD Configurator")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173"],allow_methods=["*"],allow_headers=["*"])
app.include_router(router)
@app.get("/health")
def health(): return {"status":"ok"}
@app.get("/", include_in_schema=False)
def configurator():
    return FileResponse(Path(__file__).parent / "static" / "index.html")
