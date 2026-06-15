# 🤖 AI Research Agent

> An autonomous AI agent that researches any topic on the internet and returns a structured report — powered by LangGraph ReAct, LLaMA 3, Groq, and Tavily Search.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?style=flat-square&logo=fastapi)
![LangGraph](https://img.shields.io/badge/Agent-LangGraph%20ReAct-purple?style=flat-square)
![Groq](https://img.shields.io/badge/LLM-LLaMA%203%20%7C%20Groq-orange?style=flat-square)
![Tavily](https://img.shields.io/badge/Search-Tavily-blue?style=flat-square)

---

## 🎯 What It Does

Most AI apps follow a fixed pipeline — you write the steps, the LLM executes them.

This is different. You give the agent a **goal** and **tools**. The agent decides its own steps autonomously.

```
You:   "Research the latest trends in Agentic AI systems"

Agent thinks:  "I need to search for this"
Agent acts:    calls web search → "agentic AI trends 2025"
Agent observes: reads results
Agent thinks:  "I need more context on multi-agent systems"
Agent acts:    calls web search → "multi-agent frameworks 2025"
Agent observes: reads results
Agent thinks:  "I have enough. Time to synthesise."
Agent returns: structured JSON report with findings + sources
```

You didn't write those steps. The agent decided them. That's agentic AI.

---

## ✨ Features

- **ReAct Agent Loop** — Reasoning + Acting pattern. Agent thinks, acts, observes, repeats until it has enough information
- **Autonomous web search** — Agent decides what to search for, when to search again, and when to stop
- **Depth control** — `quick` (1 search), `medium` (2 searches), `deep` (3 searches)
- **Structured output** — Returns typed, validated JSON with summary, key findings, and cited sources
- **Graceful fallback** — If agent output can't be parsed, raw response is returned — never crashes
- **Auto Swagger UI** — Interactive docs at `/docs`

---

## 📡 API Reference

### `POST /research/`

Run the research agent on any topic.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `topic` | string | ✅ | What to research |
| `depth` | string | ❌ | `"quick"`, `"medium"`, `"deep"` (default: `"medium"`) |

**Request:**
```json
{
  "topic": "Latest trends in Agentic AI systems 2025",
  "depth": "medium"
}
```

**Response:**
```json
{
  "topic": "Latest trends in Agentic AI systems 2025",
  "summary": "Agentic AI systems are rapidly evolving with multi-agent frameworks becoming the dominant pattern in production AI applications.",
  "key_findings": [
    "LangGraph and LangChain are the leading orchestration frameworks for production agent systems",
    "Companies are shifting from single LLM calls to autonomous multi-step agent pipelines",
    "Tool use and function calling are now standard in enterprise AI deployments",
    "ReAct pattern has emerged as the most reliable agent reasoning approach"
  ],
  "sources": [
    {
      "title": "The Rise of Agentic AI in 2025",
      "url": "https://example.com/agentic-ai",
      "summary": "Overview of how agent frameworks are transforming AI development"
    }
  ],
  "depth_used": "medium",
  "total_sources_found": 3
}
```

---

## 🧠 How the ReAct Agent Works

ReAct = **Re**asoning + **Act**ing. The agent alternates between thinking and doing until it reaches a conclusion.

```
START
  │
  ▼
Agent reads your topic + instructions
  │
  ▼
THINK: "What should I search for first?"
  │
  ▼
ACT: calls Tavily web search
  │
  ▼
OBSERVE: reads search results
  │
  ▼
THINK: "Do I have enough? What's missing?"
  │
  ├── Not enough → ACT: search again with different query
  │                      │
  │                      └── OBSERVE → THINK → ...
  │
  └── Enough → SYNTHESISE: generate structured JSON report
                    │
                    ▼
                  DONE
```

**The key difference from a pipeline:**

| Pipeline (RAG, PR Reviewer) | Agent (this project) |
|---|---|
| You define every step | Agent decides its own steps |
| Fixed number of operations | Variable — agent stops when satisfied |
| Deterministic | Adaptive |
| Great for known workflows | Great for open-ended research |

---

## 🏗️ Architecture

```
Client
  │
  ▼
FastAPI Router (/research)
  │
  ▼
run_research_agent()
  │
  ├── build_research_prompt(topic, depth)
  │
  ├── create_react_agent(llm=LLaMA3, tools=[TavilySearch])
  │
  └── agent.ainvoke(prompt)
        │
        ├── LLM thinks → calls TavilySearch → reads results
        ├── LLM thinks → calls TavilySearch again (if needed)
        └── LLM synthesises → returns JSON
              │
              ▼
        Parse JSON → ResearchReport (Pydantic)
              │
              ▼
        Return to client
```

**Key design decisions:**

- **LangGraph over LangChain AgentExecutor** — LangGraph is the modern approach. More reliable, better maintained, production-ready. LangChain deprecated AgentExecutor in favour of LangGraph.
- **Groq for speed** — LLaMA 3 on Groq runs at ~800 tokens/second. Agent loops complete in seconds, not minutes.
- **Tavily over SerpAPI** — Tavily is purpose-built for AI agents. Returns clean, structured content, not raw HTML. Fewer tokens, better signal.
- **Forced JSON output** — Agent is instructed to return strict JSON. Pydantic validates and structures it. If parsing fails, graceful fallback prevents crashes.
- **Depth as a cost control lever** — `depth` controls max searches which controls token usage. Practical for rate-limited free tiers and production cost management.

---

## 🗂️ Project Structure

```
ai-research-agent/
├── main.py                    # App entry, router registration
├── schemas/
│   ├── __init__.py
│   └── research.py            # ResearchRequest, ResearchReport, Source
├── services/
│   ├── __init__.py
│   ├── tools.py               # Tool definitions (Tavily search)
│   └── agent.py               # ReAct agent, prompt builder, output parser
├── routers/
│   ├── __init__.py
│   └── research.py            # POST /research/ endpoint
├── .env.example
└── .gitignore
```

---

## 🧠 Technical Highlights

**ReAct agent with LangGraph**
```python
# create_react_agent handles the full Think → Act → Observe loop
agent = create_react_agent(
    model=llm,    # LLaMA 3 via Groq
    tools=tools   # [TavilySearch] — agent decides when to call this
)

result = await agent.ainvoke({
    "messages": [("human", research_prompt)]
})
# result["messages"][-1].content = agent's final answer
```

**Depth-controlled research**
```python
depth_instructions = {
    "quick":  "Do 1 search only. Give 2-3 key findings.",
    "medium": "Do 2 searches max. Give 3-4 key findings.",
    "deep":   "Do 3 searches max. Give 4-5 key findings."
}
```

**Structured output parsing with graceful fallback**
```python
try:
    clean = raw_output.strip().strip("```json").strip("```").strip()
    data = json.loads(clean)
    return ResearchReport(**data)
except json.JSONDecodeError:
    # Never crash — return raw output as summary
    return ResearchReport(topic=topic, summary=raw_output, ...)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- [Groq API key](https://console.groq.com) — free
- [Tavily API key](https://tavily.com) — free (1000 searches/month)

### Installation

```bash
git clone https://github.com/vyavahare-kishor/ai-research-agent
cd ai-research-agent

curl -LsSf https://astral.sh/uv/install.sh | sh

uv venv
source .venv/bin/activate
uv install
```

### Configuration

```bash
cp .env.example .env
```

```bash
# .env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### Run

```bash
uvicorn main:app --reload
```

Open **http://localhost:8000/docs** ✅

### Quick test

```bash
curl -X POST http://localhost:8000/research/ \
  -H "Content-Type: application/json" \
  -d '{"topic": "Agentic AI trends 2025", "depth": "quick"}'
```

---

## 🗺️ Roadmap

- [ ] Multi-agent system — orchestrator delegates to specialist sub-agents (research, summarise, fact-check)
- [ ] Memory — agent remembers previous research sessions
- [ ] Streaming — stream agent thoughts and findings in real time via SSE
- [ ] More tools — calculator, code executor, PDF reader, database lookup
- [ ] Agent observability — trace every agent step with LangSmith
- [ ] Deploy to Railway / Render

---

## 🔗 Related Projects

Part of an AI-native engineering portfolio — built while transitioning from Ruby on Rails → AI Engineering:

| Project | Description | Key concepts |
|---------|-------------|--------------|
| [**ai-native-journey**](https://github.com/yourusername/ai-native-journey) | FastAPI foundation — REST API + AI chat + SSE streaming | FastAPI, PostgreSQL, Groq |
| [**ai-pr-reviewer**](https://github.com/yourusername/ai-pr-reviewer) | AI-powered GitHub PR code reviewer | GitHub API, structured LLM output |
| [**ai-customer-support-bot**](https://github.com/yourusername/ai-customer-support-bot) | RAG pipeline — semantic search + grounded answers | pgvector, embeddings, RAG |
| **ai-research-agent** (this) | Autonomous ReAct agent — self-directed research | LangGraph, tool use, agentic AI |

---

## 👨‍💻 Author

**Kishor Vyavahare**
Senior Software Engineer → AI Native Engineer

11+ years of backend engineering (Ruby on Rails, PostgreSQL, Redis, AWS, Docker).
Now building production AI systems — RAG pipelines, ReAct agents, agentic workflows, and LLM-powered APIs.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/vyavahare-kishor)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat-square&logo=github)](https://github.com/vyavahare-kishor)

---

## 📄 License

MIT License — use it, fork it, build on it.
