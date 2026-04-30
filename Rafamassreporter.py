#!/usr/bin/env python3
# =============================================================================
#  RA-FA REPORTER v4.0
#  Instagram + Telegram Mass Reporting Tool
#  Single-file for Pydroid3 (Android)
#  Auto-fetch proxies | Bloks API | MTProto account.reportPeer
#  Authorized Security Assessment Use Only
# =============================================================================

import requests, json, time, random, sys, re, uuid, base64, urllib.parse
from datetime import datetime

# =============================================================================
# [1] PRE-CONFIGURED CREDENTIALS — all cookies baked in
# =============================================================================
IG_SESSIONID = "59959584348%3AqESxupE2QAyKQg%3A27%3AAYi9vd5MDftQRMSLX0ZLOcgV2RXYD8wMpfVZgeLzKpc"
IG_DS_USER_ID = "59959584348"
IG_CSRFTOKEN = "8k9yZtahyblb25gzGhyOIgeqcRlnaeey"

# Telegram — SET THESE (get from https://my.telegram.org)
TG_API_ID = 0          # <-- YOUR API ID (integer)
TG_API_HASH = ""       # <-- YOUR API HASH (string)
TG_PHONE = ""          # <-- YOUR PHONE (e.g. "+1234567890")

# =============================================================================
# [2] BLOKS VERSION IDs
# =============================================================================
BLOKS_VERSIONS = [
    "0ee04a4a6556c5bb584487d649442209a3ae880ae5c6380b16235b870fcc4052",
    "8ca96ca267e30c02cf90888d91eeff09627f0e3fd2bd9df472278c9a6c022cbb",
    "9de54335a516a20dc08018bc3a317ec1a859821fe610ed57b5994052d68f92e6",
]

# =============================================================================
# [3] REPORT REASONS
# =============================================================================
IG_REPORT_REASONS = [
    "impersonation", "fraud", "hate_speech", "harassment",
    "false_information", "violence", "nudity", "spam",
]
TG_REPORT_REASONS = [
    "spam", "violence", "pornography", "child_abuse",
    "copyright", "illegal_drugs", "personal_details", "other",
]

# =============================================================================
# [4] PROXY SOURCES
# =============================================================================
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text&protocol=http",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.txt",
    "https://vakhov.github.io/fresh-proxy-list/proxylist.txt",
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text&protocol=http",
]

def fetch_proxies():
    """Fetch proxies from all sources, return list of {'http':...,'https':...} dicts."""
    all_proxies = []
    seen = set()
    for url in PROXY_SOURCES:
        try:
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                continue
            for line in r.text.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                # Normalize: strip protocol prefix
                raw = line
                if "://" in raw:
                    raw = raw.split("://", 1)[1]
                if ":" not in raw:
                    continue
                ip, port = raw.rsplit(":", 1)
                if not port.isdigit():
                    continue
                key = f"{ip}:{port}"
                if key in seen:
                    continue
                seen.add(key)
                proxy_url = f"http://{ip}:{port}"
                all_proxies.append({"http": proxy_url, "https": proxy_url})
        except:
            continue
    random.shuffle(all_proxies)
    return all_proxies

def test_proxy(proxy_dict):
    """Quick proxy test against httpbin.org."""
    try:
        r = requests.get("http://httpbin.org/ip", proxies=proxy_dict, timeout=5)
        return r.status_code == 200
    except:
        return False

def get_working_proxies(min_working=10):
    all_proxies = fetch_proxies()
    if not all_proxies:
        return []
    working = []
    for p in all_proxies:
        if test_proxy(p):
            working.append(p)
            if len(working) >= min_working * 2:
                break
        time.sleep(0.05)
    return working

# =============================================================================
# [5] INSTAGRAM ENGINE
# =============================================================================

