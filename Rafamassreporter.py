# coding=utf-8
#!/usr/bin/env python3

"""
RA-FA REPORTER v2.0
Single-file Instagram + Telegram Mass Reporting Tool
Authorized Security Testing Only
Works on Pydroid (Android)
"""

import sys
import re
import random
import string
from time import sleep
from multiprocessing import Process
from threading import Thread
from queue import Queue

# ─── Dependency Check ────────────────────────────────────────────────────────

try:
    import requests
    from requests import Session, get as rget
except ImportError:
    print("[-] 'requests' package not installed!")
    print("[*] Type 'pip install requests' in Pydroid terminal to install!")
    sys.exit(0)

try:
    from colorama import Fore, Back, Style, init
    init()
except ImportError:
    print("[-] 'colorama' package not installed!")
    print("[*] Type 'pip install colorama' in Pydroid terminal to install!")
    sys.exit(0)

import warnings
warnings.filterwarnings("ignore")


# ═══════════════════════════════════════════════════════════════════════════════
# LOGO
# ═══════════════════════════════════════════════════════════════════════════════

def print_logo():
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


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def print_success(message, *argv):
    print(Fore.GREEN + "[ OK ] " + Style.RESET_ALL + Style.BRIGHT, end="")
    print(message, end=" ")
    for arg in argv:
        print(arg, end=" ")
    print("")


def print_error(message, *argv):
    print(Fore.RED + "[ ERR ] " + Style.RESET_ALL + Style.BRIGHT, end="")
    print(message, end=" ")
    for arg in argv:
        print(arg, end=" ")
    print("")


def print_status(message, *argv):
    print(Fore.BLUE + "[ * ] " + Style.RESET_ALL + Style.BRIGHT, end="")
    print(message, end=" ")
    for arg in argv:
        print(arg, end=" ")
    print("")


def ask_question(message, *argv):
    msg = Fore.YELLOW + "[ ? ] " + Style.RESET_ALL + Style.BRIGHT + message
    for arg in argv:
        msg = msg + " " + arg
    print(msg, end="")
    ret = input(": ")
    return ret


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
]


def get_user_agent():
    return random.choice(USER_AGENTS)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# ═══════════════════════════════════════════════════════════════════════════════
# PROXY HARVESTER — FAST MODE
# ═══════════════════════════════════════════════════════════════════════════════

PROXY_SOURCES = [
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",
    "https://raw.githubusercontent.com/iplocate/free-proxy-list/master/proxies/all/data.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/proxies/all/data.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
]


def _test_http_proxy(proxy, result_queue):
    """Quick single-proxy test — runs in thread."""
    ua = get_user_agent()
    try:
        s = Session()
        s.proxies = {"http": "http://" + proxy, "https": "http://" + proxy}
        s.headers.update({"User-Agent": ua, "Connection": "close"})
        # Just check if we can connect — use short timeout
        resp = s.get("http://connectivitycheck.platform.hadielkadi.com/generate_204",
                     timeout=3, allow_redirects=False)
        if resp.status_code in (200, 204, 302, 301):
            result_queue.put(proxy)
            print_success("Proxy: " + proxy)
        else:
            result_queue.put(None)
    except:
        result_queue.put(None)


