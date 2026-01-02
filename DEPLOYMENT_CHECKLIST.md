# Streamlit Community Cloud Deployment Checklist

## Pre-Deployment Checklist

### ✅ 1. Code Files Ready
- [x] `app.py` - Main Streamlit application
- [x] `agents.py` - Agent pipeline
- [x] `output_generation.py` - Output generation
- [x] `evaluation.py` - Evaluation harness
- [x] `demo.py` - Demo script
- [x] `requirements.txt` - All dependencies listed
- [x] `README.md` - Documentation complete

### ✅ 2. Configuration Files
- [x] `.streamlit/config.toml` - Theme and settings
- [x] `.gitignore` - Excludes sensitive files
- [x] `DEPLOYMENT.md` - Deployment guide

### ✅ 3. Security
- [ ] **IMPORTANT:** Never commit `.env` file
- [ ] `OPENAI_API_KEY` will be set as secret in Streamlit Cloud
- [ ] Check `.gitignore` includes `.env` files

### ✅ 4. Data Files
- [ ] Check Data folder size (should be < 1GB for free tier)
- [ ] Verify Data files are committed (or use Git LFS for large files)
- [ ] Ensure file paths are relative (not absolute)

### ✅ 5. GitHub Repository
- [ ] Create GitHub repository (public for free tier)
- [ ] Initialize git if not already done
- [ ] Commit all necessary files
- [ ] Push to GitHub

### ✅ 6. Streamlit Cloud Setup
- [ ] Sign in to https://share.streamlit.io/ with GitHub
- [ ] Click "New app"
- [ ] Select repository and branch (usually `main`)
- [ ] Set main file path: `app.py`
- [ ] Add secret: `OPENAI_API_KEY`
- [ ] Deploy!

---

## Quick Deployment Commands

### If starting fresh with git:

```bash
# 1. Initialize git (if not already)
git init

# 2. Add all files
git add .

# 3. Commit
git commit -m "Initial commit: DisasterOps multi-agent system"

# 4. Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 5. Push to GitHub
git branch -M main
git push -u origin main
```

### After pushing to GitHub:

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Branch: `main`
6. Main file: `app.py`
7. Advanced settings → Add secret: `OPENAI_API_KEY`
8. Deploy!

---

## Post-Deployment Verification

- [ ] App loads successfully
- [ ] RAG system loads (embeddings, chunks, BM25)
- [ ] Can process incident reports
- [ ] Export functions work
- [ ] No errors in logs

---

## Troubleshooting

### If app fails to start:
1. Check `requirements.txt` has all dependencies
2. Verify environment variables are set
3. Check Streamlit Cloud logs for errors
4. Ensure file paths are relative, not absolute

### If Data files are missing:
1. Verify Data folder is committed to GitHub
2. Check file size limits (1GB total for free tier)
3. Consider using Git LFS for large files

### If API key not working:
1. Verify secret is set correctly in Streamlit Cloud
2. Check secret name matches exactly: `OPENAI_API_KEY`
3. Restart the app after adding secrets

---

## Your Deployment URL

Once deployed, your app will be available at:
```
https://YOUR_APP_NAME.streamlit.app
```

Update your README.md with this link!

