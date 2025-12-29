# Quick Deployment Reference

## Render Deployment

```bash
# 1. Push code to GitHub
git push origin main

# 2. In Render Dashboard:
- Click "New +" → "Blueprint"
- Connect GitHub repository
- Select waste-classification-app
- Click "Apply"

# 3. Configure Production (Optional):
- Go to "Environment" tab
- Set VISION_PROVIDER=openai
- Set OPENAI_API_KEY=your-key-here
- Click "Save Changes"

# Your app is live at: https://waste-classification-app.onrender.com
```

## Fly.io Deployment

```bash
# 1. Install Fly CLI
brew install flyctl  # macOS
# OR
curl -L https://fly.io/install.sh | sh  # Linux

# 2. Authenticate
flyctl auth login

# 3. Launch app
cd waste-classification-app
flyctl launch

# 4. Set production secrets (optional)
flyctl secrets set OPENAI_API_KEY=your-key-here
flyctl secrets set VISION_PROVIDER=openai

# 5. Deploy updates
flyctl deploy

# Your app is live at: https://waste-classification-app.fly.dev
```

## Test Mobile Camera

### iOS (Safari)
1. Open https://your-app-url
2. Tap file input → "Take Photo or Video"
3. Grant camera permission
4. Take photo and classify

### Android (Chrome)
1. Open https://your-app-url
2. Tap file input → "Camera"
3. Grant permission
4. Take photo and classify

## Common Commands

### Render
```bash
# View logs in Dashboard → Logs tab
# Restart: Dashboard → Manual Deploy → "Deploy latest commit"
```

### Fly.io
```bash
# View logs
flyctl logs

# Check status
flyctl status

# Open in browser
flyctl open

# SSH into container
flyctl ssh console

# Scale up/down
flyctl scale count 2
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Camera not working | Verify HTTPS URL (not HTTP) |
| 502 Error | Check OPENAI_API_KEY is set correctly |
| App won't start | Check logs for errors, verify Dockerfile builds |
| Slow first load (Render) | Free tier sleeps after 15 min inactivity |

## Environment Variables

| Variable | Default | Production |
|----------|---------|------------|
| VISION_PROVIDER | stub | openai |
| OPENAI_API_KEY | - | your-key |
| OPENAI_MODEL | gpt-4o-mini | gpt-4o-mini |
| OPENAI_TIMEOUT_SECONDS | 20 | 20-30 |
| OPENAI_MAX_RETRIES | 2 | 2-3 |

## Links

- [Full Deployment Guide](./DEPLOYMENT.md)
- [Main README](./README.md)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs)
