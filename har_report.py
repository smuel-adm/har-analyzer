#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

#
# Validate command line
#
if len(sys.argv) < 2:
    print(
        f"Usage: {Path(sys.argv[0]).name} <file.har>\n"
        "\n"
        "Example:\n"
        "    python har_report.py GOOD.har\n"
        "    python har_report.py BAD.har",
        file=sys.stderr,
    )
    sys.exit(1)

HAR_FILE = Path(sys.argv[1])

if not HAR_FILE.exists():
    print(
        f"ERROR: File not found: {HAR_FILE}",
        file=sys.stderr,
    )
    sys.exit(2)

if not HAR_FILE.is_file():
    print(
        f"ERROR: Not a file: {HAR_FILE}",
        file=sys.stderr,
    )
    sys.exit(3)


def get_host(url):
    try:
        return urlparse(url).hostname.lower()
    except Exception:
        return ""


#
# Load HAR
#
try:
    with open(HAR_FILE, encoding="utf-8") as f:
        har = json.load(f)

    entries = har["log"]["entries"]

except json.JSONDecodeError as ex:
    print(
        f"ERROR: Invalid JSON/HAR file:\n{HAR_FILE}\n\n{ex}",
        file=sys.stderr,
    )
    sys.exit(4)

except KeyError:
    print(
        f"ERROR: File does not appear to be a valid HAR file:\n{HAR_FILE}",
        file=sys.stderr,
    )
    sys.exit(5)

except Exception as ex:
    print(
        f"ERROR: Unable to open HAR file:\n{HAR_FILE}\n\n{ex}",
        file=sys.stderr,
    )
    sys.exit(6)


dns_values = []
tcp_values = []
ssl_values = []

ias_response = []
okta_response = []
callback_response = []

launchpad_start = None
tiles_finished = None

for e in entries:
    url = e["request"]["url"]
    host = get_host(url)

    timings = e.get("timings", {})

    dns = timings.get("dns", -1)
    connect = timings.get("connect", -1)
    ssl = timings.get("ssl", -1)
    wait = timings.get("wait", -1)

    status = e["response"].get("status", 0)

    #
    # DNS / TCP / TLS
    #
    if dns > 0:
        dns_values.append(dns)

    if connect > 0:
        if ssl > 0:
            tcp_values.append(connect - ssl)
        else:
            tcp_values.append(connect)

    if ssl > 0:
        ssl_values.append(ssl)

    #
    # SAP IAS
    #
    if "accounts.ondemand.com" in host:
        if wait > 0:
            ias_response.append(wait)

    #
    # Okta
    #
    if "okta.com" in host or "okta-emea.com" in host:
        if wait > 0:
            okta_response.append(wait)

    #
    # Launchpad callback
    #
    if (
        "login/callback" in url.lower()
        or "/saml/sso/" in url.lower()
        or "/oauth/authorize" in url.lower()
    ):
        if wait > 0:
            callback_response.append(wait)

    #
    # Launchpad start page
    #
    if launchpad_start is None and "launchpad.cfapps" in host and "site?" in url:
        launchpad_start = e["startedDateTime"]

    #
    # Tile services
    #
    if "launchpad" in url.lower() or "tiles" in url.lower() or "groups" in url.lower():
        tiles_finished = e["startedDateTime"]


def avg(lst):
    return round(sum(lst) / len(lst), 1) if lst else 0


print()
print(f"KPI REPORT - {HAR_FILE.name}")
print("=" * 50)

print(f"DNS lookup              : {avg(dns_values)} ms")
print(f"TCP connect             : {avg(tcp_values)} ms")
print(f"SSL/TLS handshake       : {avg(ssl_values)} ms")
print(f"SAP IAS response        : {avg(ias_response)} ms")
print(f"Okta redirect           : {avg(okta_response)} ms")
print(f"Launchpad callback      : {avg(callback_response)} ms")
print(f"HTTP status             : {status}")
