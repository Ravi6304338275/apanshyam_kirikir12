# #!/usr/bin/env python3
# """LinkedIn scraper with resume support - Repository 1"""

# import sys
# import os
# import time
# import requests
# import urllib.parse
# from dotenv import load_dotenv

# load_dotenv()

# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# from src.linkedin_scraper import LinkedInScraper


# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# TABLE = "scraper_progress_repo1"

# HEADERS = {
#     "apikey": SUPABASE_KEY,
#     "Authorization": f"Bearer {SUPABASE_KEY}",
#     "Content-Type": "application/json"
# }


# # --------------------------------------------------
# # Extract external apply links
# # --------------------------------------------------

# def extract_external_link(link):

#     if not link:
#         return link

#     if "linkedin.com/jobs/redirect" in link:

#         parsed = urllib.parse.urlparse(link)
#         params = urllib.parse.parse_qs(parsed.query)

#         if "url" in params:
#             return urllib.parse.unquote(params["url"][0])

#     return link


# # --------------------------------------------------
# # Ensure progress row exists
# # --------------------------------------------------

# def ensure_row_exists():

#     url = f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.1"

#     r = requests.get(url, headers=HEADERS)

#     if r.status_code == 200 and len(r.json()) == 0:

#         insert_url = f"{SUPABASE_URL}/rest/v1/{TABLE}"

#         data = {"id": 1, "last_index": 0}

#         headers = HEADERS.copy()
#         headers["Prefer"] = "return=minimal"

#         requests.post(insert_url, headers=headers, json=data)


# # --------------------------------------------------
# # Get progress
# # --------------------------------------------------

# def get_progress():

#     ensure_row_exists()

#     url = f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.1"

#     r = requests.get(url, headers=HEADERS)

#     if r.status_code == 200 and r.json():
#         return r.json()[0]["last_index"]

#     return 0


# # --------------------------------------------------
# # Update progress
# # --------------------------------------------------

# def update_progress(index):

#     url = f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.1"

#     headers = HEADERS.copy()
#     headers["Prefer"] = "return=minimal"

#     data = {"last_index": index}

#     r = requests.patch(url, headers=headers, json=data)

#     if r.status_code in [200,204]:
#         print(f"✅ Progress updated → {index}")
#     else:
#         print("⚠️ Failed to update progress:", r.text)


# # --------------------------------------------------
# # Main scraper
# # --------------------------------------------------

# def main():

#     print("=" * 70)
#     print("🚀 LINKEDIN SCRAPER WITH AUTO RESUME - REPO 1")
#     print("=" * 70)

#     all_keywords = [
#         "Actimize Developer","Active Directory","Agronomy Operations","AI/ML Engineer",
#         "Anti Money Laundering (AML)","Atlassian Engineer / Jira","Big Data Engineer",
#         "Bioinformatics","Bioinformatics for UK","Biotechnology","Biotechnology Internship",
#         "Business Analyst","Business Analyst for Canada","Business Intelligence Engineer",
#         "Business Intelligence Engineer Internships","Chemical Engineer","CLINICAL DATA ANALYST",
#         "Clinical Research Coordinator","Cloud Engineer","Cloud Engineer for Ireland",
#         "Computer Science","Computer Science Internship","Construction Management",
#         "Credit controller for UK","CRM Sales","CRM Specialist","Cyber security",
#         "Cybersecurity for Ireland","Cybersecurity for UK","Data Analyst",
#         "Data Analyst for Canada","Data Analyst for UK","Data Analyst Internship for Ireland",
#         "Data Analyst Internships","Database Administration","Data Center Technician",
#         "Data Engineer","Data Engineer (citizen/h4ead)","Data Engineer for UK",
#         "Data Science for Germany","Data Scientist","Design Verification Engineer",
#         "DevOps","DevOps for India","DevOps for Ireland","DevOps for UK","DevOps Internships",
#         "Dynamics 365","Electrical Engineer","Electrical Project",
#         "Electronic Health Records (EHR)","Embedded Software Engineer",
#         "Environmental Health and Safety (EHS)","Epic Analyst","ERP","Financial analyst",
#         "Financial analyst for Ireland","Frontend Engineering","Full Stack",
#         "Game Developer","Game UI / Interactive UI Designer","Generative AI"
#     ]

#     location = os.getenv("LOCATION","United States")
#     max_workers = int(os.getenv("MAX_WORKERS","5"))

#     scraper = LinkedInScraper(use_database=True)

#     start_index = get_progress()

#     print(f"\n▶ Resuming from keyword index: {start_index}")
#     print(f"📊 Total keywords: {len(all_keywords)}")

#     start_time = time.time()

#     total_jobs = 0

#     for i in range(start_index,len(all_keywords)):

#         keyword = all_keywords[i]

#         print("\n" + "-" * 60)
#         print(f"🔍 Scraping keyword {i+1}/{len(all_keywords)}: {keyword}")
#         print("-" * 60)

#         try:

#             jobs = scraper.scrape_all_jobs_batch(
#                 keywords=[keyword],
#                 location=location,
#                 max_workers=max_workers,
#                 save_to_db=True,
#             )

#             for job in jobs:
#                 if "url" in job:
#                     job["url"] = extract_external_link(job["url"])

#             total_jobs += len(jobs)

#             update_progress(i+1)

#         except Exception as e:
#             print(f"❌ Error scraping keyword {keyword}: {e}")

#     update_progress(0)

#     elapsed = time.time() - start_time

#     print("\n" + "=" * 70)
#     print("✅ SCRAPER RUN COMPLETE")
#     print("=" * 70)
#     print(f"Jobs scraped: {total_jobs}")
#     print(f"Total runtime: {elapsed/60:.1f} minutes")


# if __name__ == "__main__":
#     main()









































#!/usr/bin/env python3
"""LinkedIn scraper with resume support - Repository 1"""

import sys
import os
import re
import time
import requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.linkedin_scraper import LinkedInScraper


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

TABLE = "scraper_progress_repo1"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ── HTTP session reused across all redirect-follow calls ──────────────────────
_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
})

# All LinkedIn redirect / offsite hostname patterns
_LINKEDIN_REDIRECT_HOSTS = {
    "linkedin.com",
    "www.linkedin.com",
    "offsite.linkedin.com",
    "lnkd.in",
}

# Query-param keys LinkedIn uses to embed the destination URL
_REDIRECT_PARAM_KEYS = ["url", "redirect", "dest", "destination", "externalUrl"]


# ==============================================================================
# ROBUST EXTERNAL LINK EXTRACTOR  (multi-strategy, with HTTP fallback)
# ==============================================================================

def _decode_url(raw):
    """Aggressively decode a possibly double/triple-encoded URL."""
    prev = None
    url = raw
    while url != prev:
        prev = url
        url = urllib.parse.unquote(url)
    return url.strip()


def _extract_from_query_params(parsed):
    """Try every known redirect-param key in the query string."""
    params = urllib.parse.parse_qs(parsed.query, keep_blank_values=False)
    for key in _REDIRECT_PARAM_KEYS:
        if key in params:
            return _decode_url(params[key][0])
    # Also try case-insensitive match
    lower_params = {k.lower(): v for k, v in params.items()}
    for key in _REDIRECT_PARAM_KEYS:
        if key.lower() in lower_params:
            return _decode_url(lower_params[key.lower()][0])
    return None


def _is_linkedin_url(url):
    """Return True if the URL belongs to a LinkedIn domain."""
    try:
        host = urllib.parse.urlparse(url).netloc.lower().lstrip("www.")
        return any(host == h or host.endswith("." + h) for h in _LINKEDIN_REDIRECT_HOSTS)
    except Exception:
        return False


