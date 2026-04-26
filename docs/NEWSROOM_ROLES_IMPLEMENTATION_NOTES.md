# NEWSROOM_ROLES_IMPLEMENTATION_NOTES

## Phase 1 — Quick Wins Release v2.1

تم تنفيذ هذه المرحلة بشكل تدريجي وآمن داخل Echorouk Editorial OS مع الحفاظ على:
- Human-in-the-Loop
- عدم إضافة نشر نهائي تلقائي إلى CMS
- عدم تغيير السلوك التحريري الأساسي بدون تفعيل صريح
- إبقاء أي توسع تشغيلي خلف feature flags واضحة

## ما تم تنفيذه سابقًا

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

### 4. SocialPackageAgent Skeleton
- تمت إضافة:
  - `backend/app/agents/social_package_agent.py`
- تمت إضافة feature flag:
  - `ECHOROUK_OS_SOCIAL_PACKAGE_ENABLED=false`
- لم يكن هناك auto-trigger في هذه المرحلة الأولى.

## التحقق السابق بعد النشر

تم التحقق من النشر على السيرفر بتاريخ `2026-04-26` على الفرع:
- `production-hardening-fixes-3e6ea`

أهم النتائج المؤكدة:
- `backend` رجّع `health` بحالة `ok`
- `worker` صار `ready`
- `run_trends_scan` اشتغل بنجاح
- `run_published_monitor_scan` اشتغل بنجاح
- اختفى الخطأ القديم:
  - `AttributeError: 'Settings' object has no attribute 'published_monitor_max_concurrent_tasks'`

ملاحظة تشغيلية:
- ظهر `Soft time limit (120s)` داخل `published_monitor_scan`
- لكن المهمة أكملت بنجاح فعليًا:
  - `published_monitor_scan_complete`
  - `task_execution_completed`
  - `Task ... succeeded`

## R1 — Social Package Auto-Trigger Activation

تم تنفيذ R1 فقط داخل Tier 1، مع الإبقاء على Human-in-the-Loop وعدم إضافة أي نشر تلقائي إلى CMS أو منصات خارجية.

### ما تم تنفيذه
- إضافة `social_package_enabled: bool = False` داخل `backend/app/core/config.py`.
- تفعيل ربط `SocialPackageAgent` داخل workflow بعد الانتقال إلى `PUBLISHED` فقط.
- إضافة Celery task جديدة باسم:
  - `run_social_package_job`
- استخدام `SocialTask` و`SocialPost` الموجودتين أصلًا لتخزين الحزمة اجتماعيًا بدل اختراع schema جديدة.
- إضافة الحالة الجديدة:
  - `social_packaged`
  كحالة post-publish enhancement فقط.

### Feature Flag
- المتغير المعتمد:
  - `ECHOROUK_OS_SOCIAL_PACKAGE_ENABLED=false`
- القيمة الافتراضية تبقى `false`.
- إذا لم يتم تفعيل المتغير صراحة في production فلن يحدث أي auto-trigger.

### لماذا الافتراضي false
- لحماية الإنتاج ومنع أي سلوك جديد بعد النشر بدون تفعيل صريح.
- لتفادي توسيع أثر Quick Wins إلى أتمتة تشغيلية غير مقصودة.
- لإتاحة تفعيل R1 تدريجيًا بعد التأكد من queue واللوحات والفلترة.

### متى يتم enqueue
- بعد نجاح transition إلى `PUBLISHED` فقط.
- إذا كان `social_package_enabled == true`.
- وإذا كان:
  - `importance_score >= 6`
  - أو `is_breaking == true`
- مع حماية من التكرار عبر فحص jobs النشطة لنفس المقال.

### ماذا يحدث عند الفشل
- فشل enqueue أو فشل task لا يفشل transition إلى `PUBLISHED`.
- تبقى المقالة منشورة بشكل طبيعي.
- يتم تسجيل logs واضحة مثل:
  - `social_package_enqueue_requested`
  - `social_package_skipped_feature_disabled`
  - `social_package_skipped_low_importance`
  - `social_package_enqueue_failed`

### سلوك الحالة `social_packaged`
- لا تمنع الوصول إلى `published`.
- لا تدخل في chief pending queues.
- لا تعتبر مادة تحريرية عالقة.
- تُعامل كحالة post-publish ويمكن الرجوع منها إلى:
  - `published`
  - `archived`

