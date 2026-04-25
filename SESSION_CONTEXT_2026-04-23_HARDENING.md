# Session Context — 2026-04-23 Hardening

هذا الملف هو ملخص سياق الجلسة الحالية حتى يمكن استئناف العمل بسرعة في نافذة جديدة بدون إعادة تتبع كل الخطوات السابقة.

## الهدف العام

تم تنفيذ جولة hardening على مشروع **Echorouk Editorial OS** مع التركيز على:

- إغلاق endpoints حساسة كانت مكشوفة بدون auth
- إزالة bypass في state machine الخاصة بحالة المقال
- تشديد إعدادات Docker والأسرار
- إزالة بقايا Groq من الكود التنفيذي والواجهة والوثائق التشغيلية
- إصلاح healthchecks لخدمتي FreshRSS و RSS-Bridge
- إضافة rate limiting على `/auth/login`
- إضافة تحقق من امتداد الملفات في media upload
- تشديد إعدادات CORS
- مزامنة نموذج `ArticleVector` مع فهرس `IVFFlat` الموجود في migration

## الحالة الحالية المؤكدة

آخر حالة مؤكدة على السيرفر كانت سليمة بالكامل:

- `ech-backend`: `Up`
- `ech-worker`: `Up`
- `ech-frontend`: `Up`
- `ech-postgres`: `Up (healthy)`
- `ech-redis`: `Up (healthy)`
- `ech-freshrss`: `Up (healthy)`
- `ech-rssbridge`: `Up (healthy)`
- `/health` يرجع:
  - `status: ok`
  - `database: connected`
  - `redis: connected`

كما تم التحقق أن:

- `GET /api/v1/news/insights` بدون auth يرجع `403`
- `GET /api/v1/news/` بدون auth يرجع `403`
- كود rate limit موجود داخل `backend/app/api/routes/auth.py`
- فحص امتدادات الرفع موجود داخل `backend/app/api/routes/media_logger.py`
- CORS tightened موجود داخل `backend/app/main.py`
- فهرس `IVFFlat` معلن داخل `backend/app/models/knowledge.py`

## أهم الملفات التي عُدلت في هذه الجولة

- `backend/app/api/routes/news.py`
- `backend/app/services/echorouk_archive_service.py`
- `frontend/src/app/settings/page.tsx`
- `docker-compose.yml`
- `.env.example`
- `frontend/Dockerfile`
- `backend/app/api/routes/auth.py`
- `backend/app/api/routes/media_logger.py`
- `backend/app/main.py`
- `backend/app/models/knowledge.py`
- `backend/app/schemas/__init__.py`
- `README.md`
- `docs/agents.md`
- `docs/PROVIDER_ROUTING_COST.md`
- `docs/M10_ASYNC_ARCHITECTURE.md`
- `docs/TROUBLESHOOTING_PLAYBOOK.md`
- `docs/NEW_SERVER_DEPLOY_CHECKLIST_2026-04-20.md`
- `CLAUDE.md`

## ما الذي تم إصلاحه فعليًا

### 1. Authentication / RBAC

- تأمين 5 endpoints في `/news`:
  - `GET /api/v1/news/`
  - `GET /api/v1/news/breaking/latest`
  - `GET /api/v1/news/candidates/pending`
  - `GET /api/v1/news/insights`
  - `GET /api/v1/news/search/semantic`
- إضافة rate limiting على `POST /auth/login`
  - 5 محاولات خلال 5 دقائق لكل username

### 2. State Machine

- إزالة bypass مباشر كان يكتب `article.status = NewsStatus.ARCHIVED`
- الحالة الحالية:
  - كل transitions الإنتاجية تمر عبر `state_transition_service`
  - الضربات المتبقية على `article.status` هي:
    - اختبارات
    - مقارنات
    - نسخ من `locked_article.status` بعد transition صحيح

### 3. Docker / Infra Security

- Redis أصبح:
  - مربوطًا على `127.0.0.1:6380`
  - يتطلب `REDIS_PASSWORD`
- Flower لم يعد يستخدم fallback credentials ضعيفة
- FreshRSS / MariaDB لم تعد تستخدم `change_me_*` defaults
- FreshRSS و RSS-Bridge يستخدمان healthchecks مبنية على `php`

### 4. Input Validation