def _follow_redirect(url, timeout=8, max_hops=5):
    """
    Follow HTTP redirects manually so we can inspect every hop.
    Returns the first non-LinkedIn URL encountered, or the final URL.
    """
    current = url
    for _ in range(max_hops):
        try:
            resp = _SESSION.head(
                current,
                allow_redirects=False,
                timeout=timeout,
            )
            location = resp.headers.get("Location", "")
            if not location:
                # HEAD gave nothing - try GET (some servers block HEAD)
                resp = _SESSION.get(
                    current,
                    allow_redirects=False,
                    timeout=timeout,
                    stream=True,
                )
                resp.close()
                location = resp.headers.get("Location", "")

            if not location:
                break

            # Resolve relative redirects
            location = urllib.parse.urljoin(current, location)
            location = _decode_url(location)

            if not _is_linkedin_url(location):
                return location          # found external URL via HTTP hop

            current = location

        except requests.exceptions.RequestException:
            break   # network error - return whatever we have

    return current


def extract_external_link(link):
    """
    Robust multi-strategy LinkedIn external-link resolver.

    Strategy order:
      1. Parse query-string params directly   (fast, no network)
      2. Check for /jobs/redirect path        (fast, no network)
      3. Regex scan raw URL for embedded URLs (fast, no network)
      4. HTTP redirect-follow fallback        (slow, network)
    """
    if not link:
        return link

    try:
        parsed = urllib.parse.urlparse(link)
    except Exception:
        return link

    # ── Strategy 1: query-param extraction ────────────────────────────────────
    candidate = _extract_from_query_params(parsed)
    if candidate and not _is_linkedin_url(candidate):
        return candidate

    # ── Strategy 2: well-known redirect paths ─────────────────────────────────
    path_lower = parsed.path.lower()
    redirect_paths = (
        "/jobs/redirect",
        "/redir/",
        "/redirect",
        "/offsite/",
    )
    if any(path_lower.startswith(p) for p in redirect_paths):
        # Already tried query params above; fall through to HTTP follow
        pass

    # ── Strategy 3: regex - find any http/https URL embedded raw in the link ──
    # Handles cases like: ?url=https%3A%2F%2F... that survived partial decoding
    raw_decoded = _decode_url(link)
    embedded = re.findall(r'https?://[^\s"\'<>]+', raw_decoded)
    for found in embedded:
        if not _is_linkedin_url(found):
            # Clean trailing punctuation that regex may have grabbed
            found = found.rstrip(".,;)")
            return found

    # ── Strategy 4: HTTP redirect follow (network fallback) ───────────────────
    if _is_linkedin_url(link):
        resolved = _follow_redirect(link)
        if not _is_linkedin_url(resolved):
            return resolved

    return link   # nothing worked - return original unchanged


# ==============================================================================
# BATCH URL RESOLVER  (parallel, 5 workers max)
# ==============================================================================

def resolve_external_links_batch(jobs, max_workers=5):
    """
    Resolve external apply URLs for all jobs in parallel.
    Only jobs whose URL still points to LinkedIn get the HTTP-follow treatment;
    the rest are resolved via fast parse-only strategies.
    """
    if not jobs:
        return jobs

    def resolve_one(idx_job):
        idx, job = idx_job
        original = job.get("url") or job.get("apply_url") or ""
        if not original:
            return idx, job, False

        resolved = extract_external_link(original)

        # Write back to whichever key(s) held the URL
        if "url" in job:
            job["url"] = resolved
        if "apply_url" in job:
            job["apply_url"] = resolved

        changed = resolved != original
        return idx, job, changed

    changed_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(resolve_one, (i, job)): i
            for i, job in enumerate(jobs)
        }
        for future in as_completed(futures):
            try:
                i, resolved_job, changed = future.result()
                jobs[i] = resolved_job
                if changed:
                    changed_count += 1
            except Exception as exc:
                print(f"  URL resolution error for job index {futures[future]}: {exc}")

    if changed_count:
        print(f"  Resolved {changed_count}/{len(jobs)} external redirect(s)")

    return jobs


# ==============================================================================
# SUPABASE HELPERS
# ==============================================================================

