#!/usr/bin/env bash
# Task 10.3HD: zero downtime proof.
# Sends 2 to 3 requests every 0.2 seconds to the PUBLIC site and shows, once a
# second, which colour answered and how many requests failed.
#
# Usage:  ./scripts/bluegreen-traffic.sh <public-ip> [seconds]
# Optional: export TOKEN=<jwt> first to also call the real /courses API.
# Stop it any time with Ctrl+C, it prints the final result.

IP="${1:?Usage: $0 <public-ip> [seconds]}"
RUN_FOR="${2:-600}"

TOTAL=0
FAILED=0
API_5XX=0
START=$(date +%s)
END=$((START + RUN_FOR))
LAST_PRINT=0

colour_of() {
  sed -n 's/.*"colour":"\([a-z]*\)".*/\1/p' "$1"
}

summary() {
  echo
  echo "=================================================="
  echo " Requests sent : $TOTAL"
  echo " Failed        : $FAILED   (anything that was not HTTP 200)"
  [ -n "${TOKEN:-}" ] && echo " API 5xx       : $API_5XX"
  echo "=================================================="
  exit 0
}
trap summary INT TERM

echo "time      frontend  course-service  requests  failed  api_5xx"

while [ "$(date +%s)" -lt "$END" ]; do
  C1=$(curl -s -o /tmp/bg_colour.json -w "%{http_code}" --max-time 2 "http://$IP/colour")
  C2=$(curl -s -o /tmp/bg_health.json -w "%{http_code}" --max-time 2 "http://$IP/api/courses/health")
  TOTAL=$((TOTAL + 2))
  [ "$C1" = "200" ] || FAILED=$((FAILED + 1))
  [ "$C2" = "200" ] || FAILED=$((FAILED + 1))

  if [ -n "${TOKEN:-}" ]; then
    C3=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 \
      -H "Authorization: Bearer $TOKEN" "http://$IP/api/courses/courses")
    TOTAL=$((TOTAL + 1))
    case "$C3" in
      200) ;;
      5*) FAILED=$((FAILED + 1)); API_5XX=$((API_5XX + 1)) ;;
      *) FAILED=$((FAILED + 1)) ;;
    esac
  fi

  NOW=$(date +%s)
  if [ "$NOW" -ne "$LAST_PRINT" ]; then
    printf "%s  %-8s  %-14s  %-8s  %-6s  %s\n" \
      "$(date +%H:%M:%S)" "$(colour_of /tmp/bg_colour.json)" "$(colour_of /tmp/bg_health.json)" \
      "$TOTAL" "$FAILED" "$API_5XX"
    LAST_PRINT=$NOW
  fi

  sleep 0.2
done

summary
