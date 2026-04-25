# دليل التشغيل الكامل: المحلي + السيرفر + التثبيت من الصفر

تاريخ التحديث المرجعي: `2026-04-25`

هذا الملف هو المرجع العملي السريع عندما نريد:

- العمل محليًا على الكود
- رفع التعديلات إلى GitHub
- التحديث على السيرفر
- التثبيت من الصفر على سيرفر جديد
- التحقق بعد النشر
- الرجوع السريع لأوامر التشغيل بدون تخمين

يعتمد هذا الدليل على ما هو موجود فعليًا داخل المشروع وعلى البيئة التي تم التحقق منها عمليًا.

## 1. الحالة المرجعية المؤكدة

تم التحقق عمليًا من البيئة التالية:

- المستودع على السيرفر موجود في:
  - `~/ech-edi-os`
- الفرع الحالي الذي تم التحقق عليه:
  - `production-hardening-fixes-3e6ea`
- محرك Docker على السيرفر:
  - `Docker version 20.10.24+dfsg1`
- أداة Compose المتوفرة على السيرفر:
  - `docker-compose version 1.29.2`
- الأمر `docker compose` غير متاح على هذا السيرفر

## 2. القاعدة الذهبية على هذا السيرفر

على هذا السيرفر بالتحديد:

- استخدم `docker-compose`
- لا تستخدم `docker compose`
- استخدم الملف:
  - `docker-compose.ssh.yml`
- ثبّت اسم المشروع دائمًا على:
  - `ech-swarm`

السبب:

- `docker-compose.yml` يحتوي على السطر:
  - `name: echorouk_editorial_os`
- هذا السطر يعمل مع Compose V2، لكنه غير متوافق مع `docker-compose` V1
- الملف `docker-compose.ssh.yml` متوافق مع بيئة السيرفر الحالية وتم التحقق منه عمليًا
- الحاويات الحالية على السيرفر تعمل تحت project name:
  - `ech-swarm`

## 3. الأوامر القياسية الآمنة على السيرفر

لتفادي النسيان أو الاعتماد على متغيرات session، استخدم دائمًا الصيغة الصريحة:

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm ...
```

هذه الصيغة أفضل من:

```bash
export COMPOSE_FILE=docker-compose.ssh.yml
export COMPOSE_PROJECT_NAME=ech-swarm
```

لأنها لا تعتمد على session state، وتقلل احتمال الخطأ عند فتح terminal جديد.

## 4. ملاحظات مهمة جدًا قبل أي تشغيل

- نفّذ الأوامر سطرًا سطرًا
- لا تلصق عدة أوامر متداخلة في سطر واحد
- بعد `restart` أو `up -d` قد يفشل `curl` مباشرة لأن الخدمة لم تكتمل بعد
- إذا ظهر:
  - `curl: (56) Recv failure: Connection reset by peer`
  فهذا غالبًا يعني أن `backend` ما زال يعيد الإقلاع، أعد المحاولة بعد 5 إلى 10 ثوانٍ
- لا تستخدم `docker compose`
- لا تستخدم `docker-compose.yml` على هذا السيرفر مع النسخة الحالية من Compose
- لا تستخدم `scripts/deploy.sh` كما هو على هذا السيرفر لأنه مبني على:
  - `docker compose`
  - ومسار افتراضي مختلف: `$HOME/ech-swarm`

## 5. أوامر العمل محليًا

### 5.1 فحص الحالة محليًا

```powershell
git status --short
git branch --show-current
git log --oneline -n 8
```

### 5.2 سحب آخر التحديثات محليًا

```powershell
git pull origin production-hardening-fixes-3e6ea
```

إذا كنت تعمل على `main`:

```powershell
git pull origin main
```

### 5.3 رفع تعديلاتك من المحلي إلى GitHub

مثال على الفرع الحالي:

```powershell
git status --short
git add backend frontend alembic docs docker-compose.yml .dockerignore
git commit -m "Describe your change"
git push -u origin production-hardening-fixes-3e6ea
```

إذا كان الفرع مرفوعًا مسبقًا:

```powershell
git push origin production-hardening-fixes-3e6ea
```

### 5.4 دمج الفرع في `main` محليًا

```powershell
git checkout main
git pull origin main
git merge production-hardening-fixes-3e6ea
git push origin main
```

إذا فتح `vim` أثناء `merge commit`:

1. اضغط `Esc`
2. اكتب:

```vim
:wq
```

3. اضغط `Enter`

## 6. تشغيل محلي باستخدام Docker

هذا القسم مفيد عندما تريد تشغيل النظام محليًا على جهاز التطوير.

### 6.1 إعداد الملف البيئي

```powershell
Copy-Item .env.example .env
```

ثم عدّل `.env` بالقيم المناسبة.

### 6.2 التشغيل

إذا كانت بيئتك تدعم Compose V2:

```powershell
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

