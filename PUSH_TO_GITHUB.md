# Push to GitHub - Quick Guide

Your project is ready to push! All files are committed locally.

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** `project-samarth` (or any name you prefer)
   - **Description:** `Intelligent Agri-Climate Q&A System over data.gov.in`
   - **Visibility:** Public (recommended for internship submission)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click "Create repository"

## Step 2: Push Your Code

GitHub will show you commands. Use these:

```bash
# Navigate to project directory (if not already there)
cd /Users/paritoshdwivedi/Downloads/Projects/bharat-task

# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/project-samarth.git

# Push to GitHub
git push -u origin main
```

**Example (replace YOUR_USERNAME):**
```bash
git remote add origin https://github.com/paritoshdwivedi/project-samarth.git
git push -u origin main
```

## Step 3: Verify

1. Refresh your GitHub repository page
2. You should see:
   - ✅ Comprehensive README.md displayed
   - ✅ All source code files
   - ✅ Green badges showing test success
   - ✅ Professional project structure

## Step 4: Deploy Backend to Render

Now that code is on GitHub, deploy the backend:

1. Go to https://render.com
2. Sign in (can use GitHub account)
3. Click "New+" → "Web Service"
4. Click "Connect to GitHub" → Select your `project-samarth` repo
5. Configure:
   ```
   Name: project-samarth-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   Root Directory: backend
   ```
6. Click "Advanced" → Add Environment Variable:
   ```
   DATAGOV_API_KEY = 579b464db66ec23bdd000001df2e1e87602e4576665f24c51bc77875
   ```
7. Click "Create Web Service"
8. Wait 2-3 minutes for deployment
9. **Copy your backend URL** (e.g., `https://project-samarth-backend.onrender.com`)

## Step 5: Deploy Frontend to Netlify

### Option A: Drag & Drop (Fastest)
1. Go to https://app.netlify.com/drop
2. Drag your `frontend` folder
3. **Copy your frontend URL** (e.g., `https://unique-name.netlify.app`)

### Option B: Connect GitHub (Automatic updates)
1. Go to https://app.netlify.com
2. "Add new site" → "Import an existing project"
3. Connect to GitHub → Select `project-samarth`
4. Configure:
   - Base directory: `frontend`
   - Publish directory: `.`
5. Deploy
6. **Copy your frontend URL**

## Step 6: Test End-to-End

1. Open your Netlify frontend URL
2. Paste your Render backend URL in the "Backend Endpoint" field
3. Select a sample prompt from dropdown
4. Click "Ask Question"
5. ✅ You should see:
   - Natural language answer
   - Data tables
   - Citations to data.gov.in

## Step 7: Record Loom Video

Now you're ready! Use `LOOM_TALKING_POINTS.md` for your 2-minute demo.

**Your URLs to showcase:**
- GitHub Repo: `https://github.com/YOUR_USERNAME/project-samarth`
- Live Frontend: Your Netlify URL
- Backend API: Your Render URL
- Working Demo: Show sample prompts in action!

---

## Quick Commands Reference

```bash
# Check git status
git status

# View commit history
git log --oneline

# Check remote
git remote -v

# Push to GitHub (after adding remote)
git push -u origin main

# If you make changes later:
git add .
git commit -m "Description of changes"
git push
```

---

## 🎉 You're All Set!

Once pushed, share these links:
1. **GitHub Repository:** For code review
2. **Live Demo URL:** For testing the system
3. **Loom Video:** For walkthrough

Good luck with your internship submission! 🚀
