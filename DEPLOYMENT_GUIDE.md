# 🚀 Deployment Guide

This guide walks you through deploying the L2 Writing Style Analyzer to GitHub and Streamlit Cloud.

## 📋 Prerequisites

- A GitHub account (free at [github.com](https://github.com))
- A Streamlit Cloud account (free at [streamlit.io/cloud](https://streamlit.io/cloud))

---

## Step 1: Create a GitHub Repository

### Option A: Using GitHub Web Interface

1. Go to [github.com](https://github.com) and sign in
2. Click the **+** button (top right) → **New repository**
3. Enter repository name: `l2-writing-analyzer`
4. Choose **Public** or **Private**
5. Check **Add a README file** (optional)
6. Click **Create repository**

### Option B: Using Git Command Line

```bash
# Navigate to the project folder
cd l2-writing-analyzer

# Initialize git
git init
git add .
git commit -m "Initial commit: L2 Writing Style Analyzer"

# Create repository on GitHub and link it
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/l2-writing-analyzer.git
git push -u origin main
```

---

## Step 2: Upload Project Files

### Using GitHub Web Interface

1. Open your new repository on GitHub
2. Click **Add file** → **Upload files**
3. Drag and drop all files from this folder:
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - `.gitignore`
   - `LICENSE`
   - `packages.txt`
4. Click **Commit changes**

### Using Git Command Line

```bash
# Add all files
git add .

# Commit
git commit -m "Add all project files"

# Push to GitHub
git push origin main
```

---

## Step 3: Deploy to Streamlit Cloud

1. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and sign in with GitHub
2. Click **New app** (top right)
3. Select your GitHub repository: `YOUR_USERNAME/l2-writing-analyzer`
4. Configure:
   - **Main file path**: `app.py`
   - **Branch**: `main`
5. Click **Deploy**

Streamlit Cloud will automatically:
- Install dependencies from `requirements.txt`
- Build and deploy your app
- Provide a public URL

### Advanced Configuration (Optional)

If you need to set environment variables or configure resources:

1. In Streamlit Cloud, click your app → **Settings** (⋮ menu)
2. Configure:
   - **Python version**: 3.8, 3.9, 3.10, or 3.11
   - **Secrets**: Add any API keys (not needed for this app)
   - **Resources**: Adjust memory if needed

---

## Step 4: Update README with Live URL

After deployment:

1. Copy your Streamlit Cloud URL (e.g., `https://l2-writing-analyzer-abc123.streamlit.app`)
2. Edit `README.md` on GitHub
3. Replace `YOUR_STREAMLIT_CLOUD_URL` with your actual URL
4. Commit the change

---

## 🔄 Updating Your App

### Making Changes

When you update the code:

```bash
# Make your changes to the files

# Commit and push
git add .
git commit -m "Description of changes"
git push origin main
```

Streamlit Cloud will automatically redeploy when you push to GitHub!

---

## 📱 Testing Before Deployment

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 🐛 Troubleshooting

### Common Issues

**Import errors**
- Check `requirements.txt` has all dependencies
- Ensure versions are compatible

**App won't start**
- Verify `app.py` is the main entry point
- Check Streamlit Cloud logs (⋮ menu → "Manage app" → "Logs")

**PDF export not working**
- `fpdf` should be in `requirements.txt`
- No additional system packages needed

**Metrics not calculating**
- Check that text is being entered in the input fields
- Verify `numpy` is installed

### Getting Help

- Streamlit documentation: [docs.streamlit.io](https://docs.streamlit.io)
- Streamlit forum: [discuss.streamlit.io](https://discuss.streamlit.io)
- GitHub Issues: Open an issue in your repository

---

## 📊 Monitoring Your App

Streamlit Cloud provides:
- **Analytics**: View app usage statistics
- **Logs**: Debug issues in real-time
- **Settings**: Manage app configuration

Access these through the **⋮ menu** next to your app.

---

## 🎉 Success!

Your L2 Writing Style Analyzer should now be:
- ✅ Hosted on GitHub with full source code
- ✅ Deployed and accessible via Streamlit Cloud
- ✅ Mobile-responsive and ready for ELT users

Share your app URL with colleagues and students!
