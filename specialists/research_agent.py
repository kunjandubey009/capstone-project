"""Agent 2/6: Research Agent — gathers external + internal evidence."""
from agents import Agent
import config
from models.schemas import ResearchFindings
from tools.web_search_tool import web_search_tool
from tools.knowledge_base_tool import knowledge_base_tool

research_agent = Agent(
    name="Research Agent",
    model=config.DEFAULT_MODEL,
    instructions=(
        "You are the Research Agent. You receive a TaskPlan's research-owned "
        "tasks (owner_agent == 'research'). Use web_search_tool for external "
        "market/industry evidence and knaowledge_base_tool for internal company "
        "documents. Cross-reference both. Return a ResearchFindings object: "
        "each finding needs a topic, a concise summary, a source (url or doc "
        "title), and a confidence score between 0 and 1. List any open "
        "questions you could not resolve. Do not fabricate sources — every "
        "finding must trace back to an actual tool result."
    ),
    tools=[web_search_tool, knowledge_base_tool],
    output_type=ResearchFindings,
)
