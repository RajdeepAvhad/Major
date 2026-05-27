# ✅ PostgreSQL Migration - Verification Checklist

## 📋 Pre-Migration Verification

### **Files Generated:**
- [ ] `requirements.txt` - Updated with PostgreSQL dependencies
- [ ] `foodrec/settings.py` - Database configuration modified
- [ ] `recommender/models.py` - JSONField and indexes added
- [ ] `recommender/api_views.py` - Updated for JSONField
- [ ] `recommender/migrations/0008_migrate_to_postgresql.py` - Migration created
- [ ] `.env.example` - Environment template created
- [ ] `scripts/export_sqlite.py` - Export script created
- [ ] `recommender/management/commands/load_initial_data.py` - Import command created
- [ ] Documentation files created (4 guides)

### **Code Changes Verification:**

#### **1. Check requirements.txt:**
```bash
# Should contain:
psycopg2-binary>=2.9.9
dj-database-url>=2.1.0
Django>=4.2,<5.0
```

#### **2. Check settings.py:**
```python
# Should have:
import dj_database_url
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.config(...)}
else:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', ...}}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

#### **3. Check models.py:**
```python
# SavedDiet should have:
selected_items = models.JSONField(default=list, blank=True)

# WaterLog should have:
log_date = models.DateField(default=timezone.localdate, db_index=True)

# All models should have indexes in Meta class
```

#### **4. Check api_views.py:**
```python
# api_save_diet should have:
selected_items=items  # NOT json.dumps(items)

