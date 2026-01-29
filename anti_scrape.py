"""
Anti-Scraping Protection Module

Protects doctor data from automated scraping by:
1. Blocking known bot user agents
2. Blocking data center IP ranges
3. Rate limiting doctor listing/profile pages
4. Detecting scraping patterns
"""

import re
from functools import wraps
from flask import request, abort, session, jsonify
from datetime import datetime, timedelta
import ipaddress

# Known bot user agents (case-insensitive patterns)
BOT_USER_AGENTS = [
    r'curl',
    r'wget',
    r'python-requests',
    r'python-urllib',
    r'scrapy',
    r'httpclient',
    r'java/',
    r'libwww',
    r'httpunit',
    r'nutch',
    r'phpcrawl',
    r'msnbot',
    r'jyxobot',
    r'fast-webcrawler',
    r'fast enterprise crawler',
    r'convera',
    r'biglotron',
    r'grub\.org',
    r'usinenouvellecrawler',
    r'antibot',
    r'netresearchserver',
    r'speedy spider',
    r'fluffy',
    r'findlink',
    r'panscient',
    r'ips-agent',
    r'yanga',
    r'cyberpatrol',
    r'postrank',
    r'page2rss',
    r'linkdex',
    r'ezooms',
    r'heritrix',
    r'findthatfile',
    r'europarchive\.org',
    r'mappydata',
    r'eright',
    r'apercite',
    r'aboundex',
    r'summify',
    r'ec2',  # AWS
    r'phantom',
    r'headless',
    r'selenium',
    r'webdriver',
    r'puppeteer',
    r'playwright',
]

# Compile patterns for efficiency
BOT_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in BOT_USER_AGENTS]

# Data center IP ranges (major cloud providers)
# These are CIDR ranges - scrapers often run from these
DATA_CENTER_CIDRS = [
    # AWS (partial - main ranges)
    "3.0.0.0/8",
    "13.0.0.0/8",
    "18.0.0.0/8",
    "34.0.0.0/8",
    "35.0.0.0/8",
    "52.0.0.0/8",
    "54.0.0.0/8",
    # Google Cloud (partial)
    "34.64.0.0/10",
    "35.184.0.0/13",
    "35.192.0.0/12",
    "35.208.0.0/12",
    "35.224.0.0/12",
    "35.240.0.0/13",
    # Azure (partial)
    "13.64.0.0/11",
    "13.96.0.0/13",
    "13.104.0.0/14",
    "20.0.0.0/8",
    "40.64.0.0/10",
    "51.0.0.0/8",
    "52.0.0.0/8",
    # DigitalOcean (partial)
    "104.131.0.0/16",
    "104.236.0.0/16",
    "138.68.0.0/16",
    "139.59.0.0/16",
    "142.93.0.0/16",
    "157.230.0.0/16",
    "159.65.0.0/16",
    "159.89.0.0/16",
    "161.35.0.0/16",
    "164.90.0.0/16",
    "165.22.0.0/16",
    "167.71.0.0/16",
    "167.99.0.0/16",
    "178.62.0.0/16",
    "188.166.0.0/16",
    "206.189.0.0/16",
    # Hetzner
    "95.216.0.0/16",
    "135.181.0.0/16",
    "65.21.0.0/16",
    # OVH (partial)
    "51.68.0.0/16",
    "51.75.0.0/16",
    "51.77.0.0/16",
    "51.79.0.0/16",
    "51.83.0.0/16",
    "51.89.0.0/16",
    "51.91.0.0/16",
    "54.36.0.0/16",
    "54.37.0.0/16",
    "54.38.0.0/16",
    "54.39.0.0/16",
    # Vultr
    "45.32.0.0/16",
    "45.63.0.0/16",
    "45.76.0.0/16",
    "45.77.0.0/16",
    "64.156.0.0/16",
    "66.42.0.0/16",
    "104.156.0.0/16",
    "108.61.0.0/16",
    "140.82.0.0/16",
    "149.28.0.0/16",
    "155.138.0.0/16",
    "207.148.0.0/16",
    "209.250.0.0/16",
    "217.69.0.0/16",
    # Linode
    "45.33.0.0/16",
    "45.56.0.0/16",
    "45.79.0.0/16",
    "50.116.0.0/16",
    "66.175.0.0/16",
    "69.164.0.0/16",
    "72.14.0.0/16",
    "74.207.0.0/16",
    "96.126.0.0/16",
    "97.107.0.0/16",
    "139.162.0.0/16",
    "172.104.0.0/16",
    "173.255.0.0/16",
    "178.79.0.0/16",
    "192.155.0.0/16",
    "198.58.0.0/16",
]

# Parse CIDR ranges into network objects
DATA_CENTER_NETWORKS = []
for cidr in DATA_CENTER_CIDRS:
    try:
        DATA_CENTER_NETWORKS.append(ipaddress.ip_network(cidr, strict=False))
    except ValueError:
        pass  # Skip invalid CIDRs

