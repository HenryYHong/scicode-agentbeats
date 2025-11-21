# AgentBeats Registration Steps for SciCode Green Agent

## 📋 Registration Form Fields

Fill out the form with these values:

- **Name**: `SciCode` (or `SciCode Green Agent`)
- **Deploy Type**: `Remote`
- **Is Assessor (Green) Agent**: ✅ **Check this box** (it's a green agent)
- **Controller URL**: `https://your-ngrok-url.ngrok-free.app` (see steps below)
- **Git URL**: (Optional) Your GitHub repo if you have one
- **Git Branch**: (Optional) `main` or `master`

## 🚀 Step-by-Step Setup

### Step 1: Start Your Green Agent

Make sure your green agent is running:

```bash
cd "/Users/henryhong/Desktop/CS194 Project"
source agentbeats_env_311/bin/activate
python scicode_green_agent.py --host 0.0.0.0 --port 9001
```

**Important**: Use `0.0.0.0` instead of `localhost` so it's accessible externally.

### Step 2: Expose with ngrok

In a **new terminal**, start ngrok:

```bash
ngrok http 9001
```

You'll see output like:
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:9001
```

**Copy the HTTPS URL** (the one starting with `https://`)

### Step 3: Test Your Public URL

Before registering, test that your agent is accessible:

```bash
# Test agent card
curl https://your-ngrok-url.ngrok-free.app/.well-known/agent-card.json

# Test status
curl https://your-ngrok-url.ngrok-free.app/status
```

Both should return JSON responses.

### Step 4: Fill Out Registration Form

On the AgentBeats website, fill in:

- **Name**: `SciCode`
- **Deploy Type**: `Remote`
- **Is Assessor (Green) Agent**: ✅ **Checked**
- **Controller URL**: `https://your-ngrok-url.ngrok-free.app`
- **Git URL**: (Leave blank or add your repo)
- **Git Branch**: (Leave blank or use `main`)

### Step 5: Submit and Verify

After submitting:
1. The website should verify your agent is accessible
2. It will check the agent card at `/.well-known/agent-card.json`
3. Your agent should appear in the agent list

## ⚠️ Important Notes

### ngrok Free Tier Limitations

- **URL changes** every time you restart ngrok
- **Session timeout** after 2 hours of inactivity
- **Limited requests** per month

### For Production Use

Consider:
- **ngrok paid plan** (static URLs)
- **Railway.app** deployment (persistent URLs)
- **Your own server** with public IP
- **Cloud Run** or similar service

### Keep ngrok Running

- Keep the ngrok terminal open while your agent is registered
- If ngrok stops, your agent becomes unreachable
- Restart ngrok and update the Controller URL if it changes

## 🔧 Troubleshooting

### "Agent not accessible"
- Make sure your agent is running on `0.0.0.0:9001`
- Verify ngrok is forwarding correctly
- Check firewall settings

### "Agent card not found"
- Test: `curl https://your-url/.well-known/agent-card.json`
- Make sure the agent is running
- Check the agent card file exists: `tau_green_scicode.toml`

### "Method not allowed"
- This is normal for GET requests to `/`
- The agent card and status endpoints should work
- POST requests to `/` work for A2A protocol

## 📝 Example Registration

```
Name: SciCode Green Agent
Deploy Type: Remote
Is Assessor (Green) Agent: ✅ Yes
Controller URL: https://abc123.ngrok-free.app
Git URL: (optional)
Git Branch: (optional)
```

## ✅ After Registration

Once registered, you can:
- View your agent on the AgentBeats platform
- Run assessments through the web interface
- See evaluation results and metrics
- Share your agent with others

