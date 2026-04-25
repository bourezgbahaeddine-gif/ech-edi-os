#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if command -v rg >/dev/null 2>&1; then
  RG_BIN="rg"
elif command -v rg.exe >/dev/null 2>&1; then
  RG_BIN="rg.exe"
else
  echo "ripgrep (rg) is required to run this check." >&2
  exit 2
fi

EXCLUDES=(
  --glob '!frontend/node_modules/**'
  --glob '!frontend/.next/**'
  --glob '!backups/**'
  --glob '!*.backup*'
  --glob '!.git/**'
  --glob '!docs/SESSION_*'
  --glob '!SESSION_*'
  --glob '!docs/SESSION_HANDOFF_*'
  --glob '!docs/SESSION_CHECKPOINT_*'
  --glob '!docs/DEPLOY_RUNBOOK_LOCAL_SERVER_AR.md'
  --glob '!docs/NEW_SERVER_DEPLOY_CHECKLIST_2026-04-20.md'
  --glob '!docs/OPERATIONS_QUICK_COMMANDS.md'
  --glob '!docs/BRAND_GUIDE.md'
  --glob '!docs/PLATFORM_DETAILED_REPORT_2026-02-22.md'
  --glob '!scripts/check_brand_identity.sh'
  --glob '!SECURITY_HARDENING_CHANGELOG_*'
)

legacy_patterns=(
  'Echorouk Swarm'
  'EchoroukSwarm'
  'Smart Newsroom Platform'
  'Intelligent Newsroom Platform'
  'Newsroom Platform'
  'منصة غرفة الأخبار الذكية'
  'ech-swarm'
  'echorouk-swarm'
)

failed=0

for pattern in "${legacy_patterns[@]}"; do
  if "$RG_BIN" -n -S "${EXCLUDES[@]}" "$pattern" .; then
    failed=1
  fi
done

if "$RG_BIN" -n -P "${EXCLUDES[@]}" '(?<!Echorouk )Editorial OS' \
  README.md AGENT_ONBOARDING.md PROJECT_KNOWLEDGE_BASE.md docs backend frontend scripts docker-compose.yml .env.example; then
  failed=1
fi

if [[ "$failed" -ne 0 ]]; then
  echo "Brand identity check failed: legacy naming is still present." >&2
  exit 1
fi

echo "Brand identity check passed."