def find_proxies():
    """Fetch proxies from multiple online sources — fast threaded validation."""
    proxy_set = set()
    ua = get_user_agent()

    print_status("Fetching proxies from the Internet...")

    for url in PROXY_SOURCES:
        try:
            resp = rget(url, headers={"User-Agent": ua}, timeout=8)
            if resp.status_code != 200:
                continue
            for line in resp.text.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                if "://" in line:
                    line = line.split("://")[-1]
                if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$', line):
                    proxy_set.add(line)
        except Exception:
            pass

    proxy_list = list(proxy_set)
    print_status("Found " + str(len(proxy_list)) + " raw proxies.")

    if not proxy_list:
        print_error("No proxies found from any source!")
        return []

    # Test proxies using threads — 30 at a time
    print_status("Testing proxies (30 concurrent threads)...")
    valid = []
    to_test = proxy_list[:120]  # Test up to 120 proxies max

    # Process in batches of 30 threads
    for batch_start in range(0, len(to_test), 30):
        batch = to_test[batch_start:batch_start + 30]
        q = Queue()
        threads = []

        for proxy in batch:
            t = Thread(target=_test_http_proxy, args=(proxy, q))
            t.start()
            threads.append(t)

        # Wait for all threads to finish (max 5 seconds)
        for t in threads:
            t.join(timeout=5)

        # Collect results
        while not q.empty():
            result = q.get()
            if result:
                valid.append(result)

        if len(valid) >= 30:
            break

    if not valid:
        print_status("No valid proxies found — using raw list.")
        valid = proxy_list[:50]

    # Trim to multiples of 5
    if len(valid) % 5 != 0 and len(valid) > 5:
        valid = valid[:len(valid) - (len(valid) % 5)]

    valid = valid[:50]
    print_status("Got " + str(len(valid)) + " working proxies.")
    return valid


def parse_proxy_file(fpath):
    """Parse proxy file from local storage."""
    try:
        with open(fpath, "r") as f:
            proxies = []
            for line in f.readlines():
                line = line.strip().replace(" ", "")
                if not line:
                    continue
                if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$', line):
                    proxies.append(line)

        if len(proxies) > 50:
            proxies = random.sample(proxies, 50)

        print("")
        print_success(str(len(proxies)) + " proxies loaded from file!")
        return proxies

    except FileNotFoundError:
        print("")
        print_error("Proxy file not found! Check the path.")
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# ATTACK ENGINE — Instagram
# ═══════════════════════════════════════════════════════════════════════════════

PAGE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "DNT": "1",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
}

REPORT_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "DNT": "1",
    "Host": "help.instagram.com",
    "Origin": "https://help.instagram.com",
    "Pragma": "no-cache",
    "Referer": "https://help.instagram.com/contact/497253480400030",
    "TE": "Trailers",
}

TG_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "DNT": "1",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
}


def _setup_session(proxy):
    ses = Session()
    if proxy:
        ses.proxies = {
            "https": "https://" + proxy,
            "http": "http://" + proxy
        }
    ua = get_user_agent()
    ses.headers.update({"User-Agent": ua})
    return ses, ua


def _extract_tokens(text):
    tokens = {}
    markers = [
        ('lsd', '["LSD",[],{"token":"', '"},'),
        ('spin_r', '"__spin_r":', ','),
        ('spin_t', '"__spin_t":', ','),
        ('hsi', '"hsi":', ','),
        ('rev', '"server_revision":', ','),
    ]
    for key, start, end in markers:
        if start not in text:
            return None
        try:
            val = text.split(start)[1].split(end)[0].replace('"', '').strip()
            tokens[key] = val
        except:
            return None

    if '"__spin_b":' in text:
        try:
            tokens['spin_b'] = text.split('"__spin_b":')[1].split(',')[0].replace('"', '').strip()
        except:
            return None
    else:
        return None

    return tokens


