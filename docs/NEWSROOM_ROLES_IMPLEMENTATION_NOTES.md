# NEWSROOM_ROLES_IMPLEMENTATION_NOTES

## Phase 1 — Quick Wins Release v2.1

تم تنفيذ هذه المرحلة بشكل تدريجي وآمن داخل Echorouk Editorial OS مع الحفاظ على:
- Human-in-the-Loop
- عدم إضافة نشر نهائي تلقائي إلى CMS
- عدم تغيير السلوك التحريري الأساسي
- عدم تفعيل أي auto-trigger واسع للأتمتة الاجتماعية

## ما تم تنفيذه

### 1. الأدوار الجديدة
- تمت إضافة:
  - `presenter`
  - `show_host`
- تم ربطهما مؤقتًا بصلاحيات `journalist` الأساسية عبر طبقة RBAC.
- تم تحديث الواجهة حتى لا يظهر sidebar فارغ لهذين الدورين.

### 2. Social Variants
- تم توسيع `smart_editor_service.social_variants()` ليضيف:
  - `instagram`
  - `tiktok`
  - `tiktok_hook_3s`
  - `tiktok_main_point_10s`
  - `tiktok_cta_3s`
  - `tiktok_hashtags`
  - `tiktok_visual_direction`
  - `tiktok_sound_or_trend_suggestion`
- المخرجات القديمة بقيت كما هي:
  - `facebook`
  - `x`
  - `push`
  - `summary_120`
  - `breaking_alert`

### 3. Broadcast Rewrite Mode
- تمت إضافة endpoint جديد:
  - `POST /api/v1/services/editor/broadcast-rewrite`
- المدخلات:
  - `text`
  - `duration_target_seconds` اختياري
- المخرجات:
  - `broadcast_text`
  - `word_count`
  - `estimated_read_seconds`
  - `changes_summary`
- تم ربطه مبدئيًا بواجهة `scripts/[scriptId]` داخل تبويب النص الصوتي.

### 4. SocialPackageAgent skeleton
- تمت إضافة:
  - `backend/app/agents/social_package_agent.py`
- تمت إضافة feature flag:
  - `ECHOROUK_OS_SOCIAL_PACKAGE_ENABLED=false`
- لا يوجد auto-trigger في هذه المرحلة.

## ما تم تأجيله

### `social_packaged`
تم تأجيل إضافة `social_packaged` إلى `NewsStatus` في هذه المرحلة.

السبب:
- الأثر أوسع من Quick Wins.
- يحتاج مراجعة إضافية لكل:
  - dashboard stats
  - news filters
  - editorial queues
  - status labels
  - post-publish grouping
- الإضافة الآن بدون تدقيق أوسع قد تُدخل مادة منشورة ضمن قوائم تحريرية أو إحصاءات غير مقصودة.

## الملفات المعدلة

- `backend/app/models/user.py`
- `backend/app/api/deps/rbac.py`
- `backend/app/api/routes/editorial.py`
- `backend/app/api/routes/scripts.py`
- `backend/app/api/routes/journalist_services.py`
- `backend/app/api/routes/dashboard.py`
- `backend/app/services/smart_editor_service.py`
- `backend/app/core/config.py`
- `backend/app/agents/social_package_agent.py`
- `frontend/src/components/layout/navigation.tsx`
- `frontend/src/app/today/page.tsx`
- `frontend/src/lib/notification-policy.ts`
- `frontend/src/lib/journalist-services-api.ts`
- `frontend/src/lib/api.ts`
- `frontend/src/app/workspace-drafts/page.tsx`
- `frontend/src/app/scripts/[scriptId]/page.tsx`
- `frontend/src/app/team/page.tsx`
- `.env.example`
- `alembic/versions/20260426_add_newsroom_roles.py`
- `backend/tests/test_smart_editor_service.py`
- `backend/tests/test_newsroom_roles_phase1.py`

## خطوات الاختبار

### Backend
```bash
python -m compileall backend/app
python -m pytest backend/tests -q
```

### Frontend
```bash
cd frontend
npm run lint
npx tsc --noEmit
npm run build
```

## ملاحظات تشغيل

- migration الجديدة مطلوبة لإضافة:
  - `presenter`
  - `show_host`
  إلى enum قاعدة البيانات `user_role`.
- لم تتم إضافة migration لـ `social_packaged` عمدًا في هذه المرحلة.
