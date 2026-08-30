# DjangoGramm

A social photo-sharing application built with Django. Users register by email, create one or more profiles, publish posts with multiple images and tags, follow other profiles, and read a personalised feed.


## Tech stack

- **Backend:** Django 5.2 LTS, PostgreSQL 17
- **Database driver:** psycopg 3
- **Image storage:** Cloudinary
- **Testing:** pytest + pytest-django
- **Lint & format:** ruff
- **CI:** GitHub Actions
- **Deployment:** Docker container on Google Cloud Run

## Running locally

Requires Python 3.12 and Docker.

## Environment variables

Copy `.env.example` to `.env` and fill in the blanks.

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Generate with the command below. Alphanumeric only |
| `DJANGO_DEBUG` | `True` locally, `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated. Enforced when `DEBUG=False` |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Read by both Django and Docker Compose |
| `DB_HOST` / `DB_PORT` | `localhost:5433` — 5433 avoids clashing with a local Postgres install |
| `EMAIL_HOST` / `EMAIL_PORT` | Brevo SMTP. Port 587 with TLS |
| `EMAIL_HOST_USER` | Brevo SMTP login |
| `EMAIL_HOST_PASSWORD` | Brevo **SMTP key**, not your account password |
| `EMAIL_USE_TLS` | `True` for port 587. Use `EMAIL_USE_SSL` instead for 465, never both |
| `DEFAULT_FROM_EMAIL` | Must be a verified sender in Brevo |

Emails print to the console while `DEBUG=True` and go through SMTP when it's `False`.

Generate a secret key:

```bash
python -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(50)))"
```

Alphanumeric only — Docker Compose treats `$` in `.env` as a variable reference and silently blanks it.

```bash
git clone https://github.com/YuriiLev/DjangoGramm.git
cd DjangoGramm

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env           # then fill in the values

docker compose up -d           # starts PostgreSQL
python manage.py migrate
python manage.py runserver
```

Generate a secret key for `.env`:

```bash
python -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(50)))"
```

## Testing

```bash
pytest
```

## Development

```bash
ruff format .
ruff check . --fix
```