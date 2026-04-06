#!/usr/bin/env bash
# Update Formula/zpace.rb resource blocks and version locally.
#
# Usage:
#   ./scripts/update-formula.sh [version]
#
# If version is omitted, the latest version on PyPI is used.
# Requires: uv, curl, jq

set -euo pipefail

FORMULA="Formula/zpace.rb"
SCRIPT=".github/scripts/update_resources.py"

# Resolve repo root relative to this script
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Determine version
if [ -n "${1:-}" ]; then
  VERSION="$1"
else
  VERSION=$(curl -sSf https://pypi.org/pypi/zpace/json | jq -r '.info.version')
fi

echo "Updating formula to zpace ${VERSION} ..."

# Fetch sdist URL and sha256 from PyPI
ZPACE_INFO=$(curl -sSf "https://pypi.org/pypi/zpace/${VERSION}/json")
ZPACE_URL=$(echo "$ZPACE_INFO" | jq -r '.urls[] | select(.packagetype == "sdist") | .url')
ZPACE_SHA=$(echo "$ZPACE_INFO" | jq -r '.urls[] | select(.packagetype == "sdist") | .digests.sha256')

[ -n "$ZPACE_URL" ]  || { echo "Could not find sdist URL for zpace ${VERSION}"; exit 1; }
[ -n "$ZPACE_SHA" ]  || { echo "Could not find sha256 for zpace ${VERSION}"; exit 1; }

# Update URL and sha256 in formula (anchored to url line to avoid matching resource URLs)
sed -i.bak "/^  url/s|zpace-[0-9.]*\.tar\.gz|zpace-${VERSION}.tar.gz|" "$FORMULA"
# Only replace the first sha256 line (the package itself, not resources)
awk -v sha="$ZPACE_SHA" '
  !done && /^  sha256 "/ { print "  sha256 \"" sha "\""; done=1; next }
  { print }
' "$FORMULA" > "${FORMULA}.tmp" && mv "${FORMULA}.tmp" "$FORMULA"
rm -f "${FORMULA}.bak"

echo "Running homebrew-pypi-poet to regenerate resource blocks ..."
python3 "$SCRIPT" zpace "$FORMULA" "$VERSION"

echo ""
echo "Formula updated. Review the diff:"
git diff "$FORMULA"
