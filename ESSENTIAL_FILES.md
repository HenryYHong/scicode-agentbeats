# Essential Files for AgentBeats

## ✅ CORE FILES (Required for AgentBeats)

These are the ONLY files you need for AgentBeats.org registration:

1. **SciCodeAgent.py** - Main green agent implementation
   - Implements A2A protocol
   - Handles evaluation requests
   - Contains TauScicodeGreenExecutor

2. **tau_green_scicode.toml** - Agent card configuration
   - Defines agent metadata
   - Required for AgentBeats registration
   - Used by SciCodeAgent.py

3. **src/my_util.py** - A2A utilities
   - parse_tags() - Parse XML tags from messages
   - my_a2a - A2A client for agent communication
   - wait_agent_ready() - Wait for agents to be ready

4. **src/__init__.py** - Package initialization
   - Makes src/ a Python package
   - Exports utilities

5. **requirements.txt** - Dependencies
   - Lists required packages (a2a, uvicorn, httpx, etc.)

---

## 🧪 OPTIONAL FILES (For Testing/Development)

6. **white_agent_scicode.py** - White agent for local testing
   - Not needed for AgentBeats registration
   - Useful for testing the green agent locally

7. **launcher_scicode.py** - Launcher script
   - Not needed for AgentBeats registration
   - Useful for coordinating green + white agents locally

---

## ❌ NOT NEEDED (Can be ignored/deleted)

These are experiments, duplicates, or test files:

- `agentbeats_*.py` - Old experimental implementations
- `scicode_green_agent.py` - Alternative implementation (not used)
- `green_agent.py` - Alternative implementation (not used)
- `white_agent.py` - Old white agent (use white_agent_scicode.py)
- `*_agent_card.toml` - Other agent cards (use tau_green_scicode.toml)
- `test_*.py` - Test files (not needed for registration)
- `demo.py`, `*_demo.py` - Demo files
- `launcher.py` - Old launcher (use launcher_scicode.py)
- `*_server.py` - Various server implementations (not used)
- `railway_*.py` - Deployment scripts (optional)
- `*.md` - Documentation files (helpful but not required)
- `ngrok_*.log`, `ngrok.yml` - Logs/config (temporary)
- `*.env` files - Environment config (if used)

---

## 📦 Virtual Environment

**agentbeats_env/** - Python virtual environment
- Contains installed packages
- Required to run the agent
- Do NOT delete (but can be recreated)

---

## 🎯 Summary

**For AgentBeats.org registration, you ONLY need:**
1. SciCodeAgent.py
2. tau_green_scicode.toml
3. src/ (directory with my_util.py and __init__.py)
4. requirements.txt
5. agentbeats_env/ (virtual environment with dependencies)

Everything else is optional or can be deleted.


