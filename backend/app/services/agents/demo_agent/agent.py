# services/demo_agent.py

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder
from app.utils.constants import DEMO_AGENT_ENDPOINT, DEMO_AGENT_ID

# Reuse credential and client globally for performance
credential = DefaultAzureCredential()
project = AIProjectClient(
    credential=credential, endpoint=os.getenv(DEMO_AGENT_ENDPOINT)
)

def run_demo_agent(user_query: str, thread_id: str = None) -> dict:
    try:
        # Create or get thread
        if not thread_id:
            thread = project.agents.threads.create()
        else:
            thread = project.agents.threads.get(thread_id)

        # Add user message
        project.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_query,
        )

        # Run the agent
        run = project.agents.runs.create_and_process(
            thread_id=thread.id, agent_id=os.getenv(DEMO_AGENT_ID)
        )

        if run.status == "failed":
            return {
                "thread_id": thread.id,
                "error": "Run failed",
                "details": run.error,
            }

        # Get messages (all)
        messages = project.agents.messages.list(
            thread_id=thread.id, order=ListSortOrder.ASCENDING
        )

        # Return latest assistant message
        for message in reversed(list(messages)):
            if message.role == "assistant" and message.text_messages:
                return {
                    "thread_id": thread.id,
                    "role": message.role,
                    "text": message.text_messages[-1].text.value,
                }

        return {"thread_id": thread.id, "error": "No assistant response found"}

    except Exception as e:
        return {
            "error": str(e),
            "message": "An error occurred while processing the request.",
        }
