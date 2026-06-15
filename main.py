from routers import research
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()


app = FastAPI(
    title="AI Research Agent",
    description="Autonomous AI agent that researches topics and produces structured reports"
)

app.include_router(research.router)


@app.get("/")
def root():
    return {
        "name": "AI Research Agent",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok", "agent": "ready"}
