# دليل ما بعد النشر والإنتاج

هذا الملف يوثّق إجراءات ما بعد النشر لخدمة `Echorouk Editorial OS` بعد نجاح التشغيل على:

- `https://echswarm.agentdz.com`
- `frontend` خلف `nginx`
- `backend` خلف `nginx`
- `SSL` مفعّل

تاريخ التثبيت المرجعي لهذا الدليل: `2026-04-22`

## 1) الحالة الحالية المؤكدة

- الدومين يعمل عبر `HTTPS`.
- `nginx` يمرر الطلبات إلى `frontend` و`backend` بنجاح.
- مشكلة `Mixed Content` انتهت بعد تنظيف:
  - `.env`
  - `frontend/.env.production`
- الواجهة لم تعد تحتوي على أي مرجع إلى:
  - `136.111.208.190`
  - `echswarm.agentdz.com:8000`
- تسجيل الدخول والتحميل الأساسي للوحة يعملان من الدومين نفسه.

## 2) القيم النهائية الموصى بها للواجهة

يجب أن تكون قيمة `NEXT_PUBLIC_API_URL` موحدة، بدون تكرار، في الملفات التالية:

- `.env`
- `frontend/.env.production`

القيمة المعتمدة:

```env
NEXT_PUBLIC_API_URL=/api/v1
```

ويفضّل أيضًا أن تبقى القيم التالية متناسقة مع الدومين:

```env
CORS_ORIGINS=https://echswarm.agentdz.com,http://echswarm.agentdz.com,http://localhost:3000,http://localhost:8000
FRESHRSS_BASE_URL=https://echswarm.agentdz.com/freshrss
ECHOROUK_OS_FRESHRSS_BASE_URL=https://echswarm.agentdz.com/freshrss
```

## 3) فحص سريع بعد كل نشر

نفّذ الأوامر التالية بعد أي تحديث:

```bash
cd ~/ech-edi-os

curl -sS https://echswarm.agentdz.com/health
curl -sS https://echswarm.agentdz.com/api/v1/news/ | head -c 300

docker-compose exec frontend sh -lc 'printenv | grep NEXT_PUBLIC_API_URL'
docker-compose exec frontend sh -lc 'grep -R "136.111.208.190\|echswarm.agentdz.com:8000" -n /app/.next 2>/dev/null || true'

docker-compose logs --tail=80 frontend backend worker
```

النتيجة المتوقعة:

- `/health` يرجع `status=ok`
- `printenv` يعرض `NEXT_PUBLIC_API_URL=/api/v1`
- `grep` داخل `.next` لا يعرض أي مرجع قديم
- لا توجد أخطاء `502` أو `Mixed Content`

## 4) تأمين المنافذ المكشوفة

بعد نجاح التشغيل، الأفضل عدم إبقاء الخدمات الداخلية مكشوفة على الإنترنت إلا إذا كانت مطلوبة علنًا.

المنافذ الحساسة التي يجب مراجعتها:

- `6380` Redis
- `8082` FreshRSS
- `8083` RSS-Bridge
- `9000` MinIO API
- `9001` MinIO Console

الخيار الأفضل:

- إما ربطها بـ `127.0.0.1` فقط داخل `docker-compose.yml`
- أو إلغاء `ports` والاعتماد على الشبكة الداخلية بين الحاويات
- أو وضعها خلف `nginx` فقط عند الحاجة

أمثلة أكثر أمانًا:

```yaml
ports:
  - "127.0.0.1:8082:80"
  - "127.0.0.1:8083:80"
  - "127.0.0.1:9000:9000"
  - "127.0.0.1:9001:9001"
  - "127.0.0.1:6380:6379"
```

بعد التعديل:

```bash
cd ~/ech-edi-os
docker-compose up -d --force-recreate redis minio freshrss rssbridge
```

## 5) النسخ الاحتياطي

يجب أخذ نسخ احتياطية من ثلاثة أشياء على الأقل:

- قاعدة البيانات
- ملفات الإعداد
- شهادة وتكوين `nginx`

### نسخة احتياطية لقاعدة البيانات

```bash
cd ~/ech-edi-os
mkdir -p backups
docker exec -t ech-postgres pg_dump -U echorouk -d echorouk_db | gzip > backups/postgres_$(date +%F_%H%M).sql.gz
```

### نسخة احتياطية لملفات الإعداد

