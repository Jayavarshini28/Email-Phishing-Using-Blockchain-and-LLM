# Deployment Checklist for Chrome Web Store

## ✅ Pre-Deployment Checklist

### Backend Setup
- [ ] All backend files organized in `backend/` folder
- [ ] `requirements.txt` includes `gunicorn==21.2.0`
- [ ] `Dockerfile` is configured correctly
- [ ] `.env` file created with all API keys (NOT committed to git)
- [ ] Tested backend locally with `python app.py`

### Google Cloud Setup
- [ ] Google Cloud account created
- [ ] Billing enabled on Google Cloud
- [ ] Project created in Google Cloud Console
- [ ] Google Cloud CLI installed
- [ ] Authenticated with `gcloud auth login`
- [ ] Project set with `gcloud config set project YOUR_PROJECT_ID`

### Deployment Steps
- [ ] Navigate to `backend/` directory
- [ ] Run deployment: `gcloud run deploy email-phishing-backend --source . --platform managed --region us-central1 --allow-unauthenticated --memory 1Gi`
- [ ] Deployment successful and service URL received
- [ ] Set environment variables on Cloud Run service
- [ ] Test health endpoint: `https://YOUR-SERVICE-URL/health`
- [ ] Test analyze endpoint with sample request

### Chrome Extension Updates
- [ ] Update API_URL in `popup.js` to Cloud Run URL
- [ ] Update API_URL in `content_script.js` to Cloud Run URL
- [ ] Update API_URL in `background.js` if applicable
- [ ] Test extension locally with new backend URL
- [ ] Verify all features work (analyze, blockchain, etc.)

### Chrome Web Store Preparation
- [ ] Create 128x128 icon for extension
- [ ] Create promotional images (440x280, 920x680, 1400x560)
- [ ] Create 5-10 screenshots of extension in action
- [ ] Write compelling description (400-450 characters)
- [ ] Prepare detailed description with features
- [ ] Create privacy policy (required) and host it somewhere
- [ ] Set up support email/website
- [ ] Choose appropriate category
- [ ] Set pricing (free recommended)

### Extension Package
- [ ] Remove any development/test code
- [ ] Remove console.log statements (or make conditional)
- [ ] Update version number in `manifest.json`
- [ ] Ensure all permissions are justified
- [ ] Test on fresh Chrome profile
- [ ] Create ZIP of extension folder

### Developer Account
- [ ] Create Chrome Web Store developer account ($5 one-time fee)
- [ ] Verify email address
- [ ] Complete developer profile

### Submission
- [ ] Upload ZIP file
- [ ] Fill in all store listing details
- [ ] Add screenshots and promotional images
- [ ] Set privacy practices
- [ ] Submit for review
- [ ] Wait for approval (typically 1-7 days)

## 📋 Important URLs to Update in Extension

### Files to Update:
1. **`phish-analyzer-extension/popup.js`**
   ```javascript
   const API_URL = 'https://YOUR-SERVICE-URL';
   ```

2. **`phish-analyzer-extension/content_script.js`**
   ```javascript
   const API_URL = 'https://YOUR-SERVICE-URL';
   ```

3. **`phish-analyzer-extension/background.js`** (if used)
   ```javascript
   const API_URL = 'https://YOUR-SERVICE-URL';
   ```

## 🔧 Testing Checklist

### Backend Testing
- [ ] `/health` endpoint returns 200
- [ ] `/analyze` endpoint accepts POST requests
- [ ] Blockchain integration works
- [ ] LLM analysis functions correctly
- [ ] Error handling works properly
- [ ] CORS allows extension requests

### Extension Testing
- [ ] Extension loads in Chrome
- [ ] Popup opens correctly
- [ ] Content script injects on Gmail
- [ ] Analysis button appears
- [ ] Email analysis completes successfully
- [ ] Results display correctly
- [ ] Blockchain check works
- [ ] User can report domains
- [ ] No console errors

## 💰 Cost Monitoring

### Google Cloud Run
- [ ] Set up billing alerts
- [ ] Monitor usage in Cloud Console
- [ ] Check free tier limits (2M requests/month)
- [ ] Review costs weekly initially

### Expected Costs
- Backend: $5-10/month (or free tier)
- Chrome Web Store: $5 one-time developer fee

## 🚨 Troubleshooting

### If deployment fails:
1. Check Cloud Build logs
2. Verify Dockerfile syntax
3. Ensure all dependencies in requirements.txt
4. Check for memory/timeout issues

### If extension doesn't work:
1. Check browser console for errors
2. Verify API URL is correct
3. Test backend URL directly
4. Check CORS headers
5. Verify API key if used

## 📞 Support Resources

- Google Cloud Run Docs: https://cloud.google.com/run/docs
- Chrome Extension Docs: https://developer.chrome.com/docs/extensions/
- Chrome Web Store: https://chrome.google.com/webstore/devconsole

## ✨ Post-Deployment

- [ ] Monitor logs for errors
- [ ] Track user feedback
- [ ] Plan for updates/improvements
- [ ] Set up analytics (optional)
- [ ] Create user documentation
- [ ] Prepare for user support inquiries

---

**Good Luck with Your Deployment! 🚀**
