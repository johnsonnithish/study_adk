# Agent Development Kit Examples

Self-contained examples that show how to build agents with the Google ADK: single LLM helpers, tool-using agents, structured outputs, session/state management, persistence, orchestration (multi/sequential/parallel/loop), and callbacks.

## Setup
- Python 3.10+ recommended. Install deps: `pip install -r requirements.txt`
- Environment: set `OPENAI_KEY` for the LiteLLM example; other samples use `gemini-2.0-flash`.
- Run examples from repo root (e.g., `python 5-session-and-state/basic_stateful_session.py`).

## Repo Map
- `1-basic-agent/` – minimal greeting agent.
- `2-tool-agent/` – time lookup tool.
- `3-litellm-agent/` – OpenAI via `LiteLlm`, dad jokes tool.
- `4-structured-outputs/` – JSON-shaped email generation with Pydantic schema.
- `5-session-and-state/` – in-memory sessions and state-aware QA.
- `6-persistent-storage/` – SQLite-backed sessions plus reminder tools.
- `7-multi-agent/` – manager delegating to specialized agents/tools.
- `8-stateful-multi-agent/` – customer service hub with shared state and sub-agents.
- `9-callbacks/` – before/after callbacks for agents, tools, and model calls.
- `x-sequential-agent/` – pipeline for lead qualification.
- `xi-parallel-agent/` – parallel system monitor with psutil tools.
- `xii-loop-agent/` – iterative LinkedIn post refinement loop.

## Highlights & Snippets

**Basic agent**  
Minimal setup with an instruction-only agent:
```python
from google.adk.agents import Agent

root_agent = Agent(
    name="greeting_agent",
    model="gemini-2.0-flash",
    description="Greeting Agent",
    instruction="Ask for the user's name and greet them.",
)
```

**Tools** (`2-tool-agent`)  
Expose Python functions as tools:
```python
from datetime import datetime
from google.adk.agents import Agent

def get_current_time() -> dict:
    return {"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

root_agent = Agent(
    name="tool_agent",
    model="gemini-2.0-flash",
    tools=[get_current_time],
    instruction="Use get_current_time when asked for the time.",
)
```

**LiteLLM + OpenAI** (`3-litellm-agent`)  
Wraps a LiteLLM client and forces tool use:
```python
from google.adk.models.lite_llm import LiteLlm
model = LiteLlm(model="gpt-4o-mini", api_key=os.getenv("OPENAI_KEY"))
root_agent = Agent(
    name="litellm_agent",
    model=model,
    tools=[get_dad_joke],
    instruction="Only answer via the get_dad_joke tool.",
)
```

**Structured outputs** (`4-structured-outputs`)  
Guarantee JSON using `output_schema`:
```python
class EmailContent(BaseModel):
    subject: str
    body: str

root_agent = Agent(
    name="email_agent",
    model="gemini-2.0-flash",
    output_schema=EmailContent,
    output_key="email",
    instruction="Return valid JSON with subject and body only.",
)
```

**Sessions & state** (`5-session-and-state`)  
State placeholders inject user data; `Runner` wires sessions:
```python
session_service = InMemorySessionService()
stateful_session = session_service.create_session(
    app_name="J Bot", user_id="dev", session_id=str(uuid.uuid4()), state=initial_state
)
runner = Runner(agent=question_answering_agent, app_name="J Bot", session_service=session_service)
```

**Persistent storage** (`6-persistent-storage`)  
SQLite-backed `DatabaseSessionService` plus reminder tools that mutate `tool_context.state`:
```python
def add_reminder(reminder: str, tool_context: ToolContext) -> dict:
    reminders = tool_context.state.get("reminders", [])
    reminders.append(reminder)
    tool_context.state["reminders"] = reminders
    return {"action": "add_reminder", "reminder": reminder}
```
Run the chat loop: `python 6-persistent-storage/main.py`.

**Multi-agent manager** (`7-multi-agent`)  
Delegates to sub-agents and tools (e.g., stock quotes via `yfinance`):
```python
root_agent = Agent(
    name="manager",
    model="gemini-2.0-flash",
    sub_agents=[stock_analyst, funny_nerd],
    tools=[AgentTool(news_analyst), get_current_time],
    instruction="Route requests to the right specialist.",
)
```

**Stateful customer service** (`8-stateful-multi-agent`)  
Shared state tracks purchases and interactions; sales/order tools mutate it:
```python
def purchase_course(tool_context: ToolContext) -> dict:
    courses = tool_context.state.get("purchased_courses", [])
    courses.append({"id": "ai_marketing_platform", "purchase_date": now})
    tool_context.state["purchased_courses"] = courses
    return {"status": "success", "course_id": "ai_marketing_platform"}
```
Interactive run: `python 8-stateful-multi-agent/main.py`.

**Callbacks** (`9-callbacks`)  
- Agent-level logging with `before_agent_callback`/`after_agent_callback`.
- Model-level filtering: block messages before hitting the model and soften wording after.
- Tool-level hooks: adjust args (e.g., map "Merica" to "United States") or tweak results.

**Sequential pipeline** (`x-sequential-agent`)  
`SequentialAgent` chains validation → scoring → action recommendations for leads.

**Parallel system monitor** (`xi-parallel-agent`)  
`ParallelAgent` runs CPU/memory/disk LLM agents concurrently; each calls psutil-backed tools and a synthesizer produces a Markdown report.

**Looping refinement** (`xii-loop-agent`)  
`LoopAgent` iterates review/refine steps for a LinkedIn post; the reviewer can call `exit_loop` to stop once quality checks (including length via `count_characters`) pass.

## Running Example Scripts
- In-memory state demo: `python 5-session-and-state/basic_stateful_session.py`
- Persistent reminders: `python 6-persistent-storage/main.py`
- Stateful customer support: `python 8-stateful-multi-agent/main.py`

Each script creates its own session service and prints agent responses to the console.
