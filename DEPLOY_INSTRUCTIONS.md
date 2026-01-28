# Deploy Leap IELTS to Vercel - Quick Instructions

## What You'll Have After Deploying

✓ Live web application accessible from anywhere
✓ Free PostgreSQL database (Neon)
✓ Automatic HTTPS/SSL
✓ Auto-deploys when you push code to GitHub
✓ Production-ready infrastructure

## 5-Minute Quick Start

### 1. Push to GitHub

```bash
cd D:\leapWP
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Create Neon Database (2 min)

1. Go to https://neon.tech
2. Sign up with GitHub
3. Create project "leap-ielts"
4. Copy connection string: `postgresql://...`

### 3. Deploy on Vercel (2 min)

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repo
4. Add environment variables:
   ```
   FLASK_ENV=production
   SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
   DATABASE_URL=<paste Neon connection string>
   ```
5. Click Deploy

### 4. Initialize Database (30 sec)

Visit (once): `https://your-app.vercel.app/admin/init-db`

Done! Your app is live! 🚀

---

## Detailed Instructions

See **VERCEL_DEPLOYMENT.md** for step-by-step guide with troubleshooting.

## What Happens

1. **You**: Push code to GitHub
2. **GitHub**: Webhook notifies Vercel
3. **Vercel**:
   - Installs dependencies from requirements.txt
   - Starts Flask app using wsgi.py
   - Creates serverless functions
4. **Your App**: Live at `https://project-name.vercel.app`

## Updates

After deployment, to make changes:

```bash
# Edit files locally
# Then:
git add .
git commit -m "Updated feature X"
git push origin main
# Vercel automatically redeploys!
```

## Costs

- **Vercel**: FREE
- **Neon**: FREE (up to 3 projects, 512MB storage)
- **Total**: $0/month ✓

## Testing Live App

1. Visit https://your-app.vercel.app
2. Register a new account
3. Try features:
   - Login/logout
   - View dashboard
   - Check profile
   - Browse activities (scaffolding shows "coming soon")

## Database Status

Check your database health:
```
https://your-app.vercel.app/admin/health
https://your-app.vercel.app/admin/db-status
```

## If Something Goes Wrong

1. Check Vercel logs: Dashboard → Project → Deployments → [latest] → Logs
2. Check database: Visit `/admin/db-status` endpoint
3. Verify environment variables are set
4. Make sure requirements.txt is current

## Files Added for Deployment

- `vercel.json` - Vercel configuration
- `requirements.txt` - Python dependencies
- `.vercelignore` - Files to exclude
- `VERCEL_DEPLOYMENT.md` - Full guide
- Admin routes for database initialization

## Next Steps

1. Follow 5-minute quickstart above
2. Test app at live URL
3. Share link with others
4. Continue development locally
5. Changes auto-deploy when pushed

**Need help?** See VERCEL_DEPLOYMENT.md for detailed troubleshooting.