def report_profile_attack(username, proxy):
    """Report an Instagram profile."""
    ses, ua = _setup_session(proxy)
    page_h = {}
    page_h.update(PAGE_HEADERS)
    page_h["User-Agent"] = ua
    report_h = {}
    report_h.update(REPORT_HEADERS)
    report_h["User-Agent"] = ua

    try:
        res = ses.get("https://www.facebook.com/", headers=page_h, timeout=10)
        if res.status_code != 200 or '["_js_datr","' not in res.text:
            return
        js_datr = res.text.split('["_js_datr","')[1].split('",')[0]
    except:
        return

    try:
        res = ses.get(
            "https://help.instagram.com/contact/497253480400030",
            cookies={"_js_datr": js_datr},
            headers=page_h,
            timeout=10
        )
        if res.status_code != 200 or "datr" not in res.cookies.get_dict():
            return
        datr = res.cookies.get_dict()["datr"]
        tokens = _extract_tokens(res.text)
        if not tokens:
            return
    except:
        return

    form = {
        "jazoest": "2723",
        "lsd": tokens['lsd'],
        "sneakyhidden": "",
        "Field419623844841592": username,
        "Field1476905342523314_iso2_country_code": "US",
        "Field1476905342523314": "United States",
        "support_form_id": "440963189380968",
        "support_form_hidden_fields": '{"423417021136459":false,"419623844841592":false,"754839691215928":false,"1476905342523314":false,"284770995012493":true,"237926093076239":false}',
        "support_form_fact_false_fields": "[]",
        "__user": "0", "__a": "1",
        "__dyn": "7xe6Fo4SQ1PyUhxOnFwn84a2i5U4e1Fx-ey8kxx0LxW0DUeUhw5cx60Vo1upE4W0OE2WxO0SobEa81Vrzo5-0jx0Fwww6DwtU6e",
        "__csr": "", "__req": "d", "__beoa": "0",
        "__pc": "PHASED:DEFAULT", "dpr": "1",
        "__rev": tokens['rev'], "__s": "5gbxno:2obi73:56i3vc",
        "__hsi": tokens['hsi'], "__comet_req": "0",
        "__spin_r": tokens['spin_r'], "__spin_b": tokens['spin_b'],
        "__spin_t": tokens['spin_t'],
    }

    try:
        res = ses.post(
            "https://help.instagram.com/ajax/help/contact/submit/page",
            data=form, headers=report_h,
            cookies={"datr": datr}, timeout=10
        )
        if res.status_code == 200:
            print_success("[IG] Reported @" + username + " via " + (proxy or "direct"))
        else:
            print_error("[IG] Report failed (" + str(res.status_code) + ")")
    except:
        print_error("[IG] Submission error for " + username)


def report_video_attack(video_url, proxy):
    """Report an Instagram video."""
    ses, ua = _setup_session(proxy)
    page_h = {}
    page_h.update(PAGE_HEADERS)
    page_h["User-Agent"] = ua
    report_h = {}
    report_h.update(REPORT_HEADERS)
    report_h["User-Agent"] = ua

    try:
        res = ses.get("https://www.facebook.com/", headers=page_h, timeout=10)
        if res.status_code != 200 or '["_js_datr","' not in res.text:
            return
        js_datr = res.text.split('["_js_datr","')[1].split('",')[0]
    except:
        return

    try:
        res = ses.get(
            "https://help.instagram.com/contact/497253480400030",
            cookies={"_js_datr": js_datr},
            headers=page_h, timeout=10
        )
        if res.status_code != 200 or "datr" not in res.cookies.get_dict():
            return
        datr = res.cookies.get_dict()["datr"]
        tokens = _extract_tokens(res.text)
        if not tokens:
            return
    except:
        return

    form = {
        "jazoest": "2723",
        "lsd": tokens['lsd'],
        "sneakyhidden": "",
        "Field419623844841592": video_url,
        "Field1476905342523314_iso2_country_code": "US",
        "Field1476905342523314": "United States",
        "support_form_id": "440963189380968",
        "support_form_hidden_fields": '{"423417021136459":false,"419623844841592":false,"754839691215928":false,"1476905342523314":false,"284770995012493":true,"237926093076239":false}',
        "support_form_fact_false_fields": "[]",
        "__user": "0", "__a": "1",
        "__dyn": "7xe6Fo4SQ1PyUhxOnFwn84a2i5U4e1Fx-ey8kxx0LxW0DUeUhw5cx60Vo1upE4W0OE2WxO0SobEa81Vrzo5-0jx0Fwww6DwtU6e",
        "__csr": "", "__req": "d", "__beoa": "0",
        "__pc": "PHASED:DEFAULT", "dpr": "1",
        "__rev": tokens['rev'], "__s": "5gbxno:2obi73:56i3vc",
        "__hsi": tokens['hsi'], "__comet_req": "0",
        "__spin_r": tokens['spin_r'], "__spin_b": tokens['spin_b'],
        "__spin_t": tokens['spin_t'],
    }

    try:
        res = ses.post(
            "https://help.instagram.com/ajax/help/contact/submit/page",
            data=form, headers=report_h,
            cookies={"datr": datr}, timeout=10
        )
        if res.status_code == 200:
            print_success("[IG] Video reported via " + (proxy or "direct"))
        else:
            print_error("[IG] Video report failed (" + str(res.status_code) + ")")
    except:
        print_error("[IG] Video submission error")


