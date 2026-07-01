from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from model import get_assets, get_measurements, get_summary, get_status_counts
from langgraph.prebuilt import ToolNode

@tool
def get_assets_tool() -> list:
    """Get the list of all asset names in the database."""
    return get_assets()


@tool
def get_measurements_tool(asset_name: str, measurement_type: str) -> list:
    """Get measurement readings over time for a specific asset and measurement type.
    Returns dates, values, utilization, and status.

    Args:
        asset_name: Name of the asset, e.g. Asset_A
        measurement_type: Type of measurement: corrosion_rate, temperature, or pressure
    """
    return get_measurements(asset_name, measurement_type)


@tool
def get_summary_tool(asset_name: str) -> dict:
    """Get average, min, and max values for each measurement type for a specific asset.

    Args:
        asset_name: Name of the asset, e.g. Asset_A
    """
    return get_summary(asset_name)


@tool
def get_status_counts_tool() -> dict:
    """Get the count of busy vs idle readings for each asset."""
    return get_status_counts()


tools = [get_assets_tool, get_measurements_tool, get_summary_tool, get_status_counts_tool]

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    max_tokens=1050,
).bind_tools(tools)

SYSTEM_PROMPT = (
    "You are a formal asset monitoring assistant. You help users understand their industrial asset data. "
    "Use the available tools to query the database and provide accurate, data-driven answers.\n\n"
    "STRICT RULES:\n"
    "- NEVER use emojis, icons, or decorative symbols in your responses.\n"
    "- Use a formal, professional, and systematic tone at all times.\n"
    "- Return data directly: tables, numbers, and brief factual statements.\n"
    "- Do not add greetings, pleasantries, or filler language.\n"
    "- Be concise. Cite specific numbers from the data when relevant.\n"
    "- Structure responses with clear headers and bullet points when presenting multiple data points."
)


def chatbot(state: MessagesState):
    messages = state["messages"]
    response = llm.invoke(
        [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    )
    return {"messages": [response]}

tool_node = ToolNode(tools)

def should_continue(state: MessagesState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END 

graph = StateGraph(MessagesState)

graph.add_node("chatbot", chatbot)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chatbot")
graph.add_conditional_edges("chatbot", should_continue)
graph.add_edge("tools", "chatbot")


app = graph.compile()


def run_agent(user_message: str, conversation_history: list, api_key: str) -> str:
    messages = list(conversation_history) + [
        {"role": "user", "content": user_message}
    ]

    result = app.invoke({"messages": messages})

    return result["messages"][-1].content
