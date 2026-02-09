# 🚀 Quick Reference Card

## 📝 Your Questions Answered

### 1️⃣ How to Access PostgreSQL in Docker?
```bash
# Method 1: Interactive shell
docker exec -it dastern-postgres psql -U dastern -d dastern

# Method 2: Single command
docker exec -it dastern-postgres psql -U dastern -d dastern -c "SELECT * FROM users;"

# Method 3: From SQL file
docker exec -i dastern-postgres psql -U dastern -d dastern < your_script.sql
```

### 2️⃣ How Docker Auto-Updates Database?
**Important:** Auto-update only happens **on first startup!**

To apply new changes:
```bash
# Option 1: Run migration script
./migrate-database.sh

# Option 2: Manual migration
docker exec -i dastern-postgres psql -U dastern -d dastern < database/migrations/new.sql

# Option 3: Reset database (⚠️ deletes all data!)
docker compose down -v
docker compose up -d
docker exec -i dastern-postgres psql -U dastern -d dastern < database/seeds/test_users.sql
```

### 3️⃣ Foreign Key Error - FIXED! ✅
**Problem:** No user with ID `00000000-0000-0000-0000-000000000000`

**Solution:** Test users created!
- ✅ Patient: `patient@test.com` (ID: `00000000-0000-0000-0000-000000000000`)
- ✅ Doctor: `doctor@test.com` (ID: `00000000-0000-0000-0000-000000000001`)  
- ✅ Password: `password123`

---

## 🎯 Common Tasks

### Check Test Users
```bash
docker exec -it dastern-postgres psql -U dastern -d dastern -c "SELECT id, email, role FROM users WHERE email LIKE '%test.com';"
```

### Create More Test Users
```bash
docker exec -i dastern-postgres psql -U dastern -d dastern < database/seeds/test_users.sql
```

### View Prescriptions
```bash
docker exec -it dastern-postgres psql -U dastern -d dastern -c "SELECT * FROM prescriptions ORDER BY created_at DESC LIMIT 5;"
```

### View Medications
```bash
docker exec -it dastern-postgres psql -U dastern -d dastern -c "SELECT * FROM medications ORDER BY created_at DESC LIMIT 10;"
```

### Check Service Status
```bash
docker compose ps
```

### View Logs
```bash
docker compose logs -f backend
docker compose logs -f postgres
```

---

## 🗄️ Database Credentials

```env
Host: localhost
Port: 5432
Username: dastern
Password: dastern_capstone_2
Database: dastern
```

---

## 📚 Full Documentation

- [DATABASE_MANAGEMENT_GUIDE.md](DATABASE_MANAGEMENT_GUIDE.md) - Complete database guide
- [CURRENT_STATUS.md](CURRENT_STATUS.md) - System status
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Full implementation

---

## ✅ You're Ready!

1. **Access database:** `docker exec -it dastern-postgres psql -U dastern -d dastern`
2. **Test upload:** http://localhost:3000
3. **Check data:** See commands above

**Foreign key error is FIXED! 🎉**
