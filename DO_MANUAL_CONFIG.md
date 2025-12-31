# Fix DO App Platform Deployment - Manual Configuration

## The Problem:
DO App Platform is not detecting your Procfile. You need to manually configure the run command.

---

## 🔧 Step-by-Step Fix (5 minutes):

### Step 1: Go to Your App Settings

1. In DO dashboard, click on your **ratesewa** app
2. Click **Settings** tab (top of page)
3. Scroll down to **App Spec** section
4. Click **Edit** button

---

### Step 2: Configure the Web Service

In the YAML editor, find the `services:` section and update it to this:

```yaml
name: ratesewa
services:
- build_command: pip install -r requirements.txt
  environment_slug: python
  github:
    branch: main
    deploy_on_push: true
    repo: Prasan1/ratesewa
  http_port: 8080
  instance_count: 1
  instance_size_slug: basic-xxs
  name: web
  routes:
  - path: /
  run_command: gunicorn --worker-tmp-dir /dev/shm --workers 2 --bind 0.0.0.0:8080
    wsgi:application
  source_dir: /
```

**CRITICAL: Make sure the `run_command` line is EXACTLY:**
```
run_command: gunicorn --worker-tmp-dir /dev/shm --workers 2 --bind 0.0.0.0:8080 wsgi:application
```

---

### Step 3: Set Environment Variables

Still in the same YAML, make sure you have these under the service:

```yaml
  envs:
  - key: SECRET_KEY
    scope: RUN_TIME
    type: SECRET
    value: YOUR_GENERATED_SECRET_KEY_HERE
  - key: DATABASE_URL
    scope: RUN_TIME
    value: sqlite:///instance/doctors.db
```

**Generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and paste it as the SECRET_KEY value.

---

### Step 4: Save and Deploy

1. Click **Save** button at bottom
2. DO will ask "Deploy these changes?"
3. Click **Deploy** or **Save and Deploy**

---

## ✅ Expected Result:

Deployment should complete in 3-5 minutes with:
- ✅ Build completes successfully
- ✅ Gunicorn starts
- ✅ App responds on port 8080
- ✅ Health checks pass

---

## 🎯 Alternative: Use DO Web Interface (Easier)

If the YAML is confusing:

### Option A - Settings Tab:

1. Go to **Settings** → **Components**
2. Click on **web** component
3. Click **Edit**
4. Set these fields:

**Build Command:**
```
pip install -r requirements.txt
```

**Run Command:**
```
gunicorn --worker-tmp-dir /dev/shm --workers 2 --bind 0.0.0.0:8080 wsgi:application
```

**HTTP Port:**
```
8080
```

5. Click **Save**
6. Click **Deploy**

---

## 📋 Quick Checklist:

- [ ] Build command set to: `pip install -r requirements.txt`
- [ ] Run command set to: `gunicorn --worker-tmp-dir /dev/shm --workers 2 --bind 0.0.0.0:8080 wsgi:application`
- [ ] HTTP Port set to: `8080`
- [ ] SECRET_KEY environment variable set
- [ ] DATABASE_URL set to: `sqlite:///instance/doctors.db`
- [ ] Instance size: Basic (512MB)
- [ ] Instance count: 1

---

## 🐛 If It Still Fails:

Copy this EXACT configuration and send it to me:

1. What is your **Build Command**?
2. What is your **Run Command**?
3. What is your **HTTP Port**?
4. Screenshot of your environment variables

---

## 💡 Why This Happens:

DO App Platform sometimes doesn't auto-detect Procfile for Python apps. Manual configuration is the most reliable approach.

---

**Go to your DO dashboard now and manually set the run command!**
