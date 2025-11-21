# Key Files to Review for SciCode Green Agent

## 🔴 **Critical Files (Must Review)**

### 1. **`scicode_green_agent.py`** ⭐⭐⭐
**Main green agent implementation**
- Contains the core agent logic
- `SciCodeGreenAgentExecutor` - handles incoming assessment requests
- `ask_agent_to_solve()` - orchestrates evaluation with white agent
- `load_scicode_problem()` - loads problems from SciCode dataset
- `run_tests_against_code()` - executes code against test cases
- `start_green_agent()` - server startup function

**Key sections to review:**
- Lines 34-108: Problem loading logic
- Lines 109-186: Test execution logic
- Lines 188-271: Main evaluation orchestration
- Lines 297-343: Agent executor (handles A2A requests)
- Lines 346-376: Server startup and status endpoint

### 2. **`tau_green_scicode.toml`** ⭐⭐⭐
**Agent card configuration**
- Defines agent metadata for AgentBeats
- Contains skill descriptions and examples
- Used for registration on AgentBeats platform

**Key sections:**
- Agent name, description, version
- Capabilities (streaming, etc.)
- Skills definition with examples

### 3. **`src/my_util.py`** ⭐⭐⭐
**A2A client and utilities**
- `A2AClient` class - sends messages to other agents
- Uses official A2A SDK client
- `parse_tags()` - extracts tags from messages
- `wait_agent_ready()` - checks if agent is online

**Key sections:**
- Lines 33-120: A2AClient implementation
- Lines 39-120: `send_message()` method (uses A2A SDK)
- Lines 11-30: Tag parsing logic

## 🟡 **Important Supporting Files**

### 4. **`launcher_scicode_new.py`** ⭐⭐
**Launcher script for testing**
- Starts both green and white agents
- Sends evaluation requests
- Useful for local testing

**Key sections:**
- Lines 26-92: Main launcher function
- Lines 57-79: Task sending logic

### 5. **`white_agent_scicode.py`** ⭐⭐
**White agent (target being tested)**
- Example white agent implementation
- Uses LiteLLM for code generation
- Responds to SciCode problems

**Key sections:**
- Lines 45-102: White agent executor
- Lines 105-133: Server startup

## 🟢 **Reference/Documentation Files**

### 6. **`SCICODE_GREEN_AGENT_IMPLEMENTATION.md`** ⭐
**Implementation documentation**
- Explains the architecture
- Comparison with tau-bench pattern
- Usage instructions

### 7. **`AGENTBEATS_REGISTRATION_STEPS.md`** ⭐
**Registration guide**
- Step-by-step registration instructions
- ngrok setup
- Troubleshooting tips

### 8. **`requirements.txt`** ⭐
**Dependencies**
- All required Python packages
- Version specifications

## 📋 **Review Checklist**

When reviewing the code, check:

### `scicode_green_agent.py`:
- [ ] Problem loading works with your SciCode dataset
- [ ] Test execution logic handles your test format
- [ ] Error handling for missing problems/tests
- [ ] Multi-turn conversation logic (if tests fail)
- [ ] Response formatting matches expected output

### `src/my_util.py`:
- [ ] A2A client properly formats requests
- [ ] Response parsing handles A2A SDK format
- [ ] Error handling for network issues
- [ ] Tag parsing works with your message format

### `tau_green_scicode.toml`:
- [ ] Agent name and description are correct
- [ ] Skills match your agent's capabilities
- [ ] Examples show correct usage format

## 🔍 **Quick Review Priority**

1. **Start with**: `scicode_green_agent.py` (main logic)
2. **Then check**: `src/my_util.py` (A2A communication)
3. **Verify**: `tau_green_scicode.toml` (configuration)
4. **Test with**: `launcher_scicode_new.py` (end-to-end)

## 🐛 **Common Issues to Watch For**

1. **Problem loading**: Make sure `load_scicode_problem()` works with your dataset format
2. **Test execution**: Verify `run_tests_against_code()` handles your test case format
3. **A2A protocol**: Ensure message format matches A2A spec
4. **Error handling**: Check that failures are handled gracefully
5. **Path handling**: Verify file paths work on your system