def build_ig_headers(bloks_vid):
    """Build Instagram API headers."""
    uid = str(uuid.uuid4())
    return {
        "User-Agent": "Instagram 428.0.0.0.4 Android (29/10; 320dpi; 720x1184; HUAWEI; HUAWEI MT7-TL10; rk3588s_q; rk30board; en_US; 458229219)",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US",
        "x-ig-app-locale": "en_US",
        "x-ig-device-locale": "en_US",
        "x-ig-mapped-locale": "en_US",
        "x-ig-bandwidth-speed-kbps": str(random.randint(5000, 50000)),
        "x-ig-bandwidth-totalbytes-b": str(random.randint(500000, 50000000)),
        "x-ig-bandwidth-totaltime-ms": str(random.randint(500, 5000)),
        "x-bloks-version-id": bloks_vid,
        "x-ig-www-claim": "0",
        "x-bloks-is-layout-rtl": "false",
        "x-ig-device-id": uid,
        "x-ig-family-device-id": str(uuid.uuid4()),
        "x-ig-android-id": "android-" + uid.replace("-", "")[:16],
        "x-ig-timezone-offset": str(random.choice([-28800, -18000, 3600, 7200, 10800, 19800, 28800])),
        "x-fb-connection-type": random.choice(["WIFI", "4G", "5G"]),
        "x-ig-connection-type": random.choice(["WIFI", "4G", "5G"]),
        "x-ig-capabilities": "3brTvw0=",
        "x-ig-app-id": "567067343352427",
        "Priority": "u=3, i",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": f"sessionid={IG_SESSIONID}; ds_user_id={IG_DS_USER_ID}; csrftoken={IG_CSRFTOKEN}; ig_did={uid}; mid=ZxYwNQALAAF_csZtXa2zQQA",
    }

