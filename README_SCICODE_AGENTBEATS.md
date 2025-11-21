# 🔬 SciCode Green Agent for AgentBeats

**"In the game of agents, you evaluate or you crash"**

A complete SciCode Green Agent implementation following the exact AgentBeats tutorial pattern. This agent evaluates AI models using the SciCode benchmark and provides comprehensive metrics for scientific code generation tasks.

## 🚀 Quick Start

### 1. Start Your Agent

```bash
# Start the SciCode Green Agent
python3 scicode_green_agent.py --port 9012
```

### 2. Test Locally

```bash
# Test your agent
python3 test_simple_scicode_agent.py
```

### 3. Make It Public

```bash
# Start ngrok tunnel
ngrok http 9012
```

### 4. Register with AgentBeats

1. Go to **https://agentbeats.org**
2. Navigate to **Agents → Register Agent**
3. Use your ngrok URL for both Agent URL and Launcher URL

## 📁 Files Created

Following the AgentBeats tutorial pattern:

- **`scicode_green_agent_card.toml`** - Agent card for registration
- **`scicode_green_agent.py`** - Main agent implementation
- **`test_simple_scicode_agent.py`** - Simple test script
- **`run_scicode_green_agent.sh`** - Runner script
- **`SCICODE_AGENTBEATS_TUTORIAL.md`** - Complete tutorial

## 🎯 What This Agent Does

Your SciCode Green Agent:

1. **Receives evaluation requests** from AgentBeats
2. **Runs SciCode benchmark** on specified models
3. **Provides comprehensive metrics**:
   - Pass@1 score
   - Execution time
   - Model performance
   - Scientific accuracy
4. **Returns detailed results** for comparison

## 🔧 Key Features

- ✅ **AgentBeats Compatible**: Follows exact protocol
- ✅ **SciCode Integration**: Uses official benchmark
- ✅ **HTTP Endpoints**: `/health`, `/card`, `/evaluate`
- ✅ **Easy Setup**: One-command deployment
- ✅ **Public URLs**: Works with ngrok for registration

## 🌐 Endpoints

- **GET `/health`** - Health check
- **GET `/card`** - Agent card for registration
- **POST `/evaluate`** - Run SciCode evaluation

## 📊 Example Usage

```bash
# Health check
curl http://localhost:9012/health

# Agent card
curl http://localhost:9012/card

# Run evaluation
curl -X POST http://localhost:9012/evaluate \
  -H "Content-Type: application/json" \
  -d '{"config": {"model": "openai/gpt-4o", "max_problems": 1}}'
```

## 🎉 You're Ready!

Your SciCode Green Agent is now ready for AgentBeats battles! 

**Next Steps:**
1. Start ngrok: `ngrok http 9012`
2. Register at https://agentbeats.org
3. Use the ngrok URL for registration
4. Start evaluating AI models on scientific code generation!

## 🔗 Related Files

- `README_AGENTBEATS.md` - Original implementation docs
- `SCICODE_AGENTBEATS_TUTORIAL.md` - Complete tutorial
- `scicode_green_agent.py` - Main agent code
- `test_simple_scicode_agent.py` - Test script



