# Streamlit Community Cloud - Quick Setup Guide

## Step-by-Step Deployment

### 1. Prepare Your Repository

Your code is ready! Here's what's prepared:
- ✅ All Python files
- ✅ `requirements.txt` with dependencies
- ✅ `.streamlit/config.toml` for theme
- ✅ `.gitignore` configured
- ✅ Data folder: 178MB (under 1GB limit ✓)

### 2. Push to GitHub

If you haven't already:

```bash
# Initialize git (if needed)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: DisasterOps multi-agent system"

# Create repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

**Important:** Make sure your repository is **public** (required for free Streamlit Cloud tier).

### 3. Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit: https://share.streamlit.io/
   - Click "Sign in" and authorize with GitHub

2. **Create New App:**
   - Click "New app" button
   - Select your GitHub account
   - Choose repository: `YOUR_USERNAME/YOUR_REPO`
   - Branch: `main`
   - Main file path: `app.py`

3. **Configure Secrets (IMPORTANT):**
   - Click "Advanced settings"
   - Under "Secrets", add:
     ```
     OPENAI_API_KEY = sk-your-actual-openai-api-key-here
     ```
   - Click "Save"

4. **Deploy:**
   - Click "Deploy" button
   - Wait for build (usually 1-2 minutes)
   - Your app will be live!

### 4. Your App URL

Once deployed, your app will be available at:
```
https://YOUR_REPO_NAME.streamlit.app
```

Or a custom URL like:
```
https://disasterops-YOUR_USERNAME.streamlit.app
```

### 5. Update README

Don't forget to update `README.md` with your live app URL!

---

## Troubleshooting

### Build Fails

**Check:**
- All dependencies in `requirements.txt`
- File paths are relative (not absolute like `/Users/...`)
- No syntax errors in Python files

**Common fixes:**
```bash
# Test requirements locally first
pip install -r requirements.txt
python -c "import app; print('OK')"
```

### App Crashes on Startup

**Check Streamlit Cloud logs:**
- Click on your app in dashboard
- Go to "Manage app" → "Logs"
- Look for errors

**Common issues:**
- Missing environment variable (check secrets)
- Data files not found (check Data folder is committed)
- Import errors (check all dependencies in requirements.txt)

### Slow Loading

**This is normal!** First load takes time because:
- RAG system loads 1694 chunks
- Embeddings are loaded (384 dimensions)
- BM25 model is loaded

Subsequent runs should be faster due to caching.

---

## File Structure for Deployment

Your repository should look like:
```
DisasterOps/
├── .streamlit/
│   └── config.toml          ✅ Theme config
├── app.py                   ✅ Main app
├── agents.py                ✅ Agents
├── output_generation.py     ✅ Outputs
├── evaluation.py            ✅ Evaluation
├── demo.py                  ✅ Demo script
├── requirements.txt         ✅ Dependencies
├── README.md                ✅ Documentation
├── .gitignore               ✅ Git ignore
├── Data/                    ✅ Knowledge base
│   ├── chunks/
│   ├── embeddings/
│   ├── metadata/
│   ├── processed/
│   └── raw/
└── ... (other files)
```

---

## Environment Variables Needed

Only one secret is required:
- `OPENAI_API_KEY` - Your OpenAI API key

Set this in Streamlit Cloud secrets (not in code!)

---

## Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Repository is public
- [ ] All files committed
- [ ] Streamlit Cloud account created
- [ ] App deployed
- [ ] `OPENAI_API_KEY` secret added
- [ ] App loads successfully
- [ ] Can process incidents
- [ ] README updated with live URL

---

## Need Help?

- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- Streamlit Forum: https://discuss.streamlit.io/
- GitHub Issues: Create an issue in your repository

Good luck with your deployment! 🚀

