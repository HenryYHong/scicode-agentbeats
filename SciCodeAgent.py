"""Green agent adapted to evaluate white agents on SciCode problems."""

import os
import sys
import json
import time
import tempfile
import shutil
import subprocess
import textwrap
from typing import Tuple, Optional
import dotenv

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, SendMessageSuccessResponse, Message
from a2a.utils import new_agent_text_message, get_text_parts

from src.my_util import parse_tags, my_a2a

try: 
    import scicode  # type: ignore
except ImportError:
    scicode = None

from dataclasses import dataclass

dotenv.load_dotenv()

@dataclass
class SolveResultMinimal:
    reward: float
    info: dict
    total_cost: float = 0.0

def load_scicode_problem(problem_id: str, scicode_root: Optional[str] = None) :
    """
    Load SciCode problem text and tests. This function will attempt to use the scicode package; if not available, it will try to read from disk. 
    Returns: dict with keys: 'prompt', 'tests' (list of test strigns), 'meta'
    """

    #TODO Fix the next section. You should replace this with actual scicode functions.

    if scicode is not None:
        # NOTE: adjust to the actual API if scicode exposes a loader function.
        # For many benchmarks there's a dataset loader; here we try a common pattern.
        try:
            # Try an API on the package (may vary by version)
            if hasattr(scicode, "load_problem"):
                return scicode.load_problem(problem_id)
            # fallback: attempt dataset access
            if hasattr(scicode, "dataset") and hasattr(scicode.dataset, "get_problem"):
                return scicode.dataset.get_problem(problem_id)
        except Exception:
            pass

    # Fallback: naive file read from local repo layout (user must clone scicode repo)
    repo_root = scicode_root or os.getenv("SCICODE_ROOT", "SciCode")
    # Try to load from SciCode data format
    # SciCode problems are typically stored in HDF5 format, but for simplicity
    # we'll try to find a JSON representation or use inspect_ai format
    from pathlib import Path
    
    # Try multiple possible locations
    possible_paths = [
        os.path.join(repo_root, "eval", "data", f"{problem_id}.json"),
        os.path.join(repo_root, "eval", "data", "test_data.h5"),
        os.path.join(repo_root, "data", "problems", f"{problem_id}.json"),
    ]
    
    # For now, we'll use a simplified approach
    # In a full implementation, you'd load from HDF5 using scicode.parse.parse
    try:
        # Try to use scicode package if available
        if scicode is not None:
            # This would need the actual scicode API
            pass
    except Exception:
        pass
    
    # Fallback: try to find JSON file
    problem_file = None
    for path in possible_paths:
        if os.path.exists(path) and path.endswith(".json"):
            problem_file = path
            break
    
    if problem_file and os.path.exists(problem_file):
        with open(problem_file, "r", encoding="utf-8") as f:
            prob = json.load(f)
        return {
            "prompt": prob.get("prompt") or prob.get("statement") or prob.get("description"),
            "tests": prob.get("tests", []),
            "meta": prob.get("meta", {}),
        }
    else:
        # For demo purposes, create a minimal structure
        # In production, you'd load from the actual SciCode HDF5 format
        return {
            "prompt": f"SciCode problem {problem_id}",
            "tests": [],
            "meta": {"problem_id": problem_id},
        }

