# PostgreSQL Migration Setup Guide

## Summary
Your TTMS application has been migrated from MySQL (InfinityFree) to PostgreSQL (Render). This fixes the connection issue.

## What Changed
- **Database**: MySQL → PostgreSQL
- **Python driver**: `pymysql` → `psycopg2`
- **Schema**: Updated to PostgreSQL syntax (database/schema_postgres.sql)

## Step-by-Step Deployment Instructions

### 1. Create PostgreSQL Database on Render

1. Go to [render.com](https://render.com)
2. Click **+ New** → **PostgreSQL**
3. Fill in:
   - **Name**: `ttms-db`
   - **Database**: `timetable_db`
   - **Region**: Select closest region
   - **PostgreSQL Version**: 15
   - **Plan**: Free
4. Click **Create Database**
5. Wait 2-3 minutes for initialization
6. Copy the **Internal Database URL** (looks like: `postgresql://user:password@hostname:5432/database`)

### 2. Update Your Render Service Environment Variables

1. Go to your TTMS service on Render
2. Click **Environment** (or Settings → Environment)
3. Add these variables:

```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=<paste your Internal Database URL here>
```

4. Click **Save** - service will auto-redeploy

### 3. Initialize Database Schema

After Render redeploys (2-3 minutes), run the SQL setup script:

1. Go to your PostgreSQL database on Render
2. Click **Connect** → **PSQL**
3. Copy and paste the contents of `database/schema_postgres.sql`
4. Execute the SQL commands

### 4. Deploy Your Updated Code

Your code changes are ready:
- Updated `requirements.txt` (psycopg2 instead of pymysql)
- Updated `backend/app.py` (PostgreSQL connection)
- New PostgreSQL schema file provided

Push to GitHub/trigger redeploy and Render will install dependencies and start your app.

### 5. Test the Deployment

Visit your Render URL (e.g., `https://timetable-2-rqxg.onrender.com`)

Expected behavior:
- Login page loads (database connection successful)
- No 500 errors
- Can log in with credentials

## Local Development (Optional)

If you want to test locally with PostgreSQL:

1. Install PostgreSQL locally
2. Create a database: `createdb timetable_db`
3. Set `.env` with: `DATABASE_URL=postgresql://postgres:password@localhost:5432/timetable_db`
4. Run schema setup: `psql timetable_db < database/schema_postgres.sql`
5. Install packages: `pip install -r requirements.txt`
6. Run: `python backend/app.py`

## Troubleshooting

**Issue: "Can't connect to PostgreSQL"**
- Verify DATABASE_URL environment variable is set correctly
- Check it matches your Render PostgreSQL Internal URL
- Make sure database is created and initialized with schema

**Issue: "relation does not exist"**
- Run the SQL schema script: `database/schema_postgres.sql`
- Ensure all tables are created

**Issue: "No module named 'pymysql'"**
- This is fixed by the updated requirements.txt
- Render will install psycopg2 automatically on redeploy

## Security Notes

- Never commit `.env` with real credentials
- Update `SECRET_KEY` to a random value in production
- Render's free PostgreSQL database is suitable for development/testing
- For production, consider upgrading to a paid Render database or other provider