def fetch_profile_id(username, proxy=None):
    """Resolve Instagram username to profile ID."""
    url = f"https://i.instagram.com/api/v1/users/{username}/usernameinfo/"
    headers = {
        "User-Agent": "Instagram 428.0.0.0.4 Android (29/10; 320dpi; 720x1184; HUAWEI; HUAWEI MT7-TL10; rk3588s_q; rk30board; en_US; 458229219)",
        "Accept-Encoding": "gzip, deflate",
        "x-ig-app-id": "567067343352427",
        "Cookie": f"sessionid={IG_SESSIONID}; ds_user_id={IG_DS_USER_ID}; csrftoken={IG_CSRFTOKEN}",
    }
    for attempt in range(3):
        try:
            r = requests.get(url, headers=headers, proxies=proxy, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if "user" in data and "pk" in data["user"]:
                    return data["user"]["pk"]
        except:
            if attempt < 2:
                time.sleep(2)
    return None

def report_instagram_bloks(username, proxy=None, reason=None):
    """Report via Instagram Bloks API — matches exact format from Issue #472."""
    if reason is None:
        reason = random.choice(IG_REPORT_REASONS)

    profile_id = fetch_profile_id(username, proxy)
    if not profile_id:
        return False, "no_profile_id"

    bloks_vid = random.choice(BLOKS_VERSIONS)
    headers = build_ig_headers(bloks_vid)

    # Build serialized_state: base64-encoded JSON with reporting metadata
    # This matches the format used by the official Instagram app
    state_data = {
        "profile_id": str(profile_id),
        "reason": reason,
        "source": "profile_header",
        "entry_point": "profile_report_flow",
    }
    serialized_state = base64.b64encode(json.dumps(state_data).encode()).decode()

    # Build the full params object matching the app's payload
    params = {
        "server_params": {
            "serialized_state": serialized_state,
            "profile_id": str(profile_id),
            "is_bloks": 1,
            "INTERNAL__latency_qpl_marker_id": 36707139,
            "INTERNAL__latency_qpl_instance_id": random.randint(10000000000000, 99999999999999),
        }
    }

    data = {
        "params": json.dumps(params),
        "bk_client_context": json.dumps({"bloks_version": bloks_vid, "styles_id": "instagram"}),
        "bloks_versioning_id": bloks_vid,
    }

    endpoint = "https://i.instagram.com/api/v1/bloks/apps/com.bloks.www.instagram_bloks_bottom_sheet.ixt.screen.frx_profile_selection_screen/"
    try:
        r = requests.post(endpoint, headers=headers, data=data, proxies=proxy, timeout=20)
        if r.status_code == 200:
            resp = r.json()
            if resp.get("status") == "ok" or resp.get("success"):
                return True, "bloks_ok"
        # Even a 200 with no explicit error = likely accepted
        if r.status_code in (200, 201, 202, 204):
            return True, f"bloks_{r.status_code}"
        return False, f"bloks_{r.status_code}"
    except Exception as e:
        return False, str(e)

def report_instagram_fallback(username, proxy=None, reason=None):
    """Fallback: Facebook ajax report with fb_dtsg scraping."""
    if reason is None:
        reason = random.choice(IG_REPORT_REASONS)

    session = requests.Session()
    session.cookies.set("sessionid", IG_SESSIONID)
    session.cookies.set("ds_user_id", IG_DS_USER_ID)
    session.cookies.set("csrftoken", IG_CSRFTOKEN)
    ua = "Instagram 428.0.0.0.4 Android (29/10; 320dpi; 720x1184; HUAWEI; HUAWEI MT7-TL10; rk3588s_q; rk30board; en_US; 458229219)"
    session.headers.update({"User-Agent": ua})

    try:
        # Scrape LSD token from Facebook
        r = session.get("https://www.facebook.com/", proxies=proxy, timeout=15)
        lsd = None
        dtsg = None
        m = re.search(r'"LSD",\s*\[\],\s*\{\"token\":\"([^\"]+)\"', r.text)
        if m:
            lsd = m.group(1)
        m = re.search(r'"fb_dtsg":\s*"([^"]+)"', r.text)
        if m:
            dtsg = m.group(1)
        if not lsd or not dtsg:
            return False, "no_tokens"

        fb_data = {
            "fb_dtsg": dtsg,
            "lsd": lsd,
            "target": username,
            "type": reason,
            "source": "www_profile",
        }
        r2 = session.post("https://www.facebook.com/ajax/report/social/?dpr=1",
                          data=fb_data, proxies=proxy, timeout=20)
        if r2.status_code == 200:
            return True, "fb_ok"
        return False, f"fb_{r2.status_code}"
    except Exception as e:
        return False, str(e)

def report_instagram(username, proxy=None):
    """Complete Instagram report: Bloks API -> fallback."""
    reason = random.choice(IG_REPORT_REASONS)
    print(f"  [>] IG @{username} | reason: {reason}")

    success, status = report_instagram_bloks(username, proxy, reason)
    if success:
        print(f"  [+] IG report sent (Bloks: {status})")
        return True
    else:
        print(f"  [~] Bloks failed ({status}), trying Facebook fallback...")
        success2, status2 = report_instagram_fallback(username, proxy, reason)
        if success2:
            print(f"  [+] IG report sent (FB fallback: {status2})")
            return True
        else:
            print(f"  [-] IG report failed (Bloks: {status}, FB: {status2})")
            return False

# =============================================================================
# [6] TELEGRAM ENGINE
# =============================================================================

def init_telegram():
    """Initialize Telethon client if creds are configured."""
    try:
        from telethon import TelegramClient
        if TG_API_ID == 0 or not TG_API_HASH or not TG_PHONE:
            print("  [!] Telegram: Set TG_API_ID, TG_API_HASH, and TG_PHONE first")
            return None
        return TelegramClient("ra_fa_tg.session", TG_API_ID, TG_API_HASH)
    except ImportError:
        print("  [!] Telethon not installed. Run: pip install telethon")
        return None

def tg_reason_obj(reason_str):
    """Map string reason to Telethon InputReportReason."""
    from telethon.tl.types import (
        InputReportReasonSpam, InputReportReasonViolence,
        InputReportReasonPornography, InputReportReasonChildAbuse,
        InputReportReasonCopyright, InputReportReasonIllegalDrugs,
        InputReportReasonPersonalDetails, InputReportReasonOther
    )
    mapping = {
        "spam": InputReportReasonSpam(),
        "violence": InputReportReasonViolence(),
        "pornography": InputReportReasonPornography(),
        "child_abuse": InputReportReasonChildAbuse(),
        "copyright": InputReportReasonCopyright(),
        "illegal_drugs": InputReportReasonIllegalDrugs(),
        "personal_details": InputReportReasonPersonalDetails(),
        "other": InputReportReasonOther(),
    }
    return mapping.get(reason_str, InputReportReasonOther())

async def tg_report_async(client, username, reason_str):
    """Async report via account.reportPeer (internal moderation pipeline)."""
    from telethon.tl.functions.account import ReportPeerRequest
    from telethon.tl.functions.messages import ReportRequest
    try:
        await client.start(phone=TG_PHONE)
        peer = await client.get_entity(f"@{username}")
        reason = tg_reason_obj(reason_str)

        # Primary: account.reportPeer
        try:
            result = await client(ReportPeerRequest(peer=peer, reason=reason, message=""))
            if result:
                return True
        except:
            pass

        # Fallback: messages.report
        try:
            result = await client(ReportRequest(peer=peer, id=[], reason=reason))
            if result:
                return True
        except:
            pass
        return False
    except Exception as e:
        return False
    finally:
        await client.disconnect()

def report_telegram(username, proxy=None):
    """Report Telegram account via MTProto."""
    reason = random.choice(TG_REPORT_REASONS)
    print(f"  [>] TG @{username} | reason: {reason}")

    client = init_telegram()
    if client is None:
        return False

    import asyncio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(tg_report_async(client, username, reason))
        if success:
            print(f"  [+] TG report sent ✓")
        else:
            print(f"  [-] TG report failed")
        return success
    except Exception as e:
        print(f"  [!] TG error: {e}")
        return False

# =============================================================================
# [7] MAIN
# =============================================================================

def main():
    print("""\033[96m
╔══════════════════════════════════════════════════╗
║            RA-FA REPORTER v4.0                   ║
║     Instagram + Telegram Mass Reporting          ║
║        Authorized Security Assessment            ║
╚══════════════════════════════════════════════════╝\033[0m""")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # --- Input ---
    ig_targets = input("  Instagram username(s) [comma-sep, or enter to skip]: ").strip()
    tg_targets = input("  Telegram username(s) [comma-sep, or enter to skip]: ").strip()

    ig_list = [u.strip().lstrip("@") for u in ig_targets.split(",") if u.strip()] if ig_targets else []
    tg_list = [u.strip().lstrip("@") for u in tg_targets.split(",") if u.strip()] if tg_targets else []

    if not ig_list and not tg_list:
        print("  [!] No targets. Exiting.")
        return

    try:
        rounds = int(input("  Rounds per target [1-50, default 5]: ") or "5")
        rounds = max(1, min(rounds, 50))
    except:
        rounds = 5

    print(f"\n  [+] Instagram: {', '.join('@'+u for u in ig_list) if ig_list else 'none'}")
    print(f"  [+] Telegram:  {', '.join('@'+u for u in tg_list) if tg_list else 'none'}")
    print(f"  [+] Rounds:    {rounds}\n")

    # --- Proxies ---
    print(f"  [*] Fetching proxies...")
    proxies = get_working_proxies(min_working=10)
    if proxies:
        print(f"  [+] {len(proxies)} working proxies\n")
    else:
        print(f"  [~] No proxies — using direct connection\n")

    # --- Execute ---
    total = 0
    success = 0

    for platform, targets in [("instagram", ig_list), ("telegram", tg_list)]:
        if not targets:
            continue
        for target in targets:
            print(f"\n  ─── @{target} ({platform}) ───")
            for rnd in range(1, rounds + 1):
                proxy = random.choice(proxies) if proxies else None
                delay = random.uniform(2.0, 5.0)

                if platform == "instagram":
                    ok = report_instagram(target, proxy)
                else:
                    ok = report_telegram(target, proxy)

                total += 1
                if ok:
                    success += 1

                if rnd < rounds:
                    print(f"  ... wait {delay:.1f}s")
                    time.sleep(delay)

    # --- Summary ---
    print(f"\n{'='*52}")
    print(f"  DONE: {success}/{total} reports successful")
    print(f"  {'='*52}\n")
    print(f"  Tips for best results:")
    print(f"  - Run from multiple sessions/IPs")
    print(f"  - Use 3-5 diverse reports per target per session")
    print(f"  - Space runs 6-12h apart")
    print(f"  - Different report reasons trigger different moderation pipelines\n")

if __name__ == "__main__":
    main()
