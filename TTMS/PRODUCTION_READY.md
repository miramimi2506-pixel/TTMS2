# TTMS (Timetable Management System) - Deployment Ready

## 📋 What's Changed for Production

✅ **Debug mode disabled** - Flask runs in production mode  
✅ **Debug statements removed** - All `print()` debug calls cleaned up  
✅ **Environment variables** - DB credentials moved to `.env` file  
✅ **Gunicorn ready** - WSGI server config included  
✅ **Security hardened** - No hardcoded credentials in code  
✅ **Comprehensive docs** - Full deployment guides included

---

## 🚀 Deploy in 3 Steps

### Step 1: Setup Environment
```bash
cp .env.example .env
# Edit .env with your actual database credentials
nano .env
```

### Step 2: Install & Test
```bash
pip install -r backend/requirement.txt
python production_check.sh  # Run checklist
```

### Step 3: Run Application
```bash
# Production with Gunicorn (Linux/Mac)
gunicorn --workers 4 --bind 0.0.0.0:8000 backend.app:app

# Or Windows with Waitress
waitress-serve --host=0.0.0.0 --port=8000 backend.app:app
```

Visit: `http://your-server:8000`

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| [QUICKSTART.md](QUICKSTART.md) | 5-minute deployment guide |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Complete deployment manual |
| [production_check.sh](production_check.sh) | Pre-deployment checklist script |
| [.env.example](.env.example) | Environment variables template |
| [gunicorn_config.py](gunicorn_config.py) | Production server configuration |

---

## ✨ Key Features

- **Distributed Subject Allocation** - No back-to-back same subjects
- **Constraint Management** - Staff/room/course conflict prevention
- **Max 2-per-day Cap** - Limits same subject allocations per day
- **Dynamic Period Support** - Works with P1-P7 (or more)
- **Responsive Design** - Mobile-friendly interface
- **Master Timetable** - Admin view of all allocations
- **Print-Optimized** - A4 sheet fitting with legend deduplication

---

## 🔒 Security Improvements

| Item | Status |
|------|--------|
| Debug mode | ✅ Disabled in production |
| Debug prints | ✅ All removed |
| Hardcoded credentials | ✅ Removed (using .env) |
| SECRET_KEY | ✅ Configurable via environment |
| Database access | ✅ Via environment variables |
| HTTPS ready | ✅ Reverse proxy support included |

---

## 📊 System Requirements

**Minimum:**
- Python 3.7+
- MySQL 5.7+
- 1 CPU core
- 512 MB RAM
- 1 GB disk space

**Recommended for Production:**
- Python 3.9+
- MySQL 8.0+
- 2+ CPU cores
- 2+ GB RAM
- Gunicorn + Nginx
- SSL/TLS (HTTPS)

---

## ⚙️ Configuration

### Required Environment Variables (in `.env`)
```
FLASK_ENV=production          # Must be 'production'
SECRET_KEY=<strong-random>    # Generate with: python -c "import os; print(os.urandom(32).hex())"
DB_HOST=localhost             # Your database host
DB_USER=root                  # Database user
DB_PASSWORD=your-password     # Database password
DB_NAME=timetable_db4         # Database name
```

### Optional Environment Variables
```
PORT=8000                     # Server port (default: 5000)
FLASK_DEBUG=0                 # Always set to 0 for production
GUNICORN_WORKERS=4            # Number of gunicorn workers
GUNICORN_BIND=0.0.0.0:8000    # Server bind address
```

---

## 🔍 Pre-Deployment Checklist

- [ ] Copy `.env.example` to `.env`
- [ ] Update `.env` with your credentials
- [ ] Run `pip install -r backend/requirement.txt`
- [ ] Run `python production_check.sh` (all checks pass)
- [ ] Test database connection
- [ ] Verify no `print()` statements in logs
- [ ] Check FLASK_ENV is set to 'production'
- [ ] Set strong SECRET_KEY
- [ ] Review DEPLOYMENT.md for your platform
- [ ] Set up reverse proxy (Nginx recommended)
- [ ] Configure SSL/TLS if needed
- [ ] Set up automated backups
- [ ] Configure monitoring/logging

---

## 🚨 Troubleshooting

**App won't start?**
```bash
# Check environment variables
cat .env

# Check database connection
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "USE $DB_NAME; SHOW TABLES;"

# Check logs
journalctl -u timetable -f  # If using systemd
```

**Getting 502 errors?**
```bash
# Check Gunicorn logs
journalctl -u gunicorn -f

# Check Nginx logs
tail -f /var/log/nginx/error.log
```

**Database connection issues?**
```bash
# Verify credentials
python3 -c "
import pymysql
import os
from dotenv import load_dotenv
load_dotenv()

conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)
print('✓ Connected')
"
```

---

## 📈 Scaling & Performance

For high-traffic deployments:

1. **Database optimization**
   - Add indexes on frequently queried columns
   - Enable query caching
   - Regular VACUUM/OPTIMIZE

2. **Application scaling**
   - Increase Gunicorn workers (4-12 per CPU core)
   - Use load balancer (HAProxy, Nginx)
   - Consider caching (Redis)

3. **Infrastructure**
   - Database replication
   - Horizontal scaling with load balancer
   - CDN for static files

---

## 📞 Support

### Common Tasks

**View logs:**
```bash
# Systemd service
sudo journalctl -u timetable -f -n 100

# Direct gunicorn
tail -f /var/log/timetable/*.log
```

**Restart application:**
```bash
sudo systemctl restart timetable
```

**Check status:**
```bash
sudo systemctl status timetable
```

**Stop application:**
```bash
sudo systemctl stop timetable
```

---

## 📝 Release Notes

**Version 1.0 - Production Ready**
- ✅ Removed all debug statements
- ✅ Environment-based configuration
- ✅ Gunicorn WSGI server support
- ✅ Comprehensive deployment guides
- ✅ Production security hardening
- ✅ Pre-deployment checklist script

---

## 🔗 Quick Links

- [QUICKSTART.md](QUICKSTART.md) - Fast deployment guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Full documentation
- [.env.example](.env.example) - Configuration template
- [gunicorn_config.py](gunicorn_config.py) - Server settings
- Flask Docs: https://flask.palletsprojects.com/
- Gunicorn Docs: https://gunicorn.org/

---

**Last Updated:** January 28, 2026  
**Status:** ✅ Production Ready  
**Next Review:** Upon deployment
