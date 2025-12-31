# Facebook Login Setup Guide for RateSewa

## Current Status

✅ **Facebook login is IMPLEMENTED and READY to use**
⚠️ **Facebook credentials are NOT YET CONFIGURED**

The Facebook login button is visible on the login page, but clicking it will show:
> "Facebook login is not configured. Please contact the site admin."

---

## Why Facebook Login for Nepal?

Facebook is the **#1 social platform in Nepal** with over 9 million users. Enabling Facebook login will:

- ✅ **Increase signups** - Users don't need to remember passwords
- ✅ **Build trust** - Verified Facebook accounts reduce spam
- ✅ **Faster onboarding** - One-click registration
- ✅ **Better user experience** - Most Nepali users are already logged into Facebook

**Recommendation:** Enable this BEFORE launch for maximum user adoption!

---

## Step-by-Step Setup Guide

### Step 1: Create a Facebook App

1. **Go to Facebook Developers Console:**
   - Visit: https://developers.facebook.com/apps/
   - Click **"Create App"**

2. **Select App Type:**
   - Choose: **"Consumer"** or **"None"** (for basic login)
   - Click **"Next"**

3. **App Details:**
   - **App Name:** RateSewa (or "RateSewa - Doctor Directory")
   - **App Contact Email:** your-email@example.com
   - Click **"Create App"**

4. **Security Check:**
   - Complete the security verification (CAPTCHA)

---

### Step 2: Configure Facebook Login

1. **Add Facebook Login Product:**
   - In your app dashboard, find **"Add Products"** section
   - Click **"Set Up"** on **"Facebook Login"**

2. **Select Platform:**
   - Choose **"Web"**
   - Enter your website URL:
     - Development: `http://localhost:5000`
     - Production: `https://ratesewa.com` (or your actual domain)

3. **Configure OAuth Settings:**
   - Go to **Facebook Login** → **Settings** in left sidebar
   - Add **Valid OAuth Redirect URIs:**
     ```
     Development:
     http://localhost:5000/login/facebook/callback

     Production:
     https://ratesewa.com/login/facebook/callback
     https://www.ratesewa.com/login/facebook/callback
     ```
   - Click **"Save Changes"**

---

### Step 3: Get Your App Credentials

1. **Go to App Settings:**
   - Click **"Settings"** → **"Basic"** in left sidebar

2. **Copy Your Credentials:**
   - **App ID** - This is your `FACEBOOK_CLIENT_ID`
   - **App Secret** - Click **"Show"**, enter your Facebook password, copy this as `FACEBOOK_CLIENT_SECRET`

   **⚠️ IMPORTANT:** Never share your App Secret publicly or commit it to version control!

---

### Step 4: Configure RateSewa

1. **Edit `.env` file:**
   ```bash
   nano .env
   # OR
   vim .env
   ```

2. **Uncomment and add your credentials:**
   ```env
   # Facebook OAuth Configuration
   FACEBOOK_CLIENT_ID=123456789012345
   FACEBOOK_CLIENT_SECRET=abc123def456ghi789jkl012mno345pq
   ```

3. **Save the file** and restart the server:
   ```bash
   # Kill existing server (if running)
   lsof -ti:5000 | xargs kill -9

   # Restart
   ./run_dev.sh
   ```

---

### Step 5: Test Facebook Login

1. **Visit login page:**
   ```
   http://localhost:5000/login
   ```

2. **Click "Continue with Facebook"**

3. **First time setup:**
   - You'll see Facebook's authorization dialog
   - Click **"Continue as [Your Name]"**
   - Grant permissions (email, public profile)

4. **Success!**
   - You should be logged into RateSewa
   - A new user account is created automatically using your Facebook info

---

## Production Deployment

### Before Going Live:

1. **Update Facebook App Settings:**
   - Remove `localhost` from OAuth redirect URIs
   - Add production domain (`https://ratesewa.com`)
   - Update **App Domains** to `ratesewa.com`

2. **Set Privacy Policy URL:**
   - Facebook requires a privacy policy for apps in production
   - Add URL in **Settings** → **Basic** → **Privacy Policy URL**

3. **Submit for App Review (if needed):**
   - For basic login, you DON'T need app review
   - Your app can stay in "Development Mode" with unlimited users
   - If you want advanced permissions, submit for review

4. **Switch to Live Mode:**
   - Toggle **App Mode** from "Development" to "Live"
   - Only do this after testing thoroughly!

---

## Environment Configuration Summary

