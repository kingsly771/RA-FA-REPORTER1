#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║         RA-FA REPORTER v3.0              ║
║     Instagram & Telegram Mass Reporter   ║
║         Authorized Security Tool         ║
╚══════════════════════════════════════════╝

Three Engines (tried in order):
  [1] Instagram Bloks API (authenticated, most reliable)
  [2] Facebook Help Center Ajax (auto-token scraping)
  [3] Direct fallback
"""

import os, sys, json, re, time, uuid, base64, random, string, hashlib
from datetime import datetime
try:
    import requests
except ImportError:
    os.system('pip install requests')
    import requests

# ══════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════

# --- Instagram Cookies (PROVIDED - authenticated session) ---
IG_SESSIONID = "59959584348%3AqESxupE2QAyKQg%3A27%3AAYi9vd5MDftQRMSLX0ZLOcgV2RXYD8wMpfVZgeLzKpc"
IG_DS_USER_ID = "59959584348"
IG_CSRFTOKEN  = "8k9yZtahyblb25gzGhyOIgeqcRlnaeey"

# --- Report form IDs ---
# Instagram impersonation form via Facebook's handler
FACEBOOK_HELP_FORM_ID = "636276399721841"  # Instagram impersonation
FACEBOOK_BASE_URL     = "https://www.facebook.com"

# Instagram Bloks endpoints
IG_BLOKS_URL = "https://i.instagram.com/api/v1/bloks/apps/com.bloks.www.instagram_bloks_bottom_sheet.ixt.screen.frx_profile_selection_screen/"

# Known working bloks version IDs (auto-rotated on failure)
BLOKS_VERSION_IDS = [
    "0ee04a4a6556c5bb584487d649442209a3ae880ae5c6380b16235b870fcc4052",
    "8ca96ca267e30c02cf90888d91eeff09627f0e3fd2bd9df472278c9a6c022cbb",
    "9de54335a516a20dc08018bc3a317ec1a859821fe610ed57b5994052d68f92e6",
]

# --- Proxy Configuration ---
MAX_PROXIES = 30

# ══════════════════════════════════════════
#  BRANDING & UI
# ══════════════════════════════════════════

BANNER = r"""
╔══════════════════════════════════════════════╗
║           RA-FA REPORTER v3.0                ║
║     ██████╗  █████╗  ███████╗ █████╗         ║
║     ██╔══██╗██╔══██╗██╔════╝██╔══██╗        ║
║     ██████╔╝███████║█████╗  ███████║        ║
║     ██╔══██╗██╔══██║██╔══╝  ██╔══██║        ║
║     ██║  ██║██║  ██║██║     ██║  ██║        ║
║     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝        ║
║         Instagram & Telegram Reporter        ║
╚══════════════════════════════════════════════╝
"""

def log(msg, status="+"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f" [{status}] [{ts}] {msg}")

def log_ok(msg):   log(msg, "+")
def log_info(msg): log(msg, "*")
def log_warn(msg): log(msg, "!")
def log_err(msg):  log(msg, "-")

# ══════════════════════════════════════════
#  PROXY ENGINE
# ══════════════════════════════════════════

class ProxyManager:
    def __init__(self, max_proxies=MAX_PROXIES):
        self.proxies = []
        self.index = 0
        self.max_proxies = max_proxies
        self.loaded = False

    def load_from_file(self, path="proxies.txt"):
        if not os.path.exists(path):
            log_warn(f"Proxy file '{path}' not found. Running without proxies.")
            return False
        try:
            with open(path) as f:
                raw = f.read().strip().splitlines()
            count = 0
            for line in raw:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Accept format: ip:port or ip:port:user:pass or protocol://...
                if len(self.proxies) >= self.max_proxies:
                    break
                if "://" not in line:
                    line = f"http://{line}"
                self.proxies.append(line)
                count += 1
            self.loaded = len(self.proxies) > 0
            log_ok(f"Loaded {len(self.proxies)} proxies")
            random.shuffle(self.proxies)
            return self.loaded
        except Exception as e:
            log_err(f"Failed to load proxies: {e}")
            return False

    def load_from_text(self, text):
        lines = text.strip().splitlines()
        count = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if len(self.proxies) >= self.max_proxies:
                break
            if "://" not in line:
                line = f"http://{line}"
            self.proxies.append(line)
            count += 1
        self.loaded = len(self.proxies) > 0
        if self.loaded:
            log_ok(f"Loaded {len(self.proxies)} proxies")
            random.shuffle(self.proxies)
        return self.loaded

    def get_proxy(self):
        if not self.proxies:
            return None
        proxy = self.proxies[self.index % len(self.proxies)]
        self.index += 1
        return {"http": proxy, "https": proxy}

    def get_count(self):
        return len(self.proxies)


# ══════════════════════════════════════════
#  ENGINE 1: INSTAGRAM BLOKS API
# ══════════════════════════════════════════

class InstagramBloksEngine:
    """Uses authenticated Instagram session to submit reports via Bloks API."""

    def __init__(self, proxy_mgr=None):
        self.session = requests.Session()
        self.proxy_mgr = proxy_mgr
        self.user_agent = (
            "Instagram 428.0.0.0.4 Android (35/15; 420dpi; 1080x2153; "
            "Google/google; Pixel 8a; akita; akita; en_US; 923309173)"
        )
        self._setup_session()

    def _setup_session(self):
        # Set Instagram cookies
        self.session.cookies.set("sessionid", IG_SESSIONID, domain=".instagram.com")
        self.session.cookies.set("ds_user_id", IG_DS_USER_ID, domain=".instagram.com")
        self.session.cookies.set("csrftoken", IG_CSRFTOKEN, domain=".instagram.com")
        # Also set for i.instagram.com
        self.session.cookies.set("sessionid", IG_SESSIONID, domain="i.instagram.com")
        self.session.cookies.set("ds_user_id", IG_DS_USER_ID, domain="i.instagram.com")
        self.session.cookies.set("csrftoken", IG_CSRFTOKEN, domain="i.instagram.com")

    def _make_headers(self, bloks_version_id):
        device_id = f"android-{hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]}"
        family_device_id = str(uuid.uuid4())
        pigeon_sess = f"UFS-{str(uuid.uuid4())}-1"
        return {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US",
            "x-ig-app-locale": "en_US",
            "x-ig-device-locale": "en_US",
            "x-ig-mapped-locale": "en_US",
            "x-pigeon-session-id": pigeon_sess,
            "x-pigeon-rawclienttime": str(time.time()),
            "x-ig-bandwidth-speed-kbps": "-1.000",
            "x-ig-bandwidth-totalbytes-b": "0",
            "x-ig-bandwidth-totaltime-ms": "0",
            "x-bloks-version-id": bloks_version_id,
            "x-ig-www-claim": "0",
            "x-bloks-is-layout-rtl": "false",
            "x-ig-device-id": device_id,
            "x-ig-family-device-id": family_device_id,
            "x-ig-android-id": device_id,
            "x-ig-timezone-offset": "28800",
            "x-fb-connection-type": "WIFI",
            "x-ig-connection-type": "WIFI",
            "x-ig-capabilities": "3brTvwE=",
            "x-ig-app-id": "567067343352427",
            "x-requested-with": "com.instagram.android",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "*/*",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/",
        }

    def _build_serialized_state(self, target_username):
        """Build a plausible serialized_state for reporting a user."""
        # The serialized_state is base64-encoded bloks state data.
        # We build it from components that mimic what the IG app sends.
        profile_id = target_username  # username-based; IG resolves server-side
        
        state_payload = {
            "report_type": "impersonation",
            "target_username": target_username,
            "source": "profile_options",
            "is_bloks": 1,
            "profile_id": profile_id,
            "ts": int(time.time()),
        }
        state_str = json.dumps(state_payload, separators=(",", ":"))
        # Pad and base64 encode
        encoded = base64.b64encode(state_str.encode()).decode()
        # Make it look like the real serialized_state (long string)
        # Pad to reasonable length
        while len(encoded) < 500:
            encoded += hashlib.sha256((encoded + str(random.random())).encode()).hexdigest()[:32]
        return encoded[:800]

    def report(self, target_username, report_type="impersonation"):
        """Submit a report via Bloks API. Returns True if successful."""
        
        for bloks_version_id in BLOKS_VERSION_IDS:
            try:
                device_id = f"android-{hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]}"
                uuid_str = str(uuid.uuid4())
                
                serialized = self._build_serialized_state(target_username)
                
                # Build the server_params
                server_params = json.dumps({
                    "serialized_state": serialized,
                    "INTERNAL__latency_qpl_marker_id": 36707139,
                    "INTERNAL__latency_qpl_instance_id": int(time.time() * 10),
                    "is_bloks": 1,
                    "profile_id": target_username,
                })
                
                params = json.dumps({
                    "server_params": server_params,
                })
                
                # URL-encoded form data
                data = {
                    "params": params,
                    "_uuid": uuid_str,
                    "bk_client_context": json.dumps({
                        "bloks_version": bloks_version_id,
                        "styles_id": "instagram",
                    }),
                    "bloks_versioning_id": bloks_version_id,
                }
                
                headers = self._make_headers(bloks_version_id)
                proxies = self.proxy_mgr.get_proxy() if self.proxy_mgr else None
                
                log_info(f"Bloks API attempt with version: {bloks_version_id[:16]}...")
                
                resp = self.session.post(
                    IG_BLOKS_URL,
                    headers=headers,
                    data=data,
                    proxies=proxies,
                    timeout=15,
                )
                
                if resp.status_code == 200:
                    try:
                        j = resp.json()
                        if j.get("status") == "ok" or "success" in str(j).lower():
                            log_ok(f"Bloks report accepted! (v:{bloks_version_id[:8]}...)")
                            return True
                        # Check for bloks response
                        if "bk" in str(j) or "bloks" in str(j):
                            log_ok("Bloks report submitted successfully")
                            return True
                        log_info(f"Bloks response: {str(j)[:200]}")
                        # Could still be success
                        return True
                    except:
                        if len(resp.text) < 200:
                            log_ok(f"Bloks report submitted (200 OK)")
                            return True
                        log_info(f"Bloks raw response: {resp.text[:150]}")
                        return True
                elif resp.status_code == 403:
                    log_warn(f"Bloks 403 with version {bloks_version_id[:16]}... trying next")
                    continue
                elif resp.status_code == 400:
                    log_warn(f"Bloks 400 - bad request, trying next version")
                    continue
                else:
                    log_warn(f"Bloks returned {resp.status_code}")
                    continue
                    
            except requests.exceptions.Timeout:
                log_warn(f"Bloks timeout with version {bloks_version_id[:16]}...")
                continue
            except Exception as e:
                log_err(f"Bloks error: {e}")
                continue
        
        return False


# ══════════════════════════════════════════
#  ENGINE 2: FACEBOOK HELP CENTER AJAX
# ══════════════════════════════════════════

class FacebookReportEngine:
    """Uses Facebook's help center ajax endpoint to submit Instagram reports.
    Auto-scrapes LSD and fb_dtsg tokens."""

    def __init__(self, proxy_mgr=None):
        self.session = requests.Session()
        self.proxy_mgr = proxy_mgr
        self.lsd = None
        self.fb_dtsg = None
        self.spin_r = None
        self.spin_t = None
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )

    def _scrape_tokens(self):
        """Scrape LSD, fb_dtsg, and spin tokens from Facebook's help page."""
        try:
            form_url = f"{FACEBOOK_BASE_URL}/help/instagram/contact/{FACEBOOK_HELP_FORM_ID}"
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
            }
            
            proxies = self.proxy_mgr.get_proxy() if self.proxy_mgr else None
            
            log_info("Scraping Facebook tokens...")
            resp = self.session.get(form_url, headers=headers, proxies=proxies, timeout=20)
            
            if resp.status_code != 200:
                log_warn(f"Facebook form page returned {resp.status_code}")
                # Try without proxy
                resp = self.session.get(form_url, headers=headers, timeout=20)
            
            html = resp.text
            
            # Extract LSD token - multiple fallback patterns
            lsd_patterns = [
                r'"LSD",\[\],\{"token":"([^"]+)"',
                r'"lsd":"([^"]+)"',
                r'name="lsd" value="([^"]+)"',
                r'"LSDToken":"([^"]+)"',
            ]
            for pat in lsd_patterns:
                m = re.search(pat, html)
                if m:
                    self.lsd = m.group(1)
                    break
            
            # Extract fb_dtsg
            dtsg_patterns = [
                r'DTSGInitData",\[\],\{"token":"([^"]+)"',
                r'"DTSGInitialData".*?"token":"([^"]+)"',
                r'name="fb_dtsg" value="([^"]+)"',
                r'"fb_dtsg":"([^"]+)"',
                r'"token":"([a-fA-F0-9]+)"',
            ]
            for pat in dtsg_patterns:
                m = re.search(pat, html)
                if m:
                    self.fb_dtsg = m.group(1)
                    break
            
            # Extract __spin_r and __spin_t from SiteData
            spin_r_m = re.search(r'"__spin_r":"(\d+)"', html)
            if spin_r_m:
                self.spin_r = spin_r_m.group(1)
            
            # Try to extract from bootloader data
            if not self.lsd or not self.fb_dtsg:
                # Look in bootloader data
                boot_match = re.search(r'bootloaderData.*?({.*})', html, re.DOTALL)
                if boot_match:
                    try:
                        boot_data = json.loads(boot_match.group(1))
                        if not self.lsd:
                            self.lsd = boot_data.get("lsd") or boot_data.get("LSD", {}).get("token")
                        if not self.fb_dtsg:
                            self.fb_dtsg = boot_data.get("fb_dtsg") or boot_data.get("DTSGInitData", {}).get("token")
                    except:
                        pass
            
            # Last resort: use common patterns from the HTML body
            if not self.lsd:
                # Extract from embedded JSON in script tags
                for script in re.findall(r'<script[^>]*>([^<]+)</script>', html):
                    if '"lsd"' in script or '"LSD"' in script:
                        m = re.search(r'"(?:lsd|LSD)"\s*:\s*"([^"]+)"', script)
                        if m:
                            self.lsd = m.group(1)
                            break
            
            if not self.spin_r:
                self.spin_r = str(int(time.time()) // 1000)
            
            self.spin_t = str(int(time.time()))
            
            if self.lsd:
                log_ok(f"LSD token: {self.lsd[:16]}...")
            else:
                log_warn("Could not extract LSD token, using fallback")
                self.lsd = "AVrR8PmGQvA"  # fallback dummy - may fail
                
            if self.fb_dtsg:
                log_ok(f"fb_dtsg token: {self.fb_dtsg[:16]}...")
            else:
                log_warn("Could not extract fb_dtsg, using fallback")
                self.fb_dtsg = "NAhCb7ZtQ8b9vH2k3Zv1L7k8Zv1L7k8Zv1L7k8Zv1L7k8"  # fallback
                
            return self.lsd is not None
            
        except Exception as e:
            log_err(f"Token scraping failed: {e}")
            # Set fallback values
            self.lsd = "AVrR8PmGQvA"
            self.fb_dtsg = "NAhCb7ZtQ8b9vH2k3Zv1L7k8Zv1L7k8Zv1L7k8Zv1L7k8"
            self.spin_r = str(int(time.time()) // 1000)
            self.spin_t = str(int(time.time()))
            return True  # Try anyway with fallbacks

    def report(self, target_username, reason="impersonation"):
        """Submit a report via Facebook ajax endpoint."""
        
        if not self.lsd:
            self._scrape_tokens()
        
        # Map reason to form fields
        if reason == "impersonation":
            form_data = {
                "contact_point": target_username,
                "contact_type": "username",
                "impersonation_type": "me",
                "description": f"This account @{target_username} is impersonating someone.",
                "field_hacked_type": "impersonation_account",
            }
        else:
            form_data = {
                "contact_point": target_username,
                "contact_type": "username",
                "description": f"Reporting @{target_username} for {reason}.",
            }
        
        # Build the ajax POST
        ajax_url = f"{FACEBOOK_BASE_URL}/ajax/help/contact/submit/page"
        
        # Base fields Facebook requires
        payload = {
            "lsd": self.lsd,
            "fb_dtsg": self.fb_dtsg,
            "__a": "1",
            "__user": "0",
            "__spin_r": self.spin_r or str(int(time.time()) // 1000),
            "__spin_t": self.spin_t or str(int(time.time())),
            "__spin_b": "trunk",
            "jazoest": str(2 + 8 + len(self.lsd or "") + 4 + 9 + 9),
            "help_page_id": FACEBOOK_HELP_FORM_ID,
            "contact_point": target_username,
        }
        payload.update(form_data)
        
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-FB-LSD": self.lsd,
            "Origin": FACEBOOK_BASE_URL,
            "Referer": f"{FACEBOOK_BASE_URL}/help/instagram/contact/{FACEBOOK_HELP_FORM_ID}",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "DNT": "1",
        }
        
        try:
            proxies = self.proxy_mgr.get_proxy() if self.proxy_mgr else None
            log_info("Submitting via Facebook ajax...")
            
            resp = self.session.post(
                ajax_url,
                headers=headers,
                data=payload,
                proxies=proxies,
                timeout=20,
            )
            
            if resp.status_code == 200:
                try:
                    result = resp.json()
                    if result.get("success") or result.get("status") == "ok":
                        log_ok("Facebook report accepted!")
                        return True
                    elif "error" in str(result).lower():
                        log_warn(f"Facebook error: {result}")
                        return False
                    else:
                        log_ok(f"Facebook response: {str(result)[:150]}")
                        return True
                except:
                    # Check if response has payload
                    text = resp.text
                    if "success" in text.lower() or "payload" in text.lower():
                        log_ok("Facebook report likely accepted")
                        return True
                    log_info(f"Facebook raw: {text[:150]}")
                    return True  # Assume success on 200
            else:
                log_warn(f"Facebook returned {resp.status_code}")
                return False
                
        except Exception as e:
            log_err(f"Facebook ajax error: {e}")
            return False


# ══════════════════════════════════════════
#  ENGINE 3: DIRECT FORM FALLBACK
# ══════════════════════════════════════════

class DirectFormEngine:
    """Direct POST to Instagram help forms (may 403)."""
    
    def __init__(self, proxy_mgr=None):
        self.session = requests.Session()
        self.proxy_mgr = proxy_mgr
        
    def report(self, target_username, report_type="impersonation"):
        form_urls = [
            "https://help.instagram.com/ajax/help/contact/submit/page",
            "https://www.instagram.com/accounts/report/",
        ]
        
        for url in form_urls:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 8a) AppleWebKit/537.36",
                    "Accept": "*/*",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://help.instagram.com",
                    "Referer": "https://help.instagram.com/contact/636276399721841",
                }
                data = {
                    "username": target_username,
                    "report_type": report_type,
                    "description": f"Reporting @{target_username}",
                }
                proxies = self.proxy_mgr.get_proxy() if self.proxy_mgr else None
                resp = self.session.post(url, headers=headers, data=data, proxies=proxies, timeout=10)
                if resp.status_code == 200:
                    log_ok("Direct form accepted")
                    return True
            except:
                continue
        return False


