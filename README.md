# Vivek Verma — Freelance QA & Device Testing Lab

A Django site positioning Vivek Verma as a freelance QA Automation Engineer / SDET who
tests web, desktop, mobile (Android + iOS), API/backend, and physical devices (cameras,
IoT, VoIP/telecom hardware). International clients submit project inquiries through a
contact form; every submission is saved to the database (visible in Django admin) and
optionally emailed to `CONTACT_RECEIVER_EMAIL`. A built-in help chatbot answers common
questions instantly and gets smarter over time as you teach it new answers.

## Stack
- Django 6
- SQLite by default; Postgres-ready via `DATABASE_URL` (see "Database persistence" below)
- WhiteNoise for static file serving
- Gunicorn for production serving
- GitHub Actions (CI) + Render Blueprint (CD) — see "CI/CD pipeline" below

## Project layout
```
config/     project settings, root urls, wsgi/asgi
core/       the site itself: contact form model/views/admin, templates, static, CSS
chatbot/    the help-chat feature: KnowledgeBase + ChatQuery models, matching engine, chat API
templates/  base.html (site-wide layout)
```

## The help chatbot — how it "learns"
There's no external AI API involved (no cost, no API key). The chatbot in the bottom-right
corner matches a visitor's question against `chatbot.KnowledgeBase` entries using word-overlap
+ fuzzy string matching (see `chatbot/matching.py`). The **same** KnowledgeBase also powers the
FAQ section on the homepage, so you only maintain answers in one place.

- **Confident match** → the bot answers instantly and the FAQ shows the same answer.
- **No confident match** → the bot gives a fallback reply ("I've noted it, Vivek will follow
  up") and logs the question in `chatbot.ChatQuery` with `needs_answer=True`.

To "train" the bot, log into `/admin/` → **Chat queries** (under Help Chatbot), find the
unanswered questions, type an answer into the `answer_given` field, save, select the row, and
run the **"Add selected queries to the Knowledge Base"** action. That question is now answered
instantly for every future visitor and appears in the FAQ. You can also add/edit entries
directly under **Knowledge base** at any time — no code changes needed.

Seed data lives in `chatbot/management/commands/seed_knowledgebase.py`; re-run
`python manage.py seed_knowledgebase` any time to refresh/add to the defaults (it's safe to
run repeatedly — it updates existing entries by question text).

## Local setup
```bash
python3 -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env             # then edit values as needed

python manage.py migrate
python manage.py createsuperuser # to view leads in /admin/
python manage.py runserver
```
Visit http://127.0.0.1:8000/ for the site and http://127.0.0.1:8000/admin/ to view
contact-form submissions (`Core > Contact messages`).

A default superuser was created during setup: **admin / ChangeMe123!** — change this
password immediately (`python manage.py changepassword admin`) before going live.

## Editing content
All page copy lives in `core/templates/core/home.html`. Styling is in
`core/static/core/css/style.css` (single file, no build step — edit and refresh).

## Receiving contact-form emails
By default, email just prints to the console (`EMAIL_BACKEND` = console backend) so you
can test locally without real credentials. To get real email notifications in
production, set these in `.env` (or your host's environment variables):
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=your-gmail-address@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password   # Google Account > Security > App Passwords
DEFAULT_FROM_EMAIL=your-gmail-address@gmail.com
CONTACT_RECEIVER_EMAIL=vivkverma905@gmail.com
```
Even without email configured, every submission is always saved in the database and
visible in `/admin/`.

## CI/CD pipeline

**CI — `.github/workflows/ci.yml`**: on every push/PR to `main`, GitHub Actions installs
dependencies, checks for missing migrations, runs `manage.py check`, runs the full test
suite, and verifies `collectstatic` succeeds with `DEBUG=False`. A red X on a commit means
don't deploy it.

**CD — `render.yaml`**: a Render "Blueprint" that describes the whole web service —
build command, start command, and environment variables — as code. Render watches the
GitHub repo and redeploys automatically on every push to `main` that passes.

### One-time setup
1. Create an empty GitHub repo and push this project to it (see commands below).
2. On [render.com](https://render.com), choose **New → Blueprint**, connect the GitHub
   repo. Render reads `render.yaml` and creates the web service automatically.
3. In the Render dashboard, set the two secret env vars it left blank
   (`sync: false` in `render.yaml` means "ask me, don't store it in git"):
   - `EMAIL_HOST_USER` = `vivkverma905@gmail.com`
   - `EMAIL_HOST_PASSWORD` = your Gmail App Password
4. Deploy. Render runs migrations, `collectstatic`, and seeds the chatbot's knowledge
   base automatically as part of the build command.
5. From then on: push to `main` → CI runs → if green, Render auto-deploys. No manual steps.

```bash
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```

### Database persistence — read this before relying on the free tier
Render's **free** web service plan has an ephemeral filesystem: the SQLite database file
can be wiped on redeploy or restart. Contact-form submissions still reach your inbox via
email regardless (that path doesn't depend on the disk), but the "Contact messages" list
in `/admin/` is not a safe permanent record on the free tier.

To fix this with **zero code changes**, add a `DATABASE_URL` environment variable pointing
at a real Postgres instance — `config/settings.py` already reads it via `dj-database-url`
and falls back to SQLite only when it's absent:
- Render's own free Postgres (expires after 90 days unless upgraded), or
- [Neon](https://neon.tech) / [Supabase](https://supabase.com) free tier (no expiry as of
  writing) — create a database there, copy its connection string into Render's
  `DATABASE_URL` env var, redeploy, done.

### Custom domain
Add the domain in Render's dashboard, then add it to the `ALLOWED_HOSTS` and
`CSRF_TRUSTED_ORIGINS` env vars (e.g. `ALLOWED_HOSTS=yourdomain.com,.onrender.com`,
`CSRF_TRUSTED_ORIGINS=https://yourdomain.com`).

## Production checklist
- [ ] `DEBUG=False` (set by `render.yaml`)
- [ ] Real `SECRET_KEY` (auto-generated by `render.yaml`'s `generateValue: true`)
- [ ] `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` updated once you add a custom domain
- [ ] Real Gmail App Password set for `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` in Render
- [ ] Superuser created on the deployed instance (`render shell` → `python manage.py
      createsuperuser`) and its password is NOT `ChangeMe123!`
- [ ] Decide on the SQLite-vs-Postgres tradeoff above before relying on `/admin/` as your
      only record of leads
