from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from pathlib import Path
from schemas.research import ResearchReport, Source
import os
import json

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# ── LLM Setup ──────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)


# ── Tools ──────────────────────────────────────────────────────
def get_tools(max_results: int = 3):
    return [
        TavilySearchResults(
            max_results=max_results,
            api_key=os.getenv("TAVILY_API_KEY")
        )
    ]


def build_research_prompt(topic: str, depth: str) -> str:
    depth_instructions = {
        "quick":  "Do 1-2 searches. Give a brief overview with 3-4 key findings.",
        "medium": "Do 2-3 searches covering different aspects. Give 4-6 key findings.",
        "deep":   "Do 4-5 searches covering trends, examples, challenges, future. Give 6-8 key findings."
    }
    instruction = depth_instructions.get(depth, depth_instructions["medium"])

    return f"""Research this topic: {topic}

Instructions: {instruction}

After researching, provide your response in this EXACT JSON format:
{{
  "summary": "2-3 sentence executive summary",
  "key_findings": [
    "Finding 1 — specific and factual",
    "Finding 2 — specific and factual"
  ],
  "sources": [
    {{
      "title": "Page title",
      "url": "https://actual-url.com",
      "summary": "One sentence about what this source contributed"
    }}
  ]
}}

Return ONLY the JSON. No markdown. No explanation outside the JSON."""


async def run_research_agent(topic: str, depth: str = "medium") -> ResearchReport:
    """
    Main agent function using LangGraph ReAct agent.

    ReAct = Reasoning + Acting loop:
    1. Agent THINKS about what to do
    2. Agent ACTS by calling a tool
    3. Agent OBSERVES the result
    4. Repeats until it has enough info
    5. Returns final structured answer
    """

    # commented below to fetch always 2 results
    # tools = get_tools(max_results=5 if depth == "deep" else 3)

    tools = get_tools(max_results=2)

    # create_react_agent = modern LangGraph way
    # replaces old AgentExecutor
    agent = create_react_agent(
        model=llm,
        tools=tools
    )

    research_prompt = build_research_prompt(topic, depth)

    # ainvoke = async invoke — runs the full ReAct loop
    result = await agent.ainvoke({
        "messages": [("human", research_prompt)]
    })

    # Last message = agent's final answer
    raw_output = result["messages"][-1].content
    print("\n=== AGENT RAW OUTPUT ===")
    print(raw_output)
    print("========================\n")

    try:
        clean = raw_output.strip().strip("```json").strip("```").strip()
        data = json.loads(clean)

        sources = [
            Source(
                title=s.get("title", "Unknown"),
                url=s.get("url", ""),
                summary=s.get("summary", "")
            )
            for s in data.get("sources", [])
        ]

        return ResearchReport(
            topic=topic,
            summary=data.get("summary", ""),
            key_findings=data.get("key_findings", []),
            sources=sources,
            depth_used=depth,
            total_sources_found=len(sources)
        )

    except json.JSONDecodeError:
        return ResearchReport(
            topic=topic,
            summary=raw_output,
            key_findings=[],
            sources=[],
            depth_used=depth,
            total_sources_found=0
        )
