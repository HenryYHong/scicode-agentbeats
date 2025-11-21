"""White agent implementation - the target agent being tested."""

import uvicorn
import dotenv
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.utils import new_agent_text_message

try:
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("Warning: litellm not available. White agent will use placeholder responses.")

dotenv.load_dotenv()


def prepare_white_agent_card(url):
    """Prepare the agent card for the white agent."""
    skill = AgentSkill(
        id="task_fulfillment",
        name="Task Fulfillment",
        description="Handles user requests and completes tasks",
        tags=["general"],
        examples=[],
    )
    card = AgentCard(
        name="general_white_agent",
        description="General white agent for SciCode evaluation",
        url=url,
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(),
        skills=[skill],
    )
    return card


class GeneralWhiteAgentExecutor(AgentExecutor):
    """White agent executor that responds to SciCode problems."""
    
    def __init__(self):
        self.ctx_id_to_messages = {}

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # Parse the task
        user_input = context.get_user_input()
        
        # Maintain conversation history per context
        if context.context_id not in self.ctx_id_to_messages:
            self.ctx_id_to_messages[context.context_id] = []
        messages = self.ctx_id_to_messages[context.context_id]
        
        messages.append({
            "role": "user",
            "content": user_input,
        })
        
        # Generate response using LLM
        if LITELLM_AVAILABLE:
            try:
                response = completion(
                    messages=messages,
                    model="openai/gpt-4o",
                    custom_llm_provider="openai",
                    temperature=0.0,
                )
                next_message = response.choices[0].message.model_dump()  # type: ignore
                response_content = next_message["content"]
            except Exception as e:
                print(f"Error calling litellm: {e}")
                response_content = f"""<json>{{
    "code": "# Error generating code: {str(e)}"
}}</json>"""
        else:
            # Fallback: simple response for testing
            response_content = """<json>{
    "code": "# Placeholder code response - install litellm for full functionality"
}</json>"""
        
        # Add assistant message to history
        messages.append({
            "role": "assistant",
            "content": response_content,
        })
        
        # Send response
        await event_queue.enqueue_event(
            new_agent_text_message(
                response_content, 
                context_id=context.context_id
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError


def start_white_agent(agent_name="general_white_agent", host="localhost", port=9002):
    """Start the white agent server."""
    print("Starting white agent...")
    url = f"http://{host}:{port}"
    card = prepare_white_agent_card(url)

    request_handler = DefaultRequestHandler(
        agent_executor=GeneralWhiteAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    app = A2AStarletteApplication(
        agent_card=card,
        http_handler=request_handler,
    )
    
    # Add status endpoint for launcher compatibility
    starlette_app = app.build()
    
    @starlette_app.route("/status", methods=["GET"])
    async def status_endpoint(request):
        from starlette.responses import JSONResponse
        return JSONResponse({
            "status": "online",
            "agent_type": "white"
        })
    
    print(f"Starting White Agent on {url}")
    uvicorn.run(starlette_app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="White Agent for SciCode Evaluation")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=9002, help="Port to bind to")
    parser.add_argument("--agent-name", type=str, default="general_white_agent", help="Agent name")
    
    args = parser.parse_args()
    start_white_agent(agent_name=args.agent_name, host=args.host, port=args.port)