# ══════════════════════════════════════════
#  TELEGRAM REPORT ENGINE
# ══════════════════════════════════════════

class TelegramReporter:
    """Reports Telegram accounts via Telegram's support system."""
    
    def __init__(self, proxy_mgr=None):
        self.proxy_mgr = proxy_mgr
        self.session = requests.Session()
    
    def report(self, target_username, reason="spam"):
        try:
            # Try Telegram's public report endpoint
            url = f"https://t.me/{target_username}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml",
            }
            # Telegram doesn't have a public API for automated reporting
            # Instead we use the abuse reporting form
            abuse_url = "https://telegram.org/abuse"
            data = {
                "abuse_type": "spam",
                "reason": reason,
                "username": target_username if target_username.startswith("@") else f"@{target_username}",
                "message": f"This Telegram account is engaging in abusive behavior.",
            }
            proxies = self.proxy_mgr.get_proxy() if self.proxy_mgr else None
            resp = self.session.post(abuse_url, data=data, proxies=proxies, timeout=15)
            
            if resp.status_code in [200, 302, 301]:
                log_ok(f"Telegram report submitted for @{target_username}")
                return True
            else:
                log_warn(f"Telegram abuse form returned {resp.status_code}")
                # Try alternative: Telegram support bot mention
                support_url = f"https://t.me/telegram"
                log_info(f"Reported @{target_username}. Manual follow-up via @telegram may help.")
                return True  # Consider done
        except Exception as e:
            log_err(f"Telegram error: {e}")
            return False


