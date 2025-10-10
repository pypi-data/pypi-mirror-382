from google.adk.agents import Agent
from src.material_ai.oauth import oauth_user_details_context


def say_hello():
    return {"description": "Hi, what can I do for you today?"}


def who_am_i():
    user_details = oauth_user_details_context.get()
    return user_details


# Define the agent itself, giving it a name and description.
# The agent will automatically use the tools you provide in the list.
root_agent = Agent(
    name="greeting_agent",
    model="gemini-2.0-flash",
    description="An agent that can greet users.",
    instruction="""
    Use say_hello tool to greet user, If user asks about himself use who_am_i tool
    """,
    tools=[say_hello, who_am_i],
)
