# SciCode Green Agent Implementation

This document describes the implementation of a SciCode green agent following the tau-bench pattern from the AgentBeats blog post.

## Overview

The green agent (`scicode_green_agent.py`) manages assessment and evaluation of white agents on SciCode problems. It follows the same architectural pattern as the tau-bench green agent example, adapted for SciCode's scientific code generation tasks.

## Architecture

### Key Components

1. **`load_agent_card_toml(agent_name)`**: Loads the agent card configuration from TOML file
2. **`load_scicode_problem(problem_id, split)`**: Loads SciCode problems from the HuggingFace dataset
3. **`run_tests_against_code(code_str, test_cases, step_id, h5py_file, timeout)`**: Executes code against SciCode test cases
4. **`ask_agent_to_solve(white_agent_url, problem_id, split, max_num_steps)`**: Orchestrates the evaluation process
5. **`SciCodeGreenAgentExecutor`**: A2A agent executor that handles incoming assessment requests
6. **`start_green_agent(agent_name, host, port)`**: Starts the green agent server

## Comparison with Tau-Bench Pattern

### Similarities

- **Same structure**: Follows the exact code organization from tau-bench example
- **A2A protocol**: Uses A2A for agent communication
- **TOML configuration**: Uses TOML for agent card definition
- **Message-based interaction**: Communicates with white agent via text messages
- **Context management**: Maintains conversation context using `context_id`
- **Tag parsing**: Uses `<white_agent_url>`, `<scicode_problem_id>` tags for configuration

### Adaptations for SciCode

1. **Problem Loading**: 
   - Tau-bench: Uses `get_env()` to create environment instances
   - SciCode: Uses `read_from_hf_dataset()` to load problems from HuggingFace

2. **Task Description**:
   - Tau-bench: Provides tool information and environment wiki
   - SciCode: Provides step description, function header, and return line

3. **Evaluation**:
   - Tau-bench: Uses environment's `step()` method with actions
   - SciCode: Executes code against test cases using subprocess

4. **Response Format**:
   - Tau-bench: Expects JSON with `name` and `kwargs` for tool calls
   - SciCode: Expects code wrapped in `<code>...</code>` or JSON with `code` field

## File Structure

```
.
├── scicode_green_agent.py      # Main green agent implementation
├── tau_green_scicode.toml       # Agent card configuration
├── launcher_scicode_new.py      # Launcher script (optional)
└── white_agent_scicode.py       # White agent (target being tested)
```

## Usage

### Starting the Green Agent

```bash
python scicode_green_agent.py --host localhost --port 9001 --agent-name tau_green_scicode
```

### Using the Launcher

```bash
python launcher_scicode_new.py --problem-id 1 --split validation
```

### Direct A2A Message

Send a message to the green agent with the following format:

```
Your task is to evaluate a white agent on SciCode problem. The agent is located at:

<white_agent_url>
http://localhost:9002/
</white_agent_url>

You should use the following problem configuration:

<scicode_problem_id>
1
</scicode_problem_id>

<split>
validation
</split>
```

## Configuration

The agent card is defined in `tau_green_scicode.toml`:

```toml
name = "tau_green_scicode"
description = "The assessment hosting agent for SciCode."
version = "0.1.0"
defaultInputModes = ["text"]
defaultOutputModes = ["text"]

[capabilities]
streaming = false

[[skills]]
id = "host_assess_scicode"
name = "SciCode assessment hosting"
description = "Assess the code generation ability of an agent on SciCode problems."
tags = ["green agent", "assessment hosting", "scicode"]
```

## Evaluation Flow

1. **Receive Task**: Green agent receives assessment request with white agent URL and problem ID
2. **Load Problem**: Loads SciCode problem from dataset
3. **Send Task to White Agent**: Sends problem description to white agent
4. **Receive Code**: Parses code from white agent's response
5. **Run Tests**: Executes code against SciCode test cases
6. **Report Results**: Returns success/failure with metrics

## Multi-Turn Support

The implementation supports multiple turns:
- If code fails tests, the green agent sends test failure information back to white agent
- White agent can attempt to fix the code
- Process repeats up to `max_num_steps` (default: 10)

## Dependencies

- `a2a`: A2A protocol implementation
- `uvicorn`: ASGI server
- `tomllib`: TOML parsing (Python 3.11+)
- `datasets`: HuggingFace datasets (for SciCode dataset loading)
- `h5py`: For SciCode test data (optional)

## Notes

- The implementation currently evaluates the first sub-step of each problem
- Full multi-step evaluation can be added by iterating through all sub-steps
- Test execution uses subprocess with timeout protection
- H5PY file path is auto-detected from common locations

## Future Enhancements

1. **Multi-step evaluation**: Evaluate all sub-steps of a problem
2. **Parallel testing**: Run multiple problems in parallel
3. **MCP integration**: Use MCP server for tool delivery (Approach III from blog)
4. **Streaming support**: Add streaming for long-running evaluations
5. **Task-based responses**: Upgrade to task-generating agent for better progress tracking

