#!/usr/bin/env bash
set -euo pipefail

probe_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
report=$1
full_log=$(mktemp)
trap 'rm -f -- "$full_log"' EXIT

status=0
timeout --kill-after=8s 330s xvfb-run -a ./gradlew --no-daemon --console=plain --max-workers=2 \
  -I "$probe_dir/world.gradle" -PtestBossRegressions runClient >"$full_log" 2>&1 || status=$?

if [[ "$status" == 0 ]]; then
  for check in dust_sprite dragon_landing_ik; do
    if ! grep -Fq "FALA_BOSS_SMOKE $check PASS" "$full_log"; then
      printf 'Missing boss smoke result: %s\n' "$check" >>"$full_log"
      status=1
    fi
  done
fi

{
  printf 'Boss smoke exit %s\n' "$status"
  awk '
    /Preparing spawn area:/ {
      sub(/.*Preparing spawn area: /, "")
      if ($0 != previous) print "Spawn progress: " $0
      previous = $0
    }
    /FALA_WORLD_SMOKE|FALA_BOSS_SMOKE|BUILD (FAILED|SUCCESSFUL)|Timeout loading world/ { print }
  ' "$full_log" | tail -30
  if [[ "$status" != 0 ]]; then
    grep -E 'AssertionError|Exception|Caused by:|\[ERROR\]|What went wrong|^> Task .*FAILED|Missing boss smoke result' \
      "$full_log" | tail -18 || tail -10 "$full_log"
  fi
} >"$report"
cat "$report"
exit "$status"
