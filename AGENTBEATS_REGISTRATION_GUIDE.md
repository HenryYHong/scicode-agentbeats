# AgentBeats.org Registration Guide for SciCodeAgent.py

## ✅ **Ready for Registration!**

Your `SciCodeAgent.py` is ready to be registered on AgentBeats.org. It uses the proper A2A protocol (`A2AStarletteApplication`) which is what AgentBeats expects.

## 📋 **Pre-Registration Checklist**

### ✅ Completed:
- [x] A2A protocol implementation (`A2AStarletteApplication`)
- [x] Agent card TOML file (`tau_green_scicode.toml`)
- [x] Agent executor (`TauScicodeGreenExecutor`)
- [x] A2A client utilities (`src/my_util.py`)
- [x] Test execution functionality
- [x] Command-line arguments for configuration

### ⚠️ **Before Registration:**

1. **Install Dependencies**
   ```bash
   pip install a2a uvicorn httpx python-dotenv
   ```

2. **Get a Public URL**
   - The agent needs to be accessible from the internet
   - Options:
     - **ngrok**: `ngrok http 9001` (free, temporary)
     - **Railway**: Deploy to Railway.app (persistent)
     - **Your own server**: If you have a public IP

## 🚀 **Step-by-Step Registration**

### 1. **Start Your Agent**

```bash
python SciCodeAgent.py --host 0.0.0.0 --port 9001
```

Note: Use `0.0.0.0` instead of `localhost` so it's accessible externally.

### 2. **Expose to Internet (Choose One)**

#### Option A: ngrok (Easiest)
```bash
# In another terminal
ngrok http 9001
# Copy the HTTPS URL (e.g., https://abc123.ngrok-free.app)
```

#### Option B: Railway (Persistent)
Deploy using Railway.app with the provided `Procfile` and `requirements.txt`

### 3. **Register on AgentBeats.org**

Go to **https://agentbeats.org** and register your agent:

- **Agent URL**: `https://your-public-url.com` (the ngrok URL or your domain)
- **Launcher URL**: `https://your-public-url.com` (same URL for green agents)
- **Agent Name**: `SciCode Green Agent`
- **Description**: `Green agent for SciCode evaluation using AgentBeats A2A protocol`

### 4. **Verify Registration**

AgentBeats will try to reach:
- `GET /` - Agent status
- `GET /card` - Agent card (if implemented)
- `POST /send_message` - A2A protocol endpoint (handled by A2AStarletteApplication)

## 🔧 **A2A Protocol Endpoints**

Your agent automatically provides these endpoints via `A2AStarletteApplication`:

- ✅ `POST /send_message` - A2A protocol message sending
- ✅ `GET /` - Agent status (provided by A2A framework)
- ✅ Health check endpoints (provided by A2A framework)

## 📝 **Agent Usage**

Your agent expects messages with tags:

```xml
<white_agent_url>https://white-agent-url.com</white_agent_url>
<scicode_problem_id>1</scicode_problem_id>
```

Or:

```xml
<white_agent_url>https://white-agent-url.com</white_agent_url>
<problem_id>1</problem_id>
```

## ⚠️ **Important Notes**

1. **URL Format**: When registering, ensure your URL is publicly accessible
2. **HTTPS**: AgentBeats prefers HTTPS URLs (ngrok provides this)
3. **CORS**: A2AStarletteApplication handles CORS automatically
4. **Dependencies**: Make sure `a2a` package is installed

## 🧪 **Testing Before Registration**

Test locally first:

```bash
# Start agent
python SciCodeAgent.py --host 0.0.0.0 --port 9001

# Test A2A endpoint (in another terminal)
curl -X POST http://localhost:9001/send_message \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "parts": [{"kind": "text", "text": "<white_agent_url>http://test</white_agent_url><scicode_problem_id>1</scicode_problem_id>"}]
  }'
```

## ✅ **Final Checklist**

- [ ] Dependencies installed (`a2a`, `uvicorn`, `httpx`)
- [ ] Agent starts successfully
- [ ] Agent accessible via public URL
- [ ] HTTPS URL available (for AgentBeats registration)
- [ ] Agent card file exists (`tau_green_scicode.toml`)
- [ ] All source files present (`src/my_util.py`, etc.)

## 🎯 **You're Ready!**

Once you have a public URL, you can register on AgentBeats.org. The agent uses the standard A2A protocol, so it should work seamlessly with the platform.



