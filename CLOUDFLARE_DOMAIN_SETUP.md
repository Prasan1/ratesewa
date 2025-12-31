# Connect RateSewa Domain with Cloudflare

## 🎯 Quick Setup Guide (10 minutes)

Your app is live! Now let's connect your custom domain (ratesewa.com or ratesewa.np).

---

## Step 1: Get Your DO App URL (1 minute)

1. In DigitalOcean dashboard, go to your **ratesewa** app
2. Look at the top - you'll see a URL like:
   ```
   https://ratesewa-xxxxx.ondigitalocean.app
   ```
3. **Copy this URL** - you'll need it

**OR** get the specific CNAME target:
1. In DO app, go to **Settings** → **Domains**
2. You'll see a CNAME value like: `ratesewa-xxxxx.ondigitalocean.app`

---

## Step 2: Add Domain in DigitalOcean (3 minutes)

### 2.1 Add Your Domain:

1. In DO dashboard, go to your **ratesewa** app
2. Click **Settings** tab
3. Scroll to **Domains** section
4. Click **Add Domain**

### 2.2 Enter Your Domain:

**For .com domain:**
```
ratesewa.com
```

**For .np domain:**
```
ratesewa.com.np
```
(or whatever your actual domain is)

### 2.3 DO Will Show You DNS Records:

DO will display something like:

**For root domain (@):**
```
Type: CNAME
Name: @
Value: ratesewa-xxxxx.ondigitalocean.app
```

**For www:**
```
Type: CNAME
Name: www
Value: ratesewa-xxxxx.ondigitalocean.app
```

**Copy these values!** You'll add them to Cloudflare next.

---

## Step 3: Configure Cloudflare DNS (5 minutes)

### 3.1 Login to Cloudflare:

1. Go to **https://dash.cloudflare.com**
2. Login to your account
3. Select your domain (ratesewa.com)

### 3.2 Add DNS Records:

Click **DNS** in the left sidebar, then:

#### Record 1 - Root Domain (@ or ratesewa.com):

⚠️ **IMPORTANT for Cloudflare with CNAME at root:**

Cloudflare supports CNAME flattening, so you CAN use CNAME at root:

**Settings:**
```
Type: CNAME
Name: @ (or ratesewa.com)
Target: ratesewa-xxxxx.ondigitalocean.app
Proxy status: Proxied (orange cloud icon) ✅
TTL: Auto
```

**CRITICAL:** Make sure the **orange cloud is ON** (Proxied) - this enables Cloudflare's CDN and SSL.

#### Record 2 - WWW Subdomain:

**Settings:**
```
Type: CNAME
Name: www
Target: ratesewa-xxxxx.ondigitalocean.app
Proxy status: Proxied (orange cloud icon) ✅
TTL: Auto
```

### 3.3 Remove Conflicting Records:

⚠️ **IMPORTANT:** Delete any existing A or CNAME records for:
- `@` or root domain
- `www`

Only keep the two new CNAME records you just created.

### 3.4 Click **Save**

---

## Step 4: Configure Cloudflare SSL (2 minutes)

### 4.1 SSL/TLS Settings:

