"""Green agent implementation - manages assessment and evaluation for SciCode."""

import uvicorn
import dotenv

# Handle tomllib for Python < 3.11
try:
    import tomllib
except ImportError:
    import tomli as tomllib
import json
import time
import os
import sys
import tempfile
import subprocess
from pathlib import Path
from typing import Optional

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, SendMessageSuccessResponse, Message
from a2a.utils import new_agent_text_message, get_text_parts

from src.my_util import parse_tags, my_a2a

dotenv.load_dotenv()


def load_agent_card_toml(agent_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    agent_card_path = os.path.join(current_dir, f"{agent_name}.toml")
    with open(agent_card_path, "rb") as f:
        return tomllib.load(f)


def load_scicode_problem(problem_id: str, split: str = "validation"):
    """
    Load SciCode problem from the dataset.
    Returns dict with keys: 'problem_id', 'sub_steps', etc.
    """
    try:
        # Try to import and use SciCode dataset loader
        sys.path.insert(0, str(Path(__file__).parent / "SciCode" / "src"))
        from scicode.parse.parse import read_from_hf_dataset
        
        dataset = read_from_hf_dataset(split)
        problems = list(dataset)
        
        # Find problem by ID
        for problem in problems:
            if str(problem.get("problem_id")) == str(problem_id):
                return problem
        
        # If not found, try to get by index
        try:
            idx = int(problem_id)
            if 0 <= idx < len(problems):
                return problems[idx]
        except ValueError:
            pass
        
        raise ValueError(f"Problem {problem_id} not found in {split} split")
        
    except Exception as e:
        print(f"Warning: Failed to load from SciCode dataset: {e}")
        # Fallback: return a minimal structure
        return {
            "problem_id": problem_id,
            "sub_steps": [{
                "step_description_prompt": f"SciCode problem {problem_id}",
                "test_cases": [],
                "function_header": "def solve():",
                "return_line": "return None"
            }]
        }


def run_tests_against_code(code_str: str, test_cases: list, step_id: str, h5py_file: Optional[str] = None, timeout: int = 30):
    """
    Run the given code against SciCode test cases.
    Returns (pass_bool, info_dict)
    """
    # Create temporary directory for test execution
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write the code to a temporary file
        code_file = os.path.join(tmpdir, "solution.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code_str)
            f.write("\n\n")
            
            # Add test execution code
            if h5py_file and os.path.exists(h5py_file):
                f.write("from scicode.parse.parse import process_hdf5_to_tuple\n")
                f.write(f"targets = process_hdf5_to_tuple('{step_id}', {len(test_cases)}, '{h5py_file}')\n")
                for i, test_case in enumerate(test_cases):
                    f.write(f"target = targets[{i}]\n")
                    f.write(f"{test_case}\n")
            else:
                # Fallback: execute test cases directly
                f.write("if __name__ == '__main__':\n")
                f.write("    import sys\n")
                f.write("    passed_count = 0\n")
                f.write("    failed_count = 0\n")
                for i, test_case in enumerate(test_cases):
                    f.write(f"    # Test {i+1}\n")
                    f.write(f"    try:\n")
                    f.write(f"        {test_case}\n")
                    f.write(f"        passed_count += 1\n")
                    f.write(f"        print(f'Test {i+1} passed')\n")
                    f.write(f"    except Exception as e:\n")
                    f.write(f"        failed_count += 1\n")
                    f.write(f"        print(f'Test {i+1} failed: {{e}}', file=sys.stderr)\n")
                f.write("    if failed_count > 0:\n")
                f.write("        sys.exit(1)\n")
        
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


async def ask_agent_to_solve(white_agent_url, problem_id, split="validation", max_num_steps=10):
    """
    Orchestrate sending SciCode problem to the white agent and evaluate the returned code.
    Similar to tau-bench's ask_agent_to_solve but adapted for SciCode.
    """
    total_cost = 0.0
    
    # Load problem
    problem = load_scicode_problem(problem_id, split=split)
    sub_steps = problem.get("sub_steps", [])
    
    if not sub_steps:
        return {
            "reward": 0.0,
            "info": {"error": "No sub_steps found in problem"},
            "total_cost": total_cost
        }
    
    # For simplicity, we'll test the first sub-step
    # In a full implementation, you'd iterate through all sub-steps
    first_step = sub_steps[0]
    step_id = first_step.get("step_number", f"{problem_id}_0")
    step_prompt = first_step.get("step_description_prompt", "")
    function_header = first_step.get("function_header", "")
    return_line = first_step.get("return_line", "")
    test_cases = first_step.get("test_cases", [])
    
    # Prepare initial message to the white agent
    task_description = f"""
SciCode problem (id={problem_id}, step={step_id}):

{step_prompt}

Function signature:
{function_header}

{return_line}

Please reply with the Python code that solves this problem.
Wrap the code inside <code>...</code> tags, or reply JSON: <json>{{"code": "..."}}</json>.
Do NOT include extraneous commentary inside the tags.

We will run your code against SciCode testcases and report pass/fail.
    """
    
    next_message = task_description
    context_id = None
    last_eval_info = {}
    final_pass = False
    
    for turn in range(max_num_steps):
        print(
            f"@@@ Green agent: Sending message to white agent{'ctx_id=' + str(context_id) if context_id else ''}... -->\n{next_message[:200]}..."
        )
        
        white_agent_response = await my_a2a.send_message(
            white_agent_url, next_message, context_id=context_id
        )
        
        res_root = white_agent_response.root
        assert isinstance(res_root, SendMessageSuccessResponse)
        res_result = res_root.result
        assert isinstance(res_result, Message)
        
        if context_id is None:
            context_id = res_result.context_id
        else:
            assert context_id == res_result.context_id, (
                "Context ID should remain the same in a conversation"
            )
        
        text_parts = get_text_parts(res_result.parts)
        assert len(text_parts) >= 1, "Expecting at least one text part from the white agent"
        
        white_text = "\n".join(text_parts)
        print(f"@@@ White agent response:\n{white_text[:500]}...")
        
        # Parse code out of the white agent reply
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
            # Fallback: use the entire message body as code (risky)
            code_candidate = white_text
        
        # Find h5py file for test execution
        h5py_file = None
        scicode_root = Path(__file__).parent / "SciCode"
        possible_h5py_paths = [
            scicode_root / "eval" / "data" / "test_data.h5",
            scicode_root / "data" / "test_data.h5",
        ]
        for path in possible_h5py_paths:
            if path.exists():
                h5py_file = str(path)
                break
        
        # Run tests
        passed, info = run_tests_against_code(
            code_candidate, test_cases, step_id, h5py_file=h5py_file, timeout=30
        )
        last_eval_info = info
        final_pass = passed
        
        # If it passed, end early
        if passed:
            break
        
        # Otherwise, give the white agent test failures and let it attempt to repair
        next_message = f"""Test run result (tests failed):
{info.get('stderr', '')}

Test runner stdout:
{info.get('stdout', '')}

Please produce a revised submission (again wrap code in <code>...</code> or <json> tags)."""
    
    reward = 1.0 if final_pass else 0.0
    return {
        "reward": reward,
        "info": {
            "eval_info": last_eval_info,
            "problem_id": problem_id,
            "step_id": step_id
        },
        "total_cost": total_cost
    }


class SciCodeGreenAgentExecutor(AgentExecutor):
    def __init__(self):
        pass

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # parse the task
        print("Green agent: Received a task, parsing...")
        user_input = context.get_user_input()
        tags = parse_tags(user_input)
        
        white_agent_url = tags.get("white_agent_url")
        problem_id = tags.get("scicode_problem_id") or tags.get("problem_id")
        split = tags.get("split", "validation")
        
        if not white_agent_url:
            await event_queue.enqueue_event(
                new_agent_text_message("Missing required tag: white_agent_url")
            )
            return
        
        if not problem_id:
            await event_queue.enqueue_event(
                new_agent_text_message("Missing required tag: scicode_problem_id or problem_id")
            )
            return
        
        print(f"Green agent: Setting up evaluation for problem {problem_id}...")
        
        metrics = {}
        print("Green agent: Starting evaluation...")
        timestamp_started = time.time()
        
        res = await ask_agent_to_solve(white_agent_url, problem_id, split=split)
        
        metrics["time_used"] = time.time() - timestamp_started
        result_bool = metrics["success"] = res["reward"] == 1.0
        result_emoji = "✅" if result_bool else "❌"
        
        print("Green agent: Evaluation complete.")
        await event_queue.enqueue_event(
            new_agent_text_message(
                f"Finished. White agent success: {result_emoji}\nMetrics: {json.dumps(metrics, indent=2)}\nDetails: {json.dumps(res['info'], indent=2)}\n"
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError


def start_green_agent(agent_name="tau_green_scicode", host="localhost", port=9001):
    print("Starting green agent...")
    agent_card_dict = load_agent_card_toml(agent_name)
    url = f"http://{host}:{port}"
    agent_card_dict["url"] = url  # complete all required card fields
    
    request_handler = DefaultRequestHandler(
        agent_executor=SciCodeGreenAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    
    app = A2AStarletteApplication(
        agent_card=AgentCard(**agent_card_dict),
        http_handler=request_handler,
    )
    
    # Add status endpoint for launcher compatibility
    starlette_app = app.build()
    
    @starlette_app.route("/status", methods=["GET"])
    async def status_endpoint(request):
        from starlette.responses import JSONResponse
        return JSONResponse({
            "status": "online",
            "agent_type": "green",
            "name": agent_card_dict.get("name", "tau_green_scicode"),
            "capabilities": list(agent_card_dict.get("capabilities", {}).keys()) if isinstance(agent_card_dict.get("capabilities"), dict) else []
        })
    
    print(f"Starting SciCode Green Agent on {url}")
    uvicorn.run(starlette_app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SciCode Green Agent")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=9001, help="Port to bind to")
    parser.add_argument("--agent-name", type=str, default="tau_green_scicode", help="Agent name (for card file)")
    
    args = parser.parse_args()
    start_green_agent(agent_name=args.agent_name, host=args.host, port=args.port)