# In-memory request tracking (for pattern detection)
# In production, use Redis for distributed tracking
request_history = {}
HISTORY_CLEANUP_INTERVAL = 300  # Clean up every 5 minutes
last_cleanup = datetime.now()

# Honeypot blocked IPs (bots that followed hidden links)
honeypot_blocked_ips = set()

def add_to_honeypot_blocklist(ip):
    """Add IP to honeypot blocklist"""
    honeypot_blocked_ips.add(ip)
    print(f"[HONEYPOT] Blocked bot IP: {ip}")

def is_honeypot_blocked(ip):
    """Check if IP was caught by honeypot"""
    return ip in honeypot_blocked_ips


# Cache for verified bot IPs (IP -> is_verified)
import socket
_verified_bot_cache = {}
_bot_cache_max_size = 1000

def verify_bot_reverse_dns(ip, expected_domains):
    """
    Verify bot by reverse DNS lookup.
    Returns True if IP resolves to one of the expected domains.
    """
    if ip in _verified_bot_cache:
        return _verified_bot_cache[ip]

    try:
        # Reverse DNS lookup
        hostname, _, _ = socket.gethostbyaddr(ip)
        hostname = hostname.lower()

        # Check if hostname ends with expected domain
        is_valid = any(hostname.endswith(domain) for domain in expected_domains)

        # Forward lookup to verify (prevents DNS spoofing)
        if is_valid:
            try:
                resolved_ip = socket.gethostbyname(hostname)
                is_valid = (resolved_ip == ip)
            except socket.gaierror:
                is_valid = False

        # Cache result (limit cache size)
        if len(_verified_bot_cache) < _bot_cache_max_size:
            _verified_bot_cache[ip] = is_valid

        return is_valid
    except (socket.herror, socket.gaierror):
        # DNS lookup failed - not a verified bot
        if len(_verified_bot_cache) < _bot_cache_max_size:
            _verified_bot_cache[ip] = False
        return False


def is_legitimate_bot(user_agent):
    """
    Check if user agent is a legitimate search engine/social bot (good for SEO).
    For major bots (Google, Bing), verifies via reverse DNS to prevent spoofing.
    Note: When behind Cloudflare, we skip DNS verification since we can't verify
    the actual bot IP through the proxy.
    """
    if not user_agent:
        return False

    user_agent_lower = user_agent.lower()

    # Check if we're behind Cloudflare - if so, we can't do proper reverse DNS
    # verification because we only see Cloudflare proxy IPs, not the real bot IPs.
    # In this case, trust the user-agent for search engine bots.
    behind_cloudflare = request.headers.get('CF-Ray') is not None

    # Major search engine bots
    search_bots = ['googlebot', 'bingbot', 'apis-google', 'mediapartners-google', 'adsbot-google']

    for bot_name in search_bots:
        if bot_name in user_agent_lower:
            if behind_cloudflare:
                # Behind Cloudflare - can't verify IP, trust the user-agent
                # Cloudflare provides some bot protection already
                return True
            else:
                # Not behind Cloudflare - can verify via reverse DNS
                domains = {
                    'googlebot': ['.googlebot.com', '.google.com'],
                    'bingbot': ['.search.msn.com'],
                    'apis-google': ['.googlebot.com', '.google.com'],
                    'mediapartners-google': ['.googlebot.com', '.google.com'],
                    'adsbot-google': ['.googlebot.com', '.google.com'],
                }.get(bot_name, [])

                ip = get_real_ip()
                if verify_bot_reverse_dns(ip, domains):
                    return True
                else:
                    print(f"[ANTI-SCRAPE] Failed bot verification: {bot_name} from {ip}")
                    return False

    # Social media bots (lower risk, allow without verification)
    social_bots = ['facebookexternalhit', 'twitterbot', 'linkedinbot', 'whatsapp',
                   'slackbot', 'applebot', 'duckduckbot', 'yandexbot', 'baiduspider']
    for bot in social_bots:
        if bot in user_agent_lower:
            return True

    return False


def is_bot_user_agent(user_agent):
    """Check if user agent matches known scraping bot patterns"""
    if not user_agent:
        return True  # No user agent = suspicious

    # Allow legitimate search engine bots (good for SEO)
    if is_legitimate_bot(user_agent):
        return False  # Allow legitimate bots

    # Block scraping bots
    for pattern in BOT_PATTERNS:
        if pattern.search(user_agent):
            return True
    return False


def is_missing_browser_headers():
    """
    Detect bots by checking for missing headers that real browsers always send.
    Real browsers send Accept, Accept-Language, Accept-Encoding.
    Bots often forget these or send unusual values.
    """
    # Check for Accept header (browsers always send this)
    accept = request.headers.get('Accept', '')
    if not accept:
        return True

    # Check for Accept-Language (browsers always send this)
    accept_lang = request.headers.get('Accept-Language', '')
    if not accept_lang:
        return True

    # Check for Accept-Encoding (browsers always send this)
    accept_encoding = request.headers.get('Accept-Encoding', '')
    if not accept_encoding:
        return True

    # Check for suspicious Accept header (bots often use generic "*/*")
    # Real browsers specify html, xhtml, xml, etc.
    if accept == '*/*' and 'html' not in accept.lower():
        # Could be an API call or bot - only flag on doctor pages
        pass  # Don't block, just note it

    return False


