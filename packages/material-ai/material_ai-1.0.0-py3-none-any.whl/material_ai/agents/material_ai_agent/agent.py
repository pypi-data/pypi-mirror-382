import csv
import io

# Assuming adk.agents has these components
from google.adk.agents import Agent
from google.genai.types import Part, Blob


def create_csv_string(tool_context=None) -> str:
    """
    Creates sample CSV data and returns it as a string.
    """
    if tool_context is None:
        return {
            "status": "error",
            "message": "Tool context is missing, cannot save artifact.",
        }
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header and data rows
    writer.writerow(["ID", "Name", "Role"])
    writer.writerow(["1", "John Doe", "Engineer"])
    writer.writerow(["2", "Jane Smith", "Designer"])

    csv_content = output.getvalue()
    content_bytes = csv_content.encode("utf-8")
    output.close()
    artifact_part = Part(inline_data=Blob(data=content_bytes, mime_type="text/csv"))
    filename = "my-csv.csv"
    version = tool_context.save_artifact(filename=filename, artifact=artifact_part)
    return {
        "status": "success",
        "message": f"File '{filename}' (version {version}) has been created and is now available for download.",
    }


another_agent = Agent(
    name="sub_agent_1",
    model="gemini-2.0-flash",
    description="You should may be talk about current affairs",
    instruction="""
    Answers questions related to current affairs, call sub_agent_2
    """,
)

another_agent_2 = Agent(
    name="sub_agent_2",
    model="gemini-2.0-flash",
    description="You should greet user happy birthday",
    instruction="""
    Greet user with happy birthday
    """,
)

csv_agent = Agent(
    name="csv_creator_agent",
    model="gemini-2.0-flash",
    description="An agent that creates a CSV file when greeted.",
    instruction="When the user says 'HI', call the `create_csv` tool to generate and send a CSV file back.",
    tools=[create_csv_string],
)

root_agent = Agent(
    name="material_ai_agent",
    model="gemini-2.0-flash",
    description="You are a agnet used to build React Material UI Application",
    instruction="""
    Say Hello and pass on to sub agent called "sub_agent_1" when  user questions about current affairs
    When user says hi pass o to agent called "csv_agent"
    """,
    sub_agents=[another_agent, another_agent_2, csv_agent],
)
