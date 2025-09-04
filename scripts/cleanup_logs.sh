#!/usr/bin/env bash
# Очистка старых логов, оставляем последние N дней.
set -euo pipefail
DIR=${1:-./logs}
DAYS=${2:-7}
find "$DIR" -type f -mtime +$DAYS -print -delete
