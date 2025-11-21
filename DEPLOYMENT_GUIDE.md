# AgentBeats Deployment Guide

You're right! AgentBeats requires **public URLs**, not localhost. Here are your options:

## 🌐 **AgentBeats Platform**
- **Website**: https://agentbeats.org
- **Registration**: https://agentbeats.org/register (or similar)

## 🚀 **Deployment Options**

### **Option 1: Railway (Recommended - Easiest)**

Railway is the easiest way to deploy your agent:

```bash
# 1. Create deployment files
python3 railway_deploy.py

# 2. Install Railway CLI
npm install -g @railway/cli

# 3. Login and deploy
railway login
railway init
railway up
```

**Your URLs will be:**
- Agent URL: `https://your-app.railway.app`
- Launcher URL: `https://your-app.railway.app`

### **Option 2: Heroku (Popular)**

```bash
# 1. Create deployment files
python3 heroku_deploy.py

# 2. Install Heroku CLI
brew install heroku/brew/heroku

# 3. Deploy
heroku create your-scicode-agent
git push heroku main
```

**Your URLs will be:**
- Agent URL: `https://your-scicode-agent.herokuapp.com`
- Launcher URL: `https://your-scicode-agent.herokuapp.com`

### **Option 3: ngrok (Quick Testing)**

For quick testing with AgentBeats:

```bash
# 1. Install ngrok
brew install ngrok

# 2. Start your agent
python3 green_agent.py --port 3333

# 3. In another terminal, start ngrok
ngrok http 3333
```

**Your URLs will be:**
- Agent URL: `https://abc123.ngrok.io` (changes each restart)
- Launcher URL: `https://abc123.ngrok.io`

## 📋 **Registration Process**

1. **Deploy your agent** using one of the options above
2. **Get your public URLs** from the deployment
3. **Go to AgentBeats**: https://agentbeats.org
4. **Register your agent** with:
   - Agent URL: `https://your-deployed-url.com`
   - Launcher URL: `https://your-deployed-url.com`
   - Agent Name: `SciCode Green Agent`
   - Description: `Green agent for SciCode evaluation using AgentBeats A2A protocol`

## 🔧 **Quick Start (Recommended)**

For the fastest setup:

```bash
# 1. Create Railway deployment files
python3 railway_deploy.py

# 2. Follow the Railway instructions
cat RAILWAY_DEPLOYMENT.md

# 3. Deploy to Railway
# 4. Get your public URLs
# 5. Register with AgentBeats
```

## 🌍 **Public URLs Required**

AgentBeats needs to access your agent from the internet, so you need:

- ✅ **Public domain/IP** (not localhost)
- ✅ **HTTPS** (preferred)
- ✅ **Port 80/443** (or standard web ports)
- ✅ **Always running** (24/7 for battles)

## 🎯 **Next Steps**

1. **Choose a deployment option** (Railway recommended)
2. **Deploy your agent**
3. **Get your public URLs**
4. **Register with AgentBeats** at https://agentbeats.org
5. **Start participating in battles!**

The deployment scripts I created will handle all the configuration for you.