إذا كانت بيئتك تستخدم `docker-compose` القديم:

```powershell
docker-compose -f docker-compose.ssh.yml -p ech-swarm up -d --build
docker-compose -f docker-compose.ssh.yml -p ech-swarm exec -T backend sh -lc "PYTHONPATH=/app alembic -c /app/alembic.ini upgrade head"
```

### 6.3 التحقق

```powershell
curl http://127.0.0.1:8000/health
```

## 7. التثبيت من الصفر على سيرفر جديد

هذا هو المسار الكامل عندما نبدأ من جديد.

### 7.1 تثبيت المتطلبات الأساسية على Ubuntu

```bash
sudo apt update
sudo apt install -y git curl ca-certificates gnupg lsb-release
```

### 7.2 تثبيت Docker و docker-compose

إذا لم تكن مثبتة مسبقًا:

```bash
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

بعد إضافة المستخدم إلى مجموعة docker، اخرج من الجلسة وادخل من جديد.

### 7.3 جلب المشروع

```bash
cd ~
git clone https://github.com/bourezgbahaeddine-gif/ech-edi-os.git
cd ~/ech-edi-os
git checkout production-hardening-fixes-3e6ea
```

أو إذا أردت `main`:

```bash
git checkout main
```

### 7.4 إعداد البيئة

```bash
cp .env.example .env
nano .env
```

القيم الحساسة التي يجب مراجعتها على الأقل:

- `APP_ENV=production`
- `APP_DEBUG=false`
- `APP_SECRET_KEY`
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `MINIO_ENDPOINT=minio:9000`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `NEXT_PUBLIC_API_URL`
- `CORS_ORIGINS`
- `FRESHRSS_*`
- `FLOWER_BASIC_AUTH_USER`
- `FLOWER_BASIC_AUTH_PASSWORD`

### 7.5 التشغيل الأول

استخدم الملف المتوافق مع هذا السيرفر:

```bash
cd ~/ech-edi-os
docker-compose -f docker-compose.ssh.yml -p ech-swarm up -d --build
docker-compose -f docker-compose.ssh.yml -p ech-swarm exec -T backend sh -lc "PYTHONPATH=/app alembic -c /app/alembic.ini upgrade head"
docker-compose -f docker-compose.ssh.yml -p ech-swarm restart backend
```

### 7.6 التحقق بعد التثبيت

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm ps
curl -sS http://127.0.0.1:8000/health
```

## 8. أوامر التحديث المعتادة على السيرفر

هذا هو المسار الذي نستخدمه عادة بعد `git push`.

### 8.1 تحديث كود الفرع الحالي

