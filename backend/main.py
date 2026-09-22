import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from api.routes_research import router as research_router
from api.routes_providers import router as providers_router
from api.routes_eval import router as eval_router
from api.routes_documents import router as documents_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="VeriAI — Multi-LLM Research & Hallucination Verification Platform"
)

# Enable CORS for local and web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(research_router)
app.include_router(providers_router)
app.include_router(eval_router)
app.include_router(documents_router)

@app.get("/")
def read_root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "description": "Multi-LLM Research & Hallucination Verification Platform API"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
