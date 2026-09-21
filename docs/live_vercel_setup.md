# Fireground AI — Automatic Live VNNX → Vercel Updates

## Architecture

Local VNNX simulation → `POST /api/update` → Vercel Function → private Vercel Blob → `GET /api/latest` → Vercel dashboard.

The localhost dashboard still reads the same local result JSON. The new liveweb inference script writes the local JSON after every window and also publishes each window update to Vercel when configured.

## Required Vercel setup

1. In the Vercel project, open **Storage**.
2. Create a **Blob** store and choose **Private** access.
3. Connect the Blob store to `fireground-ai-dashboard`.
4. In **Settings → Environment Variables**, add:
   - Name: `FIREGROUND_INGEST_TOKEN`
   - Value: a long random secret token
   - Environments: Production (and Preview only if needed)
5. Redeploy after adding the environment variable.

Vercel Blob private storage requires authenticated server-side access, and Vercel Functions can use the Blob SDK. The API in this project keeps the write token on the server; the browser only talks to `/api/latest`. See the official Vercel Blob and Functions docs.

## Local setup

Create a local file at:

    /mnt/c/Users/Asus/Fireground_AI/.fireground.env

with:

    FIREGROUND_VERCEL_API_URL=https://YOUR-VERCEL-PROJECT-DOMAIN
    FIREGROUND_VERCEL_TOKEN=YOUR_SECRET_TOKEN

Do not commit this file. It is intentionally ignored by `.gitignore` in the final setup.

The API URL should be your stable production Vercel domain, without a trailing slash.

## Run

Terminal 1 (VNNX + publisher):

    cd /mnt/c/Users/Asus/Fireground_AI
    source /home/arvind/VectorBlox-SDK/setup_vars.sh
    python3 src/live_vnnx_fireground_system_liveweb.py

Terminal 2 (localhost visual dashboard):

    cd /mnt/c/Users/Asus/Fireground_AI
    python3 dashboard/fireground_visual_dashboard.py

Local dashboard:

    http://127.0.0.1:8765

Online dashboard:

    https://YOUR-VERCEL-PROJECT-DOMAIN/

The Vercel dashboard polls `/api/latest` every two seconds, so each published VNNX window appears online without manually committing `dashboard_data.json`.

## Security

Never put `FIREGROUND_INGEST_TOKEN` in HTML, JavaScript, Git, or the public Vercel dashboard. Only the local publisher and the Vercel update function should know it.