```bash
cd ~/ech-edi-os
git pull origin production-hardening-fixes-3e6ea
docker-compose -f docker-compose.ssh.yml -p ech-swarm build backend worker frontend
docker-compose -f docker-compose.ssh.yml -p ech-swarm up -d --force-recreate backend worker frontend
docker-compose -f docker-compose.ssh.yml -p ech-swarm exec -T backend sh -lc "PYTHONPATH=/app alembic -c /app/alembic.ini upgrade head"
docker-compose -f docker-compose.ssh.yml -p ech-swarm restart backend
docker-compose -f docker-compose.ssh.yml -p ech-swarm logs --tail=120 frontend backend worker
curl -sS http://127.0.0.1:8000/health
```

### 8.2 إذا كان النشر من `main`

```bash
cd ~/ech-edi-os
git checkout main
git pull origin main
docker-compose -f docker-compose.ssh.yml -p ech-swarm build backend worker frontend
docker-compose -f docker-compose.ssh.yml -p ech-swarm up -d --force-recreate backend worker frontend
docker-compose -f docker-compose.ssh.yml -p ech-swarm exec -T backend sh -lc "PYTHONPATH=/app alembic -c /app/alembic.ini upgrade head"
docker-compose -f docker-compose.ssh.yml -p ech-swarm restart backend
curl -sS http://127.0.0.1:8000/health
```

## 9. إعادة تشغيل كاملة للستاك

استخدمها عند الحاجة فقط:

```bash
cd ~/ech-edi-os
docker-compose -f docker-compose.ssh.yml -p ech-swarm up -d --build
docker-compose -f docker-compose.ssh.yml -p ech-swarm exec -T backend sh -lc "PYTHONPATH=/app alembic -c /app/alembic.ini upgrade head"
docker-compose -f docker-compose.ssh.yml -p ech-swarm restart backend
docker-compose -f docker-compose.ssh.yml -p ech-swarm ps
curl -sS http://127.0.0.1:8000/health
```

## 10. مراقبة الحاويات واللوجات

### 10.1 فحص الحالة

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm ps
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
```

### 10.2 لوجات `backend`

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm logs -f backend
```

### 10.3 لوجات `worker`

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm logs -f worker
```

### 10.4 لوجات `frontend`

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm logs -f frontend
```

### 10.5 لوجات مختصرة لكل الخدمات المهمة

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm logs --tail=120 frontend backend worker
```

## 11. أوامر Alembic وقاعدة البيانات

### 11.1 معرفة revision الحالي

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm exec -T backend sh -lc "PYTHONPATH=/app alembic -c /app/alembic.ini current"
```

### 11.2 تشغيل migrations

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm exec -T backend sh -lc "PYTHONPATH=/app alembic -c /app/alembic.ini upgrade head"
```

### 11.3 فحص الجداول داخل Postgres

```bash
docker exec -i ech-postgres psql -U echorouk -d echorouk_db -c "\dt"
```

## 12. فحوص الصحة السريعة

### 12.1 فحص backend محليًا على السيرفر

```bash
curl -sS http://127.0.0.1:8000/health
```

### 12.2 فحص الواجهة

```bash
curl -I http://127.0.0.1:3000
```

### 12.3 فحص المتغيرات داخل frontend container

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm exec frontend sh -lc 'printenv | grep NEXT_PUBLIC_API_URL'
```