def ensure_row_exists():

    url = f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.1"

    r = requests.get(url, headers=HEADERS)

    if r.status_code == 200 and len(r.json()) == 0:

        insert_url = f"{SUPABASE_URL}/rest/v1/{TABLE}"

        data = {"id": 1, "last_index": 0}

        headers = HEADERS.copy()
        headers["Prefer"] = "return=minimal"

        requests.post(insert_url, headers=headers, json=data)


def get_progress():

    ensure_row_exists()

    url = f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.1"

    r = requests.get(url, headers=HEADERS)

    if r.status_code == 200 and r.json():
        return r.json()[0]["last_index"]

    return 0


def update_progress(index):

    url = f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.1"

    headers = HEADERS.copy()
    headers["Prefer"] = "return=minimal"

    data = {"last_index": index}

    r = requests.patch(url, headers=headers, json=data)

    if r.status_code in [200, 204]:
        print(f"  Progress updated -> {index}")
    else:
        print("  Failed to update progress:", r.text)


# ==============================================================================
# MAIN
# ==============================================================================

def main():

    print("=" * 70)
    print("LINKEDIN SCRAPER WITH AUTO RESUME - REPO 1")
    print("=" * 70)

    all_keywords = [
        "Actimize Developer","Active Directory","Agronomy Operations","AI/ML Engineer",
        "Anti Money Laundering (AML)","Atlassian Engineer / Jira","Big Data Engineer",
        "Bioinformatics","Bioinformatics for UK","Biotechnology","Biotechnology Internship",
        "Business Analyst","Business Analyst for Canada","Business Intelligence Engineer",
        "Business Intelligence Engineer Internships","Chemical Engineer","CLINICAL DATA ANALYST",
        "Clinical Research Coordinator","Cloud Engineer","Cloud Engineer for Ireland",
        "Computer Science","Computer Science Internship","Construction Management",
        "Credit controller for UK","CRM Sales","CRM Specialist","Cyber security",
        "Cybersecurity for Ireland","Cybersecurity for UK","Data Analyst",
        "Data Analyst for Canada","Data Analyst for UK","Data Analyst Internship for Ireland",
        "Data Analyst Internships","Database Administration","Data Center Technician",
        "Data Engineer","Data Engineer (citizen/h4ead)","Data Engineer for UK",
        "Data Science for Germany","Data Scientist","Design Verification Engineer",
        "DevOps","DevOps for India","DevOps for Ireland","DevOps for UK","DevOps Internships",
        "Dynamics 365","Electrical Engineer","Electrical Project",
        "Electronic Health Records (EHR)","Embedded Software Engineer",
        "Environmental Health and Safety (EHS)","Epic Analyst","ERP","Financial analyst",
        "Financial analyst for Ireland","Frontend Engineering","Full Stack",
        "Game Developer","Game UI / Interactive UI Designer","Generative AI"
    ]

    location = os.getenv("LOCATION", "United States")
    max_workers = 5   # fixed at 5 workers

    scraper = LinkedInScraper(use_database=True)

    start_index = get_progress()

    print(f"\n  Resuming from keyword index: {start_index}")
    print(f"  Total keywords: {len(all_keywords)}")

    start_time = time.time()

    total_jobs = 0

    for i in range(start_index, len(all_keywords)):

        keyword = all_keywords[i]

        print("\n" + "-" * 60)
        print(f"  Scraping keyword {i+1}/{len(all_keywords)}: {keyword}")
        print("-" * 60)

        try:

            jobs = scraper.scrape_all_jobs_batch(
                keywords=[keyword],
                location=location,
                max_workers=max_workers,
                save_to_db=True,
            )

            # ── Resolve external links robustly (parallel, 5 workers) ─────────
            jobs = resolve_external_links_batch(jobs, max_workers=max_workers)

            total_jobs += len(jobs)

            update_progress(i + 1)

        except Exception as e:
            print(f"  Error scraping keyword {keyword}: {e}")

    update_progress(0)

    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print("SCRAPER RUN COMPLETE")
    print("=" * 70)
    print(f"Jobs scraped: {total_jobs}")
    print(f"Total runtime: {elapsed/60:.1f} minutes")


if __name__ == "__main__":
    main()
