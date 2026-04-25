# CLAUDE.md

Generated audit map for Claude Code. This file omits actual secret values and focuses on structure, interfaces, stateful surfaces, and likely audit hot spots.

## 1. Full Folder Structure

Directory list excluding `node_modules`, `__pycache__`, `.git`, and `postgres_data`. Generated assets like `frontend/.next` are included because they were not excluded in the request.

```text
.claude
alembic
alembic/versions
backend
backend/alembic
backend/app
backend/app/agents
backend/app/api
backend/app/api/deps
backend/app/api/routes
backend/app/core
backend/app/data
backend/app/data/events
backend/app/data/programs
backend/app/domain
backend/app/domain/mil
backend/app/domain/news
backend/app/domain/quality
backend/app/models
backend/app/msi
backend/app/msi/profiles
backend/app/ops
backend/app/queue
backend/app/queue/tasks
backend/app/repositories
backend/app/schemas
backend/app/services
backend/app/simulator
backend/app/simulator/profiles
backend/app/simulator/prompts
backend/app/utils
backend/scripts
backend/tests
backups
backups/pre_update_2026-04-14_1025
docs
docs/rssbridge
frontend
frontend/.next
frontend/.next/build
frontend/.next/build/chunks
frontend/.next/cache
frontend/.next/diagnostics
frontend/.next/server
frontend/.next/server/app
frontend/.next/server/app/_global-error
frontend/.next/server/app/_global-error.segments
frontend/.next/server/app/_global-error/page
frontend/.next/server/app/_not-found
frontend/.next/server/app/_not-found.segments
frontend/.next/server/app/_not-found.segments/_not-found
frontend/.next/server/app/_not-found/page
frontend/.next/server/app/agents
frontend/.next/server/app/agents.segments
frontend/.next/server/app/agents.segments/agents
frontend/.next/server/app/agents/page
frontend/.next/server/app/archive
frontend/.next/server/app/archive.segments
frontend/.next/server/app/archive.segments/archive
frontend/.next/server/app/archive/page
frontend/.next/server/app/competitor-xray
frontend/.next/server/app/competitor-xray.segments
frontend/.next/server/app/competitor-xray.segments/competitor-xray
frontend/.next/server/app/competitor-xray/page
frontend/.next/server/app/constitution
frontend/.next/server/app/constitution.segments
frontend/.next/server/app/constitution.segments/constitution
frontend/.next/server/app/constitution/page
frontend/.next/server/app/dashboard
frontend/.next/server/app/dashboard.segments
frontend/.next/server/app/dashboard.segments/dashboard
frontend/.next/server/app/dashboard/metric
frontend/.next/server/app/dashboard/metric/[metric]
frontend/.next/server/app/dashboard/metric/[metric]/page
frontend/.next/server/app/dashboard/page
frontend/.next/server/app/digital
frontend/.next/server/app/digital.segments
frontend/.next/server/app/digital.segments/digital
frontend/.next/server/app/digital/page
frontend/.next/server/app/editorial
frontend/.next/server/app/editorial.segments
frontend/.next/server/app/editorial.segments/editorial
frontend/.next/server/app/editorial/page
frontend/.next/server/app/events
frontend/.next/server/app/events.segments
frontend/.next/server/app/events.segments/events
frontend/.next/server/app/events/page
frontend/.next/server/app/favicon.ico
frontend/.next/server/app/favicon.ico/route
frontend/.next/server/app/help
frontend/.next/server/app/help.segments
frontend/.next/server/app/help.segments/help
frontend/.next/server/app/help/page
frontend/.next/server/app/how-editorial-os-works
frontend/.next/server/app/how-editorial-os-works.segments
frontend/.next/server/app/how-editorial-os-works.segments/how-editorial-os-works
frontend/.next/server/app/how-editorial-os-works/page
frontend/.next/server/app/index.segments
frontend/.next/server/app/login
frontend/.next/server/app/login.segments
frontend/.next/server/app/login.segments/login
frontend/.next/server/app/login/page
frontend/.next/server/app/memory
frontend/.next/server/app/memory.segments
frontend/.next/server/app/memory.segments/memory
frontend/.next/server/app/memory/page
frontend/.next/server/app/msi
frontend/.next/server/app/msi.segments
frontend/.next/server/app/msi.segments/msi
frontend/.next/server/app/msi/page
frontend/.next/server/app/news
frontend/.next/server/app/news.segments
frontend/.next/server/app/news.segments/news
frontend/.next/server/app/news/[id]
frontend/.next/server/app/news/[id]/page
frontend/.next/server/app/news/page
frontend/.next/server/app/newsroom-flow
frontend/.next/server/app/newsroom-flow.segments
frontend/.next/server/app/newsroom-flow.segments/newsroom-flow
frontend/.next/server/app/newsroom-flow/page
frontend/.next/server/app/page
frontend/.next/server/app/prompt-playbook
frontend/.next/server/app/prompt-playbook.segments
frontend/.next/server/app/prompt-playbook.segments/prompt-playbook
frontend/.next/server/app/prompt-playbook/page
frontend/.next/server/app/ready-publish
frontend/.next/server/app/ready-publish/[workId]
frontend/.next/server/app/ready-publish/[workId]/page
frontend/.next/server/app/scripts
frontend/.next/server/app/scripts.segments
frontend/.next/server/app/scripts.segments/scripts
frontend/.next/server/app/scripts/[scriptId]
frontend/.next/server/app/scripts/[scriptId]/page
frontend/.next/server/app/scripts/page
frontend/.next/server/app/services
frontend/.next/server/app/services/document-intel
frontend/.next/server/app/services/document-intel.segments
frontend/.next/server/app/services/document-intel.segments/services
frontend/.next/server/app/services/document-intel.segments/services/document-intel
frontend/.next/server/app/services/document-intel/page
frontend/.next/server/app/services/editor
frontend/.next/server/app/services/editor.segments
frontend/.next/server/app/services/editor.segments/services
frontend/.next/server/app/services/editor.segments/services/editor
frontend/.next/server/app/services/editor/page
frontend/.next/server/app/services/fact-check
frontend/.next/server/app/services/fact-check.segments
frontend/.next/server/app/services/fact-check.segments/services
frontend/.next/server/app/services/fact-check.segments/services/fact-check
frontend/.next/server/app/services/fact-check/page
frontend/.next/server/app/services/media-logger
frontend/.next/server/app/services/media-logger.segments
frontend/.next/server/app/services/media-logger.segments/services
frontend/.next/server/app/services/media-logger.segments/services/media-logger
frontend/.next/server/app/services/media-logger/page
frontend/.next/server/app/services/multimedia
frontend/.next/server/app/services/multimedia.segments
frontend/.next/server/app/services/multimedia.segments/services
frontend/.next/server/app/services/multimedia.segments/services/multimedia
frontend/.next/server/app/services/multimedia/page
frontend/.next/server/app/services/seo
frontend/.next/server/app/services/seo.segments
frontend/.next/server/app/services/seo.segments/services
frontend/.next/server/app/services/seo.segments/services/seo
frontend/.next/server/app/services/seo/page
frontend/.next/server/app/settings
frontend/.next/server/app/settings.segments
frontend/.next/server/app/settings.segments/settings
frontend/.next/server/app/settings/page
frontend/.next/server/app/simulator
frontend/.next/server/app/simulator.segments
frontend/.next/server/app/simulator.segments/simulator
frontend/.next/server/app/simulator/page
frontend/.next/server/app/sources
frontend/.next/server/app/sources.segments
frontend/.next/server/app/sources.segments/sources
frontend/.next/server/app/sources/page
frontend/.next/server/app/stories
frontend/.next/server/app/stories.segments
frontend/.next/server/app/stories.segments/stories
frontend/.next/server/app/stories/page
frontend/.next/server/app/team
frontend/.next/server/app/team.segments
frontend/.next/server/app/team.segments/team
frontend/.next/server/app/team/page
frontend/.next/server/app/today
frontend/.next/server/app/today.segments
frontend/.next/server/app/today.segments/today
frontend/.next/server/app/today/page
frontend/.next/server/app/trends
frontend/.next/server/app/trends.segments
frontend/.next/server/app/trends.segments/trends
frontend/.next/server/app/trends/page
frontend/.next/server/app/ux-insights
frontend/.next/server/app/ux-insights.segments
frontend/.next/server/app/ux-insights.segments/ux-insights
frontend/.next/server/app/ux-insights/page
frontend/.next/server/app/workspace-drafts
frontend/.next/server/app/workspace-drafts.segments
frontend/.next/server/app/workspace-drafts.segments/workspace-drafts
frontend/.next/server/app/workspace-drafts/page
frontend/.next/server/chunks
frontend/.next/server/chunks/ssr
frontend/.next/server/pages
frontend/.next/standalone
frontend/.next/standalone/.next
frontend/.next/standalone/.next/server
frontend/.next/standalone/.next/server/app
frontend/.next/standalone/.next/server/app/_global-error
frontend/.next/standalone/.next/server/app/_global-error.segments
frontend/.next/standalone/.next/server/app/_global-error/page
frontend/.next/standalone/.next/server/app/_not-found
frontend/.next/standalone/.next/server/app/_not-found.segments
frontend/.next/standalone/.next/server/app/_not-found.segments/_not-found
frontend/.next/standalone/.next/server/app/_not-found/page
frontend/.next/standalone/.next/server/app/agents
frontend/.next/standalone/.next/server/app/agents.segments
frontend/.next/standalone/.next/server/app/agents.segments/agents
frontend/.next/standalone/.next/server/app/agents/page
frontend/.next/standalone/.next/server/app/archive
frontend/.next/standalone/.next/server/app/archive.segments
frontend/.next/standalone/.next/server/app/archive.segments/archive
frontend/.next/standalone/.next/server/app/archive/page
frontend/.next/standalone/.next/server/app/competitor-xray
frontend/.next/standalone/.next/server/app/competitor-xray.segments
frontend/.next/standalone/.next/server/app/competitor-xray.segments/competitor-xray
frontend/.next/standalone/.next/server/app/competitor-xray/page
frontend/.next/standalone/.next/server/app/constitution
frontend/.next/standalone/.next/server/app/constitution.segments
frontend/.next/standalone/.next/server/app/constitution.segments/constitution
frontend/.next/standalone/.next/server/app/constitution/page
frontend/.next/standalone/.next/server/app/dashboard
frontend/.next/standalone/.next/server/app/dashboard.segments
frontend/.next/standalone/.next/server/app/dashboard.segments/dashboard
frontend/.next/standalone/.next/server/app/dashboard/metric
frontend/.next/standalone/.next/server/app/dashboard/metric/[metric]
frontend/.next/standalone/.next/server/app/dashboard/metric/[metric]/page
frontend/.next/standalone/.next/server/app/dashboard/page
frontend/.next/standalone/.next/server/app/digital
frontend/.next/standalone/.next/server/app/digital.segments
frontend/.next/standalone/.next/server/app/digital.segments/digital
frontend/.next/standalone/.next/server/app/digital/page
frontend/.next/standalone/.next/server/app/editorial
frontend/.next/standalone/.next/server/app/editorial.segments
frontend/.next/standalone/.next/server/app/editorial.segments/editorial
frontend/.next/standalone/.next/server/app/editorial/page
frontend/.next/standalone/.next/server/app/events
frontend/.next/standalone/.next/server/app/events.segments
frontend/.next/standalone/.next/server/app/events.segments/events
frontend/.next/standalone/.next/server/app/events/page
frontend/.next/standalone/.next/server/app/favicon.ico
frontend/.next/standalone/.next/server/app/favicon.ico/route
frontend/.next/standalone/.next/server/app/help
frontend/.next/standalone/.next/server/app/help.segments
frontend/.next/standalone/.next/server/app/help.segments/help
frontend/.next/standalone/.next/server/app/help/page
frontend/.next/standalone/.next/server/app/how-editorial-os-works
frontend/.next/standalone/.next/server/app/how-editorial-os-works.segments
frontend/.next/standalone/.next/server/app/how-editorial-os-works.segments/how-editorial-os-works
frontend/.next/standalone/.next/server/app/how-editorial-os-works/page
frontend/.next/standalone/.next/server/app/index.segments
frontend/.next/standalone/.next/server/app/login
frontend/.next/standalone/.next/server/app/login.segments
frontend/.next/standalone/.next/server/app/login.segments/login
frontend/.next/standalone/.next/server/app/login/page
frontend/.next/standalone/.next/server/app/memory
frontend/.next/standalone/.next/server/app/memory.segments
frontend/.next/standalone/.next/server/app/memory.segments/memory
frontend/.next/standalone/.next/server/app/memory/page
frontend/.next/standalone/.next/server/app/msi
frontend/.next/standalone/.next/server/app/msi.segments
frontend/.next/standalone/.next/server/app/msi.segments/msi
frontend/.next/standalone/.next/server/app/msi/page
frontend/.next/standalone/.next/server/app/news
frontend/.next/standalone/.next/server/app/news.segments
frontend/.next/standalone/.next/server/app/news.segments/news
frontend/.next/standalone/.next/server/app/news/[id]
frontend/.next/standalone/.next/server/app/news/[id]/page
frontend/.next/standalone/.next/server/app/news/page
frontend/.next/standalone/.next/server/app/newsroom-flow
frontend/.next/standalone/.next/server/app/newsroom-flow.segments
frontend/.next/standalone/.next/server/app/newsroom-flow.segments/newsroom-flow
frontend/.next/standalone/.next/server/app/newsroom-flow/page
frontend/.next/standalone/.next/server/app/page
frontend/.next/standalone/.next/server/app/prompt-playbook
frontend/.next/standalone/.next/server/app/prompt-playbook.segments
frontend/.next/standalone/.next/server/app/prompt-playbook.segments/prompt-playbook
frontend/.next/standalone/.next/server/app/prompt-playbook/page
frontend/.next/standalone/.next/server/app/ready-publish
frontend/.next/standalone/.next/server/app/ready-publish/[workId]
frontend/.next/standalone/.next/server/app/ready-publish/[workId]/page
frontend/.next/standalone/.next/server/app/scripts
frontend/.next/standalone/.next/server/app/scripts.segments
frontend/.next/standalone/.next/server/app/scripts.segments/scripts
frontend/.next/standalone/.next/server/app/scripts/[scriptId]
frontend/.next/standalone/.next/server/app/scripts/[scriptId]/page
frontend/.next/standalone/.next/server/app/scripts/page
frontend/.next/standalone/.next/server/app/services
frontend/.next/standalone/.next/server/app/services/document-intel
frontend/.next/standalone/.next/server/app/services/document-intel.segments
frontend/.next/standalone/.next/server/app/services/document-intel.segments/services
frontend/.next/standalone/.next/server/app/services/document-intel.segments/services/document-intel
frontend/.next/standalone/.next/server/app/services/document-intel/page
frontend/.next/standalone/.next/server/app/services/editor
frontend/.next/standalone/.next/server/app/services/editor.segments
frontend/.next/standalone/.next/server/app/services/editor.segments/services
frontend/.next/standalone/.next/server/app/services/editor.segments/services/editor
frontend/.next/standalone/.next/server/app/services/editor/page
frontend/.next/standalone/.next/server/app/services/fact-check
frontend/.next/standalone/.next/server/app/services/fact-check.segments
frontend/.next/standalone/.next/server/app/services/fact-check.segments/services
frontend/.next/standalone/.next/server/app/services/fact-check.segments/services/fact-check
frontend/.next/standalone/.next/server/app/services/fact-check/page
frontend/.next/standalone/.next/server/app/services/media-logger
frontend/.next/standalone/.next/server/app/services/media-logger.segments
frontend/.next/standalone/.next/server/app/services/media-logger.segments/services
frontend/.next/standalone/.next/server/app/services/media-logger.segments/services/media-logger
frontend/.next/standalone/.next/server/app/services/media-logger/page
frontend/.next/standalone/.next/server/app/services/multimedia
frontend/.next/standalone/.next/server/app/services/multimedia.segments
frontend/.next/standalone/.next/server/app/services/multimedia.segments/services
frontend/.next/standalone/.next/server/app/services/multimedia.segments/services/multimedia
frontend/.next/standalone/.next/server/app/services/multimedia/page
frontend/.next/standalone/.next/server/app/services/seo
frontend/.next/standalone/.next/server/app/services/seo.segments
frontend/.next/standalone/.next/server/app/services/seo.segments/services
frontend/.next/standalone/.next/server/app/services/seo.segments/services/seo
frontend/.next/standalone/.next/server/app/services/seo/page
frontend/.next/standalone/.next/server/app/settings
frontend/.next/standalone/.next/server/app/settings.segments
frontend/.next/standalone/.next/server/app/settings.segments/settings
frontend/.next/standalone/.next/server/app/settings/page
frontend/.next/standalone/.next/server/app/simulator
frontend/.next/standalone/.next/server/app/simulator.segments
frontend/.next/standalone/.next/server/app/simulator.segments/simulator
frontend/.next/standalone/.next/server/app/simulator/page
frontend/.next/standalone/.next/server/app/sources
frontend/.next/standalone/.next/server/app/sources.segments
frontend/.next/standalone/.next/server/app/sources.segments/sources
frontend/.next/standalone/.next/server/app/sources/page
frontend/.next/standalone/.next/server/app/stories
frontend/.next/standalone/.next/server/app/stories.segments
frontend/.next/standalone/.next/server/app/stories.segments/stories
frontend/.next/standalone/.next/server/app/stories/page
frontend/.next/standalone/.next/server/app/team
frontend/.next/standalone/.next/server/app/team.segments
frontend/.next/standalone/.next/server/app/team.segments/team
frontend/.next/standalone/.next/server/app/team/page
frontend/.next/standalone/.next/server/app/today
frontend/.next/standalone/.next/server/app/today.segments
frontend/.next/standalone/.next/server/app/today.segments/today
frontend/.next/standalone/.next/server/app/today/page
frontend/.next/standalone/.next/server/app/trends
frontend/.next/standalone/.next/server/app/trends.segments
frontend/.next/standalone/.next/server/app/trends.segments/trends
frontend/.next/standalone/.next/server/app/trends/page
frontend/.next/standalone/.next/server/app/ux-insights
frontend/.next/standalone/.next/server/app/ux-insights.segments
frontend/.next/standalone/.next/server/app/ux-insights.segments/ux-insights
frontend/.next/standalone/.next/server/app/ux-insights/page
frontend/.next/standalone/.next/server/app/workspace-drafts
frontend/.next/standalone/.next/server/app/workspace-drafts.segments
frontend/.next/standalone/.next/server/app/workspace-drafts.segments/workspace-drafts
frontend/.next/standalone/.next/server/app/workspace-drafts/page
frontend/.next/standalone/.next/server/chunks
frontend/.next/standalone/.next/server/chunks/ssr
frontend/.next/standalone/.next/server/pages
frontend/.next/static
frontend/.next/static/YBY2iMxTVz679QAJeY3aM
frontend/.next/static/chunks
frontend/.next/static/media
frontend/.next/types
frontend/public
frontend/src
frontend/src/app
frontend/src/app/agents
frontend/src/app/archive
frontend/src/app/competitor-xray
frontend/src/app/constitution
frontend/src/app/dashboard
frontend/src/app/dashboard/metric
frontend/src/app/dashboard/metric/[metric]
frontend/src/app/digital
frontend/src/app/editorial
frontend/src/app/events
frontend/src/app/help
frontend/src/app/how-editorial-os-works
frontend/src/app/login
frontend/src/app/memory
frontend/src/app/msi
frontend/src/app/news
frontend/src/app/news/[id]
frontend/src/app/newsroom-flow
frontend/src/app/prompt-playbook
frontend/src/app/ready-publish
frontend/src/app/ready-publish/[workId]
frontend/src/app/scripts
frontend/src/app/scripts/[scriptId]
frontend/src/app/services
frontend/src/app/services/document-intel
frontend/src/app/services/editor
frontend/src/app/services/fact-check
frontend/src/app/services/media-logger
frontend/src/app/services/multimedia
frontend/src/app/services/seo
frontend/src/app/settings
frontend/src/app/simulator
frontend/src/app/sources
frontend/src/app/stories
frontend/src/app/team
frontend/src/app/today
frontend/src/app/trends
frontend/src/app/ux-insights
frontend/src/app/workspace-drafts
frontend/src/components
frontend/src/components/dashboard
frontend/src/components/editorial-os
frontend/src/components/knowledge
frontend/src/components/layout
frontend/src/components/memory
frontend/src/components/onboarding
frontend/src/components/ui
frontend/src/components/ux
frontend/src/components/workflow
frontend/src/components/workspace-drafts
frontend/src/lib
logs
scripts
```

