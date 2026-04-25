# OPERATIONS QUICK COMMANDS — أوامر التشغيل السريعة

Echorouk Editorial OS is a newsroom operating system that manages the editorial lifecycle from signal capture to Ready for Manual Publish, with strict governance and mandatory Human-in-the-Loop.

## 1) رفع تعديلات محددة من المحلي

```powershell
cd "D:\work\ech-edi-os"
git status --short
git add README.md AGENT_ONBOARDING.md docs/BRAND_GUIDE.md docs/architecture.md docs/PLATFORM_CONTENT_MAP.md docs/PROJECT_PROFILE_AR.md docs/NEW_SERVER_DEPLOY_CHECKLIST_2026-04-20.md scripts/check_brand_identity.sh
git commit -m "Harden brand identity across app docs and deploy naming"
git push origin main
```

## 2) تحديث السيرفر بالاسم القياسي الجديد

```bash
cd ~/ech-edi-os
git pull origin main
docker compose -p ech-edi-os up -d --build backend frontend
docker compose -p ech-edi-os run --rm backend alembic upgrade head
docker compose -p ech-edi-os restart backend
```

## 3) التحقق بعد النشر

```bash
curl -sS http://127.0.0.1:8000/health
docker compose -p ech-edi-os ps
docker compose -p ech-edi-os logs --tail=120 backend frontend
```

## 4) مراقبة اللوج

```bash
docker logs ech-edi-os-backend --since 15m | tail -n 200
docker logs ech-edi-os-backend --since 15m | egrep -i "error|traceback|invalid input value|undefinedtable|router_batch_complete"
```

## 5) فحص قاعدة البيانات

```bash
docker exec -i ech-edi-os-postgres psql -U echorouk_os -d echorouk_editorial_os -c "\dt article_quality_reports"
docker exec -i ech-edi-os-postgres psql -U echorouk_os -d echorouk_editorial_os -c "\dt user_activity_logs"
```

## 6) فحص هوية العلامة

```bash
bash scripts/check_brand_identity.sh
```

## 7) ملاحظة هجرة مهمة

- إذا كان السيرفر ما زال يعمل بحاويات أو volumes قديمة باسم `ech-swarm` فلا تنفذ إعادة التسمية مباشرة على بيانات الإنتاج.
- أنشئ backup أولًا، ثم نفذ خطة ترحيل يدوية للحاويات والـ volumes قبل اعتماد أسماء `ech-edi-os` بشكل كامل.
