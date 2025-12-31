# Enable Facebook Login - Quick Setup (15 minutes)

## 🎯 Why This is Critical for Nepal

You're absolutely right! Nepali users prefer social login:
- ✅ **Facebook** - Most popular in Nepal
- ✅ **Google** - Also very common
- ❌ Email/password - Less common, seen as "too much work"

Let's enable Facebook login NOW.

---

## Step 1: Create Facebook App (5 minutes)

### 1.1 Go to Facebook Developers:
**URL:** https://developers.facebook.com/apps

### 1.2 Create New App:
1. Click **"Create App"**
2. Choose **"Consumer"** as app type
3. Click **"Next"**

### 1.3 Fill App Details:
- **App Name:** `RankSewa` (or "RankSewa Nepal")
- **App Contact Email:** Your email
- **Business Account:** Skip (not required)
- Click **"Create App"**

### 1.4 Verify with Password:
- Enter your Facebook password
- Click **"Submit"**

---

## Step 2: Configure Facebook Login (3 minutes)

### 2.1 Add Facebook Login Product:
1. In left sidebar, find **"Add Products"**
2. Find **"Facebook Login"**
3. Click **"Set Up"**

### 2.2 Choose Platform:
- Select **"Web"**

### 2.3 Enter Your Site URL:
```
https://ranksewa.com
```
Click **"Save"** and **"Continue"**

---

## Step 3: Get App Credentials (2 minutes)

### 3.1 Go to Settings:
1. Left sidebar → **Settings** → **Basic**
2. You'll see:
   - **App ID**: `123456789012345`
   - **App Secret**: Click **"Show"** to reveal

### 3.2 Copy These Values:
```
App ID: [copy this number]
App Secret: [copy this secret - click Show first]
```

**Save these somewhere safe!**

---

## Step 4: Configure Valid OAuth Redirect URIs (3 minutes)

### 4.1 Go to Facebook Login Settings:
1. Left sidebar → **Products** → **Facebook Login** → **Settings**

### 4.2 Add Valid OAuth Redirect URIs:
In the **"Valid OAuth Redirect URIs"** field, add:
```
https://ranksewa.com/login/facebook/authorized
```

**Important:** Must be HTTPS and match your domain!

### 4.3 Save Changes:
Click **"Save Changes"** at bottom

---

## Step 5: Make App Public (1 minute)

### 5.1 Switch to Live Mode:
1. Top of page: Toggle from **"In Development"** to **"Live"**
2. If asked, click **"Switch Mode"**

**OR**

### 5.2 Alternative - App Review:
If you can't switch to Live directly:
1. Go to **App Review** → **Permissions and Features**
2. Request **"public_profile"** and **"email"**
3. Or just use Development mode (works for admins/testers)

---

## Step 6: Add Environment Variables in DigitalOcean (2 minutes)

### 6.1 Go to Your App Settings:
1. DO Dashboard → Your **ratesewa** app
2. **Settings** → **App-Level Environment Variables**

### 6.2 Add These Variables:
Click **"Edit"** and add:

| Key | Value |
|-----|-------|
| `FACEBOOK_CLIENT_ID` | [Your App ID from Step 3] |
| `FACEBOOK_CLIENT_SECRET` | [Your App Secret from Step 3] |

### 6.3 Save and Deploy:
1. Click **"Save"**
2. DO will ask to redeploy
3. Click **"Deploy"** or **"Redeploy"**

---

## Step 7: Enable Facebook Login in Code (1 minute)

The code is already there, just commented out! We need to uncomment it.

**In templates/login.html**, change this:
```html
{# Facebook Login - Hidden for MVP Launch #}
{# <hr class="my-4">
<div class="d-grid">
    <a class="btn btn-outline-primary" href="{{ url_for('facebook_login') }}">
        <i class="fab fa-facebook me-2"></i>Continue with Facebook
    </a>
</div> #}
```

**To this:**
```html
<hr class="my-4">
<div class="d-grid">
    <a class="btn btn-outline-primary btn-lg" href="{{ url_for('facebook_login') }}">
        <i class="fab fa-facebook me-2"></i>Continue with Facebook
    </a>
</div>
```

---

## Step 8: Test Facebook Login (2 minutes)

Once deployment completes:

1. **Visit:** https://ranksewa.com/login
2. **You should see:** "Continue with Facebook" button
3. **Click it** → Should redirect to Facebook
4. **Authorize** → Should create account and log you in
5. **Check:** User profile should show your Facebook name/email

---

## ✅ Expected Result:

**Login page will have:**
- Email/password form (for admins)
- **"OR"** divider
- **"Continue with Facebook"** button ← NEW!

**User experience:**
1. User clicks "Continue with Facebook"
2. Facebook asks to authorize RankSewa
3. User clicks "Continue"
4. Automatically logged in to RankSewa ✅
5. Account created with Facebook name/email

---

## 🐛 Troubleshooting

### "URL Blocked" Error:
**Fix:** Make sure you added `https://ranksewa.com/login/facebook/authorized` to Valid OAuth Redirect URIs

### "App Not Setup" Error:
**Fix:**
1. App must be in **Live mode** (or you must be admin/tester in Development mode)
2. Check App ID and Secret are correct in DO environment variables

### "Invalid Client Secret":
**Fix:**
1. Copy App Secret again from Facebook (click "Show")
2. Update in DO environment variables
3. Redeploy

### Facebook Login Button Doesn't Appear:
**Fix:**
1. Check environment variables are set (`FACEBOOK_CLIENT_ID` and `FACEBOOK_CLIENT_SECRET`)
2. Make sure code is uncommented in login.html
3. Clear browser cache (Ctrl+Shift+R)

---

## 📊 Testing Checklist:

- [ ] Facebook app created
- [ ] App ID and Secret copied
- [ ] Valid OAuth Redirect URI added: `https://ranksewa.com/login/facebook/authorized`
- [ ] App in Live mode (or you're added as admin/tester)
- [ ] Environment variables added in DO
- [ ] Code uncommented in login.html
- [ ] Deployed successfully
- [ ] Facebook login button visible on login page
- [ ] Click button → redirects to Facebook
- [ ] Authorize → logs in successfully
- [ ] User account created with Facebook details

---

## 💡 Bonus: Add Google Login Too? (Optional)

Google login is also very popular in Nepal. Want to add it?

**Benefits:**
- More login options = more users
- Google very common in Nepal
- Easy to set up (similar to Facebook)

Let me know if you want to add Google OAuth too!

---

## 🎯 Summary

**What you need:**
1. Facebook App ID
2. Facebook App Secret
3. 5 minutes to set up

**What users get:**
- Click "Continue with Facebook"
- Instant login
- No password to remember
- Much better UX for Nepal users!

---

**Ready to set this up? Let me know if you need help with any step!**