- `media_logger /run/upload` صار يرفض الامتدادات غير المسموحة
- الامتدادات الحالية:
  - `.mp3`, `.wav`, `.ogg`, `.mp4`, `.webm`, `.m4a`, `.flac`

### 5. Frontend / Config

- إزالة `GROQ_API_KEY` من الإعدادات
- إضافة `NEXT_PUBLIC_BREAKING_TTL_MINUTES` إلى:
  - `frontend/Dockerfile`
  - `docker-compose.yml`

### 6. Docs / Audit Context

- تحديث `CLAUDE.md` ليعكس الحالة hardened الحالية
- إنشاء changelog مستقل:
  - `SECURITY_HARDENING_CHANGELOG_2026-04-23.md`

## ملاحظات تشغيلية مهمة جدًا

### docker-compose على السيرفر قديم

السيرفر كان يستخدم `docker-compose` قديم لا يفهم السطر الأعلى `name:` في `docker-compose.yml`.

الحل الذي نجح:

```bash
awk 'NR==1 && $1=="name:" {next} {print}' docker-compose.yml > docker-compose.ssh.yml
```

ثم استعمال `docker-compose.ssh.yml` بدل الملف الأصلي أثناء النشر على السيرفر.

### لا تعتمد على restart فقط بعد تعديل .env

إذا تغيّرت متغيرات البيئة:

- لا تستخدم `docker-compose restart` وحده
- استخدم:

```bash
docker-compose ... up -d --force-recreate
```

### healthchecks السابقة فشلت بسبب أدوات غير موجودة

جرّبنا سابقًا:

- `curl` داخل healthcheck
- ثم `wget`

وكلاهما فشل لأن الصور upstream لا تحتوي هذه الأدوات.

الحل النهائي الذي نجح:

- استخدام `php -r "file_get_contents(...)"` داخل healthcheck

## أوامر النشر التي نجحت آخر مرة

```bash
cd ~/ech-edi-os || exit 1
export COMPOSE_PROJECT_NAME=ech-swarm

awk 'NR==1 && $1=="name:" {next} {print}' docker-compose.yml > docker-compose.ssh.yml

docker-compose -f docker-compose.ssh.yml -p ech-swarm build backend worker flower frontend
docker-compose -f docker-compose.ssh.yml -p ech-swarm up -d --no-deps --force-recreate backend worker flower frontend

sleep 8

docker-compose -f docker-compose.ssh.yml -p ech-swarm exec -T backend sh -lc "PYTHONPATH=/app alembic -c /app/alembic.ini upgrade head"
```

## أوامر التحقق التي نجحت

```bash
curl -sS http://127.0.0.1:8000/health

curl -i "http://127.0.0.1:8000/api/v1/news/insights?article_ids=1"
curl -i "http://127.0.0.1:8000/api/v1/news/?page=1&per_page=1"

docker-compose -f docker-compose.ssh.yml -p ech-swarm ps
docker logs --since 2m ech-backend
docker logs --since 2m ech-worker
```

النتيجة المطلوبة:

- `/health` = `ok`
- `/api/v1/news/insights` = `401` أو `403`
- `/api/v1/news/` = `401` أو `403`

## ملفات مرجعية أنشئت أو حُدثت في هذه الجلسة

- `CLAUDE.md`
- `SECURITY_HARDENING_CHANGELOG_2026-04-23.md`
- `SESSION_CONTEXT_2026-04-23_HARDENING.md`

## Known Gaps / الخطوات المقبلة

- يوصى لاحقًا بالانتقال إلى `HNSW` إذا تجاوز جدول `article_vectors` حدودًا كبيرة
- لا يوجد حاليًا token revocation mechanism للـ JWT، فقط expiry
- endpoint `/rss/sources` ما زال low-risk public exposure ويحتاج قرارًا واضحًا إن أردنا إغلاقه
- إذا كانت هناك جولة تدقيق جديدة، ابدأ من:
  - `CLAUDE.md`
  - `SECURITY_HARDENING_CHANGELOG_2026-04-23.md`
  - هذا الملف

## Resume Prompt سريع لنافذة جديدة

يمكن بدء نافذة جديدة بهذه الجملة:

> Read `SESSION_CONTEXT_2026-04-23_HARDENING.md`, `SECURITY_HARDENING_CHANGELOG_2026-04-23.md`, and `CLAUDE.md`, then continue from the current hardened production state without redoing already-verified fixes.