```bash
cd ~/ech-edi-os
cp .env backups/.env.$(date +%F_%H%M).bak
cp frontend/.env.production backups/frontend.env.production.$(date +%F_%H%M).bak
cp docker-compose.yml backups/docker-compose.yml.$(date +%F_%H%M).bak
```

### نسخة احتياطية لتكوين `nginx`

```bash
sudo cp /etc/nginx/sites-available/echswarm.agentdz.com ~/ech-edi-os/backups/nginx.echswarm.agentdz.com.$(date +%F_%H%M).conf
```

## 6) مراقبة التشغيل

### سجلات سريعة

```bash
cd ~/ech-edi-os
docker-compose logs --tail=120 frontend backend worker
```

### متابعة مباشرة

```bash
cd ~/ech-edi-os
docker-compose logs -f --tail=100 backend
```

### فحص الحاويات

```bash
cd ~/ech-edi-os
docker-compose ps
docker stats --no-stream
```

### فحص الخدمة الخارجية

```bash
curl -I https://echswarm.agentdz.com
curl -I https://echswarm.agentdz.com/health
curl -I https://echswarm.agentdz.com/api/v1/news/
```

ملاحظة:

- `405 Method Not Allowed` مع `curl -I` لبعض المسارات قد يكون طبيعيًا إذا كان المسار يقبل `GET` فقط ولا يقبل `HEAD`.

## 7) SSL والشهادة

### عرض الشهادات

```bash
sudo certbot certificates
```

### اختبار التجديد

```bash
sudo certbot renew --dry-run
```

إذا فشل هذا الاختبار، يجب إصلاحه قبل أي انتهاء فعلي للشهادة.

## 8) تحديث آمن مستقبلي بدون كسر الخدمة

هذا هو المسار المقترح لأي تحديث كود:

```bash
cd ~/ech-edi-os
git pull origin main
docker-compose build frontend backend worker
docker-compose up -d --force-recreate frontend backend worker
docker-compose exec backend alembic upgrade head
docker-compose logs --tail=120 frontend backend worker
```

إذا كان التعديل في الواجهة فقط:

```bash
cd ~/ech-edi-os
docker-compose build frontend
docker-compose up -d --no-deps --force-recreate frontend
docker-compose logs --tail=80 frontend
```

إذا كان التعديل في `env` الخاص بالواجهة:

- تأكد من تعديل `.env`
- وتعديل `frontend/.env.production` عند الحاجة
- ثم أعد بناء `frontend`، لا يكفي `restart` فقط

## 9) أوامر إعادة تشغيل سريعة

```bash
cd ~/ech-edi-os
docker-compose restart frontend backend worker
```

ولإعادة نشر كاملة:

```bash
cd ~/ech-edi-os
docker-compose build frontend backend worker
docker-compose up -d --force-recreate frontend backend worker
docker-compose exec backend alembic upgrade head
```

## 10) علامات إنذار تستحق التدخل

راقب هذه الحالات بسرعة:

- ظهور `Mixed Content` في المتصفح
- ظهور `502 Bad Gateway` من `nginx`
- عودة مرجع قديم إلى IP أو `:8000` داخل `.next`
- ارتفاع مستمر في `403 Not authenticated` بعد تسجيل الدخول الفعلي
- فشل `alembic upgrade head`
- توقف `worker`
- فشل `certbot renew --dry-run`

## 11) ملاحظات تشغيلية مهمة

- في هذه البيئة استخدم `docker-compose` وليس `docker compose`.
- لا تترك `NEXT_PUBLIC_API_URL` مكررًا في أكثر من سطر داخل الملف نفسه.
- `frontend/.env.production` قد يطغى على `.env` وقت بناء `Next.js`.
- إذا تغيّرت إعدادات الواجهة، فلابد من `build` جديد، وليس فقط `restart`.
- مسارات `frontend` و`backend` الأفضل أن تبقى داخلية وتُعرض فقط عبر `nginx`.

## 12) الخلاصة التشغيلية

النظام الآن في وضع إنتاج صالح للعمل، والمخاطر المتبقية لم تعد في الربط أو `SSL` أو الـ API، بل في الانضباط التشغيلي:

- توحيد الإعدادات
- تقليل السطح المكشوف خارجيًا
- أخذ نسخ احتياطية دورية
- مراقبة السجلات بعد كل تحديث
- اختبار التجديد الدوري للشهادة

إذا تم الالتزام بهذه الخطوات، ستكون التحديثات اللاحقة أكثر أمانًا وأقل عرضة لكسر الخدمة.
