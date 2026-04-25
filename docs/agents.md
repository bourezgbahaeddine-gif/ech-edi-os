# Echorouk Editorial OS — Agent Documentation

Echorouk Editorial OS is an enterprise operating system for managing editorial content lifecycle from capture to manual-publish readiness, with strict governance and mandatory Human-in-the-Loop.


## Agent Overview

The Echorouk Editorial OS consists of specialized AI agents, each with a single responsibility.

---

## 🔍 Scout Agent (الوكيل الكشّاف)

**File:** `backend/app/agents/scout.py`
**Trigger:** Scheduled (every 30 minutes) or manual via API

### Responsibility

Fetch news from 300+ RSS sources, normalize data, and apply deduplication.

### Pipeline

1. Load enabled sources from DB (ordered by priority)
2. Fetch RSS feeds in batches of 10 (backpressure control)
3. For each entry:
   - Generate SHA1 hash from (source + url + normalized_title)
   - Check Redis cache (fast path)
   - Check PostgreSQL unique_hash index (slow path)
   - Fuzzy check against recent 200 titles via Levenshtein distance
   - If new: sanitize → store with status `NEW`

### Cost: $0 (pure Python)

---

## 🧭 Router Agent (الموجّه)

**File:** `backend/app/agents/router.py`
**Trigger:** After Scout run, or manual via API

### Responsibility

Classify articles by category and urgency, route to appropriate pipeline.

### Pipeline

1. Load articles with status `NEW`
2. Apply rule-based classification (keyword maps — FREE)
3. If uncertain (< 2 keyword matches) → call Gemini Flash
4. Detect breaking news → send immediate alerts
5. If importance >= 5 or breaking → set status `CANDIDATE`
6. Otherwise → set status `CLASSIFIED`

### Cost: ~$0.002 per article requiring AI (50-80% handled by rules for free)

---

## ✍️ Scribe Agent (الوكيل الكاتب)

**File:** `backend/app/agents/scribe.py`
**Trigger:** After editorial approval

### Responsibility

Transform raw content into a polished Echorouk-style article.

### Pipeline

1. Only processes articles with status `APPROVED` (cost optimization)
2. Call Gemini Flash for fast rewriting
4. Output: headline, body_html, seo_title, seo_description, tags

### Cost: ~$0.01 per article

---

## 📡 Trend Radar Agent (رادار التراند)

**File:** `backend/app/agents/trend_radar.py`
**Trigger:** Scheduled (every 15 minutes) or manual via API

### Responsibility

Detect verified trends using cross-platform validation.

### Algorithm: Semantic Intersection

1. **Source Scan:** Google Trends (DZ), Competitor RSS, RSS burst detection
2. **Cross-Validation:** A trend is "verified" only if it appears in 2+ independent sources
3. **AI Analysis:** Gemini Flash contextualizes the trend and suggests editorial angles
4. **Alert:** Send to editorial team via Telegram

### Cost: ~$0.005 per scan cycle

---

## 🎙️ Audio Agent (المذيع الآلي)

**File:** `backend/app/agents/audio_agent.py`
**Trigger:** Manual or scheduled (daily briefing)

### Responsibility

Generate audio news briefings using free TTS.

### Pipeline

1. Select top 5 articles of the day
2. AI generates radio script (Gemini Flash)
3. edge-tts converts script to speech (Microsoft TTS — $0)
4. FFmpeg mixes intro + news audio

### Cost: ~$0.001 per briefing (only the script generation)