### 12.4 فحص عدم بقاء دومين/عنوان قديم داخل build الواجهة

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm exec frontend sh -lc 'grep -R "136.111.208.190\|echswarm.agentdz.com:8000" -n /app/.next 2>/dev/null || true'
```

## 13. نسخ احتياطية قبل أي تعديل كبير

### 13.1 نسخة من قاعدة البيانات

```bash
cd ~/ech-edi-os
mkdir -p backups
docker exec -t ech-postgres pg_dump -U echorouk -d echorouk_db | gzip > backups/postgres_$(date +%F_%H%M).sql.gz
```

### 13.2 نسخة من الإعدادات

```bash
cd ~/ech-edi-os
cp .env backups/.env.$(date +%F_%H%M).bak
cp docker-compose.ssh.yml backups/docker-compose.ssh.yml.$(date +%F_%H%M).bak
```

## 14. أوامر مفيدة للتحقق من البيئة إذا نسينا الوضع

```bash
cd ~/ech-edi-os
git branch --show-current
git log --oneline -n 6
docker --version
docker-compose --version
docker inspect ech-backend --format 'project={{index .Config.Labels "com.docker.compose.project"}} service={{index .Config.Labels "com.docker.compose.service"}}'
```

النتيجة المرجعية المتوقعة تقريبًا:

- project=`ech-swarm`
- service=`backend`

## 15. المشاكل الشائعة وحلها

### 15.1 الخطأ

```text
docker: 'compose' is not a docker command.
```

الحل:

- استخدم `docker-compose`
- لا تستخدم `docker compose`

### 15.2 الخطأ

```text
The Compose file './docker-compose.yml' is invalid because:
'name' does not match any of the regexes: '^x-'
```

الحل:

- لا تستخدم `docker-compose.yml` على هذا السيرفر
- استخدم:

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm ...
```

### 15.3 الخطأ

```text
curl: (56) Recv failure: Connection reset by peer
```

الحل:

- غالبًا `backend` كان يعيد الإقلاع
- انتظر 5 إلى 10 ثوانٍ
- أعد الفحص:

```bash
curl -sS http://127.0.0.1:8000/health
```

### 15.4 إذا أردت متابعة ما يحدث عند الإقلاع

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm logs -f backend
```

## 16. لا تستخدم هذه الأوامر إلا إذا كنت تعرف أثرها

تجنب افتراضيًا:

- `docker-compose down -v`
- `git reset --hard`
- `git checkout -- .`
- أي حذف يدوي للـ volumes

لأن هذه الأوامر قد تؤدي إلى فقدان بيانات أو فقدان حالة تشغيل مهمة.

## 17. الأوامر المختصرة النهائية الجاهزة

### 17.1 تحديث عادي للفرع الحالي على السيرفر

```bash
cd ~/ech-edi-os
git pull origin production-hardening-fixes-3e6ea
docker-compose -f docker-compose.ssh.yml -p ech-swarm build backend worker frontend
docker-compose -f docker-compose.ssh.yml -p ech-swarm up -d --force-recreate backend worker frontend
docker-compose -f docker-compose.ssh.yml -p ech-swarm exec -T backend sh -lc "PYTHONPATH=/app alembic -c /app/alembic.ini upgrade head"
docker-compose -f docker-compose.ssh.yml -p ech-swarm restart backend
curl -sS http://127.0.0.1:8000/health
```

### 17.2 فحص سريع بعد النشر

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm ps
docker-compose -f docker-compose.ssh.yml -p ech-swarm logs --tail=120 frontend backend worker
curl -sS http://127.0.0.1:8000/health
```

### 17.3 تشغيل من الصفر على سيرفر جديد

```bash
cd ~
git clone https://github.com/bourezgbahaeddine-gif/ech-edi-os.git
cd ~/ech-edi-os
git checkout production-hardening-fixes-3e6ea
cp .env.example .env
nano .env
docker-compose -f docker-compose.ssh.yml -p ech-swarm up -d --build
docker-compose -f docker-compose.ssh.yml -p ech-swarm exec -T backend sh -lc "PYTHONPATH=/app alembic -c /app/alembic.ini upgrade head"
docker-compose -f docker-compose.ssh.yml -p ech-swarm restart backend
curl -sS http://127.0.0.1:8000/health
```

## 18. الخلاصة العملية

إذا نسيت كل شيء، تذكر فقط:

1. على هذا السيرفر استخدم `docker-compose`
2. استخدم `docker-compose.ssh.yml`
3. استخدم project name = `ech-swarm`
4. شغّل migration بعد أي تحديث backend
5. اختبر `/health` بعد كل نشر

الصيغة القياسية النهائية:

```bash
docker-compose -f docker-compose.ssh.yml -p ech-swarm ...
```
