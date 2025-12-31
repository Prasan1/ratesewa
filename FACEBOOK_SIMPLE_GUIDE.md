# Facebook Login - Super Simple Setup (When You're Ready)

## Current Status: DISABLED for MVP Launch ✅

Facebook login button is **hidden** from users. Launch with email/password only - it works perfectly!

**Add Facebook login later when you have time.** No rush!

---

## Why You Might Want It Later

- Facebook has 9 million users in Nepal
- Many users prefer it over email/password
- Could increase signups by 2-3x
- Takes about 20 minutes to set up (when you're ready)

---

## Super Simple Setup (Do This Later, Not Now!)

### Step 1: Create Facebook App (5 minutes)

1. Go to: **https://developers.facebook.com/apps/**
2. Click big blue button: **"Create App"**
3. Choose: **"Consumer"** → Click **Next**
4. Fill in:
   - **App name:** RateSewa
   - **Email:** your@email.com
5. Click **"Create App"**
6. Do the CAPTCHA

✅ **Done!** You now have a Facebook App.

---

### Step 2: Add Facebook Login (3 minutes)

1. You're now in the app dashboard
2. Look for **"Add products to your app"** section
3. Find **"Facebook Login"** card
4. Click **"Set up"** button
5. Choose **"Web"**
6. Enter: `http://localhost:5000` (for testing)
7. Click **Save** and **Continue** through the steps

✅ **Done!** Facebook Login is added.

---

### Step 3: Configure Callback URL (2 minutes)

1. In left sidebar, click **"Facebook Login"** → **"Settings"**
2. Find **"Valid OAuth Redirect URIs"** field
3. Add these URLs (one per line):
   ```
   http://localhost:5000/login/facebook/callback
   https://ratesewa.com/login/facebook/callback
   ```
4. Click **"Save Changes"** at bottom

✅ **Done!** Callback configured.

---

### Step 4: Get Your Credentials (2 minutes)

1. In left sidebar, click **"Settings"** → **"Basic"**
2. You'll see:
   - **App ID:** Copy this number
   - **App Secret:** Click "Show", enter your password, copy it

⚠️ **IMPORTANT:** Don't share App Secret with anyone!

✅ **Done!** You have your credentials.

---

### Step 5: Add to RateSewa (3 minutes)

1. **Open .env file:**
   ```bash
   nano .env
   ```

2. **Find these lines and uncomment + fill in:**
   ```env
   FACEBOOK_CLIENT_ID=123456789012345
   FACEBOOK_CLIENT_SECRET=abc123def456789ghi
   ```

3. **Save file** (Ctrl+X, Y, Enter)

4. **Restart server:**
   ```bash
   lsof -ti:5000 | xargs kill -9
   ./run_dev.sh
   ```

✅ **Done!** Server has the credentials.

---

### Step 6: Enable Facebook Button (1 minute)

1. **Open login template:**
   ```bash
   nano templates/login.html
   ```

2. **Find this block around line 40:**
   ```html
   {# Facebook Login - Hidden for MVP Launch #}
   {# <hr class="my-4">

   <div class="d-grid">
       <a class="btn btn-outline-primary" href="...">
           Continue with Facebook
       </a>
   </div> #}
   ```

3. **Remove the comment marks {# and #}:**
   ```html
   <hr class="my-4">

   <div class="d-grid">
       <a class="btn btn-outline-primary" href="...">
           <i class="fab fa-facebook me-2"></i>Continue with Facebook
       </a>
   </div>
   ```

4. **Save file**

5. **Restart server again:**
   ```bash
   lsof -ti:5000 | xargs kill -9
   ./run_dev.sh
   ```

✅ **Done!** Button is visible!

---

### Step 7: Test It (2 minutes)

1. Go to: **http://localhost:5000/login**
2. You should see **"Continue with Facebook"** button
3. Click it
4. Facebook asks you to login
5. Click **"Continue"**
6. You're logged into RateSewa!

✅ **WORKING!** Facebook login is live!

---

## For Production (Later)

1. In Facebook app settings:
   - Change app mode from **"Development"** to **"Live"**
   - Add privacy policy URL

2. Make sure callback URL has your real domain:
   ```
   https://ratesewa.com/login/facebook/callback
   ```

That's it!

---

## If You Get Stuck

**Error: "Invalid OAuth redirect URI"**
- Make sure callback URL in Facebook settings **exactly** matches:
  `http://localhost:5000/login/facebook/callback`

**Error: "App not setup"**
- In Facebook app, go to **Settings** → **Basic**
- Make sure app is not in **"Development Mode"** OR
- Add yourself as a test user in **"Roles"** → **"Test Users"**

**Button doesn't show up**
- Did you uncomment the code in `login.html`?
- Did you restart the server?

**Still confused?**
- Email/password login works great! You don't NEED Facebook
- Can add it later whenever you're ready

---

## Quick Reference Card

**When ready to add Facebook login:**

```bash
# 1. Get credentials from developers.facebook.com
# 2. Add to .env:
FACEBOOK_CLIENT_ID=your_app_id
FACEBOOK_CLIENT_SECRET=your_app_secret

# 3. Edit templates/login.html - uncomment Facebook button section

# 4. Restart:
lsof -ti:5000 | xargs kill -9 && ./run_dev.sh
```

**That's it!** 🎉

---

## Bottom Line

- ✅ **For now:** Launch with email/password (working perfectly)
- 📅 **Later:** Add Facebook login when you have 20 free minutes
- 🚀 **No rush:** Site works great without it
- 💪 **When ready:** Follow this guide, takes ~20 minutes total

---

**Status:** Optional feature - Add anytime!

**Last Updated:** 2025-12-31
