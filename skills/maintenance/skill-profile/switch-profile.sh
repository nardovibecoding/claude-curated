#!/bin/bash
# Copyright (c) 2026 Nardo. AGPL-3.0 — see LICENSE
PROFILE="${1:-all}"
SKILLS_DIR="$HOME/.claude/skills"
BACKUP_DIR="$HOME/.claude/skills-master"

# First time: backup master
if [ ! -d "$BACKUP_DIR" ]; then
    cp -r "$SKILLS_DIR" "$BACKUP_DIR"
fi

# Define profiles
case "$PROFILE" in
    all)
        # Re-enable everything from master
        for d in "$BACKUP_DIR"/*/; do
            name=$(basename "$d")
            if [ -f "$BACKUP_DIR/$name/SKILL.md" ] && [ -f "$SKILLS_DIR/$name/SKILL.md.disabled" ]; then
                mv "$SKILLS_DIR/$name/SKILL.md.disabled" "$SKILLS_DIR/$name/SKILL.md"
            fi
        done
        echo "Profile: ALL"
        ;;
    coding)
        KEEP="investigate review ship critic dependency-tracker plan-eng-review systematic-debugging build eli5"
        ;;
    outreach)
        KEEP="debate content-humanizer eli5 office-hours"
        ;;
    minimal)
        KEEP="chatid remind system-check home eli5"
        ;;
    *)
        echo "Unknown: $PROFILE (use: all|coding|outreach|minimal)"
        exit 1
        ;;
esac

if [ "$PROFILE" != "all" ]; then
    # Disable all custom skills
    for d in "$SKILLS_DIR"/*/; do
        name=$(basename "$d")
        [ -f "$d/SKILL.md" ] && mv "$d/SKILL.md" "$d/SKILL.md.disabled" 2>/dev/null
    done

    # Enable profile skills
    for skill in $KEEP; do
        if [ -f "$SKILLS_DIR/$skill/SKILL.md.disabled" ]; then
            mv "$SKILLS_DIR/$skill/SKILL.md.disabled" "$SKILLS_DIR/$skill/SKILL.md"
        fi
    done

    enabled=$(find "$SKILLS_DIR" -name "SKILL.md" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | wc -l | tr -d ' ')
    echo "Profile: $PROFILE — $enabled skills active"
fi
