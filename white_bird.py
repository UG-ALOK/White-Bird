
#!/usr/bin/env python3
# White Bird v2.8
# Developer: Firewall-Crusher
# Public Profile URL Checker | Python Standard Library

import os
import re
import json
import time
import socket
import ipaddress
import shutil
import subprocess
from urllib.parse import urlparse, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

APP = "WHITE BIRD"
VERSION = "2.8"
DEVELOPER = "Firewall-Crusher"
DEVELOPER_PROFILE = "https://github.com/UG-ALOK?tab=repositorie"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URL_FILE = os.path.join(BASE_DIR, "urls.txt")
SITES_FILE = os.path.join(BASE_DIR, "sites.json")

MAX_URLS = 800
REQUEST_INTERVAL = 7.5
TIMEOUT = 10

RED = "\033[91m"
WHITE = "\033[97m"
GRAY = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"

last_request = 0.0
session_results = []
session_username = ""


def clear():
    os.system("clear")


def pause():
    input(f"\n{WHITE}Press Enter to continue...{RESET}")


def banner():
    print(f"""{RED}{BOLD}
 __        __ __    _ __       ____  _         __
 \\ \\      / / \\ \\  / / _ \\     | __ )(_)_ __ __| |
  \\ \\ /\\ / /   \\ \\/ / | | |____|  _ \\| | '__/ _` |
   \\ V  V /     \\  /| |_| |____| |_) | | | | (_| |
    \\_/\\_/       \\/  \\___/     |____/|_|_|  \\__,_|
{RESET}""")
    print(f"{WHITE}  Public Profile URL Checker v{VERSION}{RESET}")
    print(f"{RED}  Developer: {DEVELOPER}{RESET}")
    print(f"{WHITE}  Profile: {DEVELOPER_PROFILE}{RESET}")
    print(RED + "-" * 48 + RESET)


