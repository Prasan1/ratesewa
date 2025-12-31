# How to Change Admin Password

## ⚠️ IMPORTANT: Change Password Before Launch!

The default admin password `admin123` is **insecure**. Change it NOW before going live!

---

## Two Ways to Change Password

### Option 1: Quick Script (Fastest - 30 seconds) ⚡

**Use this if you want to change it RIGHT NOW:**

```bash
python3 change_admin_password.py
```

**What happens:**
1. Script asks for new password (hidden while typing)
2. Asks you to confirm it
3. Updates database instantly
4. Shows you the new password

**Example:**
```bash
$ python3 change_admin_password.py
============================================================
  CHANGE ADMIN PASSWORD
============================================================

Admin user: Admin (admin@ratesewa.com)

Enter NEW password: ••••••••
Confirm NEW password: ••••••••

============================================================
✅ Password changed successfully!
============================================================

You can now login with:
  Email: admin@ratesewa.com
  Password: YourNewPassword123

⚠️  WRITE THIS DOWN and keep it safe!
```

---

### Option 2: Web Interface (User-Friendly) 🌐

**Use this if server is running:**

1. **Start the server:**
   ```bash
   ./run_dev.sh
   ```

2. **Login as admin:**
   - Go to: http://localhost:5000/login
   - Email: `admin@ratesewa.com`
   - Password: `admin123` (current password)

3. **Go to My Profile:**
   - Click your name in navbar
   - Select "My Profile"

4. **Change Password:**
   - Scroll to "Change Password" section
   - Enter current password: `admin123`
   - Enter new password (at least 6 characters)
   - Confirm new password
   - Click "Change Password"

5. **Success!**
   - You'll see: "Password changed successfully!"
   - Use new password from now on

---

## Password Requirements

✅ **At least 6 characters** (recommended: 12+)
✅ **Mix of letters and numbers** (recommended)
✅ **Avoid common words** (no "password123")
✅ **Unique to RateSewa** (don't reuse other passwords)

**Good examples:**
- `RateSewa2025!`
- `Nepal#Medical99`
- `SecureAdmin@RS`

**Bad examples:**
- `admin123` (too simple)
- `password` (too common)
- `123456` (too weak)

---

## Recommendations

### For Launch:
1. ✅ Change admin password TODAY (before launch)
2. ✅ Use a strong, unique password
3. ✅ Write it down securely
4. ✅ Don't share with anyone

### After Launch:
1. Change password every 3-6 months
2. Use different password for production vs development
3. Enable 2FA (future feature)

---

## Troubleshooting

### Script Method

**Error: "Admin user not found!"**
- Run: `python3 seed_data.py`
- Creates admin user if missing

**Error: "Passwords don't match"**
- Type carefully (passwords are hidden)
- Try again

**Error: "Password must be at least 6 characters"**
- Use a longer password
- 12+ characters recommended

### Web Interface

**Can't login:**
- Make sure you're using current password
- Check for typos
- Try script method instead

**"Current password is incorrect":**
- You entered wrong current password
- Current password is `admin123` (if not changed yet)

**"New passwords do not match":**
- New password and confirm password don't match
- Type carefully and try again

**Form not showing:**
- Make sure you're logged in
- Go to: http://localhost:5000/profile
- Password change form is at the top left

---

## Quick Reference

### Change via Script:
```bash
python3 change_admin_password.py
```

### Change via Web:
```
Login → Profile → Change Password section → Enter passwords → Submit
```

### Current Credentials:
- Email: `admin@ratesewa.com`
- Password: `admin123` (CHANGE THIS!)

---

## Security Tips

1. **Never share** admin password
2. **Use strong password** (12+ characters)
3. **Write it down** securely (password manager recommended)
4. **Change regularly** (every 3-6 months)
5. **Different from other sites** (unique password)
6. **Log out** when done using admin panel

---

## After Changing Password

1. ✅ Test new password by logging in
2. ✅ Write down new password securely
3. ✅ Update any scripts/configs using old password
4. ✅ Tell other admins (if any) that password changed

---

## What If I Forget New Password?

**Don't worry!** Use the script method:

```bash
python3 change_admin_password.py
```

The script can reset password even if you forgot it (doesn't ask for old password).

---

## Pre-Launch Checklist

- [ ] Admin password changed from `admin123`
- [ ] New password is strong (12+ characters)
- [ ] New password written down securely
- [ ] Tested new password by logging in
- [ ] Logged out of admin account
- [ ] Ready to launch!

---

**Status:** ✅ Password change feature ready!

**Estimated time:** 30 seconds (script) or 2 minutes (web)

**Last Updated:** 2025-12-31
