# 🚀 EatRight Database Migration Guide
## SQLite3 → NeonDB PostgreSQL

This guide walks you through migrating your EatRight database from SQLite3 to NeonDB (serverless PostgreSQL).

---

## 📋 Prerequisites

- Python 3.8+
- Existing EatRight project with SQLite database
- NeonDB account (free tier available at https://neon.tech/)
- All data backed up (recommended)

---

## 🎯 Migration Overview

### What's Changed:

1. **Database**: SQLite3 → PostgreSQL (NeonDB)
2. **SavedDiet.selected_items**: TextField (JSON string) → JSONField (native JSON)
3. **WaterLog.log_date**: Added database index for performance
4. **FavoriteFood**: Added composite indexes
5. **Dependencies**: Added `psycopg2-binary` and `dj-database-url`

### Why Migrate?

- **Scalability**: PostgreSQL handles concurrent users better
- **Performance**: Native JSON support, better indexing
- **Features**: Advanced querying, full-text search, JSON operations
- **Serverless**: NeonDB auto-scales and has generous free tier
- **Production-ready**: Better for deployment

---

## 📝 Step-by-Step Migration

### **Step 1: Backup Your Current Database**

```bash
# Backup SQLite database
copy db.sqlite3 db.sqlite3.backup

# Or use timestamp
copy db.sqlite3 db_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.sqlite3
```

---

### **Step 2: Export Existing Data**

```bash
# Make sure DATABASE_URL is NOT set (to use SQLite)
python scripts/export_sqlite.py
```

This creates `fixtures/initial_data.json` with all your data.

**Expected output:**
```
✓ Database engine: django.db.backends.sqlite3
📦 Exporting data to: fixtures/initial_data.json
✅ Export completed successfully!
   File size: XX.XX KB
📊 Exported records:
   auth.user: 4 records
   recommender.food: 89 records
   recommender.saveddiet: 9 records
   ...
```

---

### **Step 3: Set Up NeonDB**

1. **Sign up at https://neon.tech/**
   - Free tier includes: 0.5 GB storage, 1 compute unit
   - No credit card required

2. **Create a new project**
   - Choose a region close to your users
   - Project name: `eatright` (or your preference)

3. **Create a database**
   - Database name: `eatright`
   - Owner: (default user)

4. **Get connection string**
   - Go to Dashboard → Connection Details
   - Copy the connection string
   - Format: `postgresql://user:password@host/database?sslmode=require`

**Example:**
```
postgresql://eatright_user:AbCdEf123456@ep-cool-darkness-123456.us-east-2.aws.neon.tech/eatright?sslmode=require
```

---

### **Step 4: Update Environment Variables**

1. **Copy `.env.example` to `.env`** (if you haven't already):
   ```bash
   copy .env.example .env
   ```

2. **Add your NeonDB connection string to `.env`**:
   ```env
   DATABASE_URL=postgresql://user:password@host/database?sslmode=require
   ```

3. **Verify other variables**:
   ```env
   # Optional: AI chatbot keys
   GROQ_API_KEY=your_groq_key_here
   OPENAI_API_KEY=your_openai_key_here
   
   # Django settings
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   ```

---

### **Step 5: Install PostgreSQL Dependencies**

```bash
pip install -r requirements.txt
```

This installs:
- `psycopg2-binary` - PostgreSQL adapter
- `dj-database-url` - Database URL parser

---

### **Step 6: Run Migrations**

```bash
# Apply all migrations to PostgreSQL
python manage.py migrate
```

**Expected output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, recommender, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying recommender.0008_migrate_to_postgresql... OK
```

**What this does:**
- Creates all tables in PostgreSQL
- Converts `selected_items` to JSONField
- Adds performance indexes
- Sets up database constraints

---

### **Step 7: Load Your Data**

```bash
python manage.py load_initial_data
```

**Interactive prompts:**
```
📦 Fixture file: fixtures/initial_data.json
📊 Records to import:
   auth.user: 4 records
   recommender.food: 89 records
   ...

⚠️  WARNING: This will load data into the database!
Do you want to continue? [y/N]: y
```

**Or skip confirmation:**
```bash
python manage.py load_initial_data --skip-confirmation
```

---

### **Step 8: Verify Migration**

```bash
# Open Django shell
python manage.py shell
```

```python
# Check data
from recommender.models import Food, SavedDiet, User

print(f"Users: {User.objects.count()}")
print(f"Foods: {Food.objects.count()}")
print(f"Saved Diets: {SavedDiet.objects.count()}")

# Test JSONField
diet = SavedDiet.objects.first()
print(f"Selected items type: {type(diet.selected_items)}")
print(f"Selected items: {diet.selected_items}")

# Should be <class 'list'>, not <class 'str'>
```

---

### **Step 9: Create Superuser (Optional)**

```bash
python manage.py createsuperuser
```

Follow prompts to create admin account.

---

### **Step 10: Test the Application**

```bash
# Start Django server
python manage.py runserver

# In another terminal, start React
cd frontend
npm run dev
```

**Test these features:**
1. Login/Signup
2. Diet Planner (save a diet)
3. Diet History (view saved diets)
4. Dashboard (check charts)
5. AI Chatbot
6. Water Tracker
7. Favorites

---

## 🔍 Troubleshooting

### **Error: "No module named 'psycopg2'"**

```bash
pip install psycopg2-binary
```

### **Error: "No module named 'dj_database_url'"**

```bash
pip install dj-database-url
```

### **Error: "connection to server failed"**

- Check DATABASE_URL format
- Ensure `?sslmode=require` is at the end
- Verify NeonDB project is active
- Check firewall/network settings

### **Error: "Fixture file not found"**

```bash
# Run export script first
python scripts/export_sqlite.py
```

### **Data not loading correctly**

```bash
# Check fixture file
cat fixtures/initial_data.json

# Try loading with verbose output
python manage.py loaddata fixtures/initial_data.json --verbosity=2
```

### **Want to switch back to SQLite?**

```bash
# Remove DATABASE_URL from .env
# Or comment it out:
# DATABASE_URL=postgresql://...

# Restart server
python manage.py runserver
```

---

## 📊 Performance Improvements

### **New Indexes Added:**

1. **SavedDiet**:
   - `created_at` (descending) - faster recent diet queries
   - `user + period` - faster user-specific period queries
   - `session_key + period` - faster guest user queries

2. **WaterLog**:
   - `log_date` - faster date lookups
   - `user + log_date` - faster user water history
   - `session_key + log_date` - faster guest water logs

3. **FavoriteFood**:
   - `user + food` - faster favorite checks
   - `session_key + food` - faster guest favorites

### **JSONField Benefits:**

- **Native JSON queries**: Filter by JSON content
- **Better performance**: No JSON parsing overhead
- **Type safety**: Django validates JSON structure
- **PostgreSQL features**: JSON operators, indexing

**Example queries:**
```python
# Find diets with specific food
SavedDiet.objects.filter(selected_items__contains=[{"name": "Avocados"}])

# Count items in diet
SavedDiet.objects.annotate(item_count=models.JSONField('selected_items'))
```

---

## 🔄 Rollback Plan

If you need to rollback to SQLite:

1. **Stop the server**

2. **Remove DATABASE_URL from .env**:
   ```env
   # DATABASE_URL=postgresql://...
   ```

3. **Restore backup**:
   ```bash
   copy db.sqlite3.backup db.sqlite3
   ```

4. **Restart server**:
   ```bash
   python manage.py runserver
   ```

---

## 🚀 Deployment Considerations

### **Environment Variables**

Set these in your production environment:

```env
DATABASE_URL=postgresql://...
SECRET_KEY=<generate-new-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### **Static Files**

```bash
python manage.py collectstatic
```

### **Security**

- Use strong SECRET_KEY
- Set DEBUG=False
- Configure ALLOWED_HOSTS
- Use HTTPS (NeonDB requires SSL)
- Enable CSRF protection

### **Monitoring**

- NeonDB dashboard shows:
  - Connection count
  - Query performance
  - Storage usage
  - Compute time

---

## 📚 Additional Resources

- **NeonDB Docs**: https://neon.tech/docs/
- **Django PostgreSQL**: https://docs.djangoproject.com/en/4.2/ref/databases/#postgresql-notes
- **JSONField**: https://docs.djangoproject.com/en/4.2/ref/models/fields/#jsonfield
- **Database Indexing**: https://docs.djangoproject.com/en/4.2/ref/models/indexes/

---

## ✅ Migration Checklist

- [ ] Backup SQLite database
- [ ] Export data to JSON fixtures
- [ ] Create NeonDB account and project
- [ ] Get DATABASE_URL connection string
- [ ] Update .env file
- [ ] Install PostgreSQL dependencies
- [ ] Run migrations
- [ ] Load initial data
- [ ] Verify data integrity
- [ ] Test all features
- [ ] Create superuser (optional)
- [ ] Update documentation
- [ ] Deploy to production

---

## 🎉 Success!

Your EatRight application is now running on PostgreSQL with:
- ✅ Scalable serverless database
- ✅ Native JSON support
- ✅ Performance indexes
- ✅ Production-ready setup

**Next steps:**
1. Monitor NeonDB dashboard
2. Optimize queries as needed
3. Set up automated backups
4. Deploy to production

---

*Migration guide created for EatRight v1.0*
*Last updated: May 2026*
