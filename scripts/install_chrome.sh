#!/usr/bin/env bash
#
# Download a matched, pinned Chrome browser + chromedriver pair into the
# project-local `.chrome/` directory. This is the real browser the app uses to
# drive the site; pinning it guarantees the browser and driver versions stay in
# sync and that Chrome never auto-updates out from under the driver.
#
# Works on Linux (including WSL2) and macOS. Binaries come from Google's
# official pinned-version Chrome distribution
# (https://googlechromelabs.github.io/chrome-for-testing/).
#
# Usage:
#   scripts/install_chrome.sh [VERSION]
#
# VERSION may be:
#   - a channel name:  Stable | Beta | Dev | Canary
#   - a milestone:     140            (latest build of that major version)
#   - a full version:  140.0.7339.207
#
# When omitted, the script reads the `.chrome-version` file at the repo root,
# falling back to "Stable".

set -euo pipefail

# --- Locate repo root ------------------------------------------------------- #
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CHROME_DIR="${REPO_ROOT}/.chrome"

# --- Resolve the requested version spec ------------------------------------- #
VERSION_SPEC="${1:-}"
if [[ -z "${VERSION_SPEC}" ]]; then
    if [[ -f "${REPO_ROOT}/.chrome-version" ]]; then
        VERSION_SPEC="$(tr -d '[:space:]' < "${REPO_ROOT}/.chrome-version")"
    fi
fi
VERSION_SPEC="${VERSION_SPEC:-Stable}"

# --- Pick a Python interpreter (used only to parse the CfT JSON) ------------ #
PYTHON="$(command -v python3 || command -v python || true)"
if [[ -z "${PYTHON}" ]]; then
    echo "error: python3 is required to parse the Chrome download API." >&2
    exit 1
fi

# --- Detect the download platform string ------------------------------------ #
case "$(uname -s)" in
    Linux)  PLATFORM="linux64" ;;
    Darwin)
        if [[ "$(uname -m)" == "arm64" ]]; then PLATFORM="mac-arm64"; else PLATFORM="mac-x64"; fi
        ;;
    *)
        echo "error: unsupported OS '$(uname -s)'. Supported: Linux (incl. WSL), macOS." >&2
        exit 1
        ;;
esac

echo "Resolving pinned Chrome version '${VERSION_SPEC}' for platform '${PLATFORM}'..."

# Resolve the full version and the chrome/chromedriver download URLs.
# Prints three lines: <full_version> <chrome_url> <chromedriver_url>
read -r FULL_VERSION CHROME_URL DRIVER_URL < <(
    "${PYTHON}" - "${VERSION_SPEC}" "${PLATFORM}" <<'PY'
import json, sys, urllib.request

spec, platform = sys.argv[1], sys.argv[2]
BASE = "https://googlechromelabs.github.io/chrome-for-testing"


def fetch(name):
    with urllib.request.urlopen(f"{BASE}/{name}", timeout=30) as resp:
        return json.load(resp)


def urls_for(entry):
    out = {}
    for kind in ("chrome", "chromedriver"):
        for item in entry["downloads"].get(kind, []):
            if item["platform"] == platform:
                out[kind] = item["url"]
    return out


channels = {"stable", "beta", "dev", "canary"}
if spec.lower() in channels:
    data = fetch("last-known-good-versions-with-downloads.json")
    entry = data["channels"][spec.capitalize()]
elif spec.isdigit():  # milestone / major version
    data = fetch("latest-versions-per-milestone-with-downloads.json")
    entry = data["milestones"].get(spec)
    if entry is None:
        sys.exit(f"error: no pinned Chrome build for milestone {spec}")
else:  # full version
    data = fetch("known-good-versions-with-downloads.json")
    entry = next((v for v in data["versions"] if v["version"] == spec), None)
    if entry is None:
        sys.exit(f"error: version {spec} not found in known-good-versions")

urls = urls_for(entry)
if "chrome" not in urls or "chromedriver" not in urls:
    sys.exit(f"error: no {platform} download for version {entry['version']}")

print(entry["version"], urls["chrome"], urls["chromedriver"])
PY
)

echo "Resolved version: ${FULL_VERSION}"

# --- Skip download if already installed ------------------------------------- #
if [[ -f "${CHROME_DIR}/VERSION" && "$(cat "${CHROME_DIR}/VERSION")" == "${FULL_VERSION}" ]]; then
    echo "Chrome ${FULL_VERSION} already installed in ${CHROME_DIR}; nothing to do."
    echo "  (delete ${CHROME_DIR} to force a re-download)"
    exit 0
fi

# --- Download + extract ----------------------------------------------------- #
download() {
    local url="$1" dest="$2"
    if command -v curl >/dev/null 2>&1; then
        curl -fSL --retry 3 -o "${dest}" "${url}"
    elif command -v wget >/dev/null 2>&1; then
        wget -O "${dest}" "${url}"
    else
        echo "error: need either curl or wget to download files." >&2
        exit 1
    fi
}

if ! command -v unzip >/dev/null 2>&1; then
    echo "error: 'unzip' is required to extract the archives." >&2
    exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

echo "Downloading chrome..."
download "${CHROME_URL}" "${TMP_DIR}/chrome.zip"
echo "Downloading chromedriver..."
download "${DRIVER_URL}" "${TMP_DIR}/chromedriver.zip"

echo "Extracting into ${CHROME_DIR}..."
rm -rf "${CHROME_DIR}"
mkdir -p "${CHROME_DIR}"
unzip -q "${TMP_DIR}/chrome.zip" -d "${CHROME_DIR}"
unzip -q "${TMP_DIR}/chromedriver.zip" -d "${CHROME_DIR}"

CHROME_BIN="${CHROME_DIR}/chrome-${PLATFORM}/chrome"
DRIVER_BIN="${CHROME_DIR}/chromedriver-${PLATFORM}/chromedriver"
chmod +x "${CHROME_BIN}" "${DRIVER_BIN}"

echo "${FULL_VERSION}" > "${CHROME_DIR}/VERSION"

# --- Report ----------------------------------------------------------------- #
echo
echo "Installed pinned Chrome ${FULL_VERSION}:"
echo "  chrome:       ${CHROME_BIN}"
echo "  chromedriver: ${DRIVER_BIN}"
echo
"${DRIVER_BIN}" --version || true