### Development (.env)
```env
FACEBOOK_CLIENT_ID=your_dev_app_id
FACEBOOK_CLIENT_SECRET=your_dev_app_secret
```

### Production (.env)
```env
FACEBOOK_CLIENT_ID=your_production_app_id
FACEBOOK_CLIENT_SECRET=your_production_app_secret
SESSION_COOKIE_SECURE=True  # Enable for HTTPS
```

**Note:** You can use the same Facebook app for both dev and production, just add both redirect URIs.

---

## How It Works

1. **User clicks "Continue with Facebook"**
   - App redirects to Facebook authorization page

2. **User authorizes RateSewa**
   - Facebook asks for permission to share email and public profile

3. **Facebook redirects back to RateSewa**
   - Callback URL: `/login/facebook/callback`
   - Facebook provides an access token

4. **RateSewa fetches user info**
   - Gets name, email from Facebook Graph API

5. **Account creation/login:**
   - If email exists: Log in the user
   - If new user: Create account automatically
   - User is logged into RateSewa

---

## Troubleshooting

### Error: "Facebook login is not configured"
**Solution:** Add credentials to `.env` file and restart server

### Error: "Can't Load URL: The domain of this URL isn't included in the app's domains"
**Solution:** Add your domain to **App Domains** in Facebook app settings

### Error: "Invalid OAuth Redirect URI"
**Solution:** Ensure callback URL matches exactly in Facebook settings
```
http://localhost:5000/login/facebook/callback
```

### Error: "App Not Set Up: This app is still in development mode"
**Solution:**
- In dev: Add yourself as a test user in **Roles** → **Test Users**
- In production: Switch app to "Live" mode

### User gets logged in but name is missing
**Solution:** Check if Facebook returned email. The app creates accounts using:
- Name from Facebook profile
- Email from Facebook (required)

---

## Security Notes

1. **App Secret Protection:**
   - Never commit `.env` to git (already in `.gitignore`)
   - Use different apps for dev/production (recommended)
   - Rotate secrets if compromised

2. **HTTPS Required:**
   - Facebook requires HTTPS for production apps
   - Set `SESSION_COOKIE_SECURE=True` when using HTTPS

3. **Permissions:**
   - RateSewa only requests: `email`, `public_profile`
   - No other data is accessed from Facebook

---

## Testing Checklist

- [ ] Facebook app created
- [ ] Credentials added to `.env`
- [ ] OAuth redirect URIs configured
- [ ] Server restarted
- [ ] "Continue with Facebook" button works
- [ ] Can log in with Facebook account
- [ ] User account created automatically
- [ ] User name and email saved correctly
- [ ] Can log out and log back in

---

## Quick Commands

```bash
# Check if Facebook credentials are set
grep FACEBOOK .env

# Test login endpoint
curl http://localhost:5000/login/facebook

# View server logs for errors
tail -f /var/log/ratesewa/error.log  # if configured
# OR check terminal output when running ./run_dev.sh

# Restart server
lsof -ti:5000 | xargs kill -9 && ./run_dev.sh
```

---

## Support Resources

- **Facebook Developer Docs:** https://developers.facebook.com/docs/facebook-login/web
- **App Dashboard:** https://developers.facebook.com/apps/
- **Authlib Docs (used by RateSewa):** https://docs.authlib.org/en/latest/

---

## FAQ

**Q: Do I need to verify my Facebook app?**
A: No, for basic login you can keep it in Development Mode. Only verify if you need advanced permissions or want to make it public.

**Q: Can users sign up without Facebook?**
A: Yes! Email/password registration and login still works. Facebook is just an alternative.

**Q: What happens if Facebook is down?**
A: Users can still log in with email/password. Facebook login will show an error.

**Q: Can I use Google login instead?**
A: The code currently only supports Facebook. Google OAuth would require additional implementation.

**Q: Does Facebook charge for this?**
A: No, Facebook Login is completely free.

---

## Current Implementation Details

**Files involved:**
- `app.py` - Facebook OAuth setup and callback handling (lines 37-47, 99-150)
- `templates/login.html` - Facebook login button (line 43-45)
- `.env` - Configuration file (lines 10-13)

**Routes:**
- `/login/facebook` - Initiates Facebook OAuth flow
- `/login/facebook/callback` - Handles OAuth response

**User data stored:**
- Name (from Facebook profile)
- Email (from Facebook, must be verified)
- Account is marked as regular user (not admin)

---

**Status: Ready to configure - just add your Facebook App credentials! 🚀**

Estimated setup time: **10-15 minutes**

---

**Last Updated:** 2025-12-31