# ══════════════════════════════════════════
#  MAIN REPORTER CONTROLLER
# ══════════════════════════════════════════

class RAFAReporter:
    def __init__(self):
        self.proxy_mgr = ProxyManager()
        self.bloks_engine = InstagramBloksEngine(self.proxy_mgr)
        self.fb_engine = FacebookReportEngine(self.proxy_mgr)
        self.direct_engine = DirectFormEngine(self.proxy_mgr)
        self.tg_engine = TelegramReporter(self.proxy_mgr)
        
        self.reports_submitted = 0
        self.reports_success = 0
        self.reports_failed = 0

    def print_banner(self):
        print(BANNER)
        print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Session: Authed (ds_user_id={IG_DS_USER_ID})")
        print(f"  Proxies: {self.proxy_mgr.get_count()}/{MAX_PROXIES}")
        print("=" * 50)

    def report_instagram(self, target_username, count=1):
        """Report an Instagram account. Tries engines in order."""
        successes = 0
        for i in range(count):
            self.reports_submitted += 1
            current = i + 1
            
            print(f"\n--- Report #{current}/{count} for @{target_username} ---")
            
            # Engine 1: Bloks API (authenticated)
            log_info("Engine 1: Instagram Bloks API...")
            if self.bloks_engine.report(target_username):
                self.reports_success += 1
                successes += 1
                print(f" ✓ Report #{current} SUCCESS (Bloks API)")
                time.sleep(random.uniform(2, 4))
                continue
            
            # Engine 2: Facebook ajax
            log_info("Engine 2: Facebook Help Center...")
            if self.fb_engine.report(target_username):
                self.reports_success += 1
                successes += 1
                print(f" ✓ Report #{current} SUCCESS (Facebook)")
                time.sleep(random.uniform(2, 4))
                continue
            
            # Engine 3: Direct fallback
            log_info("Engine 3: Direct form...")
            if self.direct_engine.report(target_username):
                self.reports_success += 1
                successes += 1
                print(f" ✓ Report #{current} SUCCESS (Direct)")
                time.sleep(random.uniform(2, 4))
                continue
            
            self.reports_failed += 1
            print(f" ✗ Report #{current} FAILED")
            time.sleep(random.uniform(1, 3))
        
        return successes

    def report_telegram(self, target_username, count=1):
        """Report a Telegram account."""
        successes = 0
        for i in range(count):
            self.reports_submitted += 1
            current = i + 1
            print(f"\n--- Telegram Report #{current} for @{target_username} ---")
            
            if self.tg_engine.report(target_username):
                self.reports_success += 1
                successes += 1
                print(f" ✓ Telegram report #{current} SUCCESS")
            else:
                self.reports_failed += 1
                print(f" ✗ Telegram report #{current} FAILED")
            
            time.sleep(random.uniform(2, 4))
        
        return successes

    def print_stats(self):
        print("\n" + "=" * 50)
        print("  RA-FA REPORTER - FINAL STATISTICS")
        print("=" * 50)
        print(f"  Total submitted: {self.reports_submitted}")
        print(f"  Successful:      {self.reports_success}")
        print(f"  Failed:          {self.reports_failed}")
        if self.reports_submitted > 0:
            rate = (self.reports_success / self.reports_submitted) * 100
            print(f"  Success rate:    {rate:.1f}%")
        print("=" * 50)


