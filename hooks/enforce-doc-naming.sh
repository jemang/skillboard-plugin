#!/bin/bash
# PreToolUse guard for Write: enforce the .doc/ plan/design naming convention
# YYYY-MM-DD-NN-topic-(plan|design).md. Plan-mode auto-saves (plansDirectory)
# land with a random slug; this blocks the first write so the rename happens
# before the wrong name ever hits disk, instead of after.

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

[ -z "$file_path" ] && exit 0

case "$file_path" in
  */.doc/*.md) ;;
  *) exit 0 ;;
esac

basename_f=$(basename "$file_path")

if [[ "$basename_f" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-.+-(plan|design)\.md$ ]]; then
  exit 0
fi

doc_dir=$(dirname "$file_path")
today=$(date +%Y-%m-%d)
existing_count=$(ls "$doc_dir"/"$today"-*.md 2>/dev/null | wc -l | tr -d ' ')
nn=$(printf "%02d" $((existing_count + 1)))

reason="File '$basename_f' doesn't follow the .doc/ naming convention: YYYY-MM-DD-NN-topic-(plan|design).md. Today is $today, NN should be $nn ($existing_count existing $today-*.md docs already in $doc_dir). Rename to something like $today-$nn-<topic>-plan.md (or -design.md for a spec) before writing."

jq -n --arg reason "$reason" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $reason}}'
