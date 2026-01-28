# Vercel Deployment Checklist - Copy & Paste Instructions

## ✅ Prerequisites
- [ ] GitHub account (github.com)
- [ ] Vercel account (vercel.com, sign in with GitHub)
- [ ] Neon account (neon.tech, sign in with GitHub)

---

## 📋 Step 1: Push Code to GitHub (5 min)

```bash
cd D:\leapWP

# Configure git
git config user.name "Your Name"
git config user.email "your.email@gmail.com"

# Stage and commit
git add .
git commit -m "Leap IELTS: Ready for Vercel deployment"

# Create GitHub repo:
# 1. Go to github.com/new
# 2. Name: leapWP
# 3. Description: IELTS Engagement System
# 4. Create repository

# Then run (replace YOUR_USERNAME):
git remote add origin https://github.com/YOUR_USERNAME/leapWP.git
git branch -M main
git push -u origin main
```

✓ Your code is now on GitHub

---

## 🗄️ Step 2: Create Neon Database (2 min)

1. Go to https://neon.tech
2. Click "Sign up" → "Continue with GitHub"
3. Authorize Neon
4. Create new project:
   - **Project name**: `leap-ielts`
   - **Database name**: `leap_ielts_db`
5. Wait for database creation
6. Click "Connection string"
7. **Copy this string** - you'll need it next:
   ```
   postgresql://user:password@ep-xxxxx.us-east-1.neon.tech/leap_ielts_db?sslmode=require
   ```

✓ Database is ready

---

## 🚀 Step 3: Deploy on Vercel (2 min)

1. Go to https://vercel.com
2. Click "Sign up" → "Continue with GitHub"
3. Authorize Vercel
4. Click "Add New" → "Project"
5. Click on your **leapWP** repository
6. Click "Import"

### Configure Project

Under "Environment Variables", add these:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | See below |
| `DATABASE_URL` | Your Neon connection string |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` |

**Generate SECRET_KEY:**

Open PowerShell/Terminal and run:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste in Vercel.

### Click "Deploy"

Wait 2-3 minutes for deployment to complete.

✓ Your app is now deployed!

---

## 🗄️ Step 4: Initialize Database (30 sec)

After Vercel deployment succeeds:

1. Copy your Vercel URL (shown on dashboard):
   ```
   https://leapwp-YOUR_USERNAME.vercel.app
   ```

2. Visit this URL (add `/admin/init-db`):
   ```
   https://leapwp-YOUR_USERNAME.vercel.app/admin/init-db
   ```

3. You should see:
   ```json
   {
     "status": "success",
     "message": "Database initialized successfully",
     "tables_created": [...]
   }
   ```

✓ Database tables created!

---

## ✨ Step 5: Test Your Live App (1 min)

1. Go to: `https://leapwp-YOUR_USERNAME.vercel.app`
2. Click "Register"
3. Create test account:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `testpass123`
4. Login and explore!

✓ Your app is live! 🎉

---

## 📊 Check App Status

Visit these endpoints to check your app:

```
Health check:
https://leapwp-YOUR_USERNAME.vercel.app/admin/health

Database status:
https://leapwp-YOUR_USERNAME.vercel.app/admin/db-status
```

---

## 🔄 Making Updates

After deployment, to update your app:

```bash
cd D:\leapWP

# Make changes to code

# Commit and push
git add .
git commit -m "Description of changes"
git push origin main

# Vercel automatically redeploys!
# Check dashboard for progress
```

---

## ❌ Troubleshooting

### "Deployment failed"
→ Check Vercel Logs:
- Dashboard → Project → Deployments → [latest] → Logs

### "Database connection error"
→ Verify:
- [ ] `DATABASE_URL` is set in Vercel
- [ ] Connection string copied correctly from Neon
- [ ] `/admin/health` endpoint works

### "Page not found"
→ Wait a few minutes, Vercel might still be deploying
→ Hard refresh: Ctrl+Shift+R

### "ImportError"
→ Check that `requirements.txt` exists in root
→ Redeploy from Vercel dashboard

---

## 📱 Share Your App

Your app is now live! Share the URL:
```
https://leapwp-YOUR_USERNAME.vercel.app
```

---

## 💰 Costs

- **Vercel**: FREE (100GB/month bandwidth)
- **Neon**: FREE (512MB storage)
- **Total**: $0/month ✓

---

## 📚 Need More Help?

Read these files:
- `DEPLOY_INSTRUCTIONS.md` - Quick summary
- `VERCEL_DEPLOYMENT.md` - Detailed guide
- `VERCEL_READY.md` - Comprehensive overview

---

## ✅ Done!

Your Leap IELTS app is now live on the internet!

**Next steps:**
1. Share your URL with friends
2. Continue developing locally
3. Changes auto-deploy when pushed to GitHub
4. Monitor at https://vercel.com dashboard

---

**Deployed with:** Flask + SQLAlchemy + Neon PostgreSQL + Vercel 🚀
