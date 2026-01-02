# Deployment Guide for DisasterOps Streamlit App

## Best Options for Hosting

### Option 1: Streamlit Community Cloud (Recommended) ⭐

**Best for:** Portfolio projects, easiest setup
**Cost:** Free
**URL:** https://streamlit.io/cloud

**Pros:**
- Free forever
- Built specifically for Streamlit apps
- Automatic deployments from GitHub
- Custom subdomain (your-app.streamlit.app)
- Easy environment variable setup
- No credit card required

**Steps:**
1. Push your code to GitHub (create a repository)
2. Go to https://share.streamlit.io/
3. Sign in with GitHub
4. Click "New app"
5. Select your repository and branch
6. Set main file path: `app.py`
7. Add environment variable: `OPENAI_API_KEY`
8. Deploy!

**GitHub Repository Setup:**
```bash
# Create .streamlit/config.toml for customizations (optional)
mkdir -p .streamlit
echo '[theme]\nprimaryColor="#FF6B6B"\nbackgroundColor="#FFFFFF"\nsecondaryBackgroundColor="#F0F2F6"\ntextColor="#262730"\nfont="sans serif"' > .streamlit/config.toml
```

---

### Option 2: Hugging Face Spaces (HF) 🚀

**Best for:** ML/AI projects, sharing with ML community
**Cost:** Free
**URL:** https://huggingface.co/spaces

**Pros:**
- Free forever
- Great for ML/AI projects
- Automatic GPU/CPU resources
- Built-in community sharing
- Custom domain support
- Easy environment variable setup

**Steps:**
1. Create account at https://huggingface.co
2. Create a new Space
3. Choose "Streamlit" SDK
4. Upload your code (or connect GitHub)
5. Add secrets for `OPENAI_API_KEY` in Space settings
6. App auto-deploys!

**Required files for HF:**
- `app.py` (your main file)
- `requirements.txt` (already have this!)
- `README.md` (already have this!)
- Optional: `.env.example` file for documentation

---

### Option 3: GitHub Pages ❌

**Not suitable** - GitHub Pages only hosts static websites (HTML/CSS/JS), not Python applications like Streamlit.

---

## Recommended: Streamlit Community Cloud

### Quick Start Guide

1. **Prepare your repository:**
   ```bash
   # Make sure your code is clean
   git status
   
   # Create/update .gitignore to exclude sensitive files
   # (Already have this)
   ```

2. **Create GitHub repository:**
   - Go to https://github.com/new
   - Repository name: `DisasterOps` or `disaster-response-ai`
   - Make it public (required for free tier)
   - Initialize with README (optional)
   - Create repository

3. **Push your code:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: DisasterOps multi-agent system"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

4. **Deploy to Streamlit Cloud:**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select repository: `YOUR_USERNAME/YOUR_REPO`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Advanced settings"
   - Add secrets:
     ```
     OPENAI_API_KEY = your-actual-api-key-here
     ```
   - Click "Deploy"

5. **Your app will be live at:**
   ```
   https://YOUR_APP_NAME.streamlit.app
   ```

---

## Files to Check Before Deployment

### ✅ Required Files:
- `app.py` - Main Streamlit app
- `agents.py` - Agent pipeline
- `output_generation.py` - Output generation
- `requirements.txt` - Dependencies
- `README.md` - Documentation

### ✅ Important Considerations:

1. **Data files** - Your `Data/` folder contains the knowledge base:
   - These files are needed for the RAG system
   - Make sure to commit them or use a different storage solution
   - Check `.gitignore` - if `Data/` is ignored, you'll need to:
     - Either commit the Data folder (if not too large)
     - Or use Git LFS (Large File Storage)
     - Or upload Data folder separately and download during deployment

2. **Environment Variables:**
   - `OPENAI_API_KEY` must be set as a secret/environment variable
   - Never commit API keys to GitHub!

3. **File Size Limits:**
   - GitHub free tier: 100MB per file, 1GB per repository
   - Streamlit Cloud: 1GB storage limit
   - If your `Data/` folder is large, consider:
     - Using Git LFS
     - Hosting embeddings separately
     - Using cloud storage (S3, etc.) and downloading on startup

---

## Recommended Deployment Setup

### For Portfolio (Streamlit Cloud):

1. **Repository structure:**
   ```
   DisasterOps/
   ├── app.py
   ├── agents.py
   ├── output_generation.py
   ├── evaluation.py
   ├── demo.py
   ├── requirements.txt
   ├── README.md
   ├── .gitignore
   ├── .streamlit/
   │   └── config.toml (optional theme)
   └── Data/ (if not too large, or use LFS)
   ```

2. **Create `.streamlit/config.toml` for better UI:**
   ```toml
   [theme]
   primaryColor = "#FF6B6B"
   backgroundColor = "#FFFFFF"
   secondaryBackgroundColor = "#F0F2F6"
   textColor = "#262730"
   font = "sans serif"
   ```

3. **Update README with deployment link:**
   ```markdown
   ## 🚀 Live Demo
   
   Try the live application: https://YOUR_APP_NAME.streamlit.app
   ```

---

## Troubleshooting

### Issue: Large Data folder
**Solution:** Use Git LFS or compress/optimize the Data folder
```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "Data/**/*.npy"
git lfs track "Data/**/*.pkl"
```

### Issue: App crashes on startup
**Check:**
- All dependencies in `requirements.txt`
- Environment variables set correctly
- File paths are relative (not absolute)
- Data files are accessible

### Issue: Slow loading
**Optimizations:**
- Lazy load RAG resources (already implemented!)
- Cache expensive operations with `@st.cache_data`
- Consider pre-computing and storing results

---

## Summary

**For your portfolio project, I recommend:**

1. **Streamlit Community Cloud** - Easiest, free, perfect for demos
2. **Hugging Face Spaces** - Great if you want ML community visibility

Both are free and excellent choices. Streamlit Cloud is slightly easier to set up, while HF Spaces gives you more ML community exposure.

Would you like me to help you set up the deployment configuration files?