# ═══════════════════════════════════════════════════════════════════════════════
# ATTACK ENGINE — Telegram
# ═══════════════════════════════════════════════════════════════════════════════

def report_telegram_user(username, proxy):
    """Report a Telegram user."""
    ses, ua = _setup_session(proxy)
    tg_h = {}
    tg_h.update(TG_HEADERS)
    tg_h["User-Agent"] = ua

    try:
        ses.get("https://telegram.org/", headers=tg_h, timeout=10)
        payload = {
            "type": "user",
            "username": username,
            "reason": "Spam and abusive behavior",
            "text": "User @" + username + " is violating Telegram ToS by sending "
                    "unsolicited spam messages. Please take action.",
        }
        res = ses.post("https://telegram.org/abuse", data=payload, headers={
            "User-Agent": ua, "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://telegram.org", "Referer": "https://telegram.org/abuse",
        }, timeout=10)
        if res.status_code in (200, 302, 303):
            print_success("[TG] Report sent for @" + username + " via " + (proxy or "direct"))
        else:
            print_error("[TG] Report returned " + str(res.status_code))

        ses.get("https://t.me/" + username, headers=tg_h, timeout=10)

    except Exception as e:
        print_error("[TG] Report failed: " + str(e)[:40])


def report_telegram_channel(channel, proxy):
    """Report a Telegram channel."""
    ses, ua = _setup_session(proxy)
    tg_h = {}
    tg_h.update(TG_HEADERS)
    tg_h["User-Agent"] = ua

    try:
        payload = {
            "type": "channel",
            "username": channel,
            "reason": "Spam and illegal content",
            "message": "Channel @" + channel + " is distributing spam and violating ToS.",
        }
        res = ses.post("https://telegram.org/abuse", data=payload, headers={
            "User-Agent": ua, "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://telegram.org", "Referer": "https://telegram.org/abuse",
        }, timeout=10)
        if res.status_code in (200, 302, 303):
            print_success("[TG] Channel @" + channel + " reported via " + (proxy or "direct"))
        else:
            print_error("[TG] Channel report returned " + str(res.status_code))
    except Exception as e:
        print_error("[TG] Channel report failed: " + str(e)[:40])


# ═══════════════════════════════════════════════════════════════════════════════
# PROCESS MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def profile_attack_process(username, proxy_list):
    if not proxy_list:
        for _ in range(10):
            report_profile_attack(username, None)
            sleep(0.3)
        return
    for proxy in proxy_list:
        report_profile_attack(username, proxy)
        sleep(0.2)


def video_attack_process(video_url, proxy_list):
    if not proxy_list:
        for _ in range(10):
            report_video_attack(video_url, None)
            sleep(0.3)
        return
    for proxy in proxy_list:
        report_video_attack(video_url, proxy)
        sleep(0.2)


def telegram_user_process(username, proxy_list):
    if not proxy_list:
        for _ in range(10):
            report_telegram_user(username, None)
            sleep(0.3)
        return
    for proxy in proxy_list:
        report_telegram_user(username, proxy)
        sleep(0.2)


def telegram_channel_process(channel, proxy_list):
    if not proxy_list:
        for _ in range(10):
            report_telegram_channel(channel, None)
            sleep(0.3)
        return
    for proxy in proxy_list:
        report_telegram_channel(channel, proxy)
        sleep(0.2)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ATTACK FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def profile_attack(proxies):
    username = ask_question("Enter the Instagram username to report")
    print(Style.RESET_ALL)

    if not proxies:
        for k in range(5):
            p = Process(target=profile_attack_process, args=(username, []))
            p.start()
            print_status(str(k + 1) + ". Transaction Opened!")
        return

    chunk_list = list(chunks(proxies, 10))
    print_status("Profile attack starting!\n")
    i = 1
    for plist in chunk_list:
        p = Process(target=profile_attack_process, args=(username, plist))
        p.start()
        print_status(str(i) + ". Transaction Opened!")
        i += 1


