# Enable Google Login - Quick Setup (5 minutes)

## 🚀 Much Easier Than Facebook!

Google OAuth is straightforward - no phone verification, no device trust issues!

---

## Step 1: Go to Google Cloud Console (1 minute)

### 1.1 Open Google Cloud Console:
**URL:** https://console.cloud.google.com/

**Login** with your Google account (Gmail)

---

## Step 2: Create New Project (1 minute)

### 2.1 Create Project:
1. At the top, click the **project dropdown** (says "Select a project")
2. Click **"NEW PROJECT"** (top right)

### 2.2 Fill Project Details:
- **Project name:** `RankSewa` (or "ranksewa-nepal")
- **Organization:** Leave blank (not required)
- Click **"CREATE"**

⏱️ Wait ~10 seconds for project to be created.

### 2.3 Select Your Project:
1. Click the **project dropdown** again
2. Select **"RankSewa"** from the list

---

## Step 3: Enable Google+ API (1 minute)

### 3.1 Go to APIs & Services:
1. Left sidebar (☰ menu) → **"APIs & Services"** → **"Library"**

### 3.2 Search for Google+ API:
1. In the search box, type: **"Google+ API"**
2. Click on **"Google+ API"**
3. Click **"ENABLE"**

⏱️ Wait ~5 seconds

---

## Step 4: Create OAuth Credentials (2 minutes)

### 4.1 Go to Credentials:
1. Left sidebar → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** (top)
3. Select **"OAuth client ID"**

### 4.2 Configure Consent Screen (First Time Only):

If prompted "Configure consent screen":

1. Click **"CONFIGURE CONSENT SCREEN"**
2. Choose **"External"** (allows anyone to login)
3. Click **"CREATE"**

**Fill OAuth consent screen:**
- **App name:** `RankSewa`
- **User support email:** Your email
- **App logo:** Skip for now
- **Authorized domains:** `ranksewa.com`
- **Developer contact:** Your email
- Click **"SAVE AND CONTINUE"**

**Scopes page:**
- Click **"ADD OR REMOVE SCOPES"**
- Select: `email` and `profile`
- Click **"UPDATE"**
- Click **"SAVE AND CONTINUE"**

**Test users:**
- Skip this (click **"SAVE AND CONTINUE"**)

**Summary:**
- Click **"BACK TO DASHBOARD"**

### 4.3 Create OAuth Client ID:

1. Go back to **"Credentials"** (left sidebar)
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**

**Configure:**
- **Application type:** `Web application`
- **Name:** `RankSewa Web App`

**Authorized JavaScript origins:**
```
https://ranksewa.com
```

**Authorized redirect URIs:**
```
https://ranksewa.com/login/google/authorized
```

Click **"CREATE"**

---

## Step 5: Get Your Credentials (30 seconds)

### 5.1 Copy Credentials:

A popup will show:
- **Your Client ID:** `123456789-abcdefg.apps.googleusercontent.com`
- **Your Client Secret:** `GOCSPX-xxxxxxxxxxxxx`

**COPY BOTH!** Save them somewhere safe.

You can also click **"DOWNLOAD JSON"** to save them.

---

## Step 6: Add to DigitalOcean (1 minute)

### 6.1 Go to Your App:
1. **DigitalOcean Dashboard** → Your **ratesewa** app
2. **Settings** → **App-Level Environment Variables**
3. Click **"Edit"**

### 6.2 Add Google Credentials:

| Key | Value |
|-----|-------|
| `GOOGLE_CLIENT_ID` | [Your Client ID from Step 5] |
| `GOOGLE_CLIENT_SECRET` | [Your Client Secret from Step 5] |

### 6.3 Save and Deploy:
1. Click **"Save"**
2. Click **"Deploy"** or **"Redeploy"**

⏱️ Wait 3-5 minutes for deployment

---

## ✅ That's It!

Once I enable the Google login code and it deploys, users will see:

**Login page:**
- Email/password form
- **"Continue with Google"** button ← NEW!

**User clicks button:**
1. Redirects to Google
2. Select Google account
3. Authorize RankSewa
4. Automatically logged in! ✅

---

## 🧪 Testing:

1. Visit: https://ranksewa.com/login
2. Click **"Continue with Google"**
3. Choose your Google account
4. Click **"Continue"** or **"Allow"**
5. Should redirect back and be logged in ✅

---

## 🐛 Troubleshooting

### "Error 400: redirect_uri_mismatch"
**Fix:** Make sure you added exactly:
```
https://ranksewa.com/login/google/authorized
```
to **Authorized redirect URIs** (check for typos!)

### "This app isn't verified"
**Fix:** This is normal for new apps. Users can click **"Advanced"** → **"Go to RankSewa (unsafe)"** - it's safe, just not verified yet.

**To remove warning (optional):**
1. Go to OAuth consent screen
2. Click **"PUBLISH APP"**
3. Or go through verification process (takes 1-2 weeks)

### Button doesn't appear
**Fix:**
1. Check environment variables are set
2. Clear browser cache
3. Make sure code is uncommented

---

## 📊 Quick Summary

**What you need:**
1. Google Client ID
2. Google Client Secret

**Where to get them:**
- https://console.cloud.google.com/
- Create project → Enable Google+ API → Create OAuth credentials

**Total time:** 5 minutes

---

## ✨ Next Steps:

After I enable the code:
- ✅ Google login will work immediately
- ✅ Users can sign in with one click
- ✅ Much better UX for Nepal users!

**You can add Facebook later** when their security stops being annoying!

---

**Ready? Get your Google credentials using the steps above, then tell me when you have them!** 🚀