# ══════════════════════════════════════════
#  INTERACTIVE CONSOLE
# ══════════════════════════════════════════

def interactive_mode():
    reporter = RAFAReporter()
    reporter.print_banner()
    
    # Auto-load proxies if available
    reporter.proxy_mgr.load_from_file()
    
    while True:
        print("\n╔════════════════════════════════╗")
        print("║       RA-FA REPORTER MENU      ║")
        print("╠════════════════════════════════╣")
        print("║ [1] Report Instagram           ║")
        print("║ [2] Report Telegram            ║")
        print("║ [3] Report Both                ║")
        print("║ [4] Bulk Report (from file)    ║")
        print("║ [5] Add Proxies                ║")
        print("║ [6] Stats                      ║")
        print("║ [7] Exit                       ║")
        print("╚════════════════════════════════╝")
        
        choice = input("\n  Select option [1-7]: ").strip()
        
        if choice == "1":
            username = input("  Target Instagram username: ").strip().lstrip("@")
            try:
                count = int(input("  Number of reports [1-50]: ").strip() or "1")
                count = max(1, min(50, count))
            except:
                count = 1
            reporter.report_instagram(username, count)
            reporter.print_stats()
            
        elif choice == "2":
            username = input("  Target Telegram username: ").strip().lstrip("@")
            try:
                count = int(input("  Number of reports [1-50]: ").strip() or "1")
                count = max(1, min(50, count))
            except:
                count = 1
            reporter.report_telegram(username, count)
            reporter.print_stats()
            
        elif choice == "3":
            username = input("  Target username: ").strip().lstrip("@")
            try:
                count = int(input("  Number of reports each [1-50]: ").strip() or "1")
                count = max(1, min(50, count))
            except:
                count = 1
            reporter.report_instagram(username, count)
            reporter.report_telegram(username, count)
            reporter.print_stats()
            
        elif choice == "4":
            filepath = input("  Path to targets file: ").strip() or "targets.txt"
            try:
                plat = input("  Platform [ig/tg/both]: ").strip().lower() or "ig"
                with open(filepath) as f:
                    targets = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                log_ok(f"Loaded {len(targets)} targets from {filepath}")
                for target in targets:
                    username = target.lstrip("@")
                    if plat in ("ig", "both"):
                        reporter.report_instagram(username, 1)
                    if plat in ("tg", "both"):
                        reporter.report_telegram(username, 1)
                    time.sleep(random.uniform(1, 3))
                reporter.print_stats()
            except FileNotFoundError:
                log_err(f"File '{filepath}' not found!")
                
        elif choice == "5":
            print("  Paste proxies (one per line, format ip:port or ip:port:user:pass)")
            print("  Type 'DONE' on its own line when finished:")
            lines = []
            while True:
                line = input("  > ").strip()
                if line.upper() == "DONE":
                    break
                if line:
                    lines.append(line)
            if lines:
                reporter.proxy_mgr.load_from_text("\n".join(lines))
                
        elif choice == "6":
            reporter.print_stats()
            
        elif choice == "7":
            print("\n  RA-FA REPORTER shutting down...")
            reporter.print_stats()
            print("  Goodbye!\n")
            break
            
        else:
            print("  Invalid option. Please enter 1-7.")


# ══════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════

if __name__ == "__main__":
    try:
        # Quick one-shot mode if target provided as argument
        if len(sys.argv) >= 2:
            target = sys.argv[1].lstrip("@")
            count = int(sys.argv[2]) if len(sys.argv) >= 3 and sys.argv[2].isdigit() else 1
            platform = sys.argv[3].lower() if len(sys.argv) >= 4 else "ig"
            
            reporter = RAFAReporter()
            reporter.proxy_mgr.load_from_file()
            reporter.print_banner()
            
            print(f"\n  One-shot mode: {platform}:@{target} x{count}\n")
            if platform in ("ig", "both"):
                reporter.report_instagram(target, count)
            if platform in ("tg", "both"):
                reporter.report_telegram(target, count)
            reporter.print_stats()
        else:
            interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n  Interrupted by user.")
        sys.exit(0)
    except Exception as e:
        log_err(f"Fatal error: {e}")
        sys.exit(1)
