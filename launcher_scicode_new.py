"""Launcher script for SciCode evaluation - follows tau-bench pattern."""

import multiprocessing
import json
import asyncio
from scicode_green_agent import start_green_agent
from src.my_util import my_a2a, wait_agent_ready


# Import white agent
try:
    from white_agent_scicode import start_white_agent
except ImportError:
    try:
        from white_agent import start_white_agent
    except ImportError:
        # Fallback - create a simple white agent starter
        def start_white_agent(agent_name="general_white_agent", host="localhost", port=9002):
            """Placeholder white agent starter."""
            print(f"White agent placeholder: {agent_name} at {host}:{port}")
            print("Note: You need to implement a white agent or use an existing one")
            import time
            time.sleep(3600)  # Keep running


async def launch_scicode_evaluation(problem_id="1", split="validation"):
    """Launch SciCode evaluation with green and white agents."""
    # Start green agent
    print("Launching SciCode green agent...")
    green_address = ("localhost", 9001)
    green_url = f"http://{green_address[0]}:{green_address[1]}"
    p_green = multiprocessing.Process(
        target=start_green_agent, 
        args=("tau_green_scicode", green_address[0], green_address[1])
    )
    p_green.start()
    
    # Wait for green agent to be ready
    assert await wait_agent_ready(green_url), "Green agent not ready in time"
    print("Green agent is ready.")
    
    # Start white agent
    print("Launching white agent...")
    white_address = ("localhost", 9002)
    white_url = f"http://{white_address[0]}:{white_address[1]}"
    p_white = multiprocessing.Process(
        target=start_white_agent, 
        args=("general_white_agent", white_address[0], white_address[1])
    )
    p_white.start()
    
    # Wait for white agent to be ready
    assert await wait_agent_ready(white_url), "White agent not ready in time"
    print("White agent is ready.")
    
    # Send the task description to green agent
    print("Sending task description to green agent...")
    task_text = f"""
Your task is to evaluate a white agent on SciCode problem. The agent is located at:

<white_agent_url>
http://{white_address[0]}:{white_address[1]}/
</white_agent_url>

You should use the following problem configuration:

<scicode_problem_id>
{problem_id}
</scicode_problem_id>

<split>
{split}
</split>
    """
    print("Task description:")
    print(task_text)
    print("Sending...")
    
    response = await my_a2a.send_message(green_url, task_text)
    print("Response from green agent:")
    print(f"Response type: {type(response)}")
    if hasattr(response, 'root') and hasattr(response.root, 'result'):
        if hasattr(response.root.result, 'parts'):
            from a2a.utils import get_text_parts
            text_parts = get_text_parts(response.root.result.parts)
            print("\n".join(text_parts))
        else:
            print(response.root.result)
    else:
        print(response)
    
    print("Evaluation complete. Terminating agents...")
    p_green.terminate()
    p_green.join(timeout=5)
    p_white.terminate()
    p_white.join(timeout=5)
    print("Agents terminated.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SciCode Evaluation Launcher")
    parser.add_argument("--problem-id", type=str, default="1", help="SciCode problem ID")
    parser.add_argument("--split", type=str, default="validation", help="Dataset split (validation/test)")
    
    args = parser.parse_args()
    asyncio.run(launch_scicode_evaluation(problem_id=args.problem_id, split=args.split))