def video_attack(proxies):
    video_url = ask_question("Enter the Instagram video URL to report")
    print(Style.RESET_ALL)

    if not proxies:
        for k in range(5):
            p = Process(target=video_attack_process, args=(video_url, []))
            p.start()
            print_status(str(k + 1) + ". Transaction Opened!")
        return

    chunk_list = list(chunks(proxies, 10))
    print_status("Video attack starting!\n")
    i = 1
    for plist in chunk_list:
        p = Process(target=video_attack_process, args=(video_url, plist))
        p.start()
        print_status(str(i) + ". Transaction Opened!")
        i += 1


def telegram_attack(proxies):
    print_status("1 - Report a user account")
    print_status("2 - Report a channel/group")
    choice = ask_question("Select type")

    if choice == "1":
        username = ask_question("Enter Telegram username (without @)")
        print(Style.RESET_ALL)

        if not proxies:
            for k in range(5):
                p = Process(target=telegram_user_process, args=(username, []))
                p.start()
                print_status(str(k + 1) + ". Report thread opened!")
            return

        chunk_list = list(chunks(proxies, 10))
        i = 1
        for plist in chunk_list:
            p = Process(target=telegram_user_process, args=(username, plist))
            p.start()
            print_status(str(i) + ". Report thread opened!")
            i += 1

    elif choice == "2":
        channel = ask_question("Enter channel username (without @)")
        print(Style.RESET_ALL)

        if not proxies:
            for k in range(5):
                p = Process(target=telegram_channel_process, args=(channel, []))
                p.start()
                print_status(str(k + 1) + ". Report thread opened!")
            return

        chunk_list = list(chunks(proxies, 10))
        i = 1
        for plist in chunk_list:
            p = Process(target=telegram_channel_process, args=(channel, plist))
            p.start()
            print_status(str(i) + ". Report thread opened!")
            i += 1
    else:
        print_error("Invalid choice!")
        sys.exit(1)


def get_proxies():
    ret = ask_question("Use proxies? [Y/N]")
    proxies = []

    if ret.lower() == "y":
        ret = ask_question("Collect proxies from internet? [Y/N]")

        if ret.lower() == "y":
            print_status("Gathering proxies from internet...\n")
            proxies = find_proxies()
        elif ret.lower() == "n":
            file_path = ask_question("Enter path to proxy file")
            proxies = parse_proxy_file(file_path)
        else:
            print_error("Invalid choice!")
            sys.exit(1)

        if proxies:
            print_success(str(len(proxies)) + " proxies ready!\n")
        else:
            print_status("No proxies. Proceeding without.\n")

    elif ret.lower() == "n":
        print_status("No proxies.\n")
    else:
        print_error("Invalid choice!")
        sys.exit(1)

    return proxies


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print_success("RA-FA REPORTER loaded!\n")

    proxies = get_proxies()

    print("")
    print_status("Select Platform:")
    print_status("1 - Instagram (report profile)")
    print_status("2 - Instagram (report video)")
    print_status("3 - Telegram (report user/channel)")
    choice = ask_question("Select")

    if not choice.isdigit():
        print_error("Invalid input!")
        sys.exit(1)

    c = int(choice)
    if c < 1 or c > 3:
        print_error("Invalid selection!")
        sys.exit(1)

    if c == 1:
        profile_attack(proxies)
    elif c == 2:
        video_attack(proxies)
    elif c == 3:
        telegram_attack(proxies)


if __name__ == "__main__":
    print_logo()
    try:
        main()
        print(Style.RESET_ALL)
        print_status("RA-FA REPORTER completed. Press Enter to exit.")
        input()
    except KeyboardInterrupt:
        print("\n" + Fore.RED + "[ * ] RA-FA REPORTER shutting down.")
        print(Style.RESET_ALL)
        sys.exit(0)
    except Exception as e:
        print_error("Unhandled error: " + str(e))
        print(Style.RESET_ALL)
        sys.exit(1)
