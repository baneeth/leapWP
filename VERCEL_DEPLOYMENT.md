# Vercel Deployment Guide - Leap IELTS

## Prerequisites

You'll need:
1. **GitHub account** (Vercel deploys from Git)
2. **Vercel account** (free at vercel.com)
3. **Neon account** (free PostgreSQL database)

## Step-by-Step Deployment

### Step 1: Create GitHub Repository

```bash
cd D:\leapWP

# Initialize git (if not done)
git init
git config user.name "Your Name"
git config user.email "your@email.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Leap IELTS Engagement System"

# Create repo on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/leapWP.git
git branch -M main
git push -u origin main
```

### Step 2: Create Neon PostgreSQL Database

1. Go to **https://neon.tech**
2. Sign up with GitHub (recommended)
3. Create a new project: "leap-ielts"
4. Create a database: "leap_ielts_db"
5. Copy the connection string (looks like):
   ```
   postgresql://user:password@ep-xxxxx.us-east-1.neon.tech/leap_ielts_db?sslmode=require
   ```

### Step 3: Deploy to Vercel

1. Go to **https://vercel.com**
2. Sign up with GitHub
3. Click "New Project"
4. Select your **leapWP** repository
5. Click "Import"

#### Configure Environment Variables

In the "Environment Variables" section, add:

```
FLASK_ENV=production
SECRET_KEY=<generate-a-random-secret-key>
DATABASE_URL=<your-neon-connection-string>
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

**Generate Secret Key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Deploy Settings

- **Framework Preset**: Other
- **Root Directory**: ./
- **Build Command**: (leave empty - Vercel detects Python)
- **Output Directory**: (leave empty)
- **Install Command**: `pip install -r requirements.txt`

Click **Deploy** and wait 2-3 minutes.

### Step 4: Initialize Database on Vercel

After deployment succeeds, you need to initialize the database:

```bash
# SSH into Vercel instance (or use Functions)
# Create a setup script that runs once
```

**Better approach:** Create a simple initialization endpoint:

Create `src/leap_ielts/web/admin_routes.py`:

```python
from flask import Blueprint, jsonify
from flask_sqlalchemy import SQLAlchemy
from leap_ielts.data.models import Base

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/init-db', methods=['POST'])
def init_db():
    """Initialize database (run once after deployment)."""
    from leap_ielts.web.app import db

    try:
        db.create_all()
        return jsonify({
            "status": "success",
            "message": "Database initialized"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
```

Register in `src/leap_ielts/web/app.py`:

```python
from leap_ielts.web.blueprints import auth_bp, dashboard_bp, activity_bp
from leap_ielts.web.admin_routes import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(activity_bp)
app.register_blueprint(admin_bp)  # Add this
```

Then visit (once after deployment):
```
https://your-app.vercel.app/admin/init-db
```

### Step 5: Access Your Application

Your app is now live at:
```
https://your-project-name.vercel.app
```

Test it:
1. Visit the homepage
2. Register a new account
3. Login and explore

## Updating Your Application

After making changes locally:

```bash
cd D:\leapWP

# Commit and push
git add .
git commit -m "Description of changes"
git push origin main
```

**Vercel automatically redeploys** when you push to main!

## Troubleshooting

### Database Connection Issues

If you see database errors:

1. Verify `DATABASE_URL` in Vercel settings
2. Check Neon connection string format
3. Try adding `?sslmode=require` to connection string
4. Restart deployment in Vercel dashboard

### Build Fails

Check the Vercel logs:
1. Go to Vercel dashboard
2. Click your project
3. Go to "Deployments"
4. Click failed deployment
5. Click "Runtime Logs" tab

Common issues:
- Missing dependencies in `requirements.txt`
- Import errors
- Invalid config

### Application Errors

Check production logs:
1. In Vercel dashboard
2. Click project
3. Go to "Functions" tab
4. Click `wsgi.py`
5. See real-time logs

## Performance Notes

- **Cold starts**: First request may take 5-10 seconds (normal for serverless)
- **Session timeout**: Sessions last 24 hours (reset on app restart)
- **File storage**: Use database, not files (filesystem is ephemeral)
- **Background tasks**: APScheduler won't work well; use external scheduler

## What's Deployed

✓ Full Flask application
✓ All algorithms and services
✓ Web interface (registration, login, dashboard)
✓ SQLAlchemy ORM with PostgreSQL
✓ User authentication
✓ Activity system

✗ CLI interface (not accessible via web)
✗ Background schedulers (would need Cron service)
✗ Local database file (uses Neon PostgreSQL instead)

## Database Backups

Neon provides automated backups. To manually backup:

```bash
# Using psql (install from postgresql.org)
psql "postgresql://user:password@host/db" \
  -c "COPY (SELECT * FROM \"user\") TO STDOUT WITH CSV" > users_backup.csv
```

## Costs

- **Vercel**: Free tier includes:
  - 100 GB bandwidth/month
  - Unlimited deployments
  - Serverless functions

- **Neon**: Free tier includes:
  - 3 projects
  - 512 MB storage
  - Automatic backups

Both services are completely free for this application!

## Production Improvements

For a real production app, consider:

1. **Custom Domain**: Add in Vercel settings ($0 if you own domain)
2. **SSL/HTTPS**: Automatic with Vercel
3. **CDN**: Vercel edge network included
4. **Email Service**: SendGrid for password resets
5. **Analytics**: Vercel Analytics dashboard
6. **Monitoring**: Sentry for error tracking

## Reverting to Local Development

If you want to go back to local development:

```bash
# Switch back to SQLite
# Edit .env to not set DATABASE_URL
# Run locally with: flask run
```

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Neon Docs**: https://neon.tech/docs
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/

---

**Your app is now live on the internet!** 🚀
