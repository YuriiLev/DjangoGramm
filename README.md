# DjangoGramm

A social photo-sharing application built with Django. Users register by email, create one or more profiles, publish posts with multiple images and tags, follow other profiles, and read a personalised feed.

> 🚧 **In development.** Rebuilt from scratch — see [ROADMAP.md](ROADMAP.md) for progress.

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