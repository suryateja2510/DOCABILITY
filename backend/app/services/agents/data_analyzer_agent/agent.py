import os
from pathlib import Path
from typing import Optional, Dict

from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    FilePurpose,
    CodeInterpreterTool,
    ListSortOrder,
    MessageRole,
)
from app.utils.constants import DEVELOPED_AGENT_PROJECT_ENDPOINT, MODEL_DEPLOYMENT_NAME


def run_data_analyzer_agent(user_query: str, thread_id: Optional[str] = None) -> Dict:
    try:
        project_endpoint = os.getenv(DEVELOPED_AGENT_PROJECT_ENDPOINT)
        model_deployment = os.getenv(MODEL_DEPLOYMENT_NAME)

        if not project_endpoint or not model_deployment:
            return {
                "error": "Missing environment configuration. Please check .env settings."
            }

        file_path = (Path(__file__).parent / "data.txt").resolve()
        if not file_path.exists():
            return {"error": "Data file not found. Please upload a valid file."}

        agent_instructions = (
            "You are an AI agent that analyzes the data in the file that has been uploaded. "
            "Use Python to calculate statistical metrics as necessary."
        )
        agent_name = "data-analyzer-agent"

        agent_client = AgentsClient(
            endpoint=project_endpoint,
            credential=DefaultAzureCredential(
                exclude_environment_credential=True,
                exclude_managed_identity_credential=True,
            ),
        )

        with agent_client:
            if not thread_id:
                # Upload file and create agent
                file = agent_client.files.upload_and_poll(
                    file_path=file_path, purpose=FilePurpose.AGENTS
                )
                code_interpreter = CodeInterpreterTool(file_ids=[file.id])
                agent = agent_client.create_agent(
                    model=model_deployment,
                    name=agent_name,
                    instructions=agent_instructions,
                    tools=code_interpreter.definitions,
                    tool_resources=code_interpreter.resources,
                )
                thread = agent_client.threads.create()
            else:
                agents = list(agent_client.list_agents())
                agent = next((a for a in agents if a.name == agent_name), None)
                if not agent:
                    return {"error": "Agent not found"}
                thread = agent_client.threads.get(thread_id)

            # Add user message
            agent_client.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_query,
            )

            # Run the agent
            run = agent_client.runs.create_and_process(
                thread_id=thread.id, agent_id=agent.id
            )

            if run.status == "failed":
                return {
                    "thread_id": thread.id,
                    "error": "Run failed",
                    "details": run.last_error,
                }

            # Retrieve messages
            messages = agent_client.messages.list(
                thread_id=thread.id, order=ListSortOrder.ASCENDING
            )

            for message in reversed(list(messages)):
                if message.role == MessageRole.AGENT and message.text_messages:
                    return {
                        "thread_id": thread.id,
                        "role": message.role,
                        "text": message.text_messages[-1].text.value,
                    }

            return {"thread_id": thread.id, "error": "No agent response found"}

    except Exception as e:
        return {
            "error": str(e),
            "message": "An error occurred while processing the request.",
        }