def load_sites():
    try:
        with open(SITES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            return data[:MAX_URLS]
    except (OSError, json.JSONDecodeError):
        pass
    return []


def save_sites(sites):
    temp_file = SITES_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(sites, file, indent=2)
    os.replace(temp_file, SITES_FILE)


def normalize_url(value):
    value = value.strip()

    if not value or value.startswith("#"):
        return None

    if not re.match(r"^https?://", value, re.I):
        value = "https://" + value

    try:
        parsed = urlparse(value)

        if parsed.scheme not in ("http", "https"):
            return None
        if not parsed.hostname or parsed.username or parsed.password:
            return None
        if parsed.port and not 1 <= parsed.port <= 65535:
            return None

        return f"{parsed.scheme}://{parsed.netloc}"
    except ValueError:
        return None


def edit_urls():
    previous = load_sites()
    editor = shutil.which("nano")

    if not editor:
        print(f"{RED}Nano is not installed. Run: pkg install nano{RESET}")
        return None

    lines = [
        "# Enter your target platform URLs below, one per line.",
        "# Lines beginning with # are ignored.",
        "# Example: https://github.com/",
        "# Example: https://www.reddit.com/",
        "",
    ]

    if previous:
        lines.extend(previous)
        lines.append("")

    try:
        with open(URL_FILE, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

        subprocess.run([editor, URL_FILE], check=False)

        with open(URL_FILE, "r", encoding="utf-8") as file:
            entries = file.readlines()
    except OSError as exc:
        print(f"{RED}Could not open URL editor: {exc}{RESET}")
        return None

    sites = []
    seen = set()

    for entry in entries:
        url = normalize_url(entry)
        if url and url not in seen:
            seen.add(url)
            sites.append(url)
        if len(sites) >= MAX_URLS:
            break

    if not sites:
        print(f"{RED}No valid URLs entered.{RESET}")
        return None

    save_sites(sites)
    print(f"{WHITE}Loaded {len(sites)} URLs.{RESET}")
    return sites


def profile_url(base_url, username):
    host = (urlparse(base_url).hostname or "").lower()
    host = host.removeprefix("www.")
    user = quote(username.strip(), safe="")

    patterns = {
        "github.com": f"https://github.com/{user}",
        "gitlab.com": f"https://gitlab.com/{user}",
        "codeberg.org": f"https://codeberg.org/{user}",
        "reddit.com": f"https://www.reddit.com/user/{user}/",
        "x.com": f"https://x.com/{user}",
        "twitter.com": f"https://x.com/{user}",
        "instagram.com": f"https://www.instagram.com/{user}/",
        "tiktok.com": f"https://www.tiktok.com/@{user}",
        "youtube.com": f"https://www.youtube.com/@{user}",
        "medium.com": f"https://medium.com/@{user}",
        "pinterest.com": f"https://www.pinterest.com/{user}/",
    }

    if host in patterns:
        return patterns[host], False

    return f"https://{host}/{user}", True


def public_target(url):
    try:
        host = urlparse(url).hostname
        if not host:
            return False, "Invalid hostname"

        addresses = socket.getaddrinfo(
            host, None, type=socket.SOCK_STREAM
        )

        if not addresses:
            return False, "DNS lookup failed"

        for item in addresses:
            address = ipaddress.ip_address(item[4][0])
            if not address.is_global:
                return False, "Private or local host blocked"

        return True, ""
    except (OSError, ValueError):
        return False, "DNS lookup failed"


def check_url(url):
    global last_request

    valid, reason = public_target(url)
    if not valid:
        return "SKIPPED", reason

    wait = REQUEST_INTERVAL - (time.monotonic() - last_request)
    if wait > 0:
        time.sleep(wait)

    request = Request(
        url,
        headers={
            "User-Agent": "WhiteBird-PublicProfileChecker/2.8",
            "Accept": "text/html,application/xhtml+xml,*/*",
        },
    )

    last_request = time.monotonic()

    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            code = response.status

        if code == 200:
            return "POSSIBLE", "HTTP 200 - Page is accessible"
        return "UNKNOWN", f"HTTP {code}"

    except HTTPError as exc:
        if exc.code == 404:
            return "NOT FOUND", "HTTP 404 - Page not found"
        if exc.code in (401, 403, 429):
            return "UNKNOWN", f"HTTP {exc.code} - Restricted"
        return "UNKNOWN", f"HTTP {exc.code}"

    except (URLError, TimeoutError, OSError) as exc:
        return "ERROR", str(exc)[:100]


def display_result(index, total, result):
    status = result["status"]
    color = WHITE if status == "POSSIBLE" else RED

    print(f"\n{WHITE}[{index}/{total}] {color}{status}{RESET}")
    print(f"{WHITE}URL: {result['url']}{RESET}")
    print(f"{WHITE}Details: {result['detail']}{RESET}")

    if result["estimated"]:
        print(f"{GRAY}Estimated URL pattern; not verified.{RESET}")


def scan():
    global session_results, session_username

    print(f"\n{WHITE}Opening URL editor...{RESET}")
    sites = edit_urls()

    if not sites:
        pause()
        return

    username = input(f"\n{WHITE}Enter username: {RESET}").strip()

    if not username:
        print(f"{RED}Username cannot be empty.{RESET}")
        pause()
        return

    session_username = username
    session_results = []

    clear()
    banner()
    print(f"{WHITE}Username: {username}{RESET}")
    print(f"{WHITE}URLs to check: {len(sites)}{RESET}")
    print(f"{GRAY}Results appear here. No report files are generated.{RESET}")
    print(RED + "-" * 48 + RESET)

    for index, base in enumerate(sites, start=1):
        target, estimated = profile_url(base, username)
        status, detail = check_url(target)

        result = {
            "url": target,
            "status": status,
            "detail": detail,
            "estimated": estimated,
        }

        session_results.append(result)
        display_result(index, len(sites), result)

    possible = sum(r["status"] == "POSSIBLE" for r in session_results)
    missing = sum(r["status"] == "NOT FOUND" for r in session_results)
    other = len(session_results) - possible - missing

    print(RED + "\n" + "-" * 48 + RESET)
    print(f"{WHITE}{BOLD}SCAN SUMMARY{RESET}")
    print(f"{WHITE}Username: {username}")
    print(f"Checked: {len(session_results)}")
    print(f"Possible pages: {possible}")
    print(f"Not found: {missing}")
    print(f"Unknown / skipped / errors: {other}{RESET}")
    print(f"{GRAY}An accessible page does not confirm account ownership.{RESET}")
    pause()


def view_results():
    if not session_results:
        print(f"{RED}\nNo results in this session. Run a scan first.{RESET}")
        pause()
        return

    clear()
    banner()
    print(f"{WHITE}Last scan username: {session_username}{RESET}")
    print(RED + "-" * 48 + RESET)

    for index, result in enumerate(session_results, start=1):
        display_result(index, len(session_results), result)

    print(f"\n{GRAY}Results exist only while this program is running.{RESET}")
    pause()


def main():
    while True:
        clear()
        banner()

        print(f"{WHITE}  1. Set Scan URL")
        print("  2. View Reports")
        print("  0. Exit" + RESET)
        print(RED + "-" * 48 + RESET)
        print(f"{GRAY}Example: Add platform URLs, then enter a username.{RESET}")
        print(f"{RED}Developer: {DEVELOPER}{RESET}")
        print(f"{WHITE}Profile: {DEVELOPER_PROFILE}{RESET}")

        choice = input(f"\n{WHITE}White Bird > {RESET}").strip()

        if choice == "1":
            scan()
        elif choice == "2":
            view_results()
        elif choice == "0":
            print(f"{WHITE}White Bird closed.{RESET}")
            break
        else:
            print(f"{RED}Invalid option. Choose 1, 2, or 0.{RESET}")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}Scan interrupted.{RESET}")
