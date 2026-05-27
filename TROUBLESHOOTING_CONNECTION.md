# 🔧 NeonDB Connection Troubleshooting

## ❌ Error: "could not translate host name"

This error means Python cannot resolve the NeonDB hostname to an IP address.

---

## 🔍 Possible Causes:

### **1. Network/Firewall Issues**
- Your firewall is blocking the connection
- Corporate network restrictions
- VPN interference
- DNS resolution problems

### **2. Incorrect Connection String**
- Typo in the hostname
- Missing or incorrect parameters
- Wrong region/endpoint

### **3. NeonDB Project Issues**
- Project is suspended/deleted
- Database not fully provisioned
- Wrong connection string copied

---

## ✅ Solutions:

### **Solution 1: Verify Connection String**

1. **Go to NeonDB Dashboard:**
   - Visit: https://console.neon.tech/
   - Select your project
   - Go to "Connection Details"

2. **Copy the CORRECT connection string:**
   - Make sure it's the **Pooled connection** string
   - Should look like:
   ```
   postgresql://[user]:[password]@[host]/[database]?sslmode=require
   ```

3. **Check for typos:**
   - Current string in .env:
   ```
   ep-autumn-rain-apq62jwt-pooler.c-7.us-east-1.aws.neon.tech
   ```
   - Verify this matches your dashboard EXACTLY

### **Solution 2: Test Network Connection**

```powershell
# Test DNS resolution
nslookup ep-autumn-rain-apq62jwt-pooler.c-7.us-east-1.aws.neon.tech

# Test connection (if nslookup works)
Test-NetConnection -ComputerName ep-autumn-rain-apq62jwt-pooler.c-7.us-east-1.aws.neon.tech -Port 5432
```

### **Solution 3: Check Firewall**

1. **Windows Firewall:**
   - Allow Python through firewall
   - Allow outbound connections on port 5432

2. **Antivirus:**
   - Temporarily disable to test
   - Add Python to whitelist

3. **Corporate Network:**
   - Check if port 5432 is blocked
   - Try from different network (mobile hotspot)

### **Solution 4: Try Direct Connection (Non-Pooled)**

NeonDB provides two connection strings:
- **Pooled** (recommended for apps): `-pooler` in hostname
- **Direct** (for testing): no `-pooler`

Try the **Direct connection** string from your dashboard.

### **Solution 5: Use Different DNS**

```powershell
# Flush DNS cache
ipconfig /flushdns

# Try using Google DNS
# Go to Network Settings → Change adapter options
# Right-click your connection → Properties
# IPv4 → Properties → Use these DNS servers:
# Preferred: 8.8.8.8
# Alternate: 8.8.4.4
```

### **Solution 6: Check NeonDB Project Status**

1. Go to https://console.neon.tech/
2. Check if project is **Active**
3. Check if database is **Running**
4. Try creating a new database if needed

---

## 🧪 Test Connection with Python

Create a test file `test_connection.py`:

```python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

print(f"Testing connection to: {DATABASE_URL[:50]}...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Connection successful!")
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run it:
```bash
python test_connection.py
```

---

## 🔄 Alternative: Use SQLite for Now

If you can't resolve the connection issue immediately:

1. **Comment out DATABASE_URL in .env:**
   ```env
   # DATABASE_URL=postgresql://...
   ```

2. **Continue using SQLite:**
   ```bash
   python manage.py runserver
   ```

3. **Troubleshoot NeonDB separately**

4. **Migrate later when connection works**

---

## 📞 Get Help from NeonDB

If none of the above works:

1. **Check NeonDB Status:**
   - https://neonstatus.com/

2. **Contact NeonDB Support:**
   - Dashboard → Help → Support
   - Discord: https://discord.gg/neon
   - Email: support@neon.tech

3. **Provide this info:**
   - Error message
   - Your region
   - Connection string (hide password)
   - Network setup (home/corporate)

---

## ✅ Once Connection Works:

```bash
# Run migrations
python manage.py migrate

# Load data
python manage.py load_initial_data

# Test
python manage.py runserver
```

---

## 🎯 Quick Checklist:

- [ ] Verify connection string from NeonDB dashboard
- [ ] Check for typos in DATABASE_URL
- [ ] Test DNS resolution (nslookup)
- [ ] Check firewall settings
- [ ] Try different network
- [ ] Flush DNS cache
- [ ] Try direct (non-pooled) connection
- [ ] Check NeonDB project status
- [ ] Test with Python script
- [ ] Contact NeonDB support if needed

---

*Troubleshooting Guide - EatRight PostgreSQL Migration*
