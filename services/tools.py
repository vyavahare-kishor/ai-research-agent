from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


def get_search_tool(max_results: int = 5) -> TavilySearchResults:
    """
    Web search tool — agent calls this to search the internet.
    max_results controls how many pages it reads per search.
    """
    return TavilySearchResults(
        max_results=max_results,
        api_key=os.getenv("TAVILY_API_KEY")
    )


@tool
def summarise_findings(findings: str) -> str:
    """
    Summarise and structure raw research findings into key points.
    Agent calls this when it has gathered enough information.
    """
    return findings