# api_diet_history should have:
items = record.selected_items if isinstance(record.selected_items, list) else []
# NOT json.loads(record.selected_items)
```

---

## 🚀 Migration Execution Checklist

### **Phase 1: Preparation**
- [ ] Read `MIGRATION_COMPLETE.md`
- [ ] Choose migration guide (Quick or Comprehensive)
- [ ] Backup SQLite database: `copy db.sqlite3 db.sqlite3.backup`
- [ ] Verify backup file exists and has correct size
- [ ] Stop all running servers (Django + React)

### **Phase 2: Data Export**
- [ ] Run: `python scripts/export_sqlite.py`
- [ ] Verify `fixtures/initial_data.json` created
- [ ] Check file size (should be > 0 KB)
- [ ] Verify record counts in output
- [ ] Expected: 89 foods, 4 users, 9 diets, etc.

### **Phase 3: NeonDB Setup**
- [ ] Sign up at https://neon.tech/
- [ ] Create new project
- [ ] Create database named "eatright"
- [ ] Copy connection string from dashboard
- [ ] Verify connection string format:
  ```
  postgresql://user:pass@host/db?sslmode=require
  ```
- [ ] Ensure `?sslmode=require` is at the end

### **Phase 4: Environment Configuration**
- [ ] Copy `.env.example` to `.env` (if not exists)
- [ ] Add DATABASE_URL to `.env`
- [ ] Verify other environment variables:
  - [ ] GROQ_API_KEY (optional)
  - [ ] OPENAI_API_KEY (optional)
  - [ ] SECRET_KEY
  - [ ] DEBUG=True (for testing)
- [ ] Save `.env` file

### **Phase 5: Dependencies Installation**
- [ ] Run: `pip install -r requirements.txt`
- [ ] Verify psycopg2-binary installed
- [ ] Verify dj-database-url installed
- [ ] Check for any installation errors
- [ ] Run: `pip list | findstr /i "psycopg2 dj-database"`

### **Phase 6: Database Migration**
- [ ] Run: `python manage.py migrate`
- [ ] Verify all migrations applied successfully
- [ ] Check for migration errors
- [ ] Verify 0008_migrate_to_postgresql applied
- [ ] Expected output: "Applying recommender.0008_migrate_to_postgresql... OK"

### **Phase 7: Data Import**
- [ ] Run: `python manage.py load_initial_data`
- [ ] Review fixture statistics
- [ ] Confirm import (type 'y')
- [ ] Wait for import to complete
- [ ] Verify success message
- [ ] Check final record counts

### **Phase 8: Verification**
- [ ] Run Django shell: `python manage.py shell`
- [ ] Execute verification commands:
  ```python
  from recommender.models import Food, SavedDiet, User, WaterLog
  from django.contrib.auth.models import User
  
  # Check counts
  print(f"Users: {User.objects.count()}")  # Should be 4
  print(f"Foods: {Food.objects.count()}")  # Should be 89
  print(f"Diets: {SavedDiet.objects.count()}")  # Should be 9
  print(f"Water Logs: {WaterLog.objects.count()}")  # Should be 3
  
  # Test JSONField
  diet = SavedDiet.objects.first()
  print(f"Type: {type(diet.selected_items)}")  # Should be <class 'list'>
  print(f"Items: {diet.selected_items}")  # Should show list, not string
  
  # Test indexes
  from django.db import connection
  with connection.cursor() as cursor:
      cursor.execute("SELECT indexname FROM pg_indexes WHERE tablename='recommender_saveddiet'")
      print("Indexes:", cursor.fetchall())
  ```
- [ ] All counts match expected values
- [ ] selected_items is list, not string
- [ ] Indexes exist

---

## 🧪 Application Testing Checklist

### **Phase 9: Start Servers**
- [ ] Start Django: `python manage.py runserver`
- [ ] Verify Django starts without errors
- [ ] Check console for database connection
- [ ] Start React: `cd frontend && npm run dev`
- [ ] Verify React starts on port 5173

### **Phase 10: Feature Testing**

#### **Authentication:**
- [ ] Visit http://localhost:5173/login
- [ ] Login with existing user
- [ ] Verify successful login
- [ ] Check user session
- [ ] Logout and verify
- [ ] Create new account (signup)
- [ ] Verify new user created

#### **Body Fat Calculator:**
- [ ] Visit http://localhost:5173/bodymass
- [ ] Enter test values
- [ ] Calculate body fat
- [ ] Verify result displays
- [ ] Test without login (should work)

#### **Diet Planner:**
- [ ] Visit http://localhost:5173/dietplanner
- [ ] Enter user details
- [ ] Select goal (weight loss/gain/maintain)
- [ ] Submit form
- [ ] Verify recommendations load
- [ ] Check breakfast, lunch, dinner items
- [ ] Verify calorie calculations

#### **Save Diet:**
- [ ] Select food items
- [ ] Click "Save Diet Plan"
- [ ] Verify success message
- [ ] Check diet saved to database

#### **Diet History:**
- [ ] Visit http://localhost:5173/diet-history
- [ ] Verify saved diets display
- [ ] Check diet details
- [ ] Verify selected_items shows correctly
- [ ] Test delete diet
- [ ] Verify diet removed

#### **Dashboard:**
- [ ] Visit http://localhost:5173/progress
- [ ] Verify streak counter
- [ ] Check calorie adherence chart
- [ ] Verify recent diets widget
- [ ] Check quick stats
- [ ] Verify all data loads

#### **AI Chatbot:**
- [ ] Visit http://localhost:5173/chatbot
- [ ] Ask test question: "What is BMI?"
- [ ] Verify response received
- [ ] Test multiple questions
- [ ] Check conversation history

#### **Water Tracker:**
- [ ] Log water intake
- [ ] Verify amount saved
- [ ] Check 7-day history
- [ ] Test update/delete

#### **Favorites:**
- [ ] Add food to favorites
- [ ] Verify favorite saved
- [ ] Remove from favorites
- [ ] Verify removal

#### **Profile:**
- [ ] Visit http://localhost:5173/profile
- [ ] Check user information
- [ ] Verify data displays correctly

### **Phase 11: Performance Testing**
- [ ] Test concurrent requests (open multiple tabs)
- [ ] Check response times
- [ ] Verify no connection errors
- [ ] Monitor NeonDB dashboard
- [ ] Check connection count
- [ ] Verify query performance

### **Phase 12: Data Integrity**
- [ ] Compare record counts (SQLite vs PostgreSQL)
- [ ] Verify all users migrated
- [ ] Check all foods present
- [ ] Verify diet plans intact
- [ ] Check water logs
- [ ] Verify favorites
- [ ] Test data relationships (foreign keys)

---

## 🔍 Post-Migration Verification

### **Database Checks:**
- [ ] Run: `python check_db.py`
- [ ] Verify table counts
- [ ] Check for any errors
- [ ] Verify indexes created
- [ ] Check database size in NeonDB dashboard

### **Code Checks:**
- [ ] No JSON parsing errors in logs
- [ ] No database connection errors
- [ ] No migration warnings
- [ ] All API endpoints working

### **Performance Checks:**
- [ ] JSON queries faster than before
- [ ] Indexed queries performing well
- [ ] No slow query warnings
- [ ] Connection pooling working

---

## 🚨 Troubleshooting Checklist

### **If Migration Fails:**
- [ ] Check DATABASE_URL format
- [ ] Verify NeonDB project is active
- [ ] Check network/firewall
- [ ] Review migration logs
- [ ] Check for missing dependencies

### **If Data Import Fails:**
- [ ] Verify fixture file exists
- [ ] Check fixture file format (valid JSON)
- [ ] Review import logs
- [ ] Check for constraint violations
- [ ] Verify database is empty before import

### **If Application Errors:**
- [ ] Check Django logs
- [ ] Verify all migrations applied
- [ ] Check for import errors
- [ ] Review api_views.py changes
- [ ] Test with SQLite (remove DATABASE_URL)

---

## 🔄 Rollback Checklist

### **If You Need to Rollback:**
- [ ] Stop all servers
- [ ] Remove DATABASE_URL from `.env`
- [ ] Restore backup: `copy db.sqlite3.backup db.sqlite3`
- [ ] Restart Django: `python manage.py runserver`
- [ ] Test application with SQLite
- [ ] Verify all features work
- [ ] Document issues encountered

---

## ✅ Success Criteria

Migration is successful when:

- [ ] ✅ All migrations applied without errors
- [ ] ✅ All data imported successfully
- [ ] ✅ Record counts match (SQLite vs PostgreSQL)
- [ ] ✅ All features tested and working
- [ ] ✅ No errors in Django logs
- [ ] ✅ No errors in browser console
- [ ] ✅ Performance improved
- [ ] ✅ JSONField working correctly
- [ ] ✅ Indexes created and working
- [ ] ✅ Connection pooling active
- [ ] ✅ NeonDB dashboard shows activity
- [ ] ✅ No data loss

---

## 📊 Final Verification Report

After completing all checks, fill this out:

```
Migration Date: _______________
Migrated By: _______________

Pre-Migration:
- SQLite Database Size: _______ KB
- Total Records: _______
- Users: _______
- Foods: _______
- Diets: _______

Post-Migration:
- PostgreSQL Database Size: _______ KB
- Total Records: _______
- Users: _______
- Foods: _______
- Diets: _______

Performance:
- JSON Query Time: Before ___ms → After ___ms
- Recent Diets Query: Before ___ms → After ___ms
- Water Logs Query: Before ___ms → After ___ms

Issues Encountered: _______________
Resolution: _______________

Status: [ ] SUCCESS  [ ] PARTIAL  [ ] FAILED

Notes:
_________________________________
_________________________________
_________________________________
```

---

## 🎉 Migration Complete!

Once all checkboxes are marked:

- [ ] Document any issues encountered
- [ ] Update team/documentation
- [ ] Monitor NeonDB dashboard for 24 hours
- [ ] Set up automated backups
- [ ] Plan production deployment
- [ ] Celebrate! 🎊

---

**Status:** Ready for verification

**Next Step:** Start with Phase 1 - Preparation

---

*Verification Checklist - EatRight PostgreSQL Migration*
*Version 1.0 - May 2026*