## 2. API Endpoints

### `archive.py`

- `GET` `/archive/echorouk/status` -> `echorouk_archive_status` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/archive/echorouk/search` -> `echorouk_archive_search` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/archive/echorouk/run` -> `run_echorouk_archive_backfill` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`

### `auth.py`

- `POST` `/auth/login` -> `login` | auth: `db=Depends(get_db)`
- `GET` `/auth/me` -> `get_me` | auth: `current_user=Depends(get_current_user)`
- `POST` `/auth/logout` -> `logout` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/auth/users` -> `list_users` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/auth/users` -> `create_user` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `PUT` `/auth/users/{user_id}` -> `update_user` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/auth/users/{user_id}/activity` -> `user_activity` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`

### `competitor_xray.py`

- `POST` `/competitor-xray/sources/seed` -> `seed_sources` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/competitor-xray/sources` -> `list_sources` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/competitor-xray/sources` -> `create_source` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `PATCH` `/competitor-xray/sources/{source_id}` -> `update_source` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/competitor-xray/run` -> `run_xray` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/competitor-xray/runs/{run_id}` -> `run_status` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/competitor-xray/items/latest` -> `latest_items` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/competitor-xray/items/{item_id}/mark-used` -> `mark_item_used` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/competitor-xray/brief` -> `build_brief` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/competitor-xray/live` -> `live_events` | auth: `current_user=Depends(get_current_user)`

### `constitution.py`

- `GET` `/constitution/latest` -> `get_latest_constitution` | auth: `db=Depends(get_db)`
- `GET` `/constitution/ack` -> `get_ack_status` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/constitution/ack` -> `acknowledge` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/constitution/tips` -> `get_constitution_tips` | auth: `none`
- `GET` `/constitution/guide` -> `get_constitution_guide` | auth: `none`

### `dashboard.py`

- `GET` `/dashboard/stats` -> `get_dashboard_stats` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/dashboard/pipeline-runs` -> `get_pipeline_runs` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/dashboard/ops/overview` -> `get_operational_overview` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/dashboard/system/monitor` -> `get_system_monitor` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/dashboard/system/monitor/daily` -> `get_daily_system_monitor` | auth: `current_user=Depends(get_current_user)`
- `POST` `/dashboard/system/monitor/run` -> `run_daily_system_monitor` | auth: `current_user=Depends(get_current_user)`
- `GET` `/dashboard/time-integrity` -> `get_time_integrity_overview` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/dashboard/time-integrity/cleanup` -> `run_time_integrity_cleanup` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/dashboard/time-integrity/cleanup/restore` -> `restore_time_integrity_cleanup` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/dashboard/time-integrity/watchlist` -> `get_time_integrity_watchlist` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/dashboard/time-integrity/watchlist/apply` -> `apply_time_integrity_watchlist_actions` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/dashboard/failed-jobs` -> `get_failed_jobs` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/dashboard/agents/scout/run` -> `trigger_scout` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/dashboard/agents/router/run` -> `trigger_router` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/dashboard/agents/scribe/run` -> `trigger_scribe` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/dashboard/agents/trends/scan` -> `trigger_trend_scan` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/dashboard/agents/trends/latest` -> `get_latest_trend_scan` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/dashboard/agents/published-monitor/run` -> `trigger_published_monitor` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/dashboard/agents/published-monitor/latest` -> `get_latest_published_monitor` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/dashboard/agents/status` -> `agents_status` | auth: `current_user=Depends(get_current_user)`
- `GET` `/dashboard/notifications` -> `dashboard_notifications` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`

### `digital.py`

- `GET` `/digital/overview` -> `overview` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/digital/action-desk` -> `action_desk` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/digital/scopes` -> `list_scopes` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `PUT` `/digital/scopes/{user_id:int}` -> `upsert_scope` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/digital/program-slots/import` -> `import_program_slots` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/digital/program-slots` -> `list_program_slots` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/digital/program-slots` -> `create_program_slot` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `PATCH` `/digital/program-slots/{slot_id:int}` -> `update_program_slot` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `DELETE` `/digital/program-slots/{slot_id:int}` -> `delete_program_slot` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/digital/generate` -> `generate_tasks` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/digital/playbooks` -> `list_playbooks` | auth: `current_user=Depends(get_current_user)`
- `POST` `/digital/tasks/{task_id:int}/bundle` -> `generate_task_bundle` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/digital/tasks` -> `list_tasks` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/digital/tasks` -> `create_task` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `PATCH` `/digital/tasks/{task_id:int}` -> `update_task` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/digital/tasks/{task_id:int}/compose` -> `compose_task_post` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/digital/tasks/{task_id:int}/posts` -> `list_task_posts` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/digital/posts` -> `list_posts` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/digital/posts/{post_id:int}/versions` -> `list_post_versions` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/digital/posts/{post_id:int}/versions/duplicate` -> `duplicate_post_version` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/digital/posts/{post_id:int}/compare` -> `compare_post_versions` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/digital/posts/{post_id:int}/engagement-score` -> `score_post_engagement` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/digital/posts/{post_id:int}/regenerate` -> `regenerate_post` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/digital/tasks/{task_id:int}/posts` -> `create_task_post` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `PATCH` `/digital/posts/{post_id:int}` -> `update_post` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/digital/posts/{post_id:int}/mark-published` -> `mark_post_published` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/digital/posts/{post_id:int}/dispatch` -> `dispatch_post` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/digital/scopes/performance` -> `scope_performance` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/digital/calendar` -> `calendar` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`

### `document_intel.py`

- `POST` `/document-intel/extract/submit` -> `submit_extract_document` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/document-intel/extract/{job_id}` -> `get_extract_document_status` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/document-intel/extract` -> `extract_document` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/document-intel/documents/{document_id}` -> `get_document` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/document-intel/documents/{document_id}/actions` -> `list_document_actions` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/document-intel/documents/{document_id}/create-story` -> `create_story_from_document` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/document-intel/documents/{document_id}/create-draft` -> `create_draft_from_document` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/document-intel/documents/{document_id}/save-memory` -> `save_document_to_memory` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/document-intel/documents/{document_id}/send-to-factcheck` -> `send_document_to_factcheck` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`

### `editorial.py`

- `POST` `/editorial/{article_id}/decide` -> `make_decision` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/{article_id}/handoff` -> `handoff_to_scribe` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/{article_id}/process` -> `process_article` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/{article_id}/quality/readability` -> `run_readability_check` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/{article_id}/quality/technical` -> `run_technical_audit` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/{article_id}/quality/guardian` -> `run_guardian_check` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/{article_id}/quality/reports` -> `get_quality_reports` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/social/approved-feed` -> `social_approved_feed` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/manual-drafts` -> `create_manual_workspace_draft` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/{article_id}/social/variants` -> `article_social_variants` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/workspace/drafts` -> `workspace_drafts` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/workspace/drafts/{work_id}` -> `workspace_draft_by_work_id` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/workspace/drafts/{work_id}/context` -> `workspace_draft_context` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/workspace/drafts/{work_id}/versions` -> `workspace_draft_versions` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/workspace/drafts/{work_id}/diff` -> `workspace_draft_diff` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/autosave` -> `workspace_draft_autosave` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/restore/{version}` -> `workspace_draft_restore` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/ai/rewrite` -> `workspace_ai_rewrite` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/ai/inline` -> `workspace_ai_inline` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/ai/proofread` -> `workspace_ai_proofread` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/ai/headlines` -> `workspace_ai_headlines` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/ai/seo` -> `workspace_ai_seo` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/ai/links/suggest` -> `workspace_ai_links_suggest` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/ai/links/validate` -> `workspace_ai_links_validate` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/ai/links/apply` -> `workspace_ai_links_apply` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/workspace/drafts/{work_id}/ai/links/history` -> `workspace_ai_links_history` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/ai/social` -> `workspace_ai_social` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/ai/apply` -> `workspace_ai_apply` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/verify/claims` -> `workspace_verify_claims` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/quality/score` -> `workspace_quality_score` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/workspace/drafts/{work_id}/publish-readiness` -> `workspace_publish_readiness` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/workspace/drafts/{work_id}/ready-package` -> `workspace_ready_package` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/workspace/drafts/{work_id}/ai/orchestrator` -> `workspace_ai_orchestrator` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/ai/orchestrator/run` -> `workspace_ai_orchestrator_run` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/apply` -> `apply_draft_by_work_id` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/submit-for-chief-approval` -> `submit_draft_for_chief_approval` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/self-approve` -> `self_approve_workspace_draft` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/submit-with-reservations` -> `submit_draft_with_reservations` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/chief/pending` -> `chief_pending_queue` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(UserRole.director, UserRole.editor_chief))`
- `POST` `/editorial/{article_id}/chief/final-decision` -> `chief_final_decision` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(UserRole.director, UserRole.editor_chief))`
- `POST` `/editorial/workspace/drafts/{work_id}/archive` -> `archive_draft_by_work_id` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/workspace/drafts/{work_id}/regenerate` -> `regenerate_draft_by_work_id` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/{article_id}/drafts` -> `list_drafts` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/{article_id}/drafts/{draft_id}` -> `get_draft` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/{article_id}/drafts` -> `create_draft` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `PUT` `/editorial/{article_id}/drafts/{draft_id}` -> `update_draft` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/{article_id}/drafts/{draft_id}/apply` -> `apply_draft` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/editorial/{article_id}/decisions` -> `get_decisions` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/editorial/{article_id}/generate` -> `generate_article` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`

### `events.py`

- `GET` `/events/playbooks` -> `list_playbooks` | auth: `current_user=Depends(get_current_user)`
- `GET` `/events/overview` -> `overview` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/events/action-items` -> `action_items` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/events/reminders` -> `reminders` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/events/` -> `list_events` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/events/upcoming` -> `upcoming_events` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/events/{event_id:int}/coverage` -> `event_coverage` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/events/` -> `create_event` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `PATCH` `/events/{event_id:int}` -> `update_event` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/events/{event_id:int}/story` -> `link_event_story` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/events/{event_id:int}/automation/run` -> `run_event_automation` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `DELETE` `/events/{event_id:int}` -> `delete_event` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/events/import-db` -> `import_events_db` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`

### `jobs.py`

- `GET` `/jobs` -> `list_jobs` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/jobs/queues/depth` -> `get_queue_depths` | auth: `current_user=Depends(get_current_user)`
- `GET` `/jobs/sla` -> `get_queue_sla` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/jobs/providers/health` -> `providers_health` | auth: `current_user=Depends(get_current_user)`
- `GET` `/jobs/dead-letter` -> `list_dead_letter_jobs` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/jobs/{job_id}` -> `get_job` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/jobs/{job_id}/retry` -> `retry_job` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/jobs/recover/stale` -> `recover_stale_jobs` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`

### `journalist_services.py`

- `POST` `/services/editor/tonality` -> `editor_tonality` | auth: `none`
- `POST` `/services/editor/inverted-pyramid` -> `editor_inverted_pyramid` | auth: `none`
- `POST` `/services/editor/proofread` -> `editor_proofread` | auth: `none`
- `POST` `/services/editor/social-summary` -> `editor_social_summary` | auth: `none`
- `POST` `/services/factcheck/vision` -> `factcheck_vision` | auth: `none`
- `POST` `/services/factcheck/consistency` -> `factcheck_consistency` | auth: `none`
- `POST` `/services/factcheck/extract` -> `factcheck_extract` | auth: `none`
- `POST` `/services/factcheck/google` -> `factcheck_google` | auth: `none`
- `POST` `/services/seo/keywords` -> `seo_keywords` | auth: `none`
- `POST` `/services/seo/internal-links` -> `seo_internal_links` | auth: `none`
- `POST` `/services/seo/metadata` -> `seo_metadata` | auth: `none`
- `POST` `/services/multimedia/video-script` -> `multimedia_video_script` | auth: `none`
- `POST` `/services/multimedia/sentiment` -> `multimedia_sentiment` | auth: `none`
- `POST` `/services/multimedia/translate` -> `multimedia_translate` | auth: `none`
- `POST` `/services/multimedia/image-prompt` -> `multimedia_image_prompt` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/services/multimedia/infographic/analyze` -> `infographic_analyze` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/services/multimedia/infographic/prompt` -> `infographic_prompt` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/services/multimedia/infographic/render` -> `infographic_render` | auth: `none`

### `media_logger.py`

- `POST` `/media-logger/run/url` -> `run_from_url` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/media-logger/run/upload` -> `run_from_upload` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/media-logger/runs/{run_id}` -> `run_status` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/media-logger/result` -> `run_result` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/media-logger/runs` -> `recent_runs` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/media-logger/ask` -> `ask_quote` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/media-logger/live` -> `live_events` | auth: `current_user=Depends(get_current_user)`

### `memory.py`

- `GET` `/memory/overview` -> `overview` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/memory/items` -> `list_items` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/memory/items` -> `create_item` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/memory/items/{item_id}` -> `get_item` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `PATCH` `/memory/items/{item_id}` -> `update_item` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/memory/items/{item_id}/use` -> `mark_item_used` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/memory/recommendations` -> `recommendations` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `POST` `/memory/quick-capture` -> `quick_capture` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`
- `GET` `/memory/items/{item_id}/events` -> `get_item_events` | auth: `current_user=Depends(get_current_user) | db=Depends(get_db)`

### `mil.py`

- `POST` `/mil/analyze/recent` -> `analyze_recent` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/mil/signals` -> `list_signals` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/mil/signals/{signal_id}` -> `get_signal_detail` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/mil/signals/{signal_id}/dismiss` -> `dismiss_signal` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/mil/today/escalations` -> `today_escalations` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/mil/today/full` -> `today_full` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/mil/dashboard` -> `dashboard` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/mil/entities` -> `entities` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/mil/clusters` -> `clusters` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/mil/stories/{story_id}/insights` -> `story_insights` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/mil/events/{event_id}/insights` -> `event_insights` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/mil/editor/context` -> `editor_context` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/mil/signals/{signal_id}/useful` -> `mark_signal_useful` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/mil/signals/{signal_id}/snooze` -> `snooze_signal` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`

### `msi.py`

- `GET` `/msi/profiles` -> `get_profiles` | auth: `current_user=Depends(get_current_user)`
- `POST` `/msi/run` -> `run_msi` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/msi/runs/{run_id}` -> `get_run_status` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/msi/report` -> `get_report` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/msi/timeseries` -> `get_timeseries` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/msi/top` -> `get_top` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/msi/live` -> `live_events` | auth: `current_user=Depends(get_current_user)`
- `GET` `/msi/watchlist` -> `get_watchlist` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/msi/watchlist` -> `add_watchlist` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `PATCH` `/msi/watchlist/{item_id}` -> `patch_watchlist` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `DELETE` `/msi/watchlist/{item_id}` -> `delete_watchlist` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/msi/watchlist/seed` -> `seed_watchlist` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`

### `news.py`

- `GET` `/news/` -> `list_articles` | auth: `db=Depends(get_db)`
- `GET` `/news/breaking/latest` -> `get_breaking_news` | auth: `db=Depends(get_db)`
- `GET` `/news/candidates/pending` -> `get_pending_candidates` | auth: `db=Depends(get_db)`
- `GET` `/news/insights` -> `news_insights` | auth: `db=Depends(get_db)`
- `GET` `/news/search/semantic` -> `semantic_search` | auth: `db=Depends(get_db)`
- `GET` `/news/{article_id}` -> `get_article` | auth: `db=Depends(get_db)`
- `GET` `/news/{article_id}/related` -> `related_articles` | auth: `db=Depends(get_db)`
- `GET` `/news/{article_id}/cluster` -> `article_cluster` | auth: `db=Depends(get_db)`
- `GET` `/news/{article_id}/relations` -> `article_relations` | auth: `db=Depends(get_db)`

### `rss.py`

- `GET` `/rss/sources` -> `list_rss_sources` | auth: `db=Depends(get_db)`
- `GET` `/rss/source/{source_id}` -> `rss_for_source` | auth: `db=Depends(get_db)`
- `GET` `/rss/source/{source_id}.xml` -> `rss_for_source` | auth: `db=Depends(get_db)`
- `GET` `/rss/source/by-name/{source_name}` -> `rss_for_source_name` | auth: `db=Depends(get_db)`
- `GET` `/rss/source/by-name/{source_name}.xml` -> `rss_for_source_name` | auth: `db=Depends(get_db)`
- `GET` `/rss/source/by-slug/{source_slug}` -> `rss_for_source_slug` | auth: `db=Depends(get_db)`
- `GET` `/rss/source/by-slug/{source_slug}.xml` -> `rss_for_source_slug` | auth: `db=Depends(get_db)`

### `scripts.py`

- `GET` `/scripts` -> `list_script_projects` | auth: `db=Depends(get_db) | _=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/from-article/{article_id}` -> `create_script_from_article` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/from-story/{story_id}` -> `create_script_from_story` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/bulletin/daily` -> `generate_daily_bulletin` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/bulletin/weekly` -> `generate_weekly_bulletin` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `GET` `/scripts/{script_id}` -> `get_script_project` | auth: `db=Depends(get_db) | _=Depends(require_roles(*VIEW_ROLES))`
- `GET` `/scripts/{script_id}/outputs` -> `list_script_outputs` | auth: `db=Depends(get_db) | _=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/{script_id}/regenerate` -> `regenerate_script_project` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/{script_id}/duplicate-version` -> `duplicate_script_output_version` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `GET` `/scripts/{script_id}/versions/diff` -> `script_versions_diff` | auth: `db=Depends(get_db) | _=Depends(require_roles(*VIEW_ROLES))`
- `GET` `/scripts/{script_id}/recovery-hints` -> `script_recovery_hints` | auth: `db=Depends(get_db) | _=Depends(require_roles(*VIEW_ROLES))`
- `PATCH` `/scripts/{script_id}/video` -> `update_video_workspace` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `PATCH` `/scripts/{script_id}/scenes/{scene_idx}` -> `patch_video_scene` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/{script_id}/scenes` -> `add_video_scene` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `DELETE` `/scripts/{script_id}/scenes/{scene_idx}` -> `delete_video_scene` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/{script_id}/scenes/reorder` -> `reorder_video_scenes` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/{script_id}/scenes/{scene_idx}/split` -> `split_video_scene` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/{script_id}/scenes/merge` -> `merge_video_scenes` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/{script_id}/scenes/{scene_idx}/lock` -> `lock_video_scene` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/{script_id}/scenes/{scene_idx}/unlock` -> `unlock_video_scene` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/{script_id}/scenes/{scene_idx}/regenerate` -> `regenerate_video_scene` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `PATCH` `/scripts/{script_id}/captions` -> `update_video_captions` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `PATCH` `/scripts/{script_id}/delivery` -> `update_video_delivery` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/{script_id}/delivery/export` -> `export_video_delivery_bundle` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*VIEW_ROLES))`
- `POST` `/scripts/{script_id}/approve` -> `approve_script_project` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*CHIEF_ROLES))`
- `POST` `/scripts/{script_id}/reject` -> `reject_script_project` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(*CHIEF_ROLES))`

### `settings.py`

- `GET` `/settings/` -> `list_settings` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/settings/{key}` -> `get_setting` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `PUT` `/settings/{key}` -> `upsert_setting` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `POST` `/settings/import-env` -> `import_from_env` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/settings/audit` -> `list_audit` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/settings/test/{key}` -> `test_setting` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`

### `simulator.py`

- `POST` `/sim/run` -> `run_simulation` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/sim/runs/{run_id}` -> `sim_run_status` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/sim/result` -> `sim_result` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/sim/history` -> `sim_history` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/sim/live` -> `sim_live_events` | auth: `current_user=Depends(get_current_user)`

### `sources.py`

- `GET` `/sources/` -> `list_sources` | auth: `db=Depends(get_db)`
- `POST` `/sources/` -> `create_source` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `PUT` `/sources/{source_id:int}` -> `update_source` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `DELETE` `/sources/{source_id:int}` -> `delete_source` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/sources/stats` -> `sources_stats` | auth: `db=Depends(get_db)`
- `GET` `/sources/policy` -> `get_sources_policy` | auth: `current_user=Depends(get_current_user)`
- `PUT` `/sources/policy` -> `update_sources_policy` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/sources/health` -> `sources_health` | auth: `db=Depends(get_db)`
- `POST` `/sources/health/apply` -> `apply_sources_health_actions` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`

### `stories.py`

- `POST` `/stories` -> `create_story` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(UserRole.director, UserRole.editor_chief, UserRole.journalist, UserRole.social_media, UserRole.print_editor))`
- `GET` `/stories` -> `list_stories` | auth: `db=Depends(get_db) | _=Depends(require_roles(UserRole.director, UserRole.editor_chief, UserRole.journalist, UserRole.social_media, UserRole.print_editor))`
- `POST` `/stories/from-article/{article_id}` -> `create_story_from_article` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(UserRole.director, UserRole.editor_chief, UserRole.journalist, UserRole.social_media, UserRole.print_editor))`
- `GET` `/stories/suggest` -> `suggest_stories_for_article` | auth: `db=Depends(get_db) | _=Depends(require_roles(UserRole.director, UserRole.editor_chief, UserRole.journalist, UserRole.social_media, UserRole.print_editor))`
- `GET` `/stories/clusters` -> `list_story_clusters` | auth: `db=Depends(get_db) | _=Depends(require_roles(UserRole.director, UserRole.editor_chief, UserRole.journalist, UserRole.social_media, UserRole.print_editor))`
- `GET` `/stories/{story_id}` -> `get_story` | auth: `db=Depends(get_db) | _=Depends(require_roles(UserRole.director, UserRole.editor_chief, UserRole.journalist, UserRole.social_media, UserRole.print_editor))`
- `GET` `/stories/{story_id}/dossier` -> `get_story_dossier` | auth: `db=Depends(get_db) | _=Depends(require_roles(UserRole.director, UserRole.editor_chief, UserRole.journalist, UserRole.social_media, UserRole.print_editor))`
- `GET` `/stories/{story_id}/control-center` -> `get_story_control_center` | auth: `db=Depends(get_db) | _=Depends(require_roles(UserRole.director, UserRole.editor_chief, UserRole.journalist, UserRole.social_media, UserRole.print_editor))`
- `POST` `/stories/{story_id}/link/article/{article_id}` -> `link_story_article` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(UserRole.director, UserRole.editor_chief, UserRole.journalist, UserRole.social_media, UserRole.print_editor))`
- `POST` `/stories/{story_id}/link/draft/{draft_id}` -> `link_story_draft` | auth: `db=Depends(get_db) | current_user=Depends(require_roles(UserRole.director, UserRole.editor_chief, UserRole.journalist, UserRole.social_media, UserRole.print_editor))`

### `telemetry.py`

- `POST` `/telemetry/ux` -> `log_ux_event` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/telemetry/ux/recent` -> `get_recent_ux_events` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`
- `GET` `/telemetry/ux/summary` -> `get_ux_summary` | auth: `db=Depends(get_db) | current_user=Depends(get_current_user)`

## 3. SQLAlchemy Models

- `ArchiveCrawlState` in `archive_crawl.py`: id, source_key, source_name, base_url, status, seeded_at, last_run_started_at, last_run_finished_at, last_error, stats_json, created_at, updated_at, urls
- `ArchiveCrawlUrl` in `archive_crawl.py`: id, state_id, url, url_type, status, priority, depth, discovered_from_url, canonical_url, article_id, attempts, last_http_status, last_error, discovered_at, fetched_at, indexed_at, created_at, updated_at, state, article
- `SettingsAudit` in `audit.py`: id, key, action, old_value, new_value, actor, created_at
- `ActionAuditLog` in `audit.py`: id, action, entity_type, entity_id, from_state, to_state, reason, details_json, actor_user_id, actor_username, correlation_id, request_id, created_at
- `ArticleClaim` in `claim_support.py`: id, article_id, quality_report_id, work_id, claim_external_id, claim_text, claim_type, risk_level, confidence, sensitive, blocking, supported, unverifiable, unverifiable_reason, metadata_json, created_by, created_at, updated_at, article, quality_report, supports
- `ArticleClaimSupport` in `claim_support.py`: id, claim_id, support_kind, support_ref, source_host, metadata_json, created_at, claim
- `CompetitorXraySource` in `competitor_xray.py`: id, name, feed_url, domain, language, weight, enabled, created_at, updated_at
- `CompetitorXrayRun` in `competitor_xray.py`: id, run_id, status, total_scanned, total_gaps, idempotency_key, created_by_user_id, created_by_username, created_at, finished_at, error
- `CompetitorXrayItem` in `competitor_xray.py`: id, run_id, source_id, competitor_title, competitor_url, competitor_summary, published_at, priority_score, status, angle_title, angle_rationale, angle_questions_json, starter_sources_json, matched_article_id, created_at, updated_at
- `CompetitorXrayEvent` in `competitor_xray.py`: id, run_id, node, event_type, payload_json, ts
- `ConstitutionMeta` in `constitution.py`: id, version, file_url, is_active, updated_at
- `ConstitutionAck` in `constitution.py`: id, user_id, version, acknowledged_at
- `ImagePrompt` in `constitution.py`: id, article_id, prompt_text, style, created_at, created_by
- `InfographicData` in `constitution.py`: id, article_id, data_json, prompt_text, created_at, created_by
- `DigitalTeamScope` in `digital_team.py`: id, user_id, can_manage_news, can_manage_tv, platforms, notes, created_by_user_id, updated_by_user_id, created_at, updated_at
- `ProgramSlot` in `digital_team.py`: id, channel, program_title, program_type, description, day_of_week, start_time, duration_minutes, timezone, priority, is_active, social_focus, tags, source_ref, created_by_user_id, updated_by_user_id, created_at, updated_at
- `SocialTask` in `digital_team.py`: id, channel, platform, task_type, title, brief, status, priority, due_at, scheduled_at, started_at, completed_at, dedupe_key, program_slot_id, event_id, article_id, story_id, owner_user_id, owner_username, created_by_user_id, created_by_username, updated_by_user_id, updated_by_username, published_posts_count, last_published_at, created_at, updated_at
- `SocialPost` in `digital_team.py`: id, task_id, channel, platform, content_text, hashtags, media_urls, status, scheduled_at, published_at, published_url, external_post_id, error_message, created_by_user_id, created_by_username, updated_by_user_id, updated_by_username, created_at, updated_at
- `SocialPostVersion` in `digital_team.py`: id, post_id, version_no, version_type, content_text, hashtags, media_urls, note, created_by_user_id, created_by_username, created_at
- `DocumentIntelDocument` in `document_intel.py`: id, filename, title, parser_used, language_hint, detected_language, document_type, document_summary, stats, headings, news_candidates, entities, story_angles, data_points, warnings, preview_text, source_job_id, uploaded_by_user_id, uploaded_by_username, created_at, updated_at, claims, actions
- `DocumentIntelClaim` in `document_intel.py`: id, document_id, rank, text, claim_type, confidence, risk_level, created_at, document
- `DocumentIntelAction` in `document_intel.py`: id, document_id, action_type, target_type, target_id, note, payload_json, actor_user_id, actor_username, created_at, document
- `EventMemoItem` in `event_memo.py`: id, scope, title, summary, coverage_plan, starts_at, ends_at, timezone, country_code, is_all_day, lead_time_hours, priority, status, readiness_status, source_url, tags, checklist, preparation_started_at, playbook_key, story_id, owner_user_id, owner_username, created_by_user_id, created_by_username, updated_by_user_id, updated_by_username, created_at, updated_at
- `TaskIdempotencyKey` in `idempotency.py`: idempotency_key, task_name, status, first_job_id, last_job_id, result_json, error, created_at, updated_at
- `JobRun` in `job_queue.py`: id, job_type, queue_name, entity_id, status, priority, request_id, correlation_id, actor_user_id, actor_username, attempt, max_attempts, queued_at, started_at, finished_at, error, payload_json, result_json, created_at, updated_at
- `DeadLetterJob` in `job_queue.py`: id, original_job_id, job_type, queue_name, failed_at, error, traceback, payload_json, meta_json
- `ArticleProfile` in `knowledge.py`: id, article_id, archive_code, language, normalized_title, normalized_summary, normalized_content, canonical_url, source_name, category, editorial_status, metadata_json, search_text, created_at, updated_at, article
- `ArticleTopic` in `knowledge.py`: id, article_id, topic, confidence, source, created_at, article
- `ArticleEntity` in `knowledge.py`: id, article_id, entity, entity_type, confidence, source, created_at, article
- `ArticleChunk` in `knowledge.py`: id, article_id, chunk_index, language, content, content_length, created_at, updated_at, article
- `ArticleVector` in `knowledge.py`: id, article_id, chunk_id, vector_type, model, dim, embedding, content_hash, created_at, updated_at, article, chunk
- `StoryCluster` in `knowledge.py`: id, cluster_key, label, geography, category, created_at, updated_at
- `StoryClusterMember` in `knowledge.py`: id, cluster_id, article_id, score, created_at, cluster, article
- `ArticleFingerprint` in `knowledge.py`: id, article_id, simhash, token_count, shingles, created_at, updated_at, article
- `ArticleRelation` in `knowledge.py`: id, from_article_id, to_article_id, relation_type, score, metadata_json, created_at, from_article, to_article
- `LinkIndexItem` in `link_intelligence.py`: id, url, domain, link_type, title, summary, category, keywords_json, metadata_json, published_at, authority_score, source_article_id, is_active, first_seen_at, last_seen_at, created_at, updated_at
- `TrustedDomain` in `link_intelligence.py`: id, domain, display_name, trust_score, tier, enabled, notes, created_by, created_at, updated_at
- `LinkRecommendationRun` in `link_intelligence.py`: id, run_id, work_id, article_id, draft_id, mode, status, source_counts_json, created_by_user_id, created_by_username, created_at, finished_at, error
- `LinkRecommendationItem` in `link_intelligence.py`: id, run_id, link_index_item_id, link_type, url, title, anchor_text, placement_hint, reason, score, confidence, rel_attrs, status, metadata_json, created_at
- `LinkClickEvent` in `link_intelligence.py`: id, article_id, work_id, url, link_type, clicked_by_user_id, clicked_by_username, created_at
- `MediaLoggerRun` in `media_logger.py`: id, run_id, source_type, source_ref, source_label, language_hint, status, transcript_language, transcript_text, duration_seconds, segments_count, highlights_count, idempotency_key, created_by_user_id, created_by_username, created_at, finished_at, error
- `MediaLoggerSegment` in `media_logger.py`: id, run_id, segment_index, start_sec, end_sec, text, confidence, speaker, created_at
- `MediaLoggerHighlight` in `media_logger.py`: id, run_id, rank, quote, reason, start_sec, end_sec, confidence, created_at
- `MediaLoggerJobEvent` in `media_logger.py`: id, run_id, node, event_type, payload_json, ts
- `MILSignal` in `mil.py`: id, signal_code, signal_type, triage_action, priority, confidence_score, explanation_json, payload_json, target_surface, related_entity_id, related_story_id, related_event_id, related_cluster_id, created_from_job_id, created_at, updated_at, dismissed_at, dismissed_by, useful_count, useful_last_marked_at, useful_last_marked_by, snoozed_until, status, signal_sources, entity
- `MILSignalSource` in `mil.py`: id, signal_id, article_id, source_id, competitor_item_id, support_kind, support_ref, weight, created_at, signal
- `MILEntity` in `mil.py`: id, entity_name, entity_type, normalized_name, aliases_json, first_seen_at, last_seen_at, mention_count, trust_context_json
- `MILEntityEdge` in `mil.py`: id, source_entity_id, target_entity_id, edge_type, weight, first_seen_at, last_seen_at, evidence_count
- `MILSourceTrustScore` in `mil.py`: id, source_id, score, score_components_json, last_calculated_at
- `MILCluster` in `mil.py`: id, cluster_key, label, dominant_entity, article_count, source_diversity_count, velocity_score, confidence_score, target_surface, metadata_json, first_seen_at, last_seen_at, created_at, updated_at
- `MILClusterArticle` in `mil.py`: id, cluster_id, article_id, weight, created_at
- `MsiRun` in `msi.py`: id, run_id, profile_id, entity, mode, period_start, period_end, timezone, status, created_by_user_id, created_by_username, created_at, finished_at, error
- `MsiReport` in `msi.py`: id, run_id, report_json, created_at
- `MsiTimeseries` in `msi.py`: id, profile_id, entity, mode, period_end, msi, level, components_json, created_at
- `MsiArtifact` in `msi.py`: id, run_id, items_json, aggregates_json, created_at
- `MsiJobEvent` in `msi.py`: id, run_id, node, event_type, payload_json, ts
- `MsiWatchlist` in `msi.py`: id, profile_id, entity, aliases_json, enabled, run_daily, run_weekly, created_by_user_id, created_by_username, created_at, updated_at
- `MsiBaseline` in `msi.py`: id, profile_id, entity, pressure_history, last_topic_dist, baseline_window_days, last_updated
- `Source` in `news.py`: id, name, slug, method, url, rss_url, category, language, languages, region, source_type, description, trust_score, credibility, priority, enabled, fetch_interval_minutes, last_fetched_at, error_count, created_at, updated_at, articles
- `Article` in `news.py`: id, unique_hash, original_title, original_url, original_content, published_at, crawled_at, source_id, source_name, title_ar, summary, body_html, category, importance_score, urgency, is_breaking, sentiment, truth_score, entities, keywords, seo_title, seo_description, status, rejection_reason, reviewed_by, reviewed_at, published_url, processing_time_ms, ai_model_used, retry_count, trace_id, created_at, updated_at, source, editor_decisions
- `EditorDecision` in `news.py`: id, article_id, editor_name, decision, reason, original_ai_title, edited_title, original_ai_body, edited_body, decided_at, article
- `EditorialDraft` in `news.py`: id, article_id, work_id, source_action, parent_draft_id, change_origin, title, body, note, status, version, created_by, updated_by, applied_by, applied_at, created_at, updated_at, article, parent_draft
- `FeedbackLog` in `news.py`: id, article_id, field_name, original_value, corrected_value, correction_type, logged_at
- `FailedJob` in `news.py`: id, job_type, payload, error_message, error_traceback, retry_count, max_retries, resolved, created_at, resolved_at
- `PipelineRun` in `news.py`: id, run_type, started_at, finished_at, total_items, new_items, duplicates, errors, ai_calls, status, details
- `ProjectMemoryItem` in `project_memory.py`: id, memory_type, memory_subtype, title, content, tags, source_type, source_ref, article_id, status, importance, freshness_status, valid_until, created_by_user_id, created_by_username, updated_by_user_id, updated_by_username, created_at, updated_at, article, events
- `ProjectMemoryEvent` in `project_memory.py`: id, memory_id, event_type, note, actor_user_id, actor_username, created_at, memory_item
- `ArticleQualityReport` in `quality.py`: id, article_id, stage, passed, score, blocking_reasons, actionable_fixes, report_json, created_by, created_at, article
- `ScriptProject` in `script.py`: id, type, status, story_id, article_id, title, params_json, created_by, updated_by, created_at, updated_at, story, article, outputs
- `ScriptOutput` in `script.py`: id, script_id, version, content_json, content_text, format, quality_issues_json, created_at, project
- `ApiSetting` in `settings.py`: id, key, value, description, is_secret, updated_at
- `SimRun` in `simulator.py`: id, run_id, article_id, draft_id, headline, body_excerpt, platform, mode, status, created_by_user_id, created_by_username, idempotency_key, created_at, finished_at, error
- `SimResult` in `simulator.py`: id, run_id, risk_score, virality_score, confidence_score, breakdown_json, reactions_json, advice_json, red_flags_json, created_at
- `SimFeedback` in `simulator.py`: id, run_id, action, editor_notes, editor_id, editor_username, created_at
- `SimCalibration` in `simulator.py`: id, platform, bucket, actual_ctr, actual_backlash, actual_shares, updated_at
- `SimJobEvent` in `simulator.py`: id, run_id, node, event_type, payload_json, ts
- `Story` in `story.py`: id, story_key, title, summary, category, geography, status, priority, created_by, updated_by, created_at, updated_at, items
- `StoryItem` in `story.py`: id, story_id, article_id, draft_id, link_type, note, created_by, created_at, story, article, draft
- `User` in `user.py`: id, full_name_ar, username, hashed_password, role, departments, specialization, is_active, is_online, last_login_at, created_at, updated_at
- `UserActivityLog` in `user_activity.py`: id, actor_user_id, actor_username, target_user_id, target_username, action, details, created_at

## 4. Celery Tasks

- `run_editorial_ai_job` -> `run_editorial_ai_job` in `backend/app/queue/tasks/ai_tasks.py`
- `run_editorial_links_job` -> `run_editorial_links_job` in `backend/app/queue/tasks/ai_tasks.py`
- `run_router_batch` -> `run_router_batch` in `backend/app/queue/tasks/pipeline_tasks.py`
- `run_scout_batch` -> `run_scout_batch` in `backend/app/queue/tasks/pipeline_tasks.py`
- `run_scribe_batch` -> `run_scribe_batch` in `backend/app/queue/tasks/pipeline_tasks.py`
- `run_trends_scan` -> `run_trends_scan` in `backend/app/queue/tasks/pipeline_tasks.py`
- `run_published_monitor_scan` -> `run_published_monitor_scan` in `backend/app/queue/tasks/pipeline_tasks.py`
- `run_mil_analyze_recent` -> `run_mil_analyze_recent` in `backend/app/queue/tasks/pipeline_tasks.py`
- `run_msi_job` -> `run_msi_job` in `backend/app/queue/tasks/pipeline_tasks.py`
- `run_simulator_job` -> `run_simulator_job` in `backend/app/queue/tasks/pipeline_tasks.py`
- `run_document_intel_extract_job` -> `run_document_intel_extract_job` in `backend/app/queue/tasks/pipeline_tasks.py`
- `run_script_generate_job` -> `run_script_generate_job` in `backend/app/queue/tasks/pipeline_tasks.py`
- `run_echorouk_archive_backfill` -> `run_echorouk_archive_backfill` in `backend/app/queue/tasks/pipeline_tasks.py`

## 5. Service Files

- `__init__.py`
- `ai_service.py`
- `article_index_service.py`
- `audit_service.py`
- `cache_service.py`
- `claim_support_service.py`
- `competitor_xray_service.py`
- `digital_team_service.py`
- `document_intel_job_storage.py`
- `document_intel_service.py`
- `document_intel_workspace_service.py`
- `echorouk_archive_service.py`
- `editorial_prompt_orchestrator_service.py`
- `embedding_service.py`
- `event_reminder_service.py`
- `fact_check_tools_service.py`
- `job_queue_service.py`
- `link_intelligence_service.py`
- `media_logger_service.py`
- `mil_service.py`
- `news_knowledge_service.py`
- `notification_service.py`
- `ops_monitor_service.py`
- `project_memory_service.py`
- `provider_manager.py`
- `quality_gate_service.py`
- `script_studio_service.py`
- `script_video_workspace_service.py`
- `settings_service.py`
- `smart_editor_service.py`
- `state_transition_service.py`
- `task_execution_service.py`
- `time_integrity_service.py`
- `trend_signal_service.py`

## 6. Agent Files and Main Functions

- `audio_agent.py`: AudioAgent: generate_briefing, text_to_speech_simple, cleanup_temp_files
- `published_monitor.py`: PublishedContentMonitorAgent: scan, latest
- `router.py`: RouterAgent: process_batch
- `scout.py`: _aiohttp_ssl_context, ScoutAgent: run, fetch_single_source
- `scribe.py`: ScribeAgent: write_article, batch_write
- `trend_radar.py`: TrendRadarAgent: scan, scan_all

## 7. Docker Services

- `backend` | image/build: `build (backend/Dockerfile)` | ports: `${APP_PORT:-8000}:8000`
- `worker` | image/build: `build (backend/Dockerfile)` | ports: (none)
- `flower` | image/build: `build (backend/Dockerfile)` | ports: `127.0.0.1:5555:5555`
- `frontend` | image/build: `build (Dockerfile)` | ports: `3000:3000`
- `postgres` | image/build: `pgvector/pgvector:pg16` | ports: (none)
- `redis` | image/build: `redis:7-alpine` | ports: `127.0.0.1:6380:6379` | requires `REDIS_PASSWORD`
- `minio` | image/build: `minio/minio:latest` | ports: `9000:9000`, `9001:9001`
- `freshrss-db` | image/build: `mariadb:11` | ports: (none)
- `freshrss` | image/build: `freshrss/freshrss:latest` | ports: `8082:80` | healthcheck: `php` HTTP probe to `http://127.0.0.1/i/`
- `rssbridge` | image/build: `rssbridge/rss-bridge:latest` | ports: `8083:80` | healthcheck: `php` HTTP probe to `http://127.0.0.1/`

## 8. Environment Variable Keys from `.env.example`

```text
APP_NAME
APP_ENV
APP_DEBUG
APP_SECRET_KEY
APP_PORT
ECHOROUK_OS_APP_NAME
ECHOROUK_OS_APP_ENV
ECHOROUK_OS_APP_DEBUG
ECHOROUK_OS_APP_SECRET_KEY
ECHOROUK_OS_APP_PORT
ECHOROUK_OS_POSTGRES_HOST
ECHOROUK_OS_POSTGRES_PORT
ECHOROUK_OS_POSTGRES_DB
ECHOROUK_OS_POSTGRES_USER
ECHOROUK_OS_POSTGRES_PASSWORD
ECHOROUK_OS_REDIS_HOST
ECHOROUK_OS_REDIS_PORT
ECHOROUK_OS_REDIS_DB
ECHOROUK_OS_GEMINI_API_KEY
ECHOROUK_OS_EMBEDDING_PROVIDER
ECHOROUK_OS_EMBEDDING_MODEL_GEMINI
ECHOROUK_OS_EMBEDDING_VECTOR_DIM
ECHOROUK_OS_EMBEDDING_USE_REAL_FOR_CHUNKS
ECHOROUK_OS_ECHOROUK_ARCHIVE_ENABLED
ECHOROUK_OS_ECHOROUK_ARCHIVE_BASE_URL
ECHOROUK_OS_ECHOROUK_ARCHIVE_SECTIONS
ECHOROUK_OS_ECHOROUK_ARCHIVE_REQUEST_TIMEOUT_SECONDS
ECHOROUK_OS_ECHOROUK_ARCHIVE_DELAY_MS
ECHOROUK_OS_ECHOROUK_ARCHIVE_STALE_PROCESSING_MINUTES
ECHOROUK_OS_ECHOROUK_ARCHIVE_MAX_LISTING_PAGES_PER_RUN
ECHOROUK_OS_ECHOROUK_ARCHIVE_MAX_ARTICLES_PER_RUN
ECHOROUK_OS_ECHOROUK_ARCHIVE_MAX_LISTING_DEPTH
ECHOROUK_OS_ECHOROUK_ARCHIVE_BACKFILL_INTERVAL_MINUTES
ECHOROUK_OS_ECHOROUK_ARCHIVE_REFRESH_INTERVAL_MINUTES
ECHOROUK_OS_ECHOROUK_ARCHIVE_REFRESH_LISTING_PAGES
ECHOROUK_OS_ECHOROUK_ARCHIVE_REFRESH_ARTICLE_PAGES
ECHOROUK_OS_ECHOROUK_ARCHIVE_RAG_ENABLED
ECHOROUK_OS_ECHOROUK_ARCHIVE_RAG_LIMIT
ECHOROUK_OS_ECHOROUK_ARCHIVE_RAG_MIN_SCORE
ECHOROUK_OS_ECHOROUK_ARCHIVE_RAG_PREFER_CATEGORY_MATCH
ECHOROUK_OS_YOUTUBE_DATA_API_KEY
ECHOROUK_OS_YOUTUBE_TRENDS_ENABLED
ECHOROUK_OS_GOOGLE_FACT_CHECK_API_KEY
ECHOROUK_OS_AUTO_PIPELINE_ENABLED
ECHOROUK_OS_SCOUT_INTERVAL_MINUTES
ECHOROUK_OS_TREND_RADAR_INTERVAL_MINUTES
ECHOROUK_OS_ROUTER_BATCH_LIMIT
ECHOROUK_OS_ROUTER_SOURCE_QUOTA
ECHOROUK_OS_ROUTER_CANDIDATE_SOURCE_QUOTA
ECHOROUK_OS_ROUTER_RULE_MIN_HITS
ECHOROUK_OS_ROUTER_SKIP_AI_FOR_NON_LOCAL_AGGREGATOR
ECHOROUK_OS_ROUTER_REJECT_FILTERS_ENABLED
ECHOROUK_OS_ROUTER_AI_CALLS_PER_BATCH_CAP
ECHOROUK_OS_AUTO_PIPELINE_ROUTER_BURST_MAX
ECHOROUK_OS_AUTO_PIPELINE_ROUTER_BURST_BACKLOG_THRESHOLD
ECHOROUK_OS_DEFER_NONCRITICAL_JOBS_WHEN_BACKLOG_HIGH
ECHOROUK_OS_NONCRITICAL_BACKLOG_THRESHOLD
ECHOROUK_OS_PROVIDER_PREFER_CONFIGURED_ONLY
ECHOROUK_OS_PROVIDER_DAILY_BUDGET_USD
ECHOROUK_OS_PROVIDER_PER_JOB_MAX_USD
ECHOROUK_OS_PROVIDER_COST_ESTIMATE_GEMINI_USD
ECHOROUK_OS_PROVIDER_QUEUE_TIER_SCRIBE
ECHOROUK_OS_PROVIDER_QUEUE_TIER_QUALITY
ECHOROUK_OS_PROVIDER_QUEUE_TIER_SIMULATOR
ECHOROUK_OS_PROVIDER_QUEUE_TIER_ROUTER
ECHOROUK_OS_SCOUT_USE_FRESHRSS
ECHOROUK_OS_FRESHRSS_FEED_URL
ECHOROUK_OS_EVENT_REMINDERS_ENABLED
ECHOROUK_OS_EVENT_REMINDERS_INTERVAL_MINUTES
ECHOROUK_OS_TIME_INTEGRITY_CLEANUP_ENABLED
ECHOROUK_OS_TIME_INTEGRITY_CLEANUP_INTERVAL_MINUTES
ECHOROUK_OS_DIGITAL_TEAM_AUTO_GENERATION_ENABLED
ECHOROUK_OS_DIGITAL_TEAM_AUTO_GENERATION_INTERVAL_MINUTES
ECHOROUK_OS_DIGITAL_TEAM_AUTO_GENERATION_HOURS_AHEAD
ECHOROUK_OS_DIGITAL_TEAM_AUTO_INCLUDE_EVENTS
ECHOROUK_OS_DIGITAL_TEAM_AUTO_INCLUDE_BREAKING
ECHOROUK_OS_DOCUMENT_INTEL_DOCLING_TIMEOUT_SECONDS
ECHOROUK_OS_DOCUMENT_INTEL_DOCLING_MAX_SIZE_MB
ECHOROUK_OS_DOCUMENT_INTEL_DOCLING_SKIP_FOR_AR
ECHOROUK_OS_DOCUMENT_INTEL_MAX_UPLOAD_MB
ECHOROUK_OS_DOCUMENT_INTEL_JOB_PAYLOAD_TTL_SECONDS
ECHOROUK_OS_DOCUMENT_INTEL_OCR_ENABLED
ECHOROUK_OS_DOCUMENT_INTEL_OCR_FORCE
ECHOROUK_OS_DOCUMENT_INTEL_OCR_TIMEOUT_SECONDS
ECHOROUK_OS_DOCUMENT_INTEL_OCR_PER_PAGE_TIMEOUT_SECONDS
ECHOROUK_OS_DOCUMENT_INTEL_OCR_MAX_PAGES
ECHOROUK_OS_DOCUMENT_INTEL_OCR_DPI
ECHOROUK_OS_DOCUMENT_INTEL_OCR_TRIGGER_MIN_CHARS
ECHOROUK_OS_SCOUT_MAX_ARTICLE_AGE_HOURS
ECHOROUK_OS_SCOUT_MAX_ARTICLE_FUTURE_MINUTES
ECHOROUK_OS_SCOUT_REQUIRE_TIMESTAMP_FOR_AGGREGATOR
ECHOROUK_OS_SCOUT_REQUIRE_TIMESTAMP_FOR_ALL_SOURCES
ECHOROUK_OS_SCOUT_ALLOW_URL_DATE_FALLBACK
ECHOROUK_OS_SCOUT_INGEST_FILTERS_ENABLED
ECHOROUK_OS_SCOUT_CROSS_SOURCE_DEDUP_ENABLED
ECHOROUK_OS_SCOUT_CROSS_SOURCE_DEDUP_WINDOW_HOURS
ECHOROUK_OS_SCOUT_CROSS_SOURCE_PUBLISH_TOLERANCE_HOURS
ECHOROUK_OS_SCOUT_CROSS_SOURCE_TITLE_SIMILARITY_THRESHOLD
ECHOROUK_OS_SCOUT_CROSS_SOURCE_DEDUP_CANDIDATES_LIMIT
ECHOROUK_OS_QUALITY_CLAIM_SUPPORT_ENFORCEMENT_ENABLED
ECHOROUK_OS_QUALITY_CLAIM_SENSITIVE_THRESHOLD
ECHOROUK_OS_QUALITY_CLAIM_REQUIRE_NON_AGGREGATOR_SUPPORT
ECHOROUK_OS_QUEUE_BACKPRESSURE_RETRY_AFTER_SECONDS
ECHOROUK_OS_QUEUE_SLA_TARGET_MINUTES_DEFAULT
ECHOROUK_OS_QUEUE_SLA_TARGET_MINUTES_ROUTER
ECHOROUK_OS_QUEUE_SLA_TARGET_MINUTES_SCRIBE
ECHOROUK_OS_QUEUE_SLA_TARGET_MINUTES_QUALITY
ECHOROUK_OS_QUEUE_SLA_TARGET_MINUTES_SIMULATOR
ECHOROUK_OS_QUEUE_SLA_TARGET_MINUTES_MSI
ECHOROUK_OS_QUEUE_SLA_TARGET_MINUTES_LINKS
ECHOROUK_OS_QUEUE_SLA_TARGET_MINUTES_TRENDS
ECHOROUK_OS_QUEUE_SLA_TARGET_MINUTES_SCRIPTS
ECHOROUK_OS_QUEUE_SLA_FAILURE_RATE_THRESHOLD_PERCENT
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
REDIS_HOST
REDIS_PORT
REDIS_PASSWORD
REDIS_DB
GEMINI_API_KEY
GEMINI_MODEL_FLASH
GEMINI_MODEL_PRO
EMBEDDING_PROVIDER
EMBEDDING_MODEL_GEMINI
EMBEDDING_VECTOR_DIM
EMBEDDING_USE_REAL_FOR_CHUNKS
ECHOROUK_ARCHIVE_ENABLED
ECHOROUK_ARCHIVE_BASE_URL
ECHOROUK_ARCHIVE_SECTIONS
ECHOROUK_ARCHIVE_REQUEST_TIMEOUT_SECONDS
ECHOROUK_ARCHIVE_DELAY_MS
ECHOROUK_ARCHIVE_MAX_LISTING_PAGES_PER_RUN
ECHOROUK_ARCHIVE_MAX_ARTICLES_PER_RUN
ECHOROUK_ARCHIVE_MAX_LISTING_DEPTH
ECHOROUK_ARCHIVE_BACKFILL_INTERVAL_MINUTES
ECHOROUK_ARCHIVE_REFRESH_INTERVAL_MINUTES
ECHOROUK_ARCHIVE_REFRESH_LISTING_PAGES
ECHOROUK_ARCHIVE_REFRESH_ARTICLE_PAGES
ECHOROUK_ARCHIVE_RAG_ENABLED
ECHOROUK_ARCHIVE_RAG_LIMIT
YOUTUBE_DATA_API_KEY
YOUTUBE_TRENDS_ENABLED
GOOGLE_FACT_CHECK_API_KEY
DOCUMENT_INTEL_DOCLING_TIMEOUT_SECONDS
DOCUMENT_INTEL_DOCLING_MAX_SIZE_MB
DOCUMENT_INTEL_DOCLING_SKIP_FOR_AR
DOCUMENT_INTEL_MAX_UPLOAD_MB
DOCUMENT_INTEL_JOB_PAYLOAD_TTL_SECONDS
DOCUMENT_INTEL_OCR_ENABLED
DOCUMENT_INTEL_OCR_FORCE
DOCUMENT_INTEL_OCR_TIMEOUT_SECONDS
DOCUMENT_INTEL_OCR_PER_PAGE_TIMEOUT_SECONDS
DOCUMENT_INTEL_OCR_MAX_PAGES
DOCUMENT_INTEL_OCR_DPI
DOCUMENT_INTEL_OCR_TRIGGER_MIN_CHARS
TELEGRAM_BOT_TOKEN
TELEGRAM_CHANNEL_EDITORS
TELEGRAM_CHANNEL_ALERTS
SLACK_WEBHOOK_URL
MINIO_ENDPOINT
MINIO_ACCESS_KEY
MINIO_SECRET_KEY
MINIO_BUCKET
MINIO_USE_SSL
SCOUT_INTERVAL_MINUTES
TREND_RADAR_INTERVAL_MINUTES
ROUTER_BATCH_LIMIT
ROUTER_SOURCE_QUOTA
ROUTER_CANDIDATE_SOURCE_QUOTA
ROUTER_RULE_MIN_HITS
ROUTER_SKIP_AI_FOR_NON_LOCAL_AGGREGATOR
ROUTER_REJECT_FILTERS_ENABLED
ROUTER_AI_CALLS_PER_BATCH_CAP
AUTO_PIPELINE_ROUTER_BURST_MAX
AUTO_PIPELINE_ROUTER_BURST_BACKLOG_THRESHOLD
DEFER_NONCRITICAL_JOBS_WHEN_BACKLOG_HIGH
NONCRITICAL_BACKLOG_THRESHOLD
PROVIDER_PREFER_CONFIGURED_ONLY
PROVIDER_DAILY_BUDGET_USD
PROVIDER_PER_JOB_MAX_USD
PROVIDER_COST_ESTIMATE_GEMINI_USD
PROVIDER_QUEUE_TIER_SCRIBE
PROVIDER_QUEUE_TIER_QUALITY
PROVIDER_QUEUE_TIER_SIMULATOR
PROVIDER_QUEUE_TIER_ROUTER
AUTO_PIPELINE_ENABLED
AUTO_SCRIBE_ENABLED
PUBLISHED_MONITOR_ENABLED
PUBLISHED_MONITOR_INTERVAL_MINUTES
PUBLISHED_MONITOR_FEED_URL
PUBLISHED_MONITOR_LIMIT
PUBLISHED_MONITOR_LLM_ITEMS_LIMIT
PUBLISHED_MONITOR_FETCH_TIMEOUT
EDITORIAL_DIRECT_PUBLISH_ENABLED
EDITORIAL_DESK_INCLUDE_PRE_CANDIDATE
EDITORIAL_SENSITIVE_CATEGORIES
EDITORIAL_SENSITIVE_URGENCY_LEVELS
EDITORIAL_SENSITIVE_IMPORTANCE_THRESHOLD
PUBLISHED_MONITOR_ALERT_THRESHOLD
EVENT_REMINDERS_ENABLED
EVENT_REMINDERS_INTERVAL_MINUTES
DIGITAL_TEAM_AUTO_GENERATION_ENABLED
DIGITAL_TEAM_AUTO_GENERATION_INTERVAL_MINUTES
DIGITAL_TEAM_AUTO_GENERATION_HOURS_AHEAD
DIGITAL_TEAM_AUTO_INCLUDE_EVENTS
DIGITAL_TEAM_AUTO_INCLUDE_BREAKING
SCOUT_USE_FRESHRSS
FRESHRSS_FEED_URL
RSSBRIDGE_BASE_URL
RSSBRIDGE_ENABLED
FRESHRSS_BASE_URL
FRESHRSS_DB_NAME
FRESHRSS_DB_USER
FRESHRSS_DB_PASSWORD
FRESHRSS_DB_ROOT_PASSWORD
FRESHRSS_CRON_MIN
FRESHRSS_ADMIN_USER
FRESHRSS_ADMIN_PASSWORD
FRESHRSS_API_PASSWORD
FRESHRSS_ADMIN_EMAIL
TZ
MAX_RSS_SOURCES
RSS_FETCH_TIMEOUT
SCOUT_MAX_ARTICLE_AGE_HOURS
SCOUT_MAX_ARTICLE_FUTURE_MINUTES
SCOUT_REQUIRE_TIMESTAMP_FOR_AGGREGATOR
SCOUT_REQUIRE_TIMESTAMP_FOR_ALL_SOURCES
SCOUT_ALLOW_URL_DATE_FALLBACK
SCOUT_INGEST_FILTERS_ENABLED
SCOUT_CROSS_SOURCE_DEDUP_ENABLED
SCOUT_CROSS_SOURCE_DEDUP_WINDOW_HOURS
SCOUT_CROSS_SOURCE_PUBLISH_TOLERANCE_HOURS
SCOUT_CROSS_SOURCE_TITLE_SIMILARITY_THRESHOLD
SCOUT_CROSS_SOURCE_DEDUP_CANDIDATES_LIMIT
DEDUP_SIMILARITY_THRESHOLD
BREAKING_NEWS_URGENCY_THRESHOLD
TRUTH_SCORE_REJECT_THRESHOLD
TRUTH_SCORE_VERIFY_THRESHOLD
EDITORIAL_MIN_IMPORTANCE
EDITORIAL_REQUIRE_LOCAL_SIGNAL
QUALITY_CLAIM_SUPPORT_ENFORCEMENT_ENABLED
QUALITY_CLAIM_SENSITIVE_THRESHOLD
QUALITY_CLAIM_REQUIRE_NON_AGGREGATOR_SUPPORT
QUEUE_BACKPRESSURE_RETRY_AFTER_SECONDS
QUEUE_SLA_TARGET_MINUTES_DEFAULT
QUEUE_SLA_TARGET_MINUTES_ROUTER
QUEUE_SLA_TARGET_MINUTES_SCRIBE
QUEUE_SLA_TARGET_MINUTES_QUALITY
QUEUE_SLA_TARGET_MINUTES_SIMULATOR
QUEUE_SLA_TARGET_MINUTES_MSI
QUEUE_SLA_TARGET_MINUTES_LINKS
QUEUE_SLA_TARGET_MINUTES_TRENDS
QUEUE_SLA_TARGET_MINUTES_SCRIPTS
QUEUE_SLA_FAILURE_RATE_THRESHOLD_PERCENT
TTS_VOICE
TTS_RATE
TTS_PITCH
NEXT_PUBLIC_API_URL
NEXT_PUBLIC_FLOWER_URL
FLOWER_BASIC_AUTH_USER
FLOWER_BASIC_AUTH_PASSWORD
CORS_ORIGINS
```

## 9. Alembic Migration Filenames

```text
20260211_add_api_settings.py
20260211_add_constitution_tables.py
20260211_add_image_prompts.py
20260211_add_infographics.py
20260211_add_min_indexes.py
20260211_add_settings_audit.py
20260211_add_source_fields.py
20260211_add_source_slug.py
20260214_add_editorial_drafts.py
20260216_add_fingerprints_and_relations.py
20260216_add_knowledge_and_vectors.py
20260216_scribe_v2_statuses_and_workid.py
20260217_add_quality_reports.py
20260217_enforce_single_cluster_membership.py
20260217_fix_newsstatus_enum_case.py
20260217_m5_smart_editor.py
20260218_add_user_activity_logs.py
20260218_editorial_policy_gate_statuses.py
20260218_project_memory.py
20260219_add_msi_tables.py
20260219_msi_wl_alias_seed.py
20260219_sim_tables.py
20260221_competitor_xray_tables.py
20260221_media_logger_tables.py
20260222_link_intelligence_tables.py
20260222_m10_job_queue.py
20260222_m10_link_index_metadata.py
20260225_script_studio.py
20260225_story_idempotency_audit.py
20260225_story_item_constraints.py
20260226_script_status_failed.py
20260301_digital_team_module.py
20260301_event_memo_board.py
20260301_event_memo_sprint1.py
20260305_claim_support_tables.py
20260308_archive_crawl_tables.py
20260308_merge_archive_and_digital_heads.py
20260311_event_desk_phase3.py
20260312_digital_desk_phase2_3.py
20260317_document_intel_workspace.py
20260317_memory_context_upgrade.py
20260421_media_intelligence_layer.py
20260422_expand_article_original_url.py
20260422_mil_operator_actions.py
```

## 10. Frontend Page Routes

- `/agents`
- `/archive`
- `/competitor-xray`
- `/constitution`
- `/dashboard/metric/[metric]`
- `/dashboard`
- `/digital`
- `/editorial`
- `/events`
- `/help`
- `/how-editorial-os-works`
- `/login`
- `/memory`
- `/msi`
- `/news/[id]`
- `/news`
- `/newsroom-flow`
- `/`
- `/prompt-playbook`
- `/ready-publish/[workId]`
- `/scripts/[scriptId]`
- `/scripts`
- `/services/document-intel`
- `/services/editor`
- `/services/fact-check`
- `/services/media-logger`
- `/services/multimedia`
- `/services/seo`
- `/settings`
- `/simulator`
- `/sources`
- `/stories`
- `/team`
- `/today`
- `/trends`
- `/ux-insights`
- `/workspace-drafts`

## 11. Git Log (Last 15 Commits)

