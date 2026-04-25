# Echorouk Editorial OS — Security Hardening Changelog
Date: 2026-04-23 | Branch: production-hardening

## Authentication & Authorization
- Secured 5 previously unauthenticated /news/* endpoints:
  GET /, /breaking/latest, /candidates/pending, /insights, /search/semantic
- Added Redis-based rate limiting on POST /auth/login
  (5 attempts / 5 minutes per username)
- Verified RBAC on sensitive routes touched during this hardening cycle

## State Machine Integrity
- Fixed direct article.status bypass in echorouk_archive_service.py
- Verified remaining production status transitions route through state_transition_service

## Infrastructure Security
- Redis: bound to 127.0.0.1 and now requires REDIS_PASSWORD
- Flower: removed weak default credentials
- FreshRSS/MariaDB: removed change_me_* defaults
- CORS: restricted methods and headers (removed wildcard *)
- Fixed FreshRSS and RSS-Bridge healthchecks using php-based internal probes

## Input Validation
- Added upload file extension whitelist to media_logger /run/upload endpoint

## Code Quality
- Removed Groq provider from executable code, UI, and operational docs
- Declared IVFFlat index in ArticleVector model to match the existing DB migration
- Added NEXT_PUBLIC_BREAKING_TTL_MINUTES as a configurable build arg

## Known Gaps (future work)
- HNSW migration recommended when article_vectors exceeds ~50K rows
- JWT token revocation mechanism not implemented (12h expiry only)
- /rss/sources still exposes the internal source list without auth (LOW)
