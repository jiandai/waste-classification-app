# Cloud Deployment Guide - Stage 1 Phase 4

This guide covers deploying the Waste Classification App to cloud platforms with HTTPS support, enabling camera access on mobile devices.

## Prerequisites

- Docker installed locally (for testing)
- An account on your chosen PaaS provider (Render or Fly.io)
- OpenAI API key (optional, can use stub mode for testing)

## Why HTTPS is Required

Modern browsers require HTTPS (secure connections) to access device cameras on mobile web. This is a security requirement that prevents malicious websites from secretly accessing your camera. The `capture="environment"` attribute in our file input requires HTTPS on all mobile devices.

## Option 1: Deploy to Render

Render automatically provides HTTPS/SSL certificates for all deployed services.

### Quick Start

1. **Create a Render account** at https://render.com

2. **Connect your GitHub repository**:
   - Go to your Render Dashboard
   - Click "New +" → "Blueprint"
   - Connect your GitHub account
   - Select the `waste-classification-app` repository

3. **Deploy**:
   - Render will automatically detect the `render.yaml` configuration
   - Click "Apply" to create the service
   - Your app will be available at `https://waste-classification-app.onrender.com`

### Configure Environment Variables

For production with OpenAI:

1. Go to your service in Render Dashboard
2. Navigate to "Environment" tab
3. Update/add these variables:
   - `VISION_PROVIDER`: Change from `stub` to `openai`
   - `OPENAI_API_KEY`: Add your OpenAI API key (marked as secret)
   - `OPENAI_MODEL`: Keep as `gpt-4o-mini` (or change to your preferred model)

### Manual Deployment (Alternative)

If you prefer manual setup:

1. In Render Dashboard, click "New +" → "Web Service"
2. Connect your repository
3. Configure:
   - **Name**: waste-classification-app
   - **Runtime**: Docker
   - **Region**: Choose closest to your users
   - **Plan**: Free (for testing) or Starter (for production)
4. Add environment variables as needed
5. Click "Create Web Service"

### Render Features

- ✅ **Free tier available** (with limitations)
- ✅ **Automatic HTTPS/SSL** certificates
- ✅ **Auto-deploy** on git push
- ✅ **Health checks** configured via render.yaml
- ✅ **Zero-downtime deploys** on paid plans

## Option 2: Deploy to Fly.io

Fly.io provides automatic HTTPS with global edge deployment.

### Quick Start

1. **Install Fly CLI**:
   ```bash
   # macOS
   brew install flyctl
   
   # Linux
   curl -L https://fly.io/install.sh | sh
   
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Sign up and authenticate**:
   ```bash
   flyctl auth signup
   # Or if you have an account:
   flyctl auth login
   ```

3. **Launch your app**:
   ```bash
   cd waste-classification-app
   flyctl launch
   ```
   
   When prompted:
   - **App name**: Press Enter to use the name in fly.toml or customize
   - **Region**: Choose closest to your users (e.g., sjc for San Jose)
   - **Setup database**: No
   - **Deploy now**: Yes

4. **Your app is live!**
   - App URL: `https://waste-classification-app.fly.dev`
   - HTTPS is automatically configured

### Configure Environment Variables (Production)

Set your OpenAI API key securely:

```bash
# Set environment variables
flyctl secrets set OPENAI_API_KEY=your-api-key-here
flyctl secrets set VISION_PROVIDER=openai

# Verify secrets are set
flyctl secrets list
```

### Deploy Updates

After making code changes:

```bash
# Deploy updates
flyctl deploy

# View logs
flyctl logs

# Check status
flyctl status

# Open app in browser
flyctl open
```

### Fly.io Features

- ✅ **Free tier**: 3 shared-cpu VMs with 256MB RAM each
- ✅ **Automatic HTTPS/SSL** with custom domains
- ✅ **Global deployment** - run apps close to users
- ✅ **Fast deploys** - typically under 30 seconds
- ✅ **Built-in secrets management**

## Testing HTTPS and Camera Access

After deploying, test camera functionality on mobile:

### iOS (Safari)

1. Open your deployed app URL (https://...)
2. Tap the file upload input
3. Safari should show options: "Take Photo or Video" / "Photo Library"
4. Grant camera permission when prompted
5. Camera should open for taking photos

### Android (Chrome)

1. Open your deployed app URL (https://...)
2. Tap the file upload input  
3. Chrome should show: "Camera" / "Files"
4. Select "Camera" and grant permission
5. Camera should activate

### Desktop Testing

While HTTPS is not strictly required for localhost, you can test:

1. Open the deployed URL in Chrome/Firefox
2. Upload a test image using "Choose File"
3. Verify classification works

## Troubleshooting

### Camera Permission Denied

**Symptom**: Browser blocks camera access even on HTTPS

**Solutions**:
- Ensure URL starts with `https://` (not `http://`)
- Check browser settings: Site permissions → Camera
- Try incognito/private browsing mode
- Clear browser cache and reload

### "Not Secure" Warning

**Symptom**: Browser shows "Not Secure" or mixed content warning

**Solutions**:
- Verify deployment URL uses HTTPS
- Check that all resources (images, scripts) use relative paths or HTTPS
- Review service logs for SSL certificate issues

### App Not Loading

**Symptom**: App shows error or white screen

**Solutions**:
```bash
# Render: Check logs in Dashboard → Logs tab
# Fly.io: Check logs via CLI
flyctl logs

# Common issues:
# 1. Check environment variables are set
# 2. Verify Docker image builds successfully
# 3. Check health endpoint: curl https://your-app/health
```

### "Vision Provider Error"

**Symptom**: Classification fails with 502 error

**Solutions**:
1. **For stub mode (testing)**:
   - Verify `VISION_PROVIDER=stub` is set
   - Check logs for startup messages

2. **For OpenAI mode (production)**:
   - Verify `VISION_PROVIDER=openai` is set
   - Ensure `OPENAI_API_KEY` is configured as a secret/environment variable
   - Check OpenAI API key is valid and has credits
   - Review service logs for detailed error messages

### Deployment Fails

**Render**:
- Check the "Events" tab for build logs
- Verify `render.yaml` is in repository root
- Ensure Dockerfile is valid

**Fly.io**:
```bash
# View deployment logs
flyctl logs

# Check status
flyctl status

# Restart app
flyctl apps restart waste-classification-app
```

## Cost Estimates

### Free Tier Options

Both platforms offer free tiers suitable for testing and low-traffic apps:

**Render Free**:
- Spins down after 15 min of inactivity
- 750 hours/month free
- Good for: Testing, demos, personal projects

**Fly.io Free**:
- Up to 3 shared-cpu-1x VMs
- 256MB RAM per VM
- 3GB persistent storage
- Good for: Small production apps, testing

### Paid Plans

For production with guaranteed uptime:

**Render Starter** ($7/month):
- Always on
- 512MB RAM
- Better for consistent availability

**Fly.io** (Pay-as-you-go):
- ~$5-10/month for small app
- Scales automatically
- Pay only for what you use

## Performance Optimization

### Image Processing

The app already includes:
- 8MB max file size limit
- Automatic image format validation (JPG/PNG)
- Efficient PIL-based image processing

### Caching

Both platforms support HTTP caching:
- Static assets (icons, manifest) are cached by browsers
- Service worker provides offline support
- API responses are not cached (real-time classification)

### Monitoring

**Render**: Built-in metrics in Dashboard

**Fly.io**: 
```bash
# View metrics
flyctl dashboard metrics

# Real-time monitoring
flyctl status
```

## Security Best Practices

### Environment Variables

✅ **DO**:
- Use platform secrets management for API keys
- Set `VISION_PROVIDER=stub` for testing
- Use `VISION_PROVIDER=openai` only in production

❌ **DON'T**:
- Commit API keys to git
- Share environment files publicly
- Use production keys in development

### HTTPS Only

Both Render and Fly.io enforce HTTPS by default:
- `force_https = true` in fly.toml
- Render automatically redirects HTTP → HTTPS

### Container Security

The Dockerfile includes:
- Non-root user (UID 1000)
- Minimal base image (python:3.11-slim)
- No development dependencies in production

## Next Steps

After successful deployment:

1. ✅ **Test on actual mobile devices** (iOS and Android)
2. ✅ **Verify camera capture works** on both platforms
3. ✅ **Test classification** with real waste items
4. ✅ **Monitor performance** and error rates
5. ✅ **Configure production OpenAI key** when ready
6. 🔜 **Custom domain** (optional, available on both platforms)
7. 🔜 **Analytics** (consider adding usage tracking)
8. 🔜 **User feedback** (collect real-world testing data)

## Resources

### Render
- Documentation: https://render.com/docs
- Status: https://status.render.com
- Support: https://render.com/docs/support

### Fly.io  
- Documentation: https://fly.io/docs
- Status: https://status.flyio.net
- Community: https://community.fly.io

### Camera Access on Web
- MDN Web APIs: https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
- HTML Media Capture: https://www.w3.org/TR/html-media-capture/
- Browser compatibility: https://caniuse.com/html-media-capture

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review platform status pages
3. Check service logs for detailed errors
4. Open an issue on GitHub with deployment logs
