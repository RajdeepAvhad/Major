# ⚡ Quick Start: PostgreSQL Migration

## 🚀 5-Minute Migration Guide

### **Prerequisites:**
- NeonDB account (sign up at https://neon.tech/)
- Backup of your SQLite database

---

## 📝 Quick Steps

### **1. Backup (30 seconds)**
```bash
copy db.sqlite3 db.sqlite3.backup
```

### **2. Export Data (1 minute)**
```bash
python scripts/export_sqlite.py
```
✅ Creates `fixtures/initial_data.json`

### **3. Get NeonDB Connection String (2 minutes)**
1. Go to https://console.neon.tech/
2. Create project → Create database
3. Copy connection string from dashboard

Example:
```
postgresql://user:pass@ep-xxx.region.aws.neon.tech/eatright?sslmode=require
```

### **4. Configure Environment (30 seconds)**
Edit `.env` file:
```env
DATABASE_URL=postgresql://your-connection-string-here
```

### **5. Install & Migrate (1 minute)**
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py load_initial_data
```

### **6. Test (30 seconds)**
```bash
python manage.py runserver
```
Visit http://127.0.0.1:8000/admin/

---

## ✅ Done!

Your app is now running on PostgreSQL!

---

## 🔄 Rollback (if needed)

```bash
# Remove DATABASE_URL from .env
# Restore backup
copy db.sqlite3.backup db.sqlite3
# Restart server
python manage.py runserver
```

---

## 📚 Need More Details?

See `MIGRATION_GUIDE.md` for comprehensive instructions.

---

## 🆘 Common Issues

**"No module named 'psycopg2'"**
```bash
pip install psycopg2-binary
```

**"No module named 'dj_database_url'"**
```bash
pip install dj-database-url
```

**"Connection failed"**
- Check DATABASE_URL format
- Ensure `?sslmode=require` at end
- Verify NeonDB project is active

**"Fixture not found"**
```bash
python scripts/export_sqlite.py
```

---

## 📊 What Changed?

- ✅ Database: SQLite → PostgreSQL
- ✅ JSON storage: TextField → JSONField
- ✅ Performance: Added 8 indexes
- ✅ Scalability: Connection pooling enabled

---

## 🎯 Next Steps

1. Test all features
2. Monitor NeonDB dashboard
3. Deploy to production
4. Set up automated backups

---

*Quick Start Guide - EatRight PostgreSQL Migration*
