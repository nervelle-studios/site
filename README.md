# Nervelle Studios — Client Portal (Render-ready)

This is a small Flask app that provides:
- Two types of users: **admin** and **clients**.
- Admin can create / edit / delete client accounts and set their site preview links.
- Clients log in and see a modal with their personalized site preview (embedded via an `<iframe>`).

---

## Quick overview of files
- `app.py` — main Flask application (DB model, auth, admin CRUD).
- `templates/` — HTML templates (login, dashboard, admin pages).
- `static/styles.css` — basic styling.
- `requirements.txt` — Python dependencies.
- `runtime.txt` — Python version for Render.

---

## Local testing (quick)
1. Install Python 3.10+.
2. Create virtualenv and activate:
   ```bash
   python -m venv venv
   source venv/bin/activate   # mac/linux
   venv\Scripts\activate      # windows
   ```
3. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
4. (Optional) Set environment variables for an admin user:
   ```bash
   export ADMIN_USERNAME=youremail
   export ADMIN_PASSWORD=strongpassword
   export SECRET_KEY="pick-a-secret"
   ```
   On Windows (cmd): `set ADMIN_USERNAME=youremail`
5. Run locally:
   ```bash
   python app.py
   ```
6. Open `http://localhost:10000` and login with admin credentials (the app creates the admin from env vars on first run).

---

## Deploying to Render (step-by-step)

### A. Prepare a GitHub repository
1. Create a GitHub account (github.com) if you don't have one.
2. Create a **new repository**, e.g. `nervelle-render-client-portal`.
3. Locally:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo>.git
   git push -u origin main
   ```
   If you're unfamiliar with GitHub's UI, you can upload files using the website instead.

### B. Create a Render account & connect the repo
1. Sign up at https://render.com and verify email.
2. Click **New** → **Web Service**.
3. Connect your GitHub account and select the repo.
4. For **Environment**, choose `Python`.
5. Build command: leave blank (Render will run pip install automatically if `requirements.txt` is present).
6. Start command:
   ```
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```
7. Add Environment Variables in Render (Dashboard → Environment → Environment Variables):
   - `SECRET_KEY` = a secret string
   - `ADMIN_USERNAME` = your admin username (e.g. admin)
   - `ADMIN_PASSWORD` = a strong admin password
   - (Optional) `DATABASE_URL` = Postgres URL if you provisioned a Render Postgres DB (recommended for production)

8. Deploy. Render will build and provide a public URL like `https://your-app.onrender.com`.

### C. Using Postgres on Render (recommended for persistence)
1. In Render dashboard, click **New** → **Postgres**.
2. Create a database (note the DATABASE_URL).
3. In your Web Service settings, add the `DATABASE_URL` environment variable with that value.
4. On deploy, SQLAlchemy will pick it up automatically.

---

## Embedding on your Site.pro site
Use an `iframe` inside your Site.pro page to embed the portal:

```html
<iframe
  src="https://your-app.onrender.com"
  width="100%"
  height="700"
  style="border:none; border-radius:12px; box-shadow:0 0 15px rgba(0,0,0,0.2);">
</iframe>
```

If you'd rather open a modal on your site that contains the iframe, add a button and open a modal (we can provide that snippet later if you want).

---

## Notes & Security
- Passwords are hashed (werkzeug). Admin created from env vars on first run.
- For production, use `DATABASE_URL` (Postgres) rather than SQLite to avoid data loss across deploys.
- Consider enabling HTTPS-only cookies, CSRF protection (Flask-WTF), and stronger session management for production.

---

If you want, I can:
- Generate a GitHub-ready repo ZIP (provided here) — use it to upload to GitHub.
- Or, I can walk you through each step live and explain every command.