### الملفات المعدلة في R1
- `backend/app/core/config.py`
- `backend/app/models/news.py`
- `backend/app/domain/news/state_machine.py`
- `backend/app/services/state_transition_service.py`
- `backend/app/services/job_queue_service.py`
- `backend/app/queue/celery_app.py`
- `backend/app/queue/tasks/pipeline_tasks.py`
- `backend/app/api/routes/editorial.py`
- `backend/app/api/routes/dashboard.py`
- `backend/app/api/routes/news.py`
- `frontend/src/lib/workflow-language.ts`
- `frontend/src/app/news/page.tsx`
- `backend/tests/test_state_machine.py`
- `backend/tests/test_state_transition_service.py`

### Migration المطلوبة
- `alembic/versions/20260426_add_social_packaged_status.py`

### أوامر النشر والتحقق
```bash
cd ~/ech-edi-os
git pull origin production-hardening-fixes-3e6ea
docker-compose up -d --build backend worker frontend
docker-compose exec backend alembic upgrade head
docker-compose restart backend worker
docker-compose ps
curl -sS http://127.0.0.1:8000/health
docker-compose logs --tail=120 worker
docker-compose logs --tail=120 backend
```

### ملاحظات تحقق بعد النشر
- يجب أن يظهر `run_social_package_job` ضمن مهام worker.
- يجب ألا يحدث أي auto-trigger إذا بقيت قيمة `ECHOROUK_OS_SOCIAL_PACKAGE_ENABLED=false`.
- عند التفعيل، يجب أن تبقى المقالة قابلة للنشر حتى لو فشل enqueue أو فشل تنفيذ social package generation.

## خطوات الاختبار المحلية

### Backend
```bash
python -m compileall backend/app backend/tests
python -m pytest backend/tests -q
```

### Frontend
```bash
npx tsc --noEmit
```

## R2 — Editorial Priority Queue

تم تنفيذ R2 فقط من Tier 1 لإضافة طابور أولويات تحريرية يجيب عن سؤال:
"ما الأخبار أو المواضيع التي تحتاج تغطية الآن؟"

### ما تم تنفيذه
- إضافة endpoint جديد:
  - `GET /api/v1/news/priority-queue`
- إضافة view جديد داخل صفحة `/news` باسم:
  - `الأولوية التحريرية`
- إضافة عميل API في الواجهة لجلب الطابور وعرضه بدون صفحة جديدة.

### منطق الـ scoring
يتم حساب `priority_score` تقريبياً من:
- `importance_score * 0.35`
- `breaking_bonus = 2` إذا كانت المادة عاجلة
- `freshness_score` أعلى كلما كانت المادة أحدث
- `urgency_bonus` بحسب `urgency`
- `competitor_pressure` إذا توفرت بيانات `competitor_xray_items`
- `cluster_velocity` إذا توفرت عضوية المادة في `story_clusters`

### حدود التنفيذ الحالية
- التنفيذ لا يستخدم AI.
- التنفيذ لا يستخدم Celery.
- التنفيذ لا يضيف migrations.
- إذا كانت جداول `competitor_xray_items` أو `story_cluster_members` غير متاحة أو كانت فارغة، يرجع endpoint نتائج بدون كسر ويضع هذه الإشارات بقيمة صفرية.
- الربط الحالي مع `competitor_xray_items` يعتمد على `matched_article_id` المتاح فعلياً.
- `cluster_velocity` يعتمد على حجم العنقود القصصي الحالي وليس على time-series منفصلة.

### التصفية الحالية
- الحالات الأساسية المشمولة:
  - `candidate`
  - `approved`
  - `approved_handoff`
  - `draft_generated`
  - `ready_for_chief_approval`
  - `ready_for_manual_publish`
- افتراضياً لا تظهر:
  - `published`
  - `social_packaged`
  - `archived`
- يمكن السماح بالحالات المنشورة فقط عند تمرير:
  - `include_published=true`

### أين يظهر في الواجهة
- داخل `/news`
- عبر tab جديد ضمن نفس الصفحة
- بدون تغيير navigation وبدون صفحة مستقلة

### طريقة الاختبار المحلية
```bash
python -m compileall backend/app backend/tests
python -m pytest backend/tests -q
npx tsc --noEmit
```

### أوامر تحقق السيرفر
```bash
cd ~/ech-edi-os
git pull origin production-hardening-fixes-3e6ea
docker-compose -f docker-compose.ssh.yml -p ech-swarm up -d --build backend frontend
docker-compose -f docker-compose.ssh.yml -p ech-swarm restart backend frontend
curl -sS http://127.0.0.1:8000/health
```

ثم بعد تسجيل الدخول:
```http
GET /api/v1/news/priority-queue?hours=24&limit=20
```
