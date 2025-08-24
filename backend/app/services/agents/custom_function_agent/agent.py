import os
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    FunctionTool,
    ToolSet,
    MessageRole,
)

from app.utils.constants import CUSTOM_FUNCTION_AGENT_ENDPOINT, MODEL_DEPLOYMENT_NAME
from app.services.agents.custom_function_agent.user_functions import user_functions


def run_custom_function_agent(user_query: str, thread_id: str = None) -> dict:
    try:
        load_dotenv()
        project_endpoint = os.getenv(CUSTOM_FUNCTION_AGENT_ENDPOINT)
        model_deployment = os.getenv(MODEL_DEPLOYMENT_NAME)

        agent_name = "custom-function-agent"
        agent_instructions = """You are a technical support agent.
            When a user has a technical issue, you get their email address and a description of the issue.
            Then you use those values to submit a support ticket using the function available to you.
            If a file is saved, tell the user the file name."""

        agent_client = AgentsClient(
            endpoint=project_endpoint,
            credential=DefaultAzureCredential(
                exclude_environment_credential=True,
                exclude_managed_identity_credential=True,
            ),
        )

        with agent_client:
            functions = FunctionTool(user_functions)
            toolset = ToolSet()
            toolset.add(functions)
            agent_client.enable_auto_function_calls(toolset)

            if not thread_id:
                agent = agent_client.create_agent(
                    model=model_deployment,
                    name=agent_name,
                    instructions=agent_instructions,
                    toolset=toolset,
                )
                thread = agent_client.threads.create()
            else:
                agents = list(agent_client.list_agents())
                agent = next((a for a in agents if a.name == agent_name), None)
                if not agent:
                    return {"error": "Agent not found"}
                thread = agent_client.threads.get(thread_id)

            agent_client.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_query,
            )

            run = agent_client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id,
            )

            if run.status == "failed":
                return {
                    "thread_id": thread.id,
                    "error": "Run failed",
                    "details": run.last_error,
                }

            last_msg = agent_client.messages.get_last_message_text_by_role(
                thread_id=thread.id,
                role=MessageRole.AGENT,
            )

            if last_msg:
                return {
                    "thread_id": thread.id,
                    "role": MessageRole.AGENT,
                    "text": last_msg.text.value,
                }

            return {"thread_id": thread.id, "error": "No agent response found"}
    except Exception as e:
        return {
            "error": str(e),
            "message": "An error occurred while processing the support agent request.",
        }
