# Deployment

DjangoGramm runs as a container on **Google Cloud Run**, with **Neon** for
PostgreSQL and **Cloudinary** for media. Static files are served by the
container itself through WhiteNoise.

```
Browser → Cloud Run (gunicorn + WhiteNoise) → Neon (Postgres)
                                            → Cloudinary (images)
                                            → Brevo (email)
```

---

## Prerequisites

- `gcloud` CLI, authenticated (`gcloud auth login`)
- Docker Desktop, for building locally before deploying
- Accounts: Google Cloud (billing enabled), Neon, Cloudinary, Brevo
- OAuth apps registered with GitHub and Google

---

## One-time setup

### 1. Google Cloud project

```powershell
gcloud projects create djangogramm-yurii --name="DjangoGramm"
gcloud config set project djangogramm-yurii
gcloud auth application-default set-quota-project djangogramm-yurii

gcloud billing accounts list
gcloud billing projects link djangogramm-yurii --billing-account=ACCOUNT_ID

gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

A separate project from any other work keeps billing, logs and IAM isolated,
and means deleting it later touches nothing else.

Billing must be enabled even to stay inside the free tier.

### 2. Neon database

Create a project at neon.tech in **eu-central-1 (Frankfurt)** — the same region
as the Cloud Run service, or every query pays a cross-continent round trip.

Copy the **pooled** connection string — the hostname contains `-pooler`. Cloud
Run starts and stops containers constantly, so connections open and close
constantly; the pooler reuses a smaller set of real ones and avoids exhausting
Neon's connection limit.

Apply the schema and seed the data from a local machine, before the first
deploy, so the first request hits a database that already works:

```powershell
$env:DATABASE_URL="postgresql://...-pooler...neon.tech/neondb?sslmode=require"
python manage.py migrate
python manage.py seed_db
python manage.py createsuperuser
Remove-Item Env:DATABASE_URL
```

**Clear the variable afterwards.** Otherwise the next local `manage.py` command
runs against production.

### 3. OAuth applications

Callback URLs are **exact-match**. Every environment needs its own registration.

**GitHub allows only one callback URL per app**, so production needs a *second*
OAuth app with its own client ID and secret:

| | Callback URL |
|---|---|
| local app | `http://127.0.0.1:8000/accounts/github/login/callback/` |
| production app | `https://<service-url>/accounts/github/login/callback/` |

**Google allows several redirect URIs on one client**, so add the production one
to the existing client and reuse the same credentials:

```
http://127.0.0.1:8000/accounts/google/login/callback/
https://<service-url>/accounts/google/login/callback/
```

Google's changes can take several minutes to propagate. A `redirect_uri_mismatch`
straight after saving usually means "wait", not "wrong". The error page's
"see error details" link shows the exact URI the app sent, which is the fastest
way to spot a difference.

Check you are editing credentials in the **right Google Cloud project** — the
OAuth client may live in an older project than the one running Cloud Run.

### 4. The Site record

`django.contrib.sites` starts with a row saying `example.com`, and allauth
builds confirmation-email links from it. Log into `/admin/` → Sites → change the
domain to the Cloud Run hostname, or every registration email links to
example.com.

---

## Environment variables

Cloud Run reads them from `env.yaml` in the project root. **Not committed** —
it is in both `.gitignore` and `.dockerignore`.

```yaml
DJANGO_SECRET_KEY: "50-character alphanumeric value"
DJANGO_DEBUG: "False"
DJANGO_ALLOWED_HOSTS: "djangogramm-xxxxx.europe-west3.run.app"
CSRF_TRUSTED_ORIGINS: "https://djangogramm-xxxxx.europe-west3.run.app"
DATABASE_URL: "postgresql://...-pooler...neon.tech/neondb?sslmode=require"
CLOUDINARY_CLOUD_NAME: "..."
CLOUDINARY_API_KEY: "..."
CLOUDINARY_API_SECRET: "..."
EMAIL_HOST: "smtp-relay.brevo.com"
EMAIL_PORT: "587"
EMAIL_HOST_USER: "..."
EMAIL_HOST_PASSWORD: "..."
EMAIL_USE_TLS: "True"
DEFAULT_FROM_EMAIL: "verified-sender@example.com"
GITHUB_CLIENT_ID: "production app id"
GITHUB_CLIENT_SECRET: "production app secret"
GOOGLE_CLIENT_ID: "..."
GOOGLE_CLIENT_SECRET: "..."
```

Notes:

- **Every value in quotes.** Cloud Run rejects non-string values.
- `DJANGO_ALLOWED_HOSTS` is the **hostname only**, no scheme.
  `CSRF_TRUSTED_ORIGINS` needs the **full `https://` prefix**. Django is strict
  about both, and the failure modes differ: a wrong `ALLOWED_HOSTS` gives
  `DisallowedHost` on every request, a wrong `CSRF_TRUSTED_ORIGINS` lets pages
  load but fails every form submission.
- The `SECRET_KEY` is alphanumeric only. A `$` in it breaks Docker Compose
  variable expansion locally.
- `DEFAULT_FROM_EMAIL` must be a **verified sender** in Brevo, or mail is
  rejected.

---

## Deploying

```powershell
gcloud run deploy djangogramm --source . --region europe-west3 --allow-unauthenticated --env-vars-file env.yaml
```

The first run offers to create an Artifact Registry repository — accept.

`--source .` uploads the source and builds the `Dockerfile` with Cloud Build, so
no local image push is needed. Takes 3–5 minutes the first time, less
afterwards.

### The first deploy is a two-step

The service URL does not exist until the service does, but Django needs to know
it. So:

1. Deploy with `DJANGO_ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` set to any
   placeholder string. Cloud Run prints the URL.
2. Put the real values in `env.yaml` and deploy again.

The site is not usable between those two steps. Expected, not a fault.

---

## Verifying locally before deploying

A build that succeeds can still fail at runtime. With the local Postgres
running (`docker compose up -d`):

```powershell
docker build -t djangogramm .

docker run --rm -e DJANGO_SECRET_KEY=local-test-key -e DJANGO_DEBUG=False -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 -e DATABASE_URL="postgres://USER:PASSWORD@host.docker.internal:5433/djangogramm" djangogramm python manage.py migrate --check

docker run --rm -e DJANGO_SECRET_KEY=local-test-key -e DJANGO_DEBUG=False -e DJANGO_ALLOWED_HOSTS=localhost -e DATABASE_URL="postgres://USER:PASSWORD@host.docker.internal:5433/djangogramm" djangogramm python manage.py check --deploy
```

`host.docker.internal` is how a container reaches the Windows host —
`localhost` inside a container means the container itself.

`check --deploy` runs Django's security checklist. The only expected warning is
`security.W009` about the short test key.

Running the container with `-p 8080:8080` and opening `http://localhost:8080`
redirects to HTTPS and fails in the browser — that is `SECURE_SSL_REDIRECT`
working, since there is no TLS locally. What matters is that gunicorn starts and
logs the request.

---

## How the Dockerfile is built

Two stages:

1. **`node:20-slim`** — `npm ci`, then `npm run build`, producing
   `static/dist/bundle.{css,js}`
2. **`python:3.12-slim`** — installs `requirements.txt`, copies the source,
   copies **only the built bundle** from stage 1, runs `collectstatic`, starts
   gunicorn

`node_modules` never reaches the final image.

**Dependencies are copied before the source** so Docker's layer cache skips
`pip install` when only code has changed.

**Dummy build-time environment variables** are set before `collectstatic`,
because `settings.py` reads `os.environ["DJANGO_SECRET_KEY"]` with brackets and
raises if it is missing. Setting `DATABASE_URL` also avoids the `POSTGRES_*`
lookups in the local-database branch. Cloud Run overrides all of them at
runtime.

**`.dockerignore` is separate from `.gitignore`.** Docker does not read
`.gitignore`, so `env.yaml`, `.venv/` and `node_modules/` have to be listed in
both.

---

## Production settings

`config/settings.py`, active only when `DEBUG` is false:

```python
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

**`SECURE_PROXY_SSL_HEADER` is the critical one.** Cloud Run terminates TLS at
its load balancer and forwards plain HTTP to the container. Without this header
setting, Django considers every request insecure, and `SECURE_SSL_REDIRECT`
produces an infinite redirect loop. This is the most common Cloud Run
deployment failure.

The database configuration accepts either form:

```python
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    # local POSTGRES_* variables
```

`ssl_require` is deliberately **not** passed. Neon's connection string already
ends with `?sslmode=require`, so the URL describes the connection; forcing SSL
in settings breaks the local Docker Postgres, which does not support it.

`conn_max_age=600` reuses connections rather than opening one per request —
important with a remote database.

---

## Static files

`whitenoise.storage.CompressedManifestStaticFilesStorage`:

- **Compressed** — pre-builds gzip and Brotli at `collectstatic` time
- **Manifest** — appends a content hash to each filename, so browsers can cache
  indefinitely and still get new files when they change

Manifest storage **fails the build** if a template references a static file that
does not exist. That is why CI runs `npm ci && npm run build` before the tests:
`static/dist/` is gitignored, so without that step a missing bundle would first
surface during deployment.

`cloudinary_storage` must appear **after** `django.contrib.staticfiles` in
`INSTALLED_APPS`. It ships its own `collectstatic` command that reads the
pre-Django-5.1 `STATICFILES_STORAGE` setting and crashes with
`AttributeError: 'Settings' object has no attribute 'STATICFILES_STORAGE'`.
Ordering it after `staticfiles` makes Django's own command win. (The
Cloudinary docs prescribe the opposite order — correct only when serving
*static* files through Cloudinary, which this project does not.)

---

## Routine operations

**Redeploy after a code change:**

```powershell
gcloud run deploy djangogramm --source . --region europe-west3 --allow-unauthenticated --env-vars-file env.yaml
```

**Migrations against production** — run locally with `DATABASE_URL` set to the
Neon string, then clear it. No proxy or bastion is needed; Neon is reachable
over the public internet with SSL.

**Read the logs:**

```powershell
gcloud run services logs read djangogramm --region europe-west3 --limit 50
```

**Roll back** — Cloud Run keeps every revision:

```powershell
gcloud run revisions list --service djangogramm --region europe-west3
gcloud run services update-traffic djangogramm --region europe-west3 --to-revisions REVISION_NAME=100
```

---

## Cost

- **Cloud Run** — scales to zero; free tier covers 2M requests/month. An idle
  portfolio site costs approximately nothing.
- **Neon** — free tier; no charge while idle.
- **Cloudinary, Brevo** — free tiers.
- **Cloud Build** — free daily quota, ample for a few deploys a month.

Cloud SQL was rejected for exactly this reason: it bills continuously for an
instance nobody is using, which matters for a site that stays up for months.

---

## Known gaps

- **No automated deployment.** Deploys are manual; CI runs lint and tests only.
  A GitHub Actions job with Workload Identity Federation would close this.
- **Secrets live in `env.yaml`**, passed as plain environment variables. Google
  Secret Manager would be the production answer.
- **`seed_db` was run once by hand** against Neon. There is no scheduled
  refresh.