# Green Agent Files - Quick Reference

## 🔴 **Core Files (Essential)**

### 1. **`scicode_green_agent.py`** ⭐⭐⭐
**Main green agent implementation - THE MOST IMPORTANT FILE**

**What it does:**
- Implements the green agent server
- Handles A2A protocol requests
- Orchestrates evaluation with white agents
- Loads SciCode problems
- Executes tests against generated code

**Key Components:**
- `load_scicode_problem()` - Loads problems from SciCode dataset
- `run_tests_against_code()` - Executes code against test cases
- `ask_agent_to_solve()` - Main evaluation orchestration
- `SciCodeGreenAgentExecutor` - A2A executor class
- `start_green_agent()` - Server startup

**Lines to focus on:**
- 34-108: Problem loading
- 109-186: Test execution
- 188-271: Evaluation orchestration
- 297-343: Agent executor (handles requests)
- 346-376: Server setup

---

### 2. **`tau_green_scicode.toml`** ⭐⭐⭐
**Agent card configuration - Required for registration**

**What it does:**
- Defines agent metadata
- Specifies capabilities and skills
- Contains examples for AgentBeats
- Used during registration

**Key sections:**
- Agent name, description, version
- Capabilities (streaming, etc.)
- Skills with examples

**Why it matters:**
- AgentBeats reads this to understand your agent
- Must be present for registration
- Examples show how to use the agent

---

### 3. **`src/my_util.py`** ⭐⭐⭐
**A2A communication utilities - Critical for agent-to-agent communication**

**What it does:**
- Provides A2A client for sending messages
- Parses tags from messages
- Checks if agents are ready

**Key Components:**
- `A2AClient` class - Sends messages to other agents
- `parse_tags()` - Extracts tags like `<white_agent_url>`
- `wait_agent_ready()` - Health check utility

**Why it matters:**
- Green agent uses this to communicate with white agents
- Must work correctly for evaluation to function

---

## 🟡 **Supporting Files (Important but not critical)**

### 4. **`launcher_scicode_new.py`** ⭐⭐
**Testing launcher - Useful for local testing**

**What it does:**
- Starts both green and white agents
- Sends test evaluation requests
- Useful for debugging

**When to use:**
- Testing locally before registration
- Debugging evaluation flow
- Development

---

### 5. **`requirements.txt`** ⭐⭐
**Dependencies - Required for installation**

**What it contains:**
- All Python packages needed
- Version specifications
- A2A SDK, uvicorn, datasets, etc.

**Why it matters:**
- Must have correct dependencies
- Needed for deployment

---

## 🟢 **Optional/Reference Files**

### 6. **`run_green_agent.sh`** ⭐
**Helper script - Convenience only**

**What it does:**
- Wraps agent startup
- Activates correct Python environment

**Not required, but helpful**

---

## 📋 **File Priority for Review**

### Must Review (Critical):
1. ✅ **`scicode_green_agent.py`** - Main implementation
2. ✅ **`tau_green_scicode.toml`** - Configuration
3. ✅ **`src/my_util.py`** - Communication layer

### Should Review:
4. ✅ **`launcher_scicode_new.py`** - Testing
5. ✅ **`requirements.txt`** - Dependencies

### Optional:
6. `run_green_agent.sh` - Helper script
7. Documentation files (*.md)

---

## 🎯 **Quick Start Review Order**

1. **Start**: `scicode_green_agent.py` (understand the logic)
2. **Check**: `tau_green_scicode.toml` (verify configuration)
3. **Verify**: `src/my_util.py` (ensure communication works)
4. **Test**: `launcher_scicode_new.py` (run end-to-end)

---

## 🔍 **What to Check in Each File**

### `scicode_green_agent.py`:
- [ ] Problem loading works with your dataset
- [ ] Test execution handles your test format
- [ ] Error handling is robust
- [ ] Response formatting is correct

### `tau_green_scicode.toml`:
- [ ] Agent name/description are correct
- [ ] Examples show proper usage
- [ ] Skills match capabilities

### `src/my_util.py`:
- [ ] A2A client uses correct protocol
- [ ] Tag parsing works correctly
- [ ] Error handling for network issues

---

## 📁 **File Structure**

```
CS194 Project/
├── scicode_green_agent.py      ← MAIN FILE (review first)
├── tau_green_scicode.toml       ← CONFIG (required)
├── src/
│   └── my_util.py               ← COMMUNICATION (critical)
├── launcher_scicode_new.py      ← TESTING (helpful)
├── requirements.txt              ← DEPENDENCIES (needed)
└── run_green_agent.sh           ← HELPER (optional)
```

---

## ✅ **Summary**

**Essential files (3):**
1. `scicode_green_agent.py` - Main implementation
2. `tau_green_scicode.toml` - Agent card
3. `src/my_util.py` - A2A client

**Important files (2):**
4. `launcher_scicode_new.py` - Testing
5. `requirements.txt` - Dependencies

**Focus your review on the 3 essential files first!**