def run_tests_against_code(code_str: str, tests: list[str], timeout: int = 30):
    """
    Run the given 'code_str' against the SciCode 'tests'.
    Returns (pass_bool, info_dict)
    
    Args:
        code_str: Python code to test
        tests: List of test code strings to execute
        timeout: Timeout in seconds for test execution
        
    Returns:
        Tuple of (passed: bool, info: dict) where info contains execution details
    """
    # Create temporary directory for test execution
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write the code to a temporary file
        code_file = os.path.join(tmpdir, "solution.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code_str)
            # Add test execution code
            f.write("\n\n# Test execution\n")
            f.write("if __name__ == '__main__':\n")
            f.write("    import sys\n")
            f.write("    passed_count = 0\n")
            f.write("    failed_count = 0\n")
            
            # For each test, execute it
            for i, test in enumerate(tests):
                f.write(f"    # Test {i+1}\n")
                f.write(f"    try:\n")
                f.write(f"        exec({repr(test)})\n")
                f.write(f"        passed_count += 1\n")
                f.write(f"        print(f'Test {i+1} passed')\n")
                f.write(f"    except Exception as e:\n")
                f.write(f"        failed_count += 1\n")
                f.write(f"        print(f'Test {i+1} failed: {{e}}', file=sys.stderr)\n")
            
            f.write("    if failed_count > 0:\n")
            f.write("        print(f'Total: {{passed_count}} passed, {{failed_count}} failed', file=sys.stderr)\n")
            f.write("        sys.exit(1)\n")
            f.write("    else:\n")
            f.write("        print(f'All {{passed_count}} tests passed')\n")
        
        # Run the test
        try:
            result = subprocess.run(
                [sys.executable, code_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir
            )
            
            passed = result.returncode == 0
            info = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "passed": passed
            }
            return passed, info
            
        except subprocess.TimeoutExpired:
            return False, {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Test execution timed out after {timeout} seconds",
                "passed": False,
                "timeout": True
            }
        except Exception as e:
            return False, {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Error running tests: {str(e)}",
                "passed": False,
                "error": str(e)
            }

async def ask_scicode_to_solve(white_agent_url: str, problem_id: str, max_num_steps: int = 3):
    """
    Orchestrate sending SciCode problem to the white agent and evaluate the returned code.
    Multi-turn support: we allow a small number of clarification iterations (white agent -> green agent -> white agent).
    """
    total_cost = 0.0
    # Load problem
    problem = load_scicode_problem(problem_id)
    prompt = problem["prompt"]
    tests = problem["tests"]

    # Prepare initial message to the white agent
    # instruct them to reply with code inside <code>...</code> or a JSON tag
    task_description = f"""
SciCode problem (id={problem_id}):

{prompt}

Please reply with the code that solves this problem.
Wrap the code inside <code>...</code> tags, or reply JSON: <json>{{"code": "..."}}</json>.
Do NOT include extraneous commentary inside the tags.

We will run your code against SciCode testcases and report pass/fail.
    """
    next_message = task_description
    context_id = None
    last_eval_info = {}
    final_pass = False

    for turn in range(max_num_steps):
        print(f"Green -> White (turn {turn+1}) context_id={context_id}... sending prompt")
        white_agent_response = await my_a2a.send_message(white_agent_url, next_message, context_id=context_id)
        res_root = white_agent_response.root
        assert isinstance(res_root, SendMessageSuccessResponse)
        res_result = res_root.result
        assert isinstance(res_result, Message)
        if context_id is None:
            context_id = res_result.context_id
        else:
            assert context_id == res_result.context_id

        text_parts = get_text_parts(res_result.parts)
        assert len(text_parts) >= 1
        white_text = "\n".join(text_parts)
        print("White replied (raw):\n", white_text)

        # parse code out of the white agent reply
        tags = parse_tags(white_text)
        code_candidate = None
        # Prefer JSON with "code", then <code> tag, then raw body
        if "json" in tags:
            try:
                j = json.loads(tags["json"])
                code_candidate = j.get("code") or j.get("submission") or j.get("solution")
            except Exception:
                pass
        if code_candidate is None and "code" in tags:
            code_candidate = tags["code"]
        if code_candidate is None:
            # fallback: use the entire message body as code (risky)
            code_candidate = white_text

        # Run tests
        passed, info = run_tests_against_code(code_candidate, tests, timeout=30)
        last_eval_info = info
        final_pass = passed

        # If it passed, end early
        if passed:
            break

        # Otherwise, give the white agent test failures and let it attempt to repair
        next_message = f"""Tool-run result (tests failed):
{info['stderr']}

Test runner stdout:
{info['stdout']}

Please produce a revised submission (again wrap code in <code>...</code> or <json> tags)."""
        # continue next turn

    # reward = 1 if pass else 0
    reward = 1.0 if final_pass else 0.0
    return SolveResultMinimal(reward=reward, info={"eval_info": last_eval_info, "problem_id": problem_id}, total_cost=total_cost)


# Note: The user must provide scicode_problem_id and white_agent_url via tags in the input message. 
class TauScicodeGreenExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        print("Scicode green agent: Received task.")
        user_input = context.get_user_input()
        tags = parse_tags(user_input)
        # Expect the user to include scicode problem id and white agent url
        # Also support task_index for optional task selection
        white_agent_url = tags.get("white_agent_url") or tags.get("blue_agent") or tags.get("blue_agent_url")
        scicode_problem_id = tags.get("scicode_problem_id") or tags.get("problem_id") or tags.get("task_index")
        
        if white_agent_url is None:
            await event_queue.enqueue_event(
                new_agent_text_message("Missing required tag: white_agent_url (or blue_agent_url)")
            )
            return
        
        # task_index is optional - use problem_id if not provided
        if scicode_problem_id is None:
            await event_queue.enqueue_event(
                new_agent_text_message("Missing required tag: scicode_problem_id, problem_id, or task_index")
            )
            return

        print("Starting evaluation for SciCode problem:", scicode_problem_id)
        t0 = time.time()
        res = await ask_scicode_to_solve(white_agent_url, scicode_problem_id)
        time_used = time.time() - t0
        metrics = {"time_used": time_used, "success": res.reward == 1.0}
        result_emoji = "✅" if res.reward == 1.0 else "❌"
        print("Evaluation complete:", metrics)
        await event_queue.enqueue_event(
            new_agent_text_message(f"Finished. White agent success: {result_emoji}\nMetrics: {metrics}\nDetails: {json.dumps(res.info, indent=2)}")
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError


def load_agent_card_toml(agent_name):
    """Load agent card from TOML file."""
    current_dir = os.path.dirname(__file__)
    agent_card_path = os.path.join(current_dir, f"{agent_name}.toml")
    try:
        import tomllib
        with open(agent_card_path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"Agent card file not found: {agent_card_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to load agent card: {e}")


def start_scicode_green(agent_name="tau_green_scicode", host="localhost", port=9001):
    """Start the SciCode green agent server."""
    print("Starting SciCode green agent...")
    agent_card_dict = load_agent_card_toml(agent_name)
    url = f"http://{host}:{port}"
    agent_card_dict["url"] = url  # complete all required card fields

    # Create request handler and application
    request_handler = DefaultRequestHandler(
        agent_executor=TauScicodeGreenExecutor(), 
        task_store=InMemoryTaskStore()
    )

    app = A2AStarletteApplication(
        agent_card=AgentCard(**agent_card_dict), 
        http_handler=request_handler
    )
    
    # Add launcher endpoint for AgentBeats compatibility
    starlette_app = app.build()
    
    @starlette_app.route("/launcher", methods=["GET", "POST"])
    async def launcher_endpoint(request):
        from starlette.responses import JSONResponse
        # Get capabilities - ensure "reset" is included for launcher
        capabilities = list(agent_card_dict.get("capabilities", {}).keys()) if isinstance(agent_card_dict.get("capabilities"), dict) else []
        if "reset" not in capabilities:
            capabilities.append("reset")
        return JSONResponse({
            "status": "ready",
            "launcher": True,
            "agent_type": "green",
            "name": agent_card_dict.get("name", "SciCode Green Agent") + " Launcher",
            "capabilities": capabilities,
            "version": agent_card_dict.get("version", "1.0.0")
        })
    
    @starlette_app.route("/status", methods=["GET"])
    async def status_endpoint(request):
        from starlette.responses import JSONResponse
        return JSONResponse({
            "status": "online",
            "agent_type": "green",
            "capabilities": list(agent_card_dict.get("capabilities", {}).keys()) if isinstance(agent_card_dict.get("capabilities"), dict) else []
        })
    
    print(f"Starting SciCode Green Agent on {url}")
    uvicorn.run(starlette_app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SciCode Green Agent for AgentBeats")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=9001, help="Port to bind to")
    parser.add_argument("--agent-name", type=str, default="tau_green_scicode", help="Agent name (for card file)")
    
    args = parser.parse_args()
    start_scicode_green(agent_name=args.agent_name, host=args.host, port=args.port)

