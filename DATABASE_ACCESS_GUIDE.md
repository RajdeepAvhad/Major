# 🗄️ Database Access Guide - EatRight Project

## 📍 Database Location
**File:** `c:\Users\Rajdeep\OneDrive\Desktop\Major\db.sqlite3`
**Type:** SQLite3 Database
**Size:** 200 KB
**Last Modified:** May 24, 2026

---

## 📊 Current Database Contents

### **User Data:**
- **4 registered users** (auth_user)
- **11 legacy users** (recommender_userlist)
- **26 active sessions** (django_session)

### **Food Data:**
- **89 food items** with nutritional information (recommender_food)

### **Diet Plans:**
- **9 saved diet plans** (recommender_saveddiet)
- **1 user preference** saved (recommender_userpreference)

### **Tracking:**
- **3 water log entries** (recommender_waterlog)
- **0 favorite foods** (recommender_favoritefood)

### **Admin:**
- **10 admin actions** logged (django_admin_log)

---

## 🔧 Methods to Access Your Database

### **Method 1: Django Admin Panel (Easiest)**

1. **Create a superuser** (if you haven't):
   ```bash
   python manage.py createsuperuser
   ```

2. **Start Django server:**
   ```bash
   python manage.py runserver
   ```

3. **Open in browser:**
   ```
   http://127.0.0.1:8000/admin/
   ```

4. **Login** with your superuser credentials

5. **Browse tables:**
   - Users → Auth → Users
   - Foods → Recommender → Foods
   - Saved Diets → Recommender → Saved diets
   - Preferences → Recommender → User preferences
   - Water Logs → Recommender → Water logs
   - Favorites → Recommender → Favorite foods

---

### **Method 2: Django Shell (For Queries)**

```bash
python manage.py shell
```

**Example queries:**

```python
# Import models
from recommender.models import Food, SavedDiet, UserPreference, WaterLog
from django.contrib.auth.models import User

# View all foods
foods = Food.objects.all()
for food in foods[:5]:
    print(f"{food.name}: {food.cal} cal")

# View all users
users = User.objects.all()
for user in users:
    print(f"{user.username} - {user.email}")

# View saved diets
diets = SavedDiet.objects.all()
for diet in diets:
    print(f"Diet {diet.id}: {diet.selected_calories}/{diet.target_calories} cal")

# Count records
print(f"Total foods: {Food.objects.count()}")
print(f"Total users: {User.objects.count()}")
print(f"Total saved diets: {SavedDiet.objects.count()}")
```

---

### **Method 3: SQLite Command Line**

1. **Install SQLite** (if not installed):
   - Download from: https://www.sqlite.org/download.html
   - Or use: `winget install SQLite.SQLite`

2. **Open database:**
   ```bash
   sqlite3 db.sqlite3
   ```

3. **Useful commands:**
   ```sql
   -- List all tables
   .tables

   -- Show table structure
   .schema recommender_food

   -- Query data
   SELECT * FROM recommender_food LIMIT 5;
   SELECT username, email FROM auth_user;
   SELECT * FROM recommender_saveddiet;

   -- Count records
   SELECT COUNT(*) FROM recommender_food;

   -- Exit
   .quit
   ```

---

### **Method 4: Django dbshell**

```bash
python manage.py dbshell
```

This opens SQLite directly with your database loaded.

---

### **Method 5: GUI Tools (Visual Interface)**

#### **Option A: DB Browser for SQLite (Recommended)**
1. Download: https://sqlitebrowser.org/
2. Install and open
3. Click "Open Database"
4. Navigate to: `c:\Users\Rajdeep\OneDrive\Desktop\Major\db.sqlite3`
5. Browse tables visually

#### **Option B: DBeaver (Professional)**
1. Download: https://dbeaver.io/
2. Install and open
3. New Connection → SQLite
4. Select your `db.sqlite3` file

#### **Option C: VS Code Extension**
1. Install extension: "SQLite Viewer" or "SQLite"
2. Right-click `db.sqlite3` → "Open Database"

---

### **Method 6: Python Script (Custom Queries)**

I've created `check_db.py` for you. Run it anytime:

```bash
python check_db.py
```

**Modify it for custom queries:**

```python
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Example: Get all breakfast foods
cursor.execute("SELECT name, cal, pro FROM recommender_food WHERE bf=1")
breakfast_foods = cursor.fetchall()
for food in breakfast_foods:
    print(f"{food[0]}: {food[1]} cal, {food[2]}g protein")

conn.close()
```

---

## 📋 Important Tables

### **recommender_food**
- Stores 89 food items with nutrition data
- Columns: name, bf (breakfast), lu (lunch), di (dinner), cal, fat, pro, sug, imagepath

### **recommender_saveddiet**
- Stores user's saved diet plans
- Columns: user_id, session_key, period, plan_date, target_calories, selected_calories, selected_items (JSON), bmi, bodyfat

### **auth_user**
- Django's built-in user table
- Columns: username, email, password (hashed), date_joined, is_staff, is_superuser

### **recommender_userpreference**
- Stores user's last input for auto-fill
- Columns: age, weight, height, bodyfat, goal, activity, gender, plan_period, plan_date

### **recommender_waterlog**
- Daily water intake tracking
- Columns: user_id, log_date, amount_ml

---

## 🔍 Quick Database Queries

### **View all foods:**
```bash
python manage.py shell -c "from recommender.models import Food; [print(f.name) for f in Food.objects.all()]"
```

### **Count saved diets:**
```bash
python manage.py shell -c "from recommender.models import SavedDiet; print(SavedDiet.objects.count())"
```

### **List all users:**
```bash
python manage.py shell -c "from django.contrib.auth.models import User; [print(u.username) for u in User.objects.all()]"
```

---

## 🛠️ Database Management Commands

### **Backup database:**
```bash
copy db.sqlite3 db_backup_2026-05-24.sqlite3
```

### **Reset database (⚠️ DANGER - deletes all data):**
```bash
del db.sqlite3
python manage.py migrate
```

### **Export data:**
```bash
python manage.py dumpdata > data_backup.json
```

### **Import data:**
```bash
python manage.py loaddata data_backup.json
```

---

## 📊 Current Statistics

- **Total Tables:** 17
- **User Accounts:** 4
- **Food Items:** 89
- **Saved Diet Plans:** 9
- **Water Logs:** 3
- **Sessions:** 26

---

## 🔐 Security Notes

- Database file is in `.gitignore` (not committed to Git)
- Passwords are hashed using Django's PBKDF2 algorithm
- Never share your `db.sqlite3` file publicly
- Always backup before making changes

---

## 📞 Need Help?

Run the helper script anytime:
```bash
python check_db.py
```

Or access Django admin panel for visual interface:
```bash
python manage.py runserver
# Then visit: http://127.0.0.1:8000/admin/
```
