# 5A Premier League 2026 — Complete Deployment Guide
## Tanmay Chashak | GitHub: sr7raul

---

## WHAT YOU'LL SET UP
- App hosted FREE on Streamlit Cloud
- Data stored FREE on Supabase (cloud database)
- Works on ANY device, ANY browser, NO installation
- URL: https://5apl2026.streamlit.app (or similar)

## TOTAL TIME: ~15 minutes

---

## STEP 1 — Create GitHub Repository (3 mins)

1. Go to **github.com** → Sign in as **sr7raul**
2. Click the **+** button (top right) → **New repository**
3. Repository name: `5apl2026`
4. Set to **Private** (recommended)
5. Click **Create repository**
6. Click **uploading an existing file** link
7. Drag & drop your entire `cricket_app` folder contents
   (app.py, requirements.txt, photos folder, .streamlit folder)
8. Scroll down → Click **Commit changes**

✅ Your code is now on GitHub

---

## STEP 2 — Create Supabase Database (5 mins)

1. Go to **supabase.com** → Click **Start your project**
2. Sign up with your GitHub account (sr7raul) → Easier!
3. Click **New Project**
   - Name: `5apl2026`
   - Database Password: choose something (save it!)
   - Region: **South Asia (Mumbai)** → fastest for you
4. Click **Create new project** → Wait ~2 mins for setup

5. Once ready → Click **SQL Editor** (left sidebar)
6. Click **New query** → Paste this SQL and click **Run**:

```sql
CREATE TABLE app_state (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO app_state (key, value) VALUES ('match_state', 'null');
```

7. Now get your credentials:
   - Click **Project Settings** (gear icon, left sidebar)
   - Click **API**
   - Copy **Project URL** (looks like: https://abcdefgh.supabase.co)
   - Copy **anon public** key (long string starting with eyJ...)

✅ Supabase database is ready

---

## STEP 3 — Connect Supabase to Streamlit Cloud (5 mins)

1. Go to **share.streamlit.io**
2. Click **Sign in with GitHub** → Use sr7raul account
3. Click **New app**
4. Fill in:
   - Repository: `sr7raul/5apl2026`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: type `5apl2026` (gives you 5apl2026.streamlit.app)
5. Click **Advanced settings**
6. In the **Secrets** box, paste this (replace with your actual values):

```toml
SUPABASE_URL = "https://YOUR_PROJECT_ID.supabase.co"
SUPABASE_KEY = "YOUR_ANON_PUBLIC_KEY_HERE"
```

7. Click **Deploy!**
8. Wait 3-4 minutes for first deploy

✅ App is LIVE at your Streamlit URL!

---

## STEP 4 — TEST BEFORE TOURNAMENT DAY

1. Open your app URL on your phone
2. Go to Start Match → play a few test balls
3. Refresh the page → score should still be there ✅
4. Open on a second device → should show same score ✅
5. Click Reset All Data to clear test data before tournament

---

## TOURNAMENT DAY SETUP

### Scorer Screen (your phone or any phone):
- Open: **your-app-url.streamlit.app**
- This person enters all runs, wickets, extras

### Projector/Display Screen (borrowed laptop or TV):
- Open any browser → same URL
- Works on Smart TV browser too!
- No installation, no setup needed

### Projector with laptop:
1. Connect HDMI cable
2. Windows + P → **Extend**
3. Open browser on projector screen
4. Go to app URL
5. Done!

---

## WHAT HAPPENS IF...

| Situation | What happens |
|-----------|-------------|
| Browser closes accidentally | Reopen URL — all data safe in cloud |
| Laptop sleeps | Wake up, reopen URL — data safe |
| Internet drops for 5 mins | App shows last state, saves when reconnected |
| Someone uses phone | Full app works on mobile browser |
| Projector laptop restarts | Reopen URL — still works |

---

## UPDATING THE APP LATER

If you need any changes to the app:
1. Download new `app.py` from me
2. Go to github.com/sr7raul/5apl2026
3. Click on `app.py` → Click pencil icon (Edit)
4. Replace content → Click **Commit changes**
5. Streamlit auto-redeploys in 2 minutes ✅

---

## QUICK REFERENCE LINKS

- Your app: https://5apl2026.streamlit.app
- GitHub repo: https://github.com/sr7raul/5apl2026
- Supabase dashboard: https://supabase.com/dashboard
- Streamlit cloud: https://share.streamlit.io

---

Built for 5A Premier League 2026 ❤️