1. In Cloudflare dashboard, click **SSL/TLS** (left sidebar)
2. Select **SSL/TLS encryption mode**
3. Choose: **Full** or **Full (strict)**
   - ✅ **Full (strict)** - Most secure (recommended)
   - ✅ **Full** - Good (if strict doesn't work)
   - ❌ **NOT Flexible** - Don't use this

### 4.2 Always Use HTTPS:

1. Still in **SSL/TLS** section
2. Click **Edge Certificates**
3. Find **Always Use HTTPS**
4. Turn it **ON** ✅

This redirects all HTTP traffic to HTTPS automatically.

### 4.3 Minimum TLS Version:

1. In **Edge Certificates**
2. Set **Minimum TLS Version** to: **TLS 1.2** or higher

---

## Step 5: Wait for DNS Propagation (10-60 minutes)

### Check Propagation:

Use these tools to check if DNS is propagated:

**Check globally:**
```
https://dnschecker.org
```
Enter: `ratesewa.com` or your domain

**Check locally:**
```bash
# Check CNAME
dig ratesewa.com

# Check WWW
dig www.ratesewa.com
```

You should see the CNAME pointing to `ratesewa-xxxxx.ondigitalocean.app`

---

## Step 6: Test Your Domain (2 minutes)

Once DNS propagates (10-60 min), test:

### 6.1 Visit Your Domain:

**Root domain:**
```
https://ratesewa.com
```

**WWW subdomain:**
```
https://www.ratesewa.com
```

Both should show your RateSewa app! ✅

### 6.2 Test HTTP → HTTPS Redirect:

Try:
```
http://ratesewa.com
```

Should automatically redirect to:
```
https://ratesewa.com
```

---

## ✅ Configuration Summary

### In DigitalOcean:
- ✅ Custom domain added: `ratesewa.com`
- ✅ CNAME target provided

### In Cloudflare:
- ✅ CNAME for `@` → `ratesewa-xxxxx.ondigitalocean.app` (Proxied ☁️)
- ✅ CNAME for `www` → `ratesewa-xxxxx.ondigitalocean.app` (Proxied ☁️)
- ✅ SSL mode: Full (strict)
- ✅ Always Use HTTPS: ON
- ✅ Proxy status: Enabled (orange cloud)

---

## 🔒 SSL Certificate

**Good news:** SSL is automatic!

- **Cloudflare** provides SSL certificate (free)
- **DigitalOcean** also provides SSL (free)
- **Your domain:** Fully encrypted HTTPS ✅

No manual certificate installation needed!

---

## 🐛 Troubleshooting

### Domain shows Cloudflare error page:

**Error 521 or 522:**
- Wait a few more minutes for DNS to propagate
- Check that domain is added in DO App Platform
- Verify CNAME records are correct

**Error 525:**
- Change Cloudflare SSL mode from "Flexible" to "Full"

### Domain not loading:

1. **Check DNS propagation:**
   ```bash
   dig ratesewa.com
   ```
   Should return CNAME to DO app

2. **Check Cloudflare proxy:**
   - Orange cloud should be ON (proxied)

3. **Clear browser cache:**
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

### "Too many redirects" error:

- Change SSL mode in Cloudflare to **Full** or **Full (strict)**
- Make sure "Always Use HTTPS" is ON in Cloudflare

---

## 📊 Cloudflare Benefits

With Cloudflare enabled, you get:

✅ **Free SSL certificate** (automatic)
✅ **DDoS protection** (free tier)
✅ **CDN** - Faster loading worldwide
✅ **Caching** - Reduced server load
✅ **Analytics** - Traffic insights
✅ **Firewall** - Block malicious traffic

---

## 🎯 Quick Reference

### Your Setup:

**App URL (DO):**
```
https://ratesewa-xxxxx.ondigitalocean.app
```

**Custom Domain:**
```
https://ratesewa.com
https://www.ratesewa.com
```

**DNS Records (Cloudflare):**
```
@ (root)  → CNAME → ratesewa-xxxxx.ondigitalocean.app (Proxied)
www       → CNAME → ratesewa-xxxxx.ondigitalocean.app (Proxied)
```

**SSL Mode:** Full (strict)
**Always HTTPS:** ON
**Proxy:** Enabled (orange cloud)

---

## ⏱️ Timeline:

- **DNS configuration:** 5 minutes
- **DNS propagation:** 10-60 minutes
- **SSL activation:** Automatic
- **Total time:** ~1 hour max

---

## 🚀 After Domain is Live:

### Next Steps:

1. **Seed database** (if not done):
   ```bash
   # In DO Console
   python3 seed_data.py
   python3 change_admin_password.py
   ```

2. **Test all features:**
   - User registration
   - Doctor search
   - Reviews/ratings
   - Admin panel

3. **Announce launch!** 🎉

---

**Your app is live and ready for your custom domain!**

**What's your domain name?** I'll help you verify the DNS settings.
