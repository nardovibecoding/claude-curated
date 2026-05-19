#!/usr/bin/env bash
set -euo pipefail

NOTES_DIR="${NOTES_DIR:-$HOME/notes}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/notes-backup}"

mkdir -p "$BACKUP_DIR"
rsync -a --delete "$NOTES_DIR"/ "$BACKUP_DIR"/
echo "Backed up notes from $NOTES_DIR to $BACKUP_DIR"
