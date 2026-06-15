from fastapi import APIRouter, HTTPException
from schemas.research import ResearchRequest, ResearchReport
from services.agent import run_research_agent

router = APIRouter(prefix="/research", tags=["Research Agent"])


@router.post("/", response_model=ResearchReport)
async def research(request: ResearchRequest):
    """
    AI Research Agent — give it a topic, get a structured report.
    Agent autonomously searches the web and synthesises findings.
    """
    try:
        report = await run_research_agent(
            topic=request.topic,
            depth=request.depth
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
