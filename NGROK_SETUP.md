
# ngrok Setup for AgentBeats Testing

## 1. Install ngrok
```bash
# macOS
brew install ngrok

# Or download from https://ngrok.com/download
```

## 2. Sign up for ngrok
1. Go to https://ngrok.com
2. Create free account
3. Get your auth token

## 3. Authenticate ngrok
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

## 4. Start your agent
```bash
python3 green_agent.py --port 3333
```

## 5. In another terminal, start ngrok
```bash
ngrok http 3333
```

## 6. Copy the public URL
ngrok will show something like:
```
https://abc123.ngrok.io -> http://localhost:3333
```

## 7. Register with AgentBeats
Use the ngrok URLs:
- Agent URL: https://abc123.ngrok.io
- Launcher URL: https://abc123.ngrok.io

## 8. Keep both running
- Keep your agent running
- Keep ngrok running
- The tunnel will stay active as long as both are running

## Note: Free ngrok limitations
- URL changes each restart
- Limited bandwidth
- For production, use Railway/Heroku instead