def is_data_center_ip(ip_str):
    """Check if IP belongs to a known data center"""
    if not ip_str:
        return False

    try:
        ip = ipaddress.ip_address(ip_str)
        for network in DATA_CENTER_NETWORKS:
            if ip in network:
                return True
    except ValueError:
        pass  # Invalid IP format

    return False


def get_real_ip():
    """Get real client IP respecting proxies"""
    # Check Cloudflare header first
    cf_ip = request.headers.get('CF-Connecting-IP')
    if cf_ip:
        return cf_ip

    # Check X-Forwarded-For
    xff = request.headers.get('X-Forwarded-For')
    if xff:
        # Take the first IP (client IP)
        return xff.split(',')[0].strip()

    # Check X-Real-IP
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip

    return request.remote_addr


def track_request(ip, path):
    """Track request for pattern detection"""
    global last_cleanup, request_history

    now = datetime.now()

    # Cleanup old entries periodically
    if (now - last_cleanup).total_seconds() > HISTORY_CLEANUP_INTERVAL:
        cutoff = now - timedelta(minutes=10)
        request_history = {
            k: [t for t in v if t > cutoff]
            for k, v in request_history.items()
            if any(t > cutoff for t in v)
        }
        last_cleanup = now

    # Track this request
    key = f"{ip}:{path}"
    if key not in request_history:
        request_history[key] = []
    request_history[key].append(now)


def is_scraping_pattern(ip):
    """Detect extreme scraping patterns based on request history"""
    now = datetime.now()
    one_minute_ago = now - timedelta(minutes=1)

    # Count recent requests from this IP to doctor-related pages
    doctor_page_count = 0
    for key, timestamps in request_history.items():
        if key.startswith(f"{ip}:") and ('/doctor/' in key or '/doctors' in key):
            recent = [t for t in timestamps if t > one_minute_ago]
            doctor_page_count += len(recent)

    # Only block extreme scraping: 100+ doctor page requests per minute
    # Regular users might browse 10-20 pages, scrapers hit 100s
    return doctor_page_count > 100


def anti_scrape_check():
    """
    Main anti-scraping check. Returns None if OK, or error response if blocked.
    """
    ip = get_real_ip()

    # Check honeypot blocklist first for everyone (including logged-in users)
    if is_honeypot_blocked(ip):
        return ('Access denied', 403)

    # Logged-in users get lighter checks but not completely exempt
    if session.get('user_id'):
        # Still check for extreme scraping patterns (100+ requests/min)
        track_request(ip, request.path)
        if is_scraping_pattern(ip):
            return ('Too many requests. Please slow down.', 429)
        return None

    user_agent = request.headers.get('User-Agent', '')

    # Skip ALL checks for legitimate search engine bots (critical for SEO!)
    # Googlebot, Bingbot, etc. come from data center IPs but must be allowed
    if is_legitimate_bot(user_agent):
        return None

    path = request.path

    # 1. Check user agent (blocks bad bots like scrapy, curl, etc.)
    if is_bot_user_agent(user_agent):
        # Don't reveal why - just return 403
        return ('Access denied', 403)

    # 1.5 Check for missing browser headers (only on doctor pages to avoid false positives)
    if '/doctor' in path or '/doctors' in path:
        if is_missing_browser_headers():
            print(f"[ANTI-SCRAPE] Missing browser headers from: {ip}")
            return ('Access denied', 403)

    # 2. Check data center IPs (only for doctor data pages)
    if '/doctor' in path or '/doctors' in path or '/api/' in path:
        if is_data_center_ip(ip):
            # Log for monitoring
            print(f"[ANTI-SCRAPE] Blocked data center IP: {ip} on {path}")
            return ('Access denied', 403)

    # 3. Track and check for scraping patterns
    track_request(ip, path)
    if is_scraping_pattern(ip):
        print(f"[ANTI-SCRAPE] Scraping pattern detected: {ip}")
        return ('Too many requests', 429)

    return None


def protect_from_scraping(f):
    """
    Decorator to protect routes from scraping.
    Use on doctor listing and profile routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        result = anti_scrape_check()
        if result:
            message, code = result
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': message}), code
            abort(code)
        return f(*args, **kwargs)
    return decorated_function


# Middleware version for use with before_request
def anti_scrape_middleware():
    """
    Use with app.before_request for global protection.
    Only checks doctor-related routes to avoid blocking legitimate traffic.
    """
    path = request.path

    # Only apply to sensitive routes
    sensitive_paths = ['/doctors', '/doctor/', '/api/doctors', '/api/search']
    if not any(path.startswith(p) or p in path for p in sensitive_paths):
        return None

    result = anti_scrape_check()
    if result:
        message, code = result
        if request.is_json or path.startswith('/api/'):
            return jsonify({'error': message}), code
        abort(code)

    return None
