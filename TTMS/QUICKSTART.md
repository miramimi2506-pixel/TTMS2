# TTMS Production Deployment Quick Start

## 🚀 Quick 5-Minute Setup

### 1. Prepare Your Environment

```bash
cd /path/to/TTMS

# Create .env file
cp .env.example .env

# Edit with your actual values
nano .env
```

**Minimum required in .env:**
```
FLASK_ENV=production
SECRET_KEY=<run: python -c "import os; print(os.urandom(32).hex())">
DB_HOST=your-host
DB_USER=your-user
DB_PASSWORD=your-password
DB_NAME=timetable_db4
```

### 2. Install Dependencies

```bash
pip install -r backend/requirement.txt
```

### 3. Test Database Connection

```bash
python -c "import os; from dotenv import load_dotenv; import pymysql; load_dotenv(); conn = pymysql.connect(host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')); print('✓ Database OK'); conn.close()"
```

### 4. Run Application

**Option A - Linux/Mac (Recommended):**
```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 backend.app:app
```

**Option B - Windows:**
```bash
waitress-serve --host=0.0.0.0 --port=8000 backend.app:app
```

**Option C - Development (Testing Only):**
```bash
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
python backend/app.py
```

### 5. Access Application

- Visit: `http://your-server:8000`
- Default credentials: Check your database users table

## ⚠️ Pre-Deployment Checklist

### Security
- [ ] `FLASK_ENV=production` in .env
- [ ] `SECRET_KEY` is a strong random string (not default)
- [ ] Database password is strong
- [ ] `.env` file is NOT committed to git
- [ ] `.env` file permissions: `chmod 600 .env`

### Configuration
- [ ] Database connection works (test with step 3 above)
- [ ] All required tables exist in database
- [ ] Static files path is correct
- [ ] Template files path is correct

### Application
- [ ] No debug print statements in code ✓
- [ ] Flask debug mode is OFF ✓
- [ ] Error handling is in place ✓
- [ ] Logging is configured

### Infrastructure
- [ ] Firewall allows traffic on port 8000 (or configured port)
- [ ] Database is accessible from app server
- [ ] Backup strategy is in place
- [ ] Monitoring/alerting is set up (optional)

### Optional but Recommended
- [ ] HTTPS/SSL configured
- [ ] Nginx reverse proxy set up
- [ ] Systemd/Supervisor service created
- [ ] Log rotation configured
- [ ] Automated backups scheduled

## 🔧 Common Configurations

### Using Nginx as Reverse Proxy

```nginx
upstream app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/TTMS/static/;
    }
}
```

### Run as System Service (Linux)

Create `/etc/systemd/system/timetable.service`:

```ini
[Unit]
Description=TTMS Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/TTMS
EnvironmentFile=/path/to/TTMS/.env
ExecStart=/usr/local/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 backend.app:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable timetable
sudo systemctl start timetable
```

## 📊 Performance Tuning

### Gunicorn Workers
- **CPU-bound**: workers = (2 × CPU cores) + 1
- **I/O-bound**: workers = (4-12 × CPU cores)

### Database Connections
- Monitor MySQL: `SHOW STATUS LIKE 'Threads_connected';`
- Adjust connection pool if needed

### Nginx Settings
```nginx
# Enable gzip compression
gzip on;
gzip_types text/plain text/css application/json;

# Cache static files
expires 30d;
add_header Cache-Control "public, immutable";
```

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| App won't start | Check `.env` file and database connection |
| 502 Bad Gateway | Check gunicorn logs: `journalctl -u timetable -f` |
| Database errors | Verify DB credentials: `mysql -u user -p database` |
| Slow performance | Check query logs: `SET GLOBAL slow_query_log = 'ON';` |
| Port already in use | `lsof -i :8000` to find process, `kill -9 PID` |

## 📝 After Deployment

1. **Test the application** - Try login and basic operations
2. **Check logs** - Look for any errors or warnings
3. **Monitor resources** - Watch CPU, memory, and disk usage
4. **Set up monitoring** - Consider Datadog, New Relic, or Prometheus
5. **Plan backups** - Test restore process before issues occur

## 📖 For Detailed Information

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide.

---

**Need Help?**
- Check logs: Application will write to stderr/stdout
- Test locally first in development mode
- Verify database schema: `DESCRIBE timetable;`
- Review Flask documentation: https://flask.palletsprojects.com/
