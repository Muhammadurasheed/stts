# STTS Deployment Guide 🚀

## Architecture

| Layer | Platform | Notes |
|-------|----------|-------|
| Frontend | **Vercel** | Auto-deploys from GitHub main branch |
| Backend | **Render** | Web service with free tier |
| Database | **MongoDB Atlas** | Free tier M0 cluster (512 MB) |
| AI | **Vertex AI** | GCP project `gen-lang-client-0669834943` |

---

## Step 1 — Database: MongoDB Atlas

1. Sign up at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a **free M0 cluster** (any region)
3. Create a database user (username + password — save these)
4. Under Network Access → Add IP Address → **Allow Access from Anywhere** (`0.0.0.0/0`)
5. Get your connection string: `mongodb+srv://<user>:<password>@<cluster>.mongodb.net/stts`

---

## Step 2 — Backend: Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → **Web Service**
3. Connect your GitHub repo, select the `backend/` directory
4. Settings:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add these **Environment Variables** in the Render dashboard:

```
MONGODB_URL          = mongodb+srv://...   (your Atlas connection string)
JWT_SECRET_KEY       = <generate a strong random string>
GOOGLE_CLIENT_ID     = <your Google OAuth client ID>
GEMINI_API_KEY       = <your Gemini API key>
USE_VERTEX_AI        = true
GCP_PROJECT          = gen-lang-client-0669834943
GCP_LOCATION         = us-central1
ALLOWED_ORIGINS      = https://your-app.vercel.app
DEBUG                = false
```

> ⚠️ **Vertex AI on Render**: For production Vertex AI authentication, you need to set the `GOOGLE_APPLICATION_CREDENTIALS` env var pointing to a service account JSON key, OR use the google-auth library's `impersonated_credentials`. The simplest path for now: set `USE_VERTEX_AI=false` and use `GEMINI_API_KEY` for production until you set up a service account.

6. Deploy — your backend URL will be `https://stts-backend.onrender.com`

---

## Step 3 — Frontend: Vercel

1. Go to [vercel.com](https://vercel.com) → New Project
2. Import your GitHub repo, select the `frontend/` directory
3. Framework: **Next.js** (auto-detected)
4. Add these **Environment Variables**:

```
NEXT_PUBLIC_API_URL          = https://stts-backend.onrender.com
NEXT_PUBLIC_GOOGLE_CLIENT_ID = <your Google OAuth client ID>
```

5. Deploy — your frontend URL will be `https://stts-frontend.vercel.app`

---

## Step 4 — Update Backend CORS

Once you have your Vercel URL, go back to Render → Environment Variables and update:

```
ALLOWED_ORIGINS = https://stts-frontend.vercel.app
```

Redeploy the backend. Done.

---

## Step 5 — Google OAuth: Update Authorized Origins

In [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials → your OAuth 2.0 Client:

- Add to **Authorized JavaScript origins**: `https://stts-frontend.vercel.app`
- Add to **Authorized redirect URIs**: `https://stts-frontend.vercel.app`

---

## Local Development

```bash
# Start Docker Desktop first

# Backend
cd backend
python run.py          # Starts MongoDB container + FastAPI on :8000

# Frontend (new terminal)
cd frontend
npm run dev            # http://localhost:3000
```

---

## Vercel + Vertex AI Note

For full AI triage on Vercel/Render without a service account key file:
1. Create a Service Account in GCP project `gen-lang-client-0669834943`
2. Grant it the `Vertex AI User` role
3. Download the JSON key
4. Base64-encode it and set as `GOOGLE_SERVICE_ACCOUNT_JSON` on Render
5. In `gateway.py`, load it via `google.oauth2.service_account.Credentials`

This is optional — Mock Triage ensures tickets are always classified even without Vertex AI.
