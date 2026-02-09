# TTMS (Timetable Management System) - Deployment Guide

## Prerequisites

- Python 3.7+
- MySQL Server 5.7+
- Git (optional, for version control)
- A Linux/Unix server OR Windows Server (production)

## Pre-Deployment Checklist

- [ ] Database is set up and running with schema imported
- [ ] All environment variables are configured in `.env`
- [ ] `SECRET_KEY` is set to a strong, random value
- [ ] Database credentials are valid and tested
- [ ] SSL/TLS certificates obtained (if using HTTPS)
- [ ] Firewall rules configured (port 5000 or 8000)
- [ ] Application has been tested locally in development mode

## Step 1: Install Dependencies

```bash
# Navigate to project directory
cd /path/to/TTMS

# Install all required Python packages
pip install -r backend/requirement.txt
```

## Step 2: Configure Environment Variables

### Create .env file from template

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env with your production values
nano .env
```

### Essential Environment Variables

```
FLASK_ENV=production
FLASK_APP=backend/app.py
SECRET_KEY=your-super-secret-key-generate-with-os.urandom(32)
DB_HOST=your-database-host
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_NAME=timetable_db4
PORT=8000
```

### Generate a Strong SECRET_KEY

```bash
python -c "import os; print(os.urandom(32).hex())"
```

Copy the output and set it in your `.env` file.

## Step 3: Database Setup

### Import Schema

```bash
# Connect to MySQL and run schema
mysql -h DB_HOST -u DB_USER -p DB_NAME < database/schema.sql
```

### Verify Database Connection

```bash
python -c "
import os
from dotenv import load_dotenv
import pymysql
load_dotenv()

conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)
print('✓ Database connection successful')
conn.close()
"
```

## Step 4: Run Application with Gunicorn (Recommended)

### Option A: Using Gunicorn (Linux/Mac/Windows WSL)

```bash
# Using gunicorn config file
gunicorn -c gunicorn_config.py backend.app:app

# Or with custom parameters
gunicorn \
  --workers 4 \
  --worker-class sync \
  --bind 0.0.0.0:8000 \
  --timeout 30 \
  --access-logfile - \
  --error-logfile - \
  backend.app:app
```

### Option B: Using Waitress (Windows Recommended)

```bash
# Install waitress
pip install waitress

# Run with waitress
waitress-serve \
  --host=0.0.0.0 \
  --port=8000 \
  --threads=4 \
  backend.app:app
```

### Option C: Using Flask Development Server (NOT for Production)

```bash
# Only for testing - NOT RECOMMENDED for production
python backend/app.py
```

## Step 5: Process Management (Linux/Mac)

### Using systemd Service

Create `/etc/systemd/system/timetable.service`:

```ini
[Unit]
Description=TTMS - Timetable Management System
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/TTMS
Environment="PATH=/path/to/TTMS/.venv/bin"
EnvironmentFile=/path/to/TTMS/.env
ExecStart=/path/to/TTMS/.venv/bin/gunicorn -c /path/to/TTMS/gunicorn_config.py backend.app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGTERM
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable timetable
sudo systemctl start timetable
sudo systemctl status timetable
```

### Using Supervisor

Create `/etc/supervisor/conf.d/timetable.conf`:

```ini
[program:timetable]
directory=/path/to/TTMS
command=/path/to/TTMS/.venv/bin/gunicorn -c /path/to/TTMS/gunicorn_config.py backend.app:app
autostart=true
autorestart=true
stderr_logfile=/var/log/timetable/err.log
stdout_logfile=/var/log/timetable/out.log
user=www-data
environment=FLASK_ENV=production,DB_HOST=localhost
```

Reload supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start timetable
```

## Step 6: Reverse Proxy Setup (Nginx)

### Create Nginx Config

Create `/etc/nginx/sites-available/timetable`:

```nginx
upstream timetable_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    client_max_body_size 20M;

    # Redirect HTTP to HTTPS (optional but recommended)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://timetable_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /path/to/TTMS/static/;
        expires 30d;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/timetable /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 7: SSL/TLS Setup (HTTPS)

### Using Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d your-domain.com

# Update nginx config to use SSL
sudo certbot --nginx -d your-domain.com
```

Update Nginx config for HTTPS:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## Step 8: Verify Deployment

### Check Application Status

```bash
# Check if service is running
sudo systemctl status timetable

# Check logs
sudo journalctl -u timetable -f

# Test endpoint
curl -I http://localhost:8000/
curl -I https://your-domain.com/
```

### Performance Testing

```bash
# Using Apache Bench
ab -n 100 -c 10 http://localhost:8000/

# Using wrk (install wrk first)
wrk -t4 -c100 -d30s http://localhost:8000/
```

## Step 9: Monitoring and Logging

### Set Up Log Rotation

Create `/etc/logrotate.d/timetable`:

```
/var/log/timetable/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### Monitor System Health

```bash
# View real-time logs
tail -f /var/log/timetable/out.log
tail -f /var/log/timetable/err.log

# Check process
ps aux | grep gunicorn

# Check disk space
df -h

# Check memory usage
free -h
```

## Troubleshooting

### Application Won't Start

1. Check environment variables:
   ```bash
   cat .env
   ```

2. Check database connection:
   ```bash
   mysql -h DB_HOST -u DB_USER -p DB_NAME -e "SELECT 1;"
   ```

3. Check logs:
   ```bash
   journalctl -u timetable -n 50
   ```

### High Memory Usage

- Reduce `--workers` in gunicorn
- Check for database query issues
- Monitor with `top` or `htop`

### Database Connection Errors

```bash
# Test connection
python -c "
import pymysql
conn = pymysql.connect(host='localhost', user='root', password='pwd', database='db')
print('Connected')
"
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process if needed
kill -9 <PID>
```

## Security Best Practices

1. **Change Default Credentials**: Update any default usernames/passwords in database
2. **Use HTTPS**: Always use SSL/TLS in production
3. **Keep Dependencies Updated**: Run `pip install --upgrade -r requirements.txt` regularly
4. **Database Security**:
   - Use strong passwords
   - Restrict database access to application server only
   - Regular backups
5. **Application Security**:
   - Review logs regularly
   - Monitor for suspicious activity
   - Keep Flask and dependencies updated
6. **Server Security**:
   - Use firewall rules
   - SSH key authentication (disable password SSH)
   - Automatic security updates enabled

## Backup and Recovery

### Database Backup

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -h DB_HOST -u DB_USER -p DB_PASSWORD DB_NAME > $BACKUP_DIR/db_$DATE.sql
gzip $BACKUP_DIR/db_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup-script.sh
```

### Database Restore

```bash
mysql -h DB_HOST -u DB_USER -p DB_NAME < backup.sql
```

## Performance Optimization

1. **Database**: Index frequently queried columns
2. **Gunicorn**: Adjust workers based on CPU cores
3. **Nginx**: Enable gzip compression
4. **Caching**: Consider redis for session management

## Support and Maintenance

- Monitor application daily
- Review logs for errors
- Check disk space regularly
- Test database backups periodically
- Plan regular maintenance windows

---

**Version**: 1.0  
**Last Updated**: 2026-01-28  
**Maintainer**: [Your Name/Organization]
