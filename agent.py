import json
import anthropic
from model import get_assets, get_measurements, get_summary, get_status_counts
from graph import line_chart, bar_chart, pie_chart

TOOL_SCHEMAS = [
    {
        "name": "get_assets",
        "description": "Get the list of all asset names in the database.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_measurements",
        "description": "Get measurement readings over time for a specific asset and measurement type. Returns dates, values, utilization, and status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "asset_name": {"type": "string", "description": "Name of the asset, e.g. Asset_A"},
                "measurement_type": {"type": "string", "description": "Type of measurement: corrosion_rate, temperature, or pressure"},
            },
            "required": ["asset_name", "measurement_type"],
        },
    },
    {
        "name": "get_summary",
        "description": "Get average, min, and max values for each measurement type for a specific asset.",
        "input_schema": {
            "type": "object",
            "properties": {
                "asset_name": {"type": "string", "description": "Name of the asset, e.g. Asset_A"},
            },
            "required": ["asset_name"],
        },
    },
    {
        "name": "get_status_counts",
        "description": "Get the count of busy vs idle readings for each asset.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

TOOL_FUNCTIONS = {
    "get_assets": get_assets,
    "get_measurements": get_measurements,
    "get_summary": get_summary,
    "get_status_counts": get_status_counts,
}

SYSTEM_PROMPT = (
    "You are an asset monitoring assistant. You help users understand their asset data by querying the database and generating charts. "
    "When a user asks about an asset, use the tools to get real data. "
    "After getting data, describe what you see and suggest which chart type would be useful: "
    "line chart for trends over time, bar chart for comparing averages, pie chart for busy vs idle breakdown."
)


def run_agent(user_message, conversation_history, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    conversation_history.append({"role": "user", "content": user_message})
    charts = []

    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=conversation_history,
        )

        if response.stop_reason == "tool_use":
            conversation_history.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    func = TOOL_FUNCTIONS.get(block.name)
                    result = func(**block.input) if block.input else func()

                    if block.name == "get_measurements" and result:
                        chart = line_chart(result, f"{block.input['measurement_type']} - {block.input['asset_name']}", result[0].get("unit", ""))
                        charts.append(chart)
                    elif block.name == "get_summary" and result:
                        chart = bar_chart(result, f"Summary - {block.input['asset_name']}")
                        charts.append(chart)
                    elif block.name == "get_status_counts" and result:
                        chart = pie_chart(result, "Asset Status Distribution")
                        charts.append(chart)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    })

            conversation_history.append({"role": "user", "content": tool_results})

        else:
            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text
            conversation_history.append({"role": "assistant", "content": response.content})
            return {"text": text, "charts": charts}


