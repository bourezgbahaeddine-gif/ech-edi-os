# New Server Deploy Checklist

## Stack Summary

- `frontend`: Next.js 16 standalone container on port `3000`
- `backend`: FastAPI container on port `8000`
- `worker`: Celery worker for queues
- `flower`: Celery dashboard on port `5555` bound to localhost only
- `postgres`: PostgreSQL 16 with `pgvector`
- `redis`: Redis 7
- `minio`: S3-compatible object storage
- `freshrss-db`: MariaDB for FreshRSS
- `freshrss`: feed hub on port `8082`
- `rssbridge`: bridge on port `8083`

## Important Findings Before Migration

1. Production depends on `alembic upgrade head`.
   `backend/app/core/database.py` creates tables only in development.

2. `frontend/.env.production` currently points to the old domain.
   Rebuild the frontend after updating `NEXT_PUBLIC_API_URL`.

3. Default CORS values are local-only.
   Update `CORS_ORIGINS` for the new public domain.

4. `MINIO_ENDPOINT` must not stay `localhost:9000` inside Docker production.
   Use `minio:9000` when backend connects to the MinIO service over the compose network.

5. Several admin services are publicly exposed by default in `docker-compose.yml`.
   Review firewall or bind these ports to `127.0.0.1` if they should stay private:
   `3000`, `8000`, `6380`, `9000`, `9001`, `8082`, `8083`

6. The repo contains a seed users script with initial passwords in source control.
   Do not use those passwords as-is on the new production server.

7. There is no reverse proxy config in the repo.
   Nginx or Caddy on the server still needs to be prepared for domain routing and SSL.

## Files To Review Before First Deploy

- `.env`
- `.env.example`
- `frontend/.env.production`
- `docker-compose.yml`
- `scripts/deploy.sh`
- `backend/scripts/seed_users.py`

## Minimum Environment Values To Set

### Core

- `APP_ENV=production`
- `APP_DEBUG=false`
- `APP_SECRET_KEY=<strong-random-secret>`
- `APP_PORT=8000`

### Database

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

### Redis

- `REDIS_HOST=redis`
- `REDIS_PORT=6379`
- `REDIS_DB=0`
- `REDIS_QUEUE_DB=1`

### Storage

- `MINIO_ENDPOINT=minio:9000`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET`
- `MINIO_USE_SSL=false`

### AI / Integrations

- `GEMINI_API_KEY`
- `TELEGRAM_BOT_TOKEN` if alerts are required
- `SLACK_WEBHOOK_URL` if used

### FreshRSS / RSS-Bridge

- `SCOUT_USE_FRESHRSS`
- `FRESHRSS_FEED_URL`
- `RSSBRIDGE_ENABLED`
- `RSSBRIDGE_BASE_URL`
- `FRESHRSS_BASE_URL`
- `FRESHRSS_DB_NAME`
- `FRESHRSS_DB_USER`
- `FRESHRSS_DB_PASSWORD`
- `FRESHRSS_DB_ROOT_PASSWORD`
- `FRESHRSS_ADMIN_USER`
- `FRESHRSS_ADMIN_PASSWORD`
- `FRESHRSS_API_PASSWORD`
- `FRESHRSS_ADMIN_EMAIL`
- `TZ=Africa/Algiers`

### Frontend / Browser Access

- `NEXT_PUBLIC_API_URL=https://<new-domain>/api/v1`
- `NEXT_PUBLIC_FLOWER_URL=https://<new-domain>/flower` or a private URL if not public
- `CORS_ORIGINS=https://<new-domain>,https://www.<new-domain>`

## Recommended First-Time Deploy Order

1. Copy project to server.
2. Create `.env` from `.env.example` and replace all placeholder values.
3. Update `frontend/.env.production` for the new domain.
4. Review `docker-compose.yml` public ports and restrict admin ports if needed.
5. Start containers:
   `docker compose up -d --build`
6. Run migrations:
   `docker compose exec -T backend sh -lc "PYTHONPATH=/app alembic -c /app/alembic.ini upgrade head"`
7. Restart backend:
   `docker compose restart backend`
8. Seed users only if required, and rotate credentials immediately.
9. Verify:
   `curl http://127.0.0.1:8000/health`
   `curl http://127.0.0.1:3000`

## Reverse Proxy Notes

Recommended public routing:

- `/` -> frontend `127.0.0.1:3000`
- `/api/` -> backend `127.0.0.1:8000`
- `/flower/` -> flower `127.0.0.1:5555` if intentionally exposed
- `/freshrss/` -> FreshRSS `127.0.0.1:8082` if intentionally exposed
- `/rssbridge/` -> RSS-Bridge `127.0.0.1:8083` if intentionally exposed

## First Post-Deploy Checks

- Backend health returns `ok`
- Frontend loads without calling the old domain
- Login works with the intended production users
- `alembic_version` matches head
- Worker is consuming queues
- Redis and PostgreSQL are healthy
- FreshRSS is reachable if enabled
- MinIO uploads work if media/document features are enabled
