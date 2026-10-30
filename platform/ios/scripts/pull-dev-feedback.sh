#!/usr/bin/env bash
# Copies Debug-build feedback (Documents/DevFeedback in the app container) from a
# connected iPhone into platform/ios/dev-feedback/, which is git-ignored.
#
# Usage:  bash scripts/pull-dev-feedback.sh
# Env:    DEVICE=<devicectl identifier or name>   BUNDLE_ID=<bundle identifier>
#
# Requires macOS with Xcode 15 or later (xcrun devicectl). The iPhone must be
# paired with this Mac, unlocked, and running a Debug build of the app.
set -euo pipefail

cd "$(dirname "$0")/.."
project=$(find . -maxdepth 1 -name '*.xcodeproj' | head -n 1)
[ -n "$project" ] || { echo "No .xcodeproj in $(pwd)" >&2; exit 1; }

bundle_id=${BUNDLE_ID:-$(xcodebuild -project "$project" -configuration Debug -showBuildSettings 2>/dev/null \
  | awk -F' = ' '/^ *PRODUCT_BUNDLE_IDENTIFIER = / { print $2; exit }')}
[ -n "$bundle_id" ] || { echo "Could not read the bundle ID; set BUNDLE_ID." >&2; exit 1; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

device=${DEVICE:-}
if [ -z "$device" ]; then
  xcrun devicectl list devices --json-output "$tmp/devices.json" >/dev/null
  device=$(python3 - "$tmp/devices.json" <<'PY'
import json, sys
for d in json.load(open(sys.argv[1]))["result"]["devices"]:
    hw, conn = d.get("hardwareProperties", {}), d.get("connectionProperties", {})
    if hw.get("platform") == "iOS" and conn.get("pairingState") == "paired" \
            and conn.get("tunnelState") != "unavailable":
        print(d["identifier"])
        break
PY
)
fi
[ -n "$device" ] || { echo "No paired iPhone found. Connect and unlock it, or set DEVICE." >&2; exit 1; }

echo "Pulling $bundle_id from $device"
if ! xcrun devicectl device copy from --device "$device" \
    --domain-type appDataContainer --domain-identifier "$bundle_id" \
    --source Documents/DevFeedback --destination "$tmp/out" >/dev/null; then
  echo "Copy failed. Fallback: Xcode > Window > Devices and Simulators > select the app >" >&2
  echo "gear menu > Download Container, then copy AppData/Documents/DevFeedback to dev-feedback/." >&2
  exit 1
fi

marker=$(find "$tmp/out" \( -name events.jsonl -o -name reports \) -print -quit)
[ -n "$marker" ] || { echo "No feedback found on the device yet." >&2; exit 1; }

# Merge into the local archive; never delete what is already on the Mac, so
# feedback survives the app being deleted or the phone being reset.
src=$(dirname "$marker")
mkdir -p dev-feedback/reports
if [ -d "$src/reports" ]; then
  cp -n "$src"/reports/* dev-feedback/reports/ 2>/dev/null || true
fi
for log in events.jsonl answers.jsonl; do
  [ -f "$src/$log" ] || continue
  touch "dev-feedback/$log"
  awk '!seen[$0]++' "dev-feedback/$log" "$src/$log" > "$tmp/$log"
  mv "$tmp/$log" "dev-feedback/$log"
done
count=$(find dev-feedback/reports -name '*.json' | wc -l | tr -d ' ')
echo "Archive now holds $count report(s) in $(pwd)/dev-feedback"
