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

#     try:

#         # Handle LinkedIn redirect links
#         if "linkedin.com/jobs/redirect" in link or "linkedin.com/redir" in link:

#             parsed = urllib.parse.urlparse(link)
#             params = urllib.parse.parse_qs(parsed.query)

#             for key in ["url", "redirect", "target"]:
#                 if key in params:
#                     return urllib.parse.unquote(params[key][0])

#         # Some LinkedIn jobs use tracking parameters
#         parsed = urllib.parse.urlparse(link)
#         clean_link = parsed.scheme + "://" + parsed.netloc + parsed.path

#         return clean_link

#     except Exception:
#         return link


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

#     if r.status_code in [200, 204]:
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

#     for i in range(start_index, len(all_keywords)):

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

#             # Normalize possible link fields
#             for job in jobs:

#                 link_fields = [
#                     "url",
#                     "job_url",
#                     "apply_url",
#                     "apply_link",
#                     "external_apply_link"
#                 ]

#                 for field in link_fields:
#                     if field in job and job[field]:
#                         job[field] = extract_external_link(job[field])

#             total_jobs += len(jobs)

#             update_progress(i + 1)

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
import time
import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.linkedin_scraper import LinkedInScraper


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

TABLE   = "scraper_progress_repo1"
WORKERS = 5   # fixed — do not change

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


# ─────────────────────────────────────────────────────────────────────────────
# Supabase progress helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_row():
    url = f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.1"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200 and len(r.json()) == 0:
        h = {**HEADERS, "Prefer": "return=minimal"}
        requests.post(f"{SUPABASE_URL}/rest/v1/{TABLE}",
                      headers=h, json={"id": 1, "last_index": 0})


def get_progress() -> int:
    _ensure_row()
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.1", headers=HEADERS)
    if r.status_code == 200 and r.json():
        return r.json()[0]["last_index"]
    return 0


def update_progress(index: int):
    url = f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.1"
    h   = {**HEADERS, "Prefer": "return=minimal"}
    r   = requests.patch(url, headers=h, json={"last_index": index})
    if r.status_code in (200, 204):
        print(f"✅ Progress saved → {index}")
    else:
        print(f"⚠️  Progress save failed: {r.text}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("🚀 LINKEDIN SCRAPER WITH AUTO RESUME - REPO 1")
    print("=" * 70)

    all_keywords = [
        "Actimize Developer", "Active Directory", "Agronomy Operations",
        "AI/ML Engineer", "Anti Money Laundering (AML)",
        "Atlassian Engineer / Jira", "Big Data Engineer", "Bioinformatics",
        "Bioinformatics for UK", "Biotechnology", "Biotechnology Internship",
        "Business Analyst", "Business Analyst for Canada",
        "Business Intelligence Engineer",
        "Business Intelligence Engineer Internships", "Chemical Engineer",
        "CLINICAL DATA ANALYST", "Clinical Research Coordinator",
        "Cloud Engineer", "Cloud Engineer for Ireland", "Computer Science",
        "Computer Science Internship", "Construction Management",
        "Credit controller for UK", "CRM Sales", "CRM Specialist",
        "Cyber security", "Cybersecurity for Ireland", "Cybersecurity for UK",
        "Data Analyst", "Data Analyst for Canada", "Data Analyst for UK",
        "Data Analyst Internship for Ireland", "Data Analyst Internships",
        "Database Administration", "Data Center Technician", "Data Engineer",
        "Data Engineer (citizen/h4ead)", "Data Engineer for UK",
        "Data Science for Germany", "Data Scientist",
        "Design Verification Engineer", "DevOps", "DevOps for India",
        "DevOps for Ireland", "DevOps for UK", "DevOps Internships",
        "Dynamics 365", "Electrical Engineer", "Electrical Project",
        "Electronic Health Records (EHR)", "Embedded Software Engineer",
        "Environmental Health and Safety (EHS)", "Epic Analyst", "ERP",
        "Financial analyst", "Financial analyst for Ireland",
        "Frontend Engineering", "Full Stack", "Game Developer",
        "Game UI / Interactive UI Designer", "Generative AI",
    ]

    location = os.getenv("LOCATION", "United States")

    scraper     = LinkedInScraper(use_database=True)
    start_index = get_progress()

    print(f"\n▶  Resuming from keyword index : {start_index}")
    print(f"📊 Total keywords              : {len(all_keywords)}")
    print(f"⚙️  Workers                     : {WORKERS}")

    start_time = time.time()
    total_jobs = 0

    for i in range(start_index, len(all_keywords)):
        keyword = all_keywords[i]

        print("\n" + "-" * 60)
        print(f"🔍 Keyword {i+1}/{len(all_keywords)}: {keyword}")
        print("-" * 60)

        try:
            jobs = scraper.scrape_all_jobs_batch(
                keywords=[keyword],
                location=location,
                max_workers=WORKERS,
                save_to_db=True,
            )
            total_jobs += len(jobs)
            update_progress(i + 1)

        except Exception as e:
            print(f"❌ Error on keyword '{keyword}': {e}")
            # save progress so we can resume from this keyword
            update_progress(i)
            raise

    # reset progress so next full run starts from the beginning
    update_progress(0)

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("✅ SCRAPER RUN COMPLETE")
    print("=" * 70)
    print(f"Jobs scraped  : {total_jobs}")
    print(f"Total runtime : {elapsed / 60:.1f} minutes")


if __name__ == "__main__":
    main()
