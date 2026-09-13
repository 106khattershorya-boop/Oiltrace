from fastapi import FastAPI

from app.core.config import settings
from app.routers import (
    incidents,
    vessels,
    correlation,
    behaviour,
    spectral,
    evidence,
    priority,
    investigation,
    cargo,
    ml_analysis
)


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(incidents.router)
app.include_router(vessels.router)
app.include_router(correlation.router)
app.include_router(behaviour.router)
app.include_router(spectral.router)
app.include_router(evidence.router)
app.include_router(priority.router)
app.include_router(investigation.router)
app.include_router(cargo.router)
app.include_router(ml_analysis.router)

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "service": "SIH26143 backend running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}