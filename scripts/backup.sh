#!/usr/bin/env bash
# Бэкап PostgreSQL. Почему просто: для демо достаточно cron-совместимого скрипта.
set -euo pipefail

TS=$(date +%Y%m%d_%H%M%S)
OUT_DIR=${1:-./backups}
mkdir -p "$OUT_DIR"
PGURL=${DATABASE_URL:-"postgresql://postgres:postgres@localhost:5432/appdb"}

pg_dump "$PGURL" > "$OUT_DIR/backup_$TS.sql"
echo "Backup saved to $OUT_DIR/backup_$TS.sql"