```text
d06eb8b **Title:** Secure Infrastructure and Resilient AI Services Implementation
d441a8a Align documentation with current backend and frontend behavior
7cbab2d Normalize validation errors and return 422 for invalid payloads
e3314ff Handle Pydantic validation errors as 422 responses
4ccc4c8 Add strict request validation for backend service payloads
f2005a4 Harden backend identity handling and reject client-supplied actor fields
c9742ca Secure sensitive backend routes and enforce RBAC
9f9f2a1 Add daily ops monitoring scheduler and snapshot
5142a61 Add system monitoring for DB, vectors, and app sections
47d2124 Fix social post list response type
7c640e1 Refocus digital coverage flow and add digital archive list
d205024 Generate multi-platform copies in one click
76b38d4 Refocus digital desk on copy generation only
c7a10b3 Add fast publish templates and quick-fill for digital team
10b7ef3 Add fast publish flow for digital team
```

## 12. Files Larger Than 100KB

- `backups/2026-04-11_13-35.tar.gz` | `2295595008` bytes
- `backups/backup_db_2026-04-14_1204.sql.gz` | `2148099992` bytes
- `backups/public_backup.sql.gz` | `2148099992` bytes
- `backup_db_2026-04-14_1142.sql.gz` | `2146455950` bytes
- `backup_pre_deploy_2026-04-14_1050.sql.gz` | `2145894538` bytes
- `backup_db_only_2026-04-14_1119.sql.gz` | `211025920` bytes
- `full_swarm_backup.tar.gz` | `13741738` bytes
- `frontend/.next/server/chunks/ssr/src_app_workspace-drafts_page_tsx_a5006b05._.js.map` | `2572427` bytes
- `frontend/.next/server/chunks/ssr/_bb9fd558._.js.map` | `1691109` bytes
- `frontend/.next/server/chunks/ssr/node_modules_next_dist_2e7de858._.js.map` | `796227` bytes
- `frontend/.next/server/chunks/[root-of-the-server]__206abf59._.js.map` | `732146` bytes
- `frontend/.next/server/chunks/ssr/[root-of-the-server]__ed7fd7ec._.js.map` | `696301` bytes
- `frontend/.next/server/chunks/ssr/node_modules_next_dist_esm_eedfc1fd._.js.map` | `583283` bytes
- `frontend/.next/server/chunks/ssr/node_modules_next_dist_c2965c68._.js.map` | `563536` bytes
- `frontend/.next/static/chunks/2f2471b224901ea7.js` | `557807` bytes
- `frontend/.next/standalone/.next/server/chunks/ssr/src_app_workspace-drafts_page_tsx_a5006b05._.js` | `553575` bytes
- `frontend/.next/server/chunks/ssr/src_app_workspace-drafts_page_tsx_a5006b05._.js` | `553575` bytes
- `frontend/.next/build/chunks/node_modules_fe693df6._.js.map` | `372684` bytes
- `frontend/.next/static/chunks/f1528462f0ce4021.js` | `338640` bytes
- `frontend/.next/standalone/.next/server/chunks/ssr/_bb9fd558._.js` | `337786` bytes
- `frontend/.next/server/chunks/ssr/_bb9fd558._.js` | `337786` bytes
- `frontend/.next/server/chunks/ssr/node_modules_next_dist_70ed294b._.js.map` | `307103` bytes
- `frontend/package-lock.json` | `281247` bytes
- `frontend/src/app/workspace-drafts/page.tsx` | `264554` bytes
- `frontend/.next/server/chunks/ssr/src_app_digital_page_tsx_7ca3e971._.js.map` | `261915` bytes
- `frontend/.next/standalone/.next/server/chunks/ssr/[root-of-the-server]__ed7fd7ec._.js` | `256993` bytes
- `frontend/.next/server/chunks/ssr/[root-of-the-server]__ed7fd7ec._.js` | `256993` bytes
- `frontend/.next/build/chunks/node_modules_fe693df6._.js` | `256154` bytes
- `frontend/.next/static/chunks/aee6c7720838f8a2.js` | `224413` bytes
- `frontend/.next/standalone/.next/server/chunks/[root-of-the-server]__206abf59._.js` | `187611` bytes
- `frontend/.next/server/chunks/[root-of-the-server]__206abf59._.js` | `187611` bytes
- `frontend/src/app/digital/page.tsx` | `172780` bytes
- `frontend/.next/server/chunks/ssr/src_3877a5ae._.js.map` | `171018` bytes
- `frontend/.next/cache/.tsbuildinfo` | `165705` bytes
- `frontend/.next/server/chunks/ssr/[root-of-the-server]__a53e08cd._.js.map` | `153653` bytes
- `frontend/.next/standalone/.next/server/chunks/ssr/node_modules_next_dist_2e7de858._.js` | `149274` bytes
- `frontend/.next/server/chunks/ssr/node_modules_next_dist_2e7de858._.js` | `149274` bytes
- `backend/app/api/routes/editorial.py` | `125608` bytes
- `frontend/.next/static/chunks/1615b6e9eabd6d90.css` | `125030` bytes
- `frontend/.next/server/chunks/ssr/_0efddc1b._.js.map` | `116891` bytes
- `frontend/.next/static/chunks/a6dad97d9634a72d.js.map` | `115717` bytes
- `frontend/.next/static/chunks/a6dad97d9634a72d.js` | `112594` bytes
- `frontend/.next/static/chunks/eb739c8670e14f70.js` | `111078` bytes
- `frontend/.next/server/chunks/ssr/src_app_stories_page_tsx_cdbe2e30._.js.map` | `110508` bytes
- `frontend/src/lib/api.ts` | `106878` bytes
- `frontend/.next/server/chunks/ssr/node_modules_next_920e7746._.js.map` | `104401` bytes
- `frontend/.next/static/chunks/ec5f3aba5dce1917.js` | `102713` bytes

## 13. Files Containing `groq`

- `groq` has been fully removed from executable backend code, frontend UI, and operational docs.
- Historical reports are intentionally excluded from this statement:
  - `docs/PLATFORM_DETAILED_REPORT_2026-02-22.md`
  - `STUDY_REPORT.md`
- Current audit target paths show no active `groq` / `GROQ` references in:
  - `backend/`
  - `frontend/src/`
  - `README.md`
  - operational docs under `docs/`

## 14. Direct `article.status =` Assignments

```text
backend\tests\test_editorial_chief_decision.py:124:        article.status = target_status
backend\tests\test_state_transition_service.py:47:    assert locked_article.status == NewsStatus.APPROVED_HANDOFF
backend\app\agents\router.py:296:        article.status = locked_article.status
backend\app\agents\scribe.py:136:            article.status = locked_article.status
backend\app\api\routes\dashboard.py:1014:            with_reservations = article.status == NewsStatus.APPROVAL_REQUEST_WITH_RESERVATIONS
backend\app\api\routes\editorial.py:926:    article.status = locked_article.status
backend\app\api\routes\editorial.py:1456:        was_rejected = article.status == NewsStatus.REJECTED
backend\app\services\state_transition_service.py:80:        article.status = target
```

Current hardened interpretation:

- All remaining production `article.status` writes now go through `state_transition_service`.
- `backend/app/services/state_transition_service.py:80` is the canonical state-machine write point.
- `router.py`, `scribe.py`, and `editorial.py` only copy back `locked_article.status` after calling `state_transition_service.transition_article(...)`.
- The old direct archive write in `backend/app/services/echorouk_archive_service.py` has been removed.
- Remaining non-service hits are test-only assignments or status comparisons, not bypasses.

## 15. Password / Secret Pattern Hits in `docker-compose.yml`

These are secret-related lines or required secret references only. No actual runtime secret values are included below.

```text
69:     command: celery -A app.queue.celery_app:celery_app flower --port=5555 --basic-auth=${FLOWER_BASIC_AUTH_USER?FLOWER_BASIC_AUTH_USER is required}:${FLOWER_BASIC_AUTH_PASSWORD?FLOWER_BASIC_AUTH_PASSWORD is required}
111:       POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
134:       REDIS_PASSWORD: ${REDIS_PASSWORD?REDIS_PASSWORD is required}
154:       MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
174:       MYSQL_ROOT_PASSWORD: ${FRESHRSS_DB_ROOT_PASSWORD?FRESHRSS_DB_ROOT_PASSWORD is required}
177:       MYSQL_PASSWORD: ${FRESHRSS_DB_PASSWORD?FRESHRSS_DB_PASSWORD is required}
203:         --db-password ${FRESHRSS_DB_PASSWORD?FRESHRSS_DB_PASSWORD is required}
210:         --api-password=${FRESHRSS_API_PASSWORD?FRESHRSS_API_PASSWORD is required}
213:         --password=${FRESHRSS_ADMIN_PASSWORD?FRESHRSS_ADMIN_PASSWORD is required}
```

## 16. Security Hardening Applied 2026-04-23

Fixed findings applied in code/config and verified during deployment:

1. `GET /api/v1/news/` now requires authentication.
2. `GET /api/v1/news/breaking/latest` now requires authentication.
3. `GET /api/v1/news/candidates/pending` now requires authentication.
4. `GET /api/v1/news/insights` now requires authentication.
5. `GET /api/v1/news/search/semantic` now requires authentication.
6. Direct archive-state bypass was removed from `echorouk_archive_service.py`.
7. Redis now requires `REDIS_PASSWORD`.
8. Redis is now bound to `127.0.0.1:6380` instead of all interfaces.
9. Flower now requires `FLOWER_BASIC_AUTH_USER`.
10. Flower now requires `FLOWER_BASIC_AUTH_PASSWORD`.
11. FreshRSS MariaDB root password now requires `FRESHRSS_DB_ROOT_PASSWORD`.
12. FreshRSS MariaDB user password now requires `FRESHRSS_DB_PASSWORD`.
13. FreshRSS install flow now requires `FRESHRSS_DB_PASSWORD` instead of using a weak default.
14. FreshRSS API password now requires `FRESHRSS_API_PASSWORD`.
15. FreshRSS admin password now requires `FRESHRSS_ADMIN_PASSWORD`.
16. FreshRSS healthcheck was hardened and now uses a `php`-based HTTP probe.
17. RSS-Bridge healthcheck was hardened and now uses a `php`-based HTTP probe.
18. `GROQ_API_KEY` was removed from the frontend settings UI.
19. `GROQ_API_KEY` was removed from the new-server deploy checklist.
20. `backend/app/schemas/__init__.py` now documents Gemini-only analysis output.
21. README Cost-Efficiency row no longer references Groq.
22. README Scribe model routing no longer references Groq.
23. README no longer suggests an optional Groq API key.
24. README AI environment-variable summary no longer lists `GROQ_API_KEY`.
25. README cost-analysis table no longer lists Groq as the writing provider.
26. `docs/agents.md` now documents Gemini Flash for rewriting.
27. `docs/agents.md` no longer documents Groq fallback routing.
28. `docs/agents.md` cost note no longer references Groq free tier coverage.
29. `docs/PROVIDER_ROUTING_COST.md` no longer documents `PROVIDER_COST_ESTIMATE_GROQ_USD`.
30. `docs/PROVIDER_ROUTING_COST.md` no longer recommends `groq` for low-tier routing.
31. `docs/M10_ASYNC_ARCHITECTURE.md` no longer references `provider_weight_groq`.
32. `docs/TROUBLESHOOTING_PLAYBOOK.md` no longer tells operators to configure `GROQ_API_KEY`.
33. `NEXT_PUBLIC_BREAKING_TTL_MINUTES` is now declared for frontend build/runtime in Docker and Compose.

## Audit Notes

- `frontend/.next` is present in the workspace and inflates the directory and large-file inventory.
- `backend/app/api/routes/editorial.py` is one of the largest backend route files and should be treated as a prime audit target.
- Production `article.status` writes are now centralized through `state_transition_service`; remaining direct hits are tests, comparisons, or status propagation from a state-machine-locked instance.
- Compose file now requires runtime secrets for Redis, Flower, and FreshRSS instead of relying on weak placeholder defaults.
- FreshRSS and RSS-Bridge healthchecks are php-based because `curl` and `wget` were not available inside the upstream images.
- Active code, UI, and operational docs no longer contain `groq` references; only historical reports may still mention it.

