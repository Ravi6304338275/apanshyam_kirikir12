# """Main LinkedIn scraper class - optimized for external link extraction with Supabase"""

# import time
# import random
# import re
# from datetime import datetime, date
# from typing import Optional, List, Dict, Any, Tuple
# from urllib.parse import urlparse, unquote, parse_qs
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import threading

# import requests
# from bs4 import BeautifulSoup
# from bs4.element import Tag

# from .models import JobPost, Location, Compensation, Country, JobType
# from .constant import headers
# from .util import (
#     job_type_code,
#     parse_job_type,
#     parse_job_level,
#     parse_company_industry,
#     is_job_remote,
#     extract_external_url_from_html,
#     extract_emails_from_text,
#     currency_parser,
#     parse_relative_date,
#     create_session,
#     remove_attributes,
# )
# from .database import SupabaseManager


# class LinkedInScraper:
#     """High-performance LinkedIn scraper focused on external links with Supabase storage"""
    
#     def __init__(self, proxies=None, ca_cert=None, user_agent=None, use_database=True):
#         self.base_url = "https://www.linkedin.com"
#         self.session = create_session(proxies=proxies, ca_cert=ca_cert)
#         self.session.headers.update(headers)
        
#         # Rate limiting
#         self.min_delay = 1.0
#         self.max_delay = 3.0
#         self.current_delay = self.min_delay
#         self.consecutive_errors = 0
#         self.max_consecutive_errors = 3
#         self.error_backoff = 1.5
        
#         # Thread safety
#         self._lock = threading.Lock()
#         self._extracted_links = set()
        
#         # Database
#         self.use_database = use_database
#         self.db = SupabaseManager() if use_database else None
#         if use_database:
#             self.db.initialize()
        
#     def _throttle(self):
#         """Apply throttling based on current delay"""
#         with self._lock:
#             time.sleep(self.current_delay + random.uniform(0, 0.5))
    
#     def _handle_error(self):
#         """Increase delay on errors"""
#         with self._lock:
#             self.consecutive_errors += 1
#             if self.consecutive_errors >= self.max_consecutive_errors:
#                 self.current_delay = min(self.current_delay * self.error_backoff, self.max_delay)
#                 self.consecutive_errors = 0
#                 print(f"⚠️ Increasing delay to {self.current_delay:.1f}s due to errors")
    
#     def _handle_success(self):
#         """Gradually decrease delay on success"""
#         with self._lock:
#             self.consecutive_errors = 0
#             if self.current_delay > self.min_delay:
#                 self.current_delay = max(self.current_delay / self.error_backoff, self.min_delay)
    
#     def search_jobs(self, keyword: str, location: str = "United States", 
#                    hours_old: int = 24, limit: int = 25) -> List[Dict]:
#         """
#         Search for jobs and return basic info
        
#         Returns list of dicts with keys: job_id, title, company, location, link
#         """
#         jobs = []
#         start = 0
        
#         while len(jobs) < limit:
#             # Build search URL
#             params = {
#                 "keywords": keyword,
#                 "location": location,
#                 "distance": "100",
#                 "f_TPR": f"r{hours_old * 3600}",
#                 "start": start,
#                 "refresh": True,
#             }
            
#             url = f"{self.base_url}/jobs-guest/jobs/api/seeMoreJobPostings/search"
            
#             try:
#                 self._throttle()
#                 response = self.session.get(url, params=params, timeout=10)
                
#                 if response.status_code == 429:
#                     print(f"⚠️ Rate limited, waiting...")
#                     time.sleep(5)
#                     continue
                    
#                 if response.status_code != 200:
#                     print(f"❌ Search failed: {response.status_code}")
#                     break
                
#                 # Parse HTML response
#                 soup = BeautifulSoup(response.text, "html.parser")
#                 job_cards = soup.find_all("div", class_="base-card")
                
#                 if not job_cards:
#                     print(f"No more jobs found")
#                     break
                
#                 # Extract basic info from each card
#                 for card in job_cards:
#                     try:
#                         # Get job ID from link
#                         link_tag = card.find("a", class_="base-card__full-link")
#                         if not link_tag or not link_tag.get("href"):
#                             continue
                            
#                         href = link_tag["href"]
#                         job_id = href.split("?")[0].split("-")[-1]
                        
#                         # Get title
#                         title_tag = card.find("h3", class_="base-search-card__title")
#                         title = title_tag.get_text(strip=True) if title_tag else "Unknown"
                        
#                         # Get company
#                         company_tag = card.find("h4", class_="base-search-card__subtitle")
#                         company = company_tag.get_text(strip=True) if company_tag else "Unknown"
                        
#                         # Get location
#                         location_tag = card.find("span", class_="job-search-card__location")
#                         location_str = location_tag.get_text(strip=True) if location_tag else ""
                        
#                         jobs.append({
#                             "job_id": job_id,
#                             "title": title,
#                             "company": company,
#                             "location": location_str,
#                             "link": f"{self.base_url}/jobs/view/{job_id}",
#                         })
                        
#                         if len(jobs) >= limit:
#                             break
                            
#                     except Exception as e:
#                         print(f"⚠️ Error parsing job card: {e}")
#                         continue
                
#                 start += 25
#                 self._handle_success()
                
#             except Exception as e:
#                 print(f"❌ Search error: {e}")
#                 self._handle_error()
#                 break
        
#         return jobs[:limit]
    
#     def get_job_details(self, job_id: str, job_data: Dict = None) -> Optional[JobPost]:
#         """
#         Fetch detailed job information including external apply link
        
#         This is the KEY function that extracts external URLs
#         """
#         url = f"{self.base_url}/jobs/view/{job_id}"
        
#         try:
#             self._throttle()
#             response = self.session.get(url, timeout=10)
            
#             if response.status_code == 429:
#                 print(f"⚠️ Rate limited for job {job_id}")
#                 return None
                
#             if response.status_code != 200:
#                 print(f"❌ Failed to fetch job {job_id}: {response.status_code}")
#                 return None
            
#             html = response.text
#             soup = BeautifulSoup(html, "html.parser")
            
#             # Extract external apply URL - THIS IS CRITICAL
#             external_url = self._extract_external_url(soup, html, job_id)
            
#             # Skip if it's a LinkedIn internal page (signup, etc.)
#             if external_url and self._is_linkedin_internal(external_url):
#                 external_url = None
            
#             # Extract job title
#             title = job_data.get("title") if job_data else ""
#             if not title:
#                 title_tag = soup.find("h1", class_="top-card-layout__title")
#                 title = title_tag.get_text(strip=True) if title_tag else "Unknown"
            
#             # Extract company
#             company = job_data.get("company") if job_data else ""
#             if not company:
#                 company_tag = soup.find("a", class_="topcard__org-name-link")
#                 company = company_tag.get_text(strip=True) if company_tag else "Unknown"
            
#             # Extract description
#             description = ""
#             desc_selectors = [
#                 "div.show-more-less-html__markup",
#                 "div.description__text",
#                 "div.jobs-description__content",
#             ]
#             for selector in desc_selectors:
#                 desc_tag = soup.select_one(selector)
#                 if desc_tag:
#                     description = desc_tag.get_text(strip=True)
#                     break
            
#             # Extract location
#             location_str = job_data.get("location") if job_data else ""
#             if not location_str:
#                 location_tag = soup.find("span", class_="topcard__flavor--bullet")
#                 if location_tag:
#                     location_str = location_tag.get_text(strip=True)
            
#             location = Location.from_string(location_str) if location_str else Location()
            
#             # Extract date posted
#             date_posted = None
#             time_tag = soup.find("span", class_="posted-time-ago__text")
#             if time_tag:
#                 date_posted = parse_relative_date(time_tag.get_text(strip=True))
            
#             # Extract job type, level, industry
#             job_type = parse_job_type(soup)
#             job_level = parse_job_level(soup)
#             company_industry = parse_company_industry(soup)
            
#             # Check if remote
#             is_remote = is_job_remote(title, description, location)
            
#             # Check if easy apply (no external URL)
#             is_easy_apply = not external_url
            
#             # Extract compensation if available
#             compensation = None
#             salary_tag = soup.find("span", class_="salary")
#             if salary_tag:
#                 salary_text = salary_tag.get_text(strip=True)
#                 if "-" in salary_text:
#                     parts = salary_text.split("-")
#                     min_amount = currency_parser(parts[0])
#                     max_amount = currency_parser(parts[1])
#                     compensation = Compensation(
#                         min_amount=min_amount,
#                         max_amount=max_amount,
#                         currency="USD"
#                     )
            
#             # Get search keyword from job_data if available
#             search_keyword = job_data.get("keyword") if job_data else None
            
#             # Create JobPost object
#             job = JobPost(
#                 job_id=job_id,
#                 title=title,
#                 company_name=company,
#                 location=location,
#                 description=description[:10000] if description else None,  # Limit description
#                 date_posted=date_posted,
#                 job_url=url,
#                 apply_url=external_url,  # This is the external link we want!
#                 job_url_direct=external_url,  # For backward compatibility
#                 job_type=job_type,
#                 job_level=job_level,
#                 company_industry=company_industry,
#                 is_remote=is_remote,
#                 is_easy_apply=is_easy_apply,
#                 compensation=compensation,
#                 emails=extract_emails_from_text(description or ""),
#                 search_keyword=search_keyword,
#             )
            
#             self._handle_success()
#             return job
            
#         except Exception as e:
#             print(f"❌ Error fetching job {job_id}: {e}")
#             self._handle_error()
#             return None
    
#     def _extract_external_url(self, soup: BeautifulSoup, html: str, job_id: str) -> Optional[str]:
#         """
#         Extract external apply URL using multiple methods
#         This is the core function that gets the actual external links
#         """
        
#         # METHOD 1: Look for code#applyUrl (MOST RELIABLE)
#         apply_code = soup.find("code", id="applyUrl")
#         if apply_code:
#             code_html = str(apply_code)
            
#             # Look for URL in HTML comments
#             comment_match = re.search(r'<!--\s*"([^"]+)"\s*-->', code_html)
#             if comment_match:
#                 url_candidate = comment_match.group(1)
                
#                 # Extract url parameter
#                 url_match = re.search(r'url=([^&\s]+)', url_candidate)
#                 if url_match:
#                     encoded = url_match.group(1)
#                     decoded = unquote(encoded)
                    
#                     # Filter out LinkedIn internal pages
#                     if not self._is_linkedin_internal(decoded):
#                         return decoded.split('&urlHash=')[0]
        
#         # METHOD 2: Look for externalApply pattern in HTML
#         pattern = rf'externalApply/{job_id}\?url=([^"&\s>]+)'
#         match = re.search(pattern, html, re.IGNORECASE)
#         if match:
#             encoded = match.group(1)
#             decoded = unquote(encoded)
#             if not self._is_linkedin_internal(decoded):
#                 return decoded.split('&urlHash=')[0]
        
#         # METHOD 3: Look for any external apply links
#         apply_selectors = [
#             'a[href*="apply"]',
#             'a[href*="lever"]',
#             'a[href*="greenhouse"]',
#             'a[href*="workable"]',
#             'a[href*="ashby"]',
#             'a[href*="bamboo"]',
#             'a[href*="icims"]',
#             'a.jobs-apply-button',
#         ]
        
#         for selector in apply_selectors:
#             links = soup.select(selector)
#             for link in links:
#                 href = link.get("href")
#                 if href and not self._is_linkedin_internal(href):
#                     return href
        
#         # METHOD 4: Try to fetch externalApply endpoint
#         try:
#             ext_url = f"{self.base_url}/jobs/view/externalApply/{job_id}"
#             ext_response = self.session.get(ext_url, timeout=5, allow_redirects=True)
            
#             final_url = ext_response.url
#             if final_url and not self._is_linkedin_internal(final_url):
#                 return final_url
                
#         except:
#             pass
        
#         return None
    
#     def _is_linkedin_internal(self, url: str) -> bool:
#         """Check if URL is a LinkedIn internal page (signup, login, etc.)"""
#         if not url:
#             return True
        
#         url_lower = url.lower()
        
#         # Check if it's a LinkedIn domain
#         if 'linkedin.com' in url_lower:
#             return True
        
#         # Check for signup/login patterns
#         internal_patterns = ['signup', 'login', 'auth', 'checkpoint', 'cold-join', 'registration']
#         for pattern in internal_patterns:
#             if pattern in url_lower:
#                 return True
        
#         return False
    
#     def scrape_batch(self, keywords: List[str], location: str = "United States", 
#                     jobs_per_keyword: int = 10, max_workers: int = 5, 
#                     save_to_db: bool = True) -> List[JobPost]:
#         """
#         Scrape jobs for multiple keywords in parallel and save to Supabase
        
#         This is the main method to call
#         """
#         all_jobs = []
#         all_job_dicts = []  # For database storage
        
#         # Phase 1: Search for jobs
#         all_search_results = []
#         for keyword in keywords:
#             print(f"\n🔍 Searching: {keyword}")
#             jobs = self.search_jobs(keyword, location, limit=jobs_per_keyword)
#             print(f"   Found {len(jobs)} jobs")
            
#             for job in jobs:
#                 job["keyword"] = keyword
#                 all_search_results.append(job)
            
#             # Small delay between keywords
#             time.sleep(2)
        
#         print(f"\n📊 Total jobs found: {len(all_search_results)}")
        
#         # Phase 2: Fetch details in parallel (this gets external links)
#         print(f"\n🔗 Fetching job details with external links...")
        
#         with ThreadPoolExecutor(max_workers=max_workers) as executor:
#             future_to_job = {
#                 executor.submit(self.get_job_details, job["job_id"], job): job
#                 for job in all_search_results
#             }
            
#             completed = 0
#             for future in as_completed(future_to_job):
#                 completed += 1
#                 job = future_to_job[future]
                
#                 try:
#                     job_post = future.result(timeout=15)
#                     if job_post:
#                         all_jobs.append(job_post)
                        
#                         # Convert to dict for database
#                         job_dict = job_post.to_supabase_dict()
#                         all_job_dicts.append(job_dict)
                        
#                         # Show progress with external link status
#                         if job_post.apply_url:
#                             print(f"  ✓ [{completed}/{len(all_search_results)}] {job['title'][:30]}... → EXTERNAL LINK FOUND")
#                         else:
#                             print(f"  ○ [{completed}/{len(all_search_results)}] {job['title'][:30]}... (internal apply)")
#                     else:
#                         print(f"  ✗ [{completed}/{len(all_search_results)}] Failed to fetch {job['title'][:30]}...")
                        
#                 except Exception as e:
#                     print(f"  ✗ [{completed}/{len(all_search_results)}] Error: {e}")
        
#         # Phase 3: Save to Supabase
#         if save_to_db and self.db and self.db.initialized and all_job_dicts:
#             db_results = self.db.save_jobs_batch(all_job_dicts)
#         elif save_to_db:
#             print("\n⚠️ Supabase not initialized, skipping database save")
        
#         # Summary
#         external_count = sum(1 for j in all_jobs if j.apply_url)
#         print(f"\n✅ Complete! Found {external_count} external links out of {len(all_jobs)} jobs")
        
#         return all_jobs
    
#     def save_to_csv(self, jobs: List[JobPost], filename: str = None):
#         """Save jobs to CSV file"""
#         if not filename:
#             filename = f"linkedin_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
#         import csv
#         with open(filename, 'w', newline='', encoding='utf-8') as f:
#             writer = csv.writer(f)
#             writer.writerow([
#                 'Job ID', 'Title', 'Company', 'Location', 'Date Posted',
#                 'Job URL', 'External Apply URL', 'Is Remote', 'Is Easy Apply',
#                 'Job Type', 'Job Level', 'Industry', 'Search Keyword'
#             ])
            
#             for job in jobs:
#                 writer.writerow([
#                     job.job_id,
#                     job.title,
#                     job.company_name,
#                     job.location.display_location(),
#                     job.date_posted,
#                     job.job_url,
#                     job.apply_url or '',
#                     job.is_remote,
#                     job.is_easy_apply,
#                     ', '.join([jt.value for jt in job.job_type]) if job.job_type else '',
#                     job.job_level or '',
#                     job.company_industry or '',
#                     job.search_keyword or ''
#                 ])
        
#         print(f"💾 Saved {len(jobs)} jobs to {filename}")































# """Main LinkedIn scraper class - optimized for external link extraction with Supabase"""

# import time
# import random
# import re
# from datetime import datetime, date
# from typing import Optional, List, Dict, Any, Tuple
# from urllib.parse import urlparse, unquote, parse_qs
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import threading

# import requests
# from bs4 import BeautifulSoup
# from bs4.element import Tag

# from .models import JobPost, Location, Compensation, Country, JobType
# from .constant import headers
# from .util import (
#     job_type_code,
#     parse_job_type,
#     parse_job_level,
#     parse_company_industry,
#     is_job_remote,
#     extract_external_url_from_html,
#     extract_emails_from_text,
#     currency_parser,
#     parse_relative_date,
#     create_session,
#     remove_attributes,
#     parse_salary_from_text,
#     parse_experience_from_text,
#     extract_company_logo,
# )
# from .database import SupabaseManager


# class LinkedInScraper:
#     """High-performance LinkedIn scraper focused on external links with Supabase storage"""
    
#     def __init__(self, proxies=None, ca_cert=None, user_agent=None, use_database=True):
#         self.base_url = "https://www.linkedin.com"
#         self.session = create_session(proxies=proxies, ca_cert=ca_cert)
#         self.session.headers.update(headers)
        
#         # Rate limiting
#         self.min_delay = 1.0
#         self.max_delay = 3.0
#         self.current_delay = self.min_delay
#         self.consecutive_errors = 0
#         self.max_consecutive_errors = 3
#         self.error_backoff = 1.5
        
#         # Thread safety
#         self._lock = threading.Lock()
#         self._extracted_links = set()
        
#         # Database
#         self.use_database = use_database
#         self.db = SupabaseManager() if use_database else None
#         if use_database:
#             self.db.initialize()
        
#     def _throttle(self):
#         """Apply throttling based on current delay"""
#         with self._lock:
#             time.sleep(self.current_delay + random.uniform(0, 0.5))
    
#     def _handle_error(self):
#         """Increase delay on errors"""
#         with self._lock:
#             self.consecutive_errors += 1
#             if self.consecutive_errors >= self.max_consecutive_errors:
#                 self.current_delay = min(self.current_delay * self.error_backoff, self.max_delay)
#                 self.consecutive_errors = 0
#                 print(f"⚠️ Increasing delay to {self.current_delay:.1f}s due to errors")
    
#     def _handle_success(self):
#         """Gradually decrease delay on success"""
#         with self._lock:
#             self.consecutive_errors = 0
#             if self.current_delay > self.min_delay:
#                 self.current_delay = max(self.current_delay / self.error_backoff, self.min_delay)
    
#     def search_jobs(self, keyword: str, location: str = "United States", 
#                    hours_old: int = 24, limit: int = 25) -> List[Dict]:
#         """
#         Search for jobs and return basic info
        
#         Returns list of dicts with keys: job_id, title, company, location, link
#         """
#         jobs = []
#         start = 0
        
#         while len(jobs) < limit:
#             # Build search URL
#             params = {
#                 "keywords": keyword,
#                 "location": location,
#                 "distance": "100",
#                 "f_TPR": f"r{hours_old * 3600}",
#                 "start": start,
#                 "refresh": True,
#             }
            
#             url = f"{self.base_url}/jobs-guest/jobs/api/seeMoreJobPostings/search"
            
#             try:
#                 self._throttle()
#                 response = self.session.get(url, params=params, timeout=10)
                
#                 if response.status_code == 429:
#                     print(f"⚠️ Rate limited, waiting...")
#                     time.sleep(5)
#                     continue
                    
#                 if response.status_code != 200:
#                     print(f"❌ Search failed: {response.status_code}")
#                     break
                
#                 # Parse HTML response
#                 soup = BeautifulSoup(response.text, "html.parser")
#                 job_cards = soup.find_all("div", class_="base-card")
                
#                 if not job_cards:
#                     print(f"No more jobs found")
#                     break
                
#                 # Extract basic info from each card
#                 for card in job_cards:
#                     try:
#                         # Get job ID from link
#                         link_tag = card.find("a", class_="base-card__full-link")
#                         if not link_tag or not link_tag.get("href"):
#                             continue
                            
#                         href = link_tag["href"]
#                         job_id = href.split("?")[0].split("-")[-1]
                        
#                         # Get title
#                         title_tag = card.find("h3", class_="base-search-card__title")
#                         title = title_tag.get_text(strip=True) if title_tag else "Unknown"
                        
#                         # Get company
#                         company_tag = card.find("h4", class_="base-search-card__subtitle")
#                         company = company_tag.get_text(strip=True) if company_tag else "Unknown"
                        
#                         # Get location
#                         location_tag = card.find("span", class_="job-search-card__location")
#                         location_str = location_tag.get_text(strip=True) if location_tag else ""
                        
#                         jobs.append({
#                             "job_id": job_id,
#                             "title": title,
#                             "company": company,
#                             "location": location_str,
#                             "link": f"{self.base_url}/jobs/view/{job_id}",
#                         })
                        
#                         if len(jobs) >= limit:
#                             break
                            
#                     except Exception as e:
#                         print(f"⚠️ Error parsing job card: {e}")
#                         continue
                
#                 start += 25
#                 self._handle_success()
                
#             except Exception as e:
#                 print(f"❌ Search error: {e}")
#                 self._handle_error()
#                 break
        
#         return jobs[:limit]
    
#     def get_job_details(self, job_id: str, job_data: Dict = None) -> Optional[JobPost]:
#         """
#         Fetch detailed job information including external apply link
        
#         This is the KEY function that extracts external URLs
#         """
#         url = f"{self.base_url}/jobs/view/{job_id}"
        
#         try:
#             self._throttle()
#             response = self.session.get(url, timeout=10)
            
#             if response.status_code == 429:
#                 print(f"⚠️ Rate limited for job {job_id}")
#                 return None
                
#             if response.status_code != 200:
#                 print(f"❌ Failed to fetch job {job_id}: {response.status_code}")
#                 return None
            
#             html = response.text
#             soup = BeautifulSoup(html, "html.parser")
            
#             # Extract external apply URL - THIS IS CRITICAL
#             external_url = self._extract_external_url(soup, html, job_id)
            
#             # Skip if it's a LinkedIn internal page (signup, etc.)
#             if external_url and self._is_linkedin_internal(external_url):
#                 external_url = None
            
#             # Extract job title
#             title = job_data.get("title") if job_data else ""
#             if not title:
#                 title_tag = soup.find("h1", class_="top-card-layout__title")
#                 title = title_tag.get_text(strip=True) if title_tag else "Unknown"
            
#             # Extract company
#             company = job_data.get("company") if job_data else ""
#             if not company:
#                 company_tag = soup.find("a", class_="topcard__org-name-link")
#                 company = company_tag.get_text(strip=True) if company_tag else "Unknown"
            
#             # Extract company logo
#             company_logo = extract_company_logo(soup)
            
#             # Extract description
#             description = ""
#             desc_selectors = [
#                 "div.show-more-less-html__markup",
#                 "div.description__text",
#                 "div.jobs-description__content",
#             ]
#             for selector in desc_selectors:
#                 desc_tag = soup.select_one(selector)
#                 if desc_tag:
#                     description = desc_tag.get_text(strip=True)
#                     break
            
#             # Extract location
#             location_str = job_data.get("location") if job_data else ""
#             if not location_str:
#                 location_tag = soup.find("span", class_="topcard__flavor--bullet")
#                 if location_tag:
#                     location_str = location_tag.get_text(strip=True)
            
#             location = Location.from_string(location_str) if location_str else Location()
            
#             # Extract date posted
#             date_posted = None
#             time_tag = soup.find("span", class_="posted-time-ago__text")
#             if time_tag:
#                 date_posted = parse_relative_date(time_tag.get_text(strip=True))
            
#             # Extract job type, level, industry
#             job_type = parse_job_type(soup)
#             job_level = parse_job_level(soup)
#             company_industry = parse_company_industry(soup)
            
#             # Extract salary information
#             salary_min, salary_max, salary_text = parse_salary_from_text(description, html)
            
#             # Extract experience requirements
#             experience = parse_experience_from_text(description, html)
            
#             # Check if remote
#             is_remote = is_job_remote(title, description, location)
            
#             # Check if easy apply (no external URL)
#             is_easy_apply = not external_url
            
#             # Create compensation object if salary found
#             compensation = None
#             if salary_min or salary_max:
#                 compensation = Compensation(
#                     min_amount=salary_min,
#                     max_amount=salary_max,
#                     currency="USD",
#                     interval="yearly"
#                 )
            
#             # Get search keyword from job_data if available
#             search_keyword = job_data.get("keyword") if job_data else None
            
#             # Create JobPost object
#             job = JobPost(
#                 job_id=job_id,
#                 title=title,
#                 company_name=company,
#                 company_logo=company_logo,
#                 location=location,
#                 description=description[:10000] if description else None,
#                 date_posted=date_posted,
#                 job_url=url,
#                 apply_url=external_url,
#                 job_url_direct=external_url,
#                 job_type=job_type,
#                 job_level=job_level,
#                 company_industry=company_industry,
#                 is_remote=is_remote,
#                 is_easy_apply=is_easy_apply,
#                 compensation=compensation,
#                 emails=extract_emails_from_text(description or ""),
#                 search_keyword=search_keyword,
#                 experience=experience,
#                 salary_text=salary_text,
#             )
            
#             self._handle_success()
#             return job
            
#         except Exception as e:
#             print(f"❌ Error fetching job {job_id}: {e}")
#             self._handle_error()
#             return None
    
#     def _extract_external_url(self, soup: BeautifulSoup, html: str, job_id: str) -> Optional[str]:
#         """
#         Extract external apply URL using multiple methods
#         This is the core function that gets the actual external links
#         """
        
#         # METHOD 1: Look for code#applyUrl (MOST RELIABLE)
#         apply_code = soup.find("code", id="applyUrl")
#         if apply_code:
#             code_html = str(apply_code)
            
#             # Look for URL in HTML comments
#             comment_match = re.search(r'<!--\s*"([^"]+)"\s*-->', code_html)
#             if comment_match:
#                 url_candidate = comment_match.group(1)
                
#                 # Extract url parameter
#                 url_match = re.search(r'url=([^&\s]+)', url_candidate)
#                 if url_match:
#                     encoded = url_match.group(1)
#                     decoded = unquote(encoded)
                    
#                     # Filter out LinkedIn internal pages
#                     if not self._is_linkedin_internal(decoded):
#                         return decoded.split('&urlHash=')[0]
        
#         # METHOD 2: Look for externalApply pattern in HTML
#         pattern = rf'externalApply/{job_id}\?url=([^"&\s>]+)'
#         match = re.search(pattern, html, re.IGNORECASE)
#         if match:
#             encoded = match.group(1)
#             decoded = unquote(encoded)
#             if not self._is_linkedin_internal(decoded):
#                 return decoded.split('&urlHash=')[0]
        
#         # METHOD 3: Look for any external apply links
#         apply_selectors = [
#             'a[href*="apply"]',
#             'a[href*="lever"]',
#             'a[href*="greenhouse"]',
#             'a[href*="workable"]',
#             'a[href*="ashby"]',
#             'a[href*="bamboo"]',
#             'a[href*="icims"]',
#             'a.jobs-apply-button',
#         ]
        
#         for selector in apply_selectors:
#             links = soup.select(selector)
#             for link in links:
#                 href = link.get("href")
#                 if href and not self._is_linkedin_internal(href):
#                     return href
        
#         # METHOD 4: Try to fetch externalApply endpoint
#         try:
#             ext_url = f"{self.base_url}/jobs/view/externalApply/{job_id}"
#             ext_response = self.session.get(ext_url, timeout=5, allow_redirects=True)
            
#             final_url = ext_response.url
#             if final_url and not self._is_linkedin_internal(final_url):
#                 return final_url
                
#         except:
#             pass
        
#         return None
    
#     def _is_linkedin_internal(self, url: str) -> bool:
#         """Check if URL is a LinkedIn internal page (signup, login, etc.)"""
#         if not url:
#             return True
        
#         url_lower = url.lower()
        
#         # Check if it's a LinkedIn domain
#         if 'linkedin.com' in url_lower:
#             return True
        
#         # Check for signup/login patterns
#         internal_patterns = ['signup', 'login', 'auth', 'checkpoint', 'cold-join', 'registration']
#         for pattern in internal_patterns:
#             if pattern in url_lower:
#                 return True
        
#         return False
    
#     def scrape_batch(self, keywords: List[str], location: str = "United States", 
#                     jobs_per_keyword: int = 10, max_workers: int = 5, 
#                     save_to_db: bool = True) -> List[JobPost]:
#         """
#         Scrape jobs for multiple keywords in parallel and save to Supabase
        
#         This is the main method to call
#         """
#         all_jobs = []
#         all_job_dicts = []  # For database storage
        
#         # Phase 1: Search for jobs
#         all_search_results = []
#         for keyword in keywords:
#             print(f"\n🔍 Searching: {keyword}")
#             jobs = self.search_jobs(keyword, location, limit=jobs_per_keyword)
#             print(f"   Found {len(jobs)} jobs")
            
#             for job in jobs:
#                 job["keyword"] = keyword
#                 all_search_results.append(job)
            
#             # Small delay between keywords
#             time.sleep(2)
        
#         print(f"\n📊 Total jobs found: {len(all_search_results)}")
        
#         # Phase 2: Fetch details in parallel (this gets external links)
#         print(f"\n🔗 Fetching job details with external links...")
        
#         with ThreadPoolExecutor(max_workers=max_workers) as executor:
#             future_to_job = {
#                 executor.submit(self.get_job_details, job["job_id"], job): job
#                 for job in all_search_results
#             }
            
#             completed = 0
#             for future in as_completed(future_to_job):
#                 completed += 1
#                 job = future_to_job[future]
                
#                 try:
#                     job_post = future.result(timeout=15)
#                     if job_post:
#                         all_jobs.append(job_post)
                        
#                         # Convert to dict for database
#                         job_dict = job_post.to_supabase_dict()
#                         all_job_dicts.append(job_dict)
                        
#                         # Show progress with external link status
#                         if job_post.apply_url:
#                             salary_info = f" ${job_post.compensation.min_amount}-{job_post.compensation.max_amount}" if job_post.compensation and job_post.compensation.min_amount else ""
#                             exp_info = f" Exp:{job_post.experience}" if job_post.experience else ""
#                             print(f"  ✓ [{completed}/{len(all_search_results)}] {job['title'][:30]}... → EXTERNAL LINK{salary_info}{exp_info}")
#                         else:
#                             print(f"  ○ [{completed}/{len(all_search_results)}] {job['title'][:30]}... (internal apply)")
#                     else:
#                         print(f"  ✗ [{completed}/{len(all_search_results)}] Failed to fetch {job['title'][:30]}...")
                        
#                 except Exception as e:
#                     print(f"  ✗ [{completed}/{len(all_search_results)}] Error: {e}")
        
#         # Phase 3: Save to Supabase
#         if save_to_db and self.db and self.db.initialized and all_job_dicts:
#             db_results = self.db.save_jobs_batch(all_job_dicts)
#         elif save_to_db:
#             print("\n⚠️ Supabase not initialized, skipping database save")
        
#         # Summary
#         external_count = sum(1 for j in all_jobs if j.apply_url)
#         salary_count = sum(1 for j in all_jobs if j.compensation and j.compensation.min_amount)
#         exp_count = sum(1 for j in all_jobs if j.experience)
#         logo_count = sum(1 for j in all_jobs if j.company_logo)
        
#         print(f"\n✅ Complete! Found:")
#         print(f"   📊 Total jobs: {len(all_jobs)}")
#         print(f"   🔗 External links: {external_count}")
#         print(f"   💰 Jobs with salary: {salary_count}")
#         print(f"   📝 Jobs with experience: {exp_count}")
#         print(f"   🖼️  Jobs with logo: {logo_count}")
        
#         return all_jobs
    
#     def save_to_csv(self, jobs: List[JobPost], filename: str = None):
#         """Save jobs to CSV file with enhanced fields"""
#         if not filename:
#             filename = f"linkedin_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
#         import csv
#         with open(filename, 'w', newline='', encoding='utf-8') as f:
#             writer = csv.writer(f)
#             writer.writerow([
#                 'Job ID', 'Title', 'Company', 'Company Logo', 'Location', 'Date Posted',
#                 'Job URL', 'External Apply URL', 'Is Remote', 'Is Easy Apply',
#                 'Job Type', 'Job Level', 'Industry', 'Search Keyword',
#                 'Salary Min', 'Salary Max', 'Salary Text', 'Experience Required',
#                 'Description Preview'
#             ])
            
#             for job in jobs:
#                 writer.writerow([
#                     job.job_id,
#                     job.title,
#                     job.company_name,
#                     job.company_logo or '',
#                     job.location.display_location(),
#                     job.date_posted,
#                     job.job_url,
#                     job.apply_url or '',
#                     job.is_remote,
#                     job.is_easy_apply,
#                     ', '.join([jt.value for jt in job.job_type]) if job.job_type else '',
#                     job.job_level or '',
#                     job.company_industry or '',
#                     job.search_keyword or '',
#                     job.compensation.min_amount if job.compensation else '',
#                     job.compensation.max_amount if job.compensation else '',
#                     getattr(job, 'salary_text', ''),
#                     getattr(job, 'experience', ''),
#                     job.description[:200] + '...' if job.description and len(job.description) > 200 else (job.description or '')
#                 ])






























































































# """Main LinkedIn scraper class - optimized for external link extraction with Supabase"""

# import time
# import random
# import re
# from datetime import datetime, date
# from typing import Optional, List, Dict, Any, Tuple
# from urllib.parse import urlparse, unquote, parse_qs
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import threading
# import json

# import requests
# from bs4 import BeautifulSoup
# from bs4.element import Tag

# from .models import JobPost, Location, Compensation, Country, JobType
# from .constant import headers
# from .util import (
#     job_type_code,
#     parse_job_type,
#     parse_job_level,
#     parse_company_industry,
#     is_job_remote,
#     extract_external_url_from_html,
#     extract_emails_from_text,
#     currency_parser,
#     parse_relative_date,
#     create_session,
#     remove_attributes,
#     parse_salary_from_text,
#     parse_experience_from_text,
#     extract_company_logo,
# )
# from .database import SupabaseManager


# class LinkedInScraper:
#     """High-performance LinkedIn scraper focused on external links with Supabase storage"""

#     def __init__(self, proxies=None, ca_cert=None, user_agent=None, use_database=True):
#         self.base_url = "https://www.linkedin.com"
#         self.session = create_session(proxies=proxies, ca_cert=ca_cert)
#         self.session.headers.update(headers)

#         # Rate limiting
#         self.min_delay = 1.0
#         self.max_delay = 3.0
#         self.current_delay = self.min_delay
#         self.consecutive_errors = 0
#         self.max_consecutive_errors = 3
#         self.error_backoff = 1.5

#         # Thread safety
#         self._lock = threading.Lock()
#         self._extracted_links = set()

#         # Database
#         self.use_database = use_database
#         self.db = SupabaseManager() if use_database else None
#         if use_database:
#             self.db.initialize()

#     def _throttle(self):
#         """Apply throttling based on current delay"""
#         with self._lock:
#             time.sleep(self.current_delay + random.uniform(0, 0.5))

#     def _handle_error(self):
#         """Increase delay on errors"""
#         with self._lock:
#             self.consecutive_errors += 1
#             if self.consecutive_errors >= self.max_consecutive_errors:
#                 self.current_delay = min(self.current_delay * self.error_backoff, self.max_delay)
#                 self.consecutive_errors = 0
#                 print(f"⚠️ Increasing delay to {self.current_delay:.1f}s due to errors")

#     def _handle_success(self):
#         """Gradually decrease delay on success"""
#         with self._lock:
#             self.consecutive_errors = 0
#             if self.current_delay > self.min_delay:
#                 self.current_delay = max(self.current_delay / self.error_backoff, self.min_delay)

#     def search_all_jobs(self, keyword: str, location: str = "United States", hours_old: int = 24) -> List[Dict]:
#         """
#         Search for ALL jobs posted in the last N hours for a keyword.
#         Continues pagination until LinkedIn returns an empty page.

#         LinkedIn returns up to 25 jobs per page. We keep fetching pages
#         (start=0, 25, 50, ...) until we get an empty response, which signals
#         that we've exhausted all results for this keyword/time window.
#         """
#         jobs = []
#         seen_job_ids = set()  # Dedup guard
#         start = 0
#         page = 1
#         max_pages = 200        # Safety cap: 200 pages × 25 = up to 5,000 jobs per keyword
#         empty_page_retries = 2  # Retry an empty page before giving up (handles transient gaps)
#         consecutive_empty = 0

#         print(f"\n   📍 Searching all pages for: {keyword}")

#         while page <= max_pages:
#             params = {
#                 "keywords": keyword,
#                 "location": location,
#                 "distance": "100",
#                 "f_TPR": f"r{hours_old * 3600}",  # e.g. r86400 = last 24 hours
#                 "start": start,
#                 "refresh": True,
#             }

#             url = f"{self.base_url}/jobs-guest/jobs/api/seeMoreJobPostings/search"

#             try:
#                 self._throttle()
#                 response = self.session.get(url, params=params, timeout=15)

#                 if response.status_code == 429:
#                     wait = random.uniform(10, 20)
#                     print(f"   ⚠️ Rate limited (429). Waiting {wait:.0f}s before retry...")
#                     time.sleep(wait)
#                     # Don't advance the page — retry the same offset
#                     continue

#                 if response.status_code != 200:
#                     print(f"   ❌ Search failed: HTTP {response.status_code}")
#                     self._handle_error()
#                     break

#                 soup = BeautifulSoup(response.text, "html.parser")
#                 job_cards = soup.find_all("div", class_="base-card")

#                 # ---- Empty page handling ----------------------------------------
#                 if not job_cards:
#                     consecutive_empty += 1
#                     if consecutive_empty <= empty_page_retries:
#                         print(f"   ⚠️ Empty page at start={start} (attempt {consecutive_empty}/{empty_page_retries}), retrying...")
#                         time.sleep(random.uniform(3, 6))
#                         continue
#                     else:
#                         print(f"   ✅ Confirmed end of results after {len(jobs)} jobs (empty response at start={start})")
#                         break
#                 # ---- Non-empty page: reset the empty counter --------------------
#                 consecutive_empty = 0

#                 page_jobs = 0
#                 for card in job_cards:
#                     try:
#                         link_tag = card.find("a", class_="base-card__full-link")
#                         if not link_tag or not link_tag.get("href"):
#                             continue

#                         href = link_tag["href"]
#                         job_id = href.split("?")[0].split("-")[-1]

#                         # Skip duplicates (can happen across pages near boundaries)
#                         if job_id in seen_job_ids:
#                             continue
#                         seen_job_ids.add(job_id)

#                         title_tag = card.find("h3", class_="base-search-card__title")
#                         title = title_tag.get_text(strip=True) if title_tag else "Unknown"

#                         company_tag = card.find("h4", class_="base-search-card__subtitle")
#                         company = company_tag.get_text(strip=True) if company_tag else "Unknown"

#                         location_tag = card.find("span", class_="job-search-card__location")
#                         location_str = location_tag.get_text(strip=True) if location_tag else ""

#                         jobs.append({
#                             "job_id": job_id,
#                             "title": title,
#                             "company": company,
#                             "location": location_str,
#                             "link": f"{self.base_url}/jobs/view/{job_id}",
#                         })

#                         page_jobs += 1

#                     except Exception as e:
#                         print(f"   ⚠️ Error parsing job card: {e}")
#                         continue

#                 print(f"   📄 Page {page} (start={start}): {page_jobs} new jobs | Running total: {len(jobs)}")

#                 # Advance to next page unconditionally — stop only when page is empty
#                 start += 25
#                 page += 1
#                 self._handle_success()

#                 # Brief pause between pages to be polite
#                 time.sleep(random.uniform(1.0, 2.5))

#             except Exception as e:
#                 print(f"   ❌ Search error on page {page}: {e}")
#                 self._handle_error()
#                 # Give it one more shot after a backoff, then bail
#                 time.sleep(5)
#                 break

#         if page > max_pages:
#             print(f"   ⚠️ Reached safety limit of {max_pages} pages for '{keyword}'")

#         print(f"   📊 Total unique jobs found for '{keyword}': {len(jobs)}")
#         return jobs

#     def get_job_details(self, job_id: str, job_data: Dict = None) -> Optional[JobPost]:
#         """
#         Fetch detailed job information including external apply link.
#         This is the KEY function that extracts external URLs.
#         """
#         url = f"{self.base_url}/jobs/view/{job_id}"

#         try:
#             self._throttle()
#             response = self.session.get(url, timeout=10)

#             if response.status_code == 429:
#                 print(f"⚠️ Rate limited for job {job_id}")
#                 return None

#             if response.status_code != 200:
#                 print(f"❌ Failed to fetch job {job_id}: {response.status_code}")
#                 return None

#             html = response.text
#             soup = BeautifulSoup(html, "html.parser")

#             # ===== ULTIMATE EXTERNAL LINK EXTRACTION =====
#             external_url = self._extract_external_url_ultimate(soup, html, job_id)
#             # =============================================

#             # Skip if it's a LinkedIn internal page
#             if external_url and self._is_linkedin_internal(external_url):
#                 external_url = None

#             # Extract job title
#             title = job_data.get("title") if job_data else ""
#             if not title:
#                 title_tag = soup.find("h1", class_="top-card-layout__title")
#                 title = title_tag.get_text(strip=True) if title_tag else "Unknown"

#             # Extract company
#             company = job_data.get("company") if job_data else ""
#             if not company:
#                 company_tag = soup.find("a", class_="topcard__org-name-link")
#                 company = company_tag.get_text(strip=True) if company_tag else "Unknown"

#             # Extract company logo
#             company_logo = extract_company_logo(soup)

#             # Extract description
#             description = ""
#             desc_selectors = [
#                 "div.show-more-less-html__markup",
#                 "div.description__text",
#                 "div.jobs-description__content",
#             ]
#             for selector in desc_selectors:
#                 desc_tag = soup.select_one(selector)
#                 if desc_tag:
#                     description = desc_tag.get_text(strip=True)
#                     break

#             # Extract location
#             location_str = job_data.get("location") if job_data else ""
#             if not location_str:
#                 location_tag = soup.find("span", class_="topcard__flavor--bullet")
#                 if location_tag:
#                     location_str = location_tag.get_text(strip=True)

#             location = Location.from_string(location_str) if location_str else Location()

#             # Extract date posted
#             date_posted = None
#             time_tag = soup.find("span", class_="posted-time-ago__text")
#             if time_tag:
#                 date_posted = parse_relative_date(time_tag.get_text(strip=True))

#             # Extract job type, level, industry
#             job_type = parse_job_type(soup)
#             job_level = parse_job_level(soup)
#             company_industry = parse_company_industry(soup)

#             # Extract salary information
#             salary_min, salary_max, salary_text = parse_salary_from_text(description, html)

#             # Extract experience requirements
#             experience = parse_experience_from_text(description, html)

#             # Check if remote
#             is_remote = is_job_remote(title, description, location)

#             # Check if easy apply (no external URL)
#             is_easy_apply = not external_url

#             # Create compensation object if salary found
#             compensation = None
#             if salary_min or salary_max:
#                 compensation = Compensation(
#                     min_amount=salary_min,
#                     max_amount=salary_max,
#                     currency="USD",
#                     interval="yearly"
#                 )

#             # Get search keyword from job_data if available
#             search_keyword = job_data.get("keyword") if job_data else None

#             # Create JobPost object
#             job = JobPost(
#                 job_id=job_id,
#                 title=title,
#                 company_name=company,
#                 company_logo=company_logo,
#                 location=location,
#                 description=description[:10000] if description else None,
#                 date_posted=date_posted,
#                 job_url=url,
#                 apply_url=external_url,
#                 job_url_direct=external_url,
#                 job_type=job_type,
#                 job_level=job_level,
#                 company_industry=company_industry,
#                 is_remote=is_remote,
#                 is_easy_apply=is_easy_apply,
#                 compensation=compensation,
#                 emails=extract_emails_from_text(description or ""),
#                 search_keyword=search_keyword,
#                 experience=experience,
#                 salary_text=salary_text,
#             )

#             self._handle_success()
#             return job

#         except Exception as e:
#             print(f"❌ Error fetching job {job_id}: {e}")
#             self._handle_error()
#             return None

#     # ===== ULTIMATE EXTERNAL LINK EXTRACTION =====
#     def _extract_external_url_ultimate(self, soup: BeautifulSoup, html: str, job_id: str) -> Optional[str]:
#         """
#         ULTIMATE extraction method - tries EVERY possible way to find external links
#         """

#         print(f"      🔍 Searching for external link...")

#         # METHOD 1: Find ALL script tags and search for applyUrl patterns
#         script_tags = soup.find_all('script')
#         for script in script_tags:
#             if script.string:
#                 script_text = script.string

#                 patterns = [
#                     r'"applyUrl"\s*:\s*"([^"]+)"',
#                     r'"externalApplyUrl"\s*:\s*"([^"]+)"',
#                     r'applyUrl["\']?\s*:\s*["\']([^"\']+)["\']',
#                     r'applyUrl\\":\\"([^\\]+)\\"',
#                 ]

#                 for pattern in patterns:
#                     matches = re.findall(pattern, script_text, re.IGNORECASE)
#                     for match in matches:
#                         url = match.replace('\\/', '/').replace('\\\\', '\\')
#                         if url and 'linkedin.com' not in url and url.startswith('http'):
#                             print(f"      ✅ FOUND external link in script: {url[:60]}...")
#                             return url

#         # METHOD 2: Look for applyUrl in the entire HTML
#         patterns = [
#             r'applyUrl["\']?\s*[:=]\s*["\']([^"\']+)["\']',
#             r'externalApplyUrl["\']?\s*[:=]\s*["\']([^"\']+)["\']',
#             r'<code[^>]*id="applyUrl"[^>]*>(.*?)</code>',
#         ]

#         for pattern in patterns:
#             matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
#             for match in matches:
#                 if isinstance(match, tuple):
#                     match = match[0]
#                 url = str(match).replace('\\/', '/').replace('\\\\', '\\')

#                 comment_match = re.search(r'<!--.*?url=([^&\s]+).*?-->', url)
#                 if comment_match:
#                     url = unquote(comment_match.group(1))

#                 if url and 'linkedin.com' not in url and url.startswith('http'):
#                     print(f"      ✅ FOUND external link in HTML: {url[:60]}...")
#                     return url

#         # METHOD 3: Look for externalApply endpoint pattern
#         ext_pattern = rf'(?:externalApply|jobs/view/externalApply)/{job_id}\?url=([^"&\s>]+)'
#         match = re.search(ext_pattern, html, re.IGNORECASE)
#         if match:
#             url = unquote(match.group(1))
#             if url and 'linkedin.com' not in url:
#                 print(f"      ✅ FOUND external link via endpoint pattern: {url[:60]}...")
#                 return url

#         # METHOD 4: Look for any external links that might be apply buttons
#         apply_links = soup.find_all('a', href=True)
#         for link in apply_links:
#             href = link.get('href', '')
#             if href and 'linkedin.com' not in href and href.startswith('http'):
#                 link_text = link.get_text(strip=True).lower()
#                 link_classes = str(link.get('class', '')).lower()

#                 apply_indicators = ['apply', 'application', 'submit', 'external', 'careers']
#                 if any(ind in link_text for ind in apply_indicators) or any(ind in link_classes for ind in apply_indicators):
#                     print(f"      ✅ FOUND external link via button: {href[:60]}...")
#                     return href

#         # METHOD 5: Try the externalApply endpoint directly
#         try:
#             ext_url = f"{self.base_url}/jobs/view/externalApply/{job_id}"
#             ext_response = self.session.get(ext_url, timeout=5, allow_redirects=True)

#             final_url = ext_response.url
#             if final_url and 'linkedin.com' not in final_url:
#                 print(f"      ✅ FOUND external link via endpoint: {final_url[:60]}...")
#                 return final_url
#         except Exception:
#             pass

#         print(f"      ❌ No external link found (Easy Apply job)")
#         return None

#     def _is_linkedin_internal(self, url: str) -> bool:
#         """Check if URL is a LinkedIn internal page"""
#         if not url:
#             return True

#         url_lower = url.lower()

#         if 'linkedin.com' in url_lower:
#             return True

#         internal_patterns = ['signup', 'login', 'auth', 'checkpoint', 'cold-join', 'registration', 'sign-in']
#         for pattern in internal_patterns:
#             if pattern in url_lower:
#                 return True

#         return False

#     def scrape_all_jobs_batch(self, keywords: List[str], location: str = "United States",
#                               max_workers: int = 5, save_to_db: bool = True) -> List[JobPost]:
#         """
#         Scrape ALL jobs posted in last 24 hours for multiple keywords in parallel.
#         No per-keyword job limit — fetches every page until LinkedIn returns empty.
#         """
#         all_jobs = []
#         all_job_dicts = []

#         # ── Phase 1: collect job IDs for every keyword ──────────────────────
#         all_search_results = []
#         seen_global_ids = set()   # Global dedup across keywords
#         total_keywords = len(keywords)

#         for idx, keyword in enumerate(keywords):
#             print(f"\n{'='*60}")
#             print(f"🔍 [{idx+1}/{total_keywords}] Searching ALL jobs for: {keyword}")
#             print(f"{'='*60}")

#             jobs = self.search_all_jobs(keyword, location, hours_old=24)

#             added = 0
#             for job in jobs:
#                 if job["job_id"] not in seen_global_ids:
#                     seen_global_ids.add(job["job_id"])
#                     job["keyword"] = keyword
#                     all_search_results.append(job)
#                     added += 1

#             print(f"   ✅ {idx+1}/{total_keywords} done  |  +{added} new unique jobs  |  running total: {len(all_search_results)}")

#             if idx < len(keywords) - 1:
#                 delay = random.uniform(3, 6)
#                 print(f"   ⏱️  Waiting {delay:.1f}s before next keyword...")
#                 time.sleep(delay)

#         print(f"\n{'='*60}")
#         print(f"📊 TOTAL UNIQUE JOBS FOUND: {len(all_search_results)}")
#         print(f"{'='*60}")

#         if not all_search_results:
#             print("❌ No jobs found for any keyword")
#             return []

#         # ── Phase 2: fetch details in parallel (extracts external links) ────
#         print(f"\n🔗 Fetching details for {len(all_search_results)} jobs ({max_workers} parallel workers)...")

#         actual_workers = min(max_workers, 10)

#         with ThreadPoolExecutor(max_workers=actual_workers) as executor:
#             future_to_job = {
#                 executor.submit(self.get_job_details, job["job_id"], job): job
#                 for job in all_search_results
#             }

#             completed = 0
#             external_count = 0
#             salary_count = 0
#             exp_count = 0
#             total = len(all_search_results)

#             for future in as_completed(future_to_job):
#                 completed += 1
#                 job = future_to_job[future]

#                 if completed % 25 == 0 or completed == 1 or completed == total:
#                     pct = completed / total * 100
#                     print(f"   Progress: {completed}/{total} ({pct:.1f}%) | "
#                           f"external={external_count} salary={salary_count}")

#                 try:
#                     job_post = future.result(timeout=15)
#                     if job_post:
#                         all_jobs.append(job_post)

#                         if job_post.apply_url:
#                             external_count += 1
#                         if job_post.compensation and job_post.compensation.min_amount:
#                             salary_count += 1
#                         if job_post.experience:
#                             exp_count += 1

#                         job_dict = job_post.to_supabase_dict()
#                         all_job_dicts.append(job_dict)

#                 except Exception as e:
#                     print(f"   ✗ Error processing job {job['job_id']}: {e}")

#         # ── Phase 3: save to Supabase ────────────────────────────────────────
#         if save_to_db and self.db and self.db.initialized and all_job_dicts:
#             self.db.save_jobs_batch(all_job_dicts)
#         elif save_to_db:
#             print("\n⚠️ Supabase not initialised — skipping database save")

#         # ── Final summary ────────────────────────────────────────────────────
#         print(f"\n{'='*60}")
#         print("✅ SCRAPE COMPLETE")
#         print(f"{'='*60}")
#         if all_jobs:
#             print(f"📊 Total jobs processed : {len(all_jobs)}")
#             print(f"🔗 External links found : {external_count} ({external_count/len(all_jobs)*100:.1f}%)")
#             print(f"💰 Jobs with salary info: {salary_count} ({salary_count/len(all_jobs)*100:.1f}%)")
#             print(f"📝 Jobs with experience : {exp_count} ({exp_count/len(all_jobs)*100:.1f}%)")

#         return all_jobs

#     def save_to_csv(self, jobs: List[JobPost], filename: str = None):
#         """Save jobs to CSV file with enhanced fields"""
#         if not filename:
#             filename = f"linkedin_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

#         import csv
#         with open(filename, 'w', newline='', encoding='utf-8') as f:
#             writer = csv.writer(f)
#             writer.writerow([
#                 'Job ID', 'Title', 'Company', 'Company Logo', 'Location', 'Date Posted',
#                 'Job URL', 'External Apply URL', 'Is Remote', 'Is Easy Apply',
#                 'Job Type', 'Job Level', 'Industry', 'Search Keyword',
#                 'Salary Min', 'Salary Max', 'Salary Text', 'Experience Required',
#                 'Description Preview'
#             ])

#             for job in jobs:
#                 writer.writerow([
#                     job.job_id,
#                     job.title,
#                     job.company_name,
#                     job.company_logo or '',
#                     job.location.display_location(),
#                     job.date_posted,
#                     job.job_url,
#                     job.apply_url or '',
#                     job.is_remote,
#                     job.is_easy_apply,
#                     ', '.join([jt.value for jt in job.job_type]) if job.job_type else '',
#                     job.job_level or '',
#                     job.company_industry or '',
#                     job.search_keyword or '',
#                     job.compensation.min_amount if job.compensation else '',
#                     job.compensation.max_amount if job.compensation else '',
#                     getattr(job, 'salary_text', ''),
#                     getattr(job, 'experience', ''),
#                     job.description[:200] + '...' if job.description and len(job.description) > 200 else (job.description or '')
#                 ])

#         print(f"💾 Saved {len(jobs)} jobs to {filename}")
        
# #         print(f"💾 Saved {len(jobs)} jobs to {filename}")




























# """Main LinkedIn scraper class - optimized for external link extraction with Supabase"""

# import time
# import random
# import re
# from datetime import datetime, date
# from typing import Optional, List, Dict, Any, Tuple
# from urllib.parse import urlparse, unquote, parse_qs
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import threading
# import json

# import requests
# from bs4 import BeautifulSoup
# from bs4.element import Tag

# from .models import JobPost, Location, Compensation, Country, JobType
# from .constant import headers
# from .util import (
#     job_type_code,
#     parse_job_type,
#     parse_job_level,
#     parse_company_industry,
#     is_job_remote,
#     extract_external_url_from_html,
#     extract_emails_from_text,
#     currency_parser,
#     parse_relative_date,
#     create_session,
#     remove_attributes,
#     parse_salary_from_text,
#     parse_experience_from_text,
#     extract_company_logo,
# )
# from .database import SupabaseManager


# class LinkedInScraper:
#     """High-performance LinkedIn scraper focused on external links with Supabase storage"""

#     def __init__(self, proxies=None, ca_cert=None, user_agent=None, use_database=True):
#         self.base_url = "https://www.linkedin.com"
#         self.session = create_session(proxies=proxies, ca_cert=ca_cert)
#         self.session.headers.update(headers)

#         # Rate limiting
#         self.min_delay = 1.0
#         self.max_delay = 3.0
#         self.current_delay = self.min_delay
#         self.consecutive_errors = 0
#         self.max_consecutive_errors = 3
#         self.error_backoff = 1.5

#         # Thread safety
#         self._lock = threading.Lock()
#         self._extracted_links = set()

#         # Database
#         self.use_database = use_database
#         self.db = SupabaseManager() if use_database else None
#         if use_database:
#             self.db.initialize()

#     def _throttle(self):
#         """Apply throttling based on current delay"""
#         with self._lock:
#             time.sleep(self.current_delay + random.uniform(0, 0.5))

#     def _handle_error(self):
#         """Increase delay on errors"""
#         with self._lock:
#             self.consecutive_errors += 1
#             if self.consecutive_errors >= self.max_consecutive_errors:
#                 self.current_delay = min(self.current_delay * self.error_backoff, self.max_delay)
#                 self.consecutive_errors = 0
#                 print(f"⚠️ Increasing delay to {self.current_delay:.1f}s due to errors")

#     def _handle_success(self):
#         """Gradually decrease delay on success"""
#         with self._lock:
#             self.consecutive_errors = 0
#             if self.current_delay > self.min_delay:
#                 self.current_delay = max(self.current_delay / self.error_backoff, self.min_delay)

#     def search_all_jobs(self, keyword: str, location: str = "United States", hours_old: int = 24) -> List[Dict]:
#         """
#         Search for ALL jobs posted in the last N hours for a keyword.
#         Continues pagination until LinkedIn returns an empty page.

#         LinkedIn returns up to 25 jobs per page. We keep fetching pages
#         (start=0, 25, 50, ...) until we get an empty response, which signals
#         that we've exhausted all results for this keyword/time window.
#         """
#         jobs = []
#         seen_job_ids = set()  # Dedup guard
#         start = 0
#         page = 1
#         max_pages = 200        # Safety cap: 200 pages × 25 = up to 5,000 jobs per keyword
#         empty_page_retries = 2  # Retry an empty page before giving up (handles transient gaps)
#         consecutive_empty = 0

#         print(f"\n   📍 Searching all pages for: {keyword}")

#         while page <= max_pages:
#             params = {
#                 "keywords": keyword,
#                 "location": location,
#                 "distance": "100",
#                 "f_TPR": f"r{hours_old * 3600}",  # e.g. r86400 = last 24 hours
#                 "start": start,
#                 "refresh": True,
#             }

#             url = f"{self.base_url}/jobs-guest/jobs/api/seeMoreJobPostings/search"

#             try:
#                 self._throttle()
#                 response = self.session.get(url, params=params, timeout=15)

#                 if response.status_code == 429:
#                     wait = random.uniform(10, 20)
#                     print(f"   ⚠️ Rate limited (429). Waiting {wait:.0f}s before retry...")
#                     time.sleep(wait)
#                     # Don't advance the page — retry the same offset
#                     continue

#                 if response.status_code != 200:
#                     print(f"   ❌ Search failed: HTTP {response.status_code}")
#                     self._handle_error()
#                     break

#                 soup = BeautifulSoup(response.text, "html.parser")
#                 job_cards = soup.find_all("div", class_="base-card")

#                 # ---- Empty page handling ----------------------------------------
#                 if not job_cards:
#                     consecutive_empty += 1
#                     if consecutive_empty <= empty_page_retries:
#                         print(f"   ⚠️ Empty page at start={start} (attempt {consecutive_empty}/{empty_page_retries}), retrying...")
#                         time.sleep(random.uniform(3, 6))
#                         continue
#                     else:
#                         print(f"   ✅ Confirmed end of results after {len(jobs)} jobs (empty response at start={start})")
#                         break
#                 # ---- Non-empty page: reset the empty counter --------------------
#                 consecutive_empty = 0

#                 page_jobs = 0
#                 for card in job_cards:
#                     try:
#                         link_tag = card.find("a", class_="base-card__full-link")
#                         if not link_tag or not link_tag.get("href"):
#                             continue

#                         href = link_tag["href"]
#                         job_id = href.split("?")[0].split("-")[-1]

#                         # Skip duplicates (can happen across pages near boundaries)
#                         if job_id in seen_job_ids:
#                             continue
#                         seen_job_ids.add(job_id)

#                         title_tag = card.find("h3", class_="base-search-card__title")
#                         title = title_tag.get_text(strip=True) if title_tag else "Unknown"

#                         company_tag = card.find("h4", class_="base-search-card__subtitle")
#                         company = company_tag.get_text(strip=True) if company_tag else "Unknown"

#                         location_tag = card.find("span", class_="job-search-card__location")
#                         location_str = location_tag.get_text(strip=True) if location_tag else ""

#                         jobs.append({
#                             "job_id": job_id,
#                             "title": title,
#                             "company": company,
#                             "location": location_str,
#                             "link": f"{self.base_url}/jobs/view/{job_id}",
#                         })

#                         page_jobs += 1

#                     except Exception as e:
#                         print(f"   ⚠️ Error parsing job card: {e}")
#                         continue

#                 print(f"   📄 Page {page} (start={start}): {page_jobs} new jobs | Running total: {len(jobs)}")

#                 # Advance to next page unconditionally — stop only when page is empty
#                 start += 25
#                 page += 1
#                 self._handle_success()

#                 # Brief pause between pages to be polite
#                 time.sleep(random.uniform(1.0, 2.5))

#             except Exception as e:
#                 print(f"   ❌ Search error on page {page}: {e}")
#                 self._handle_error()
#                 # Give it one more shot after a backoff, then bail
#                 time.sleep(5)
#                 break

#         if page > max_pages:
#             print(f"   ⚠️ Reached safety limit of {max_pages} pages for '{keyword}'")

#         print(f"   📊 Total unique jobs found for '{keyword}': {len(jobs)}")
#         return jobs

#     def get_job_details(self, job_id: str, job_data: Dict = None) -> Optional[JobPost]:
#         """
#         Fetch detailed job information including external apply link.
#         This is the KEY function that extracts external URLs.

#         We fetch TWO endpoints:
#           1. /jobs-guest/jobs/api/jobPosting/{id}  - guest API, contains applyUrl in JSON-LD
#           2. /jobs/view/{id}                       - full page, used for metadata only
#         """
#         job_view_url = f"{self.base_url}/jobs/view/{job_id}"
#         api_url      = f"{self.base_url}/jobs-guest/jobs/api/jobPosting/{job_id}"

#         try:
#             # Step 1: guest API page - PRIMARY source for applyUrl
#             self._throttle()
#             api_response = self.session.get(api_url, timeout=10)

#             if api_response.status_code == 429:
#                 print(f"Rate limited for job {job_id}")
#                 return None

#             if api_response.status_code != 200:
#                 print(f"Failed to fetch job API {job_id}: {api_response.status_code}")
#                 return None

#             api_html = api_response.text
#             api_soup = BeautifulSoup(api_html, "html.parser")

#             # Step 2: view page for metadata (title, description, etc.)
#             self._throttle()
#             view_response = self.session.get(job_view_url, timeout=10)
#             if view_response.status_code == 200:
#                 html = view_response.text
#                 soup = BeautifulSoup(html, "html.parser")
#             else:
#                 html = api_html
#                 soup = api_soup

#             # EXTERNAL LINK EXTRACTION - api_html/api_soup is the primary source
#             external_url = self._extract_external_url_ultimate(api_soup, api_html, job_id, soup, html)

#             # Skip if it is a LinkedIn internal page
#             if external_url and self._is_linkedin_internal(external_url):
#                 external_url = None

#             # Extract job title
#             title = job_data.get("title") if job_data else ""
#             if not title:
#                 title_tag = soup.find("h1", class_="top-card-layout__title")
#                 title = title_tag.get_text(strip=True) if title_tag else "Unknown"

#             # Extract company
#             company = job_data.get("company") if job_data else ""
#             if not company:
#                 company_tag = soup.find("a", class_="topcard__org-name-link")
#                 company = company_tag.get_text(strip=True) if company_tag else "Unknown"

#             # Extract company logo
#             company_logo = extract_company_logo(soup)

#             # Extract description
#             description = ""
#             desc_selectors = [
#                 "div.show-more-less-html__markup",
#                 "div.description__text",
#                 "div.jobs-description__content",
#             ]
#             for selector in desc_selectors:
#                 desc_tag = soup.select_one(selector)
#                 if desc_tag:
#                     description = desc_tag.get_text(strip=True)
#                     break

#             # Extract location
#             location_str = job_data.get("location") if job_data else ""
#             if not location_str:
#                 location_tag = soup.find("span", class_="topcard__flavor--bullet")
#                 if location_tag:
#                     location_str = location_tag.get_text(strip=True)

#             location = Location.from_string(location_str) if location_str else Location()

#             # Extract date posted
#             date_posted = None
#             time_tag = soup.find("span", class_="posted-time-ago__text")
#             if time_tag:
#                 date_posted = parse_relative_date(time_tag.get_text(strip=True))

#             # Extract job type, level, industry
#             job_type = parse_job_type(soup)
#             job_level = parse_job_level(soup)
#             company_industry = parse_company_industry(soup)

#             # Extract salary information
#             salary_min, salary_max, salary_text = parse_salary_from_text(description, html)

#             # Extract experience requirements
#             experience = parse_experience_from_text(description, html)

#             # Check if remote
#             is_remote = is_job_remote(title, description, location)

#             # Check if easy apply (no external URL)
#             is_easy_apply = not external_url

#             # Create compensation object if salary found
#             compensation = None
#             if salary_min or salary_max:
#                 compensation = Compensation(
#                     min_amount=salary_min,
#                     max_amount=salary_max,
#                     currency="USD",
#                     interval="yearly"
#                 )

#             # Get search keyword from job_data if available
#             search_keyword = job_data.get("keyword") if job_data else None

#             # Create JobPost object
#             job = JobPost(
#                 job_id=job_id,
#                 title=title,
#                 company_name=company,
#                 company_logo=company_logo,
#                 location=location,
#                 description=description[:10000] if description else None,
#                 date_posted=date_posted,
#                 job_url=job_view_url,
#                 apply_url=external_url,
#                 job_url_direct=external_url,
#                 job_type=job_type,
#                 job_level=job_level,
#                 company_industry=company_industry,
#                 is_remote=is_remote,
#                 is_easy_apply=is_easy_apply,
#                 compensation=compensation,
#                 emails=extract_emails_from_text(description or ""),
#                 search_keyword=search_keyword,
#                 experience=experience,
#                 salary_text=salary_text,
#             )

#             self._handle_success()
#             return job

#         except Exception as e:
#             print(f"❌ Error fetching job {job_id}: {e}")
#             self._handle_error()
#             return None

#     # ===== EXTERNAL LINK EXTRACTION =====
#     def _extract_external_url_ultimate(self, api_soup: BeautifulSoup, api_html: str,
#                                         job_id: str,
#                                         view_soup: BeautifulSoup = None,
#                                         view_html: str = None) -> str:
#         """
#         Extract the external apply URL.

#         api_soup / api_html  = /jobs-guest/jobs/api/jobPosting/{id}
#                                The ONLY reliable source of applyUrl for guests.
#                                LinkedIn embeds it in a JSON-LD <script> block.

#         view_soup / view_html = /jobs/view/{id}  (fallback only)
#         """
#         print("      Searching for external link...")

#         # METHOD 1: JSON-LD block in API response
#         # LinkedIn JobPosting schema: {"@type":"JobPosting", "url":"https://..."}
#         for script in api_soup.find_all("script", {"type": "application/ld+json"}):
#             try:
#                 data = json.loads(script.string or "")
#                 for key in ("applyUrl", "url", "applicationContact", "sameAs"):
#                     val = data.get(key)
#                     if val and isinstance(val, str) and val.startswith("http") and "linkedin.com" not in val:
#                         print(f"      FOUND via JSON-LD [{key}]: {val[:80]}")
#                         return val
#             except Exception:
#                 pass

#         # METHOD 2: Regex on raw API HTML
#         # Handles: "applyUrl":"https://..."  AND  applyUrl\":\"https://...
#         pat1 = r'"applyUrl"\s*:\s*"(https?://[^"]+)"'
#         pat2 = r'"externalApplyUrl"\s*:\s*"(https?://[^"]+)"'
#         pat3 = r'applyUrl\\":\\"(https?://[^\\"]+)\\"'
#         for pattern in [pat1, pat2, pat3]:
#             for raw in re.findall(pattern, api_html, re.IGNORECASE):
#                 url = unquote(raw.replace("\\u002F", "/").replace("\\/", "/"))
#                 if url and "linkedin.com" not in url and url.startswith("http"):
#                     print(f"      FOUND via API regex: {url[:80]}")
#                     return url

#         # METHOD 3: <code id="applyUrl"> tag
#         code_tag = api_soup.find("code", {"id": "applyUrl"})
#         if code_tag:
#             raw = code_tag.get_text(strip=True)
#             url = unquote(raw.replace("\\/", "/"))
#             if url and "linkedin.com" not in url and url.startswith("http"):
#                 print(f"      FOUND via <code id=applyUrl>: {url[:80]}")
#                 return url

#         # METHOD 4: <a> anchors in API response pointing outside LinkedIn
#         for a in api_soup.find_all("a", href=True):
#             href = a["href"]
#             if href.startswith("http") and "linkedin.com" not in href:
#                 txt = a.get_text(strip=True).lower()
#                 cls = " ".join(a.get("class", [])).lower()
#                 if any(w in txt or w in cls for w in ["apply", "application", "submit", "external"]):
#                     print(f"      FOUND via API anchor: {href[:80]}")
#                     return href

#         # METHOD 5: /jobs/view/externalApply/{id}?url=... redirect in API HTML
#         ext_re = rf'(?:externalApply|jobs/view/externalApply)/{re.escape(job_id)}\?url=([^"&\s>]+)'
#         m = re.search(ext_re, api_html, re.IGNORECASE)
#         if m:
#             url = unquote(m.group(1))
#             if url and "linkedin.com" not in url:
#                 print(f"      FOUND via externalApply redirect: {url[:80]}")
#                 return url

#         # FALLBACK: search the /jobs/view/ page
#         if view_html and view_soup:
#             fp1 = r'"applyUrl"\s*:\s*"(https?://[^"]+)"'
#             fp2 = r'applyUrl\\":\\"(https?://[^\\"]+)\\"'
#             for script in view_soup.find_all("script"):
#                 if not script.string:
#                     continue
#                 for pattern in [fp1, fp2]:
#                     for raw in re.findall(pattern, script.string, re.IGNORECASE):
#                         url = unquote(raw.replace("\\/", "/"))
#                         if url and "linkedin.com" not in url and url.startswith("http"):
#                             print(f"      FOUND via view-page script: {url[:80]}")
#                             return url
#             m = re.search(ext_re, view_html, re.IGNORECASE)
#             if m:
#                 url = unquote(m.group(1))
#                 if url and "linkedin.com" not in url:
#                     print(f"      FOUND via view-page externalApply: {url[:80]}")
#                     return url

#         print("      No external link found (Easy Apply job)")
#         return None

#     def _is_linkedin_internal(self, url: str) -> bool:
#         """Check if URL is a LinkedIn internal page"""
#         if not url:
#             return True

#         url_lower = url.lower()

#         if 'linkedin.com' in url_lower:
#             return True

#         internal_patterns = ['signup', 'login', 'auth', 'checkpoint', 'cold-join', 'registration', 'sign-in']
#         for pattern in internal_patterns:
#             if pattern in url_lower:
#                 return True

#         return False

#     def scrape_all_jobs_batch(self, keywords: List[str], location: str = "United States",
#                               max_workers: int = 5, save_to_db: bool = True) -> List[JobPost]:
#         """
#         Scrape ALL jobs posted in last 24 hours for multiple keywords in parallel.
#         No per-keyword job limit — fetches every page until LinkedIn returns empty.
#         After each keyword: search → fetch details → save to DB, then move to next keyword.
#         """
#         all_jobs = []
#         all_job_dicts = []

#         seen_global_ids = set()   # Global dedup across keywords
#         total_keywords = len(keywords)
#         actual_workers = min(max_workers, 10)
#         total_saved_to_db = 0

#         # ── Grand totals for final summary ──────────────────────────────────
#         grand_external = 0
#         grand_salary = 0
#         grand_exp = 0

#         def _flush_to_db(batch: list, keyword: str):
#             """Save a batch of job dicts to Supabase immediately."""
#             nonlocal total_saved_to_db
#             if not (save_to_db and self.db and self.db.initialized and batch):
#                 return
#             try:
#                 self.db.save_jobs_batch(batch)
#                 total_saved_to_db += len(batch)
#                 print(f"   💾 [{keyword}] Saved {len(batch)} jobs to Supabase "
#                       f"(total saved so far: {total_saved_to_db})")
#             except Exception as db_err:
#                 print(f"   ⚠️ DB save error for [{keyword}]: {db_err} — {len(batch)} jobs NOT saved")

#         if save_to_db and not (self.db and self.db.initialized):
#             print("\n⚠️ Supabase not initialised — DB saves will be skipped")

#         # ── Per-keyword loop: search → fetch details → save → next ──────────
#         for idx, keyword in enumerate(keywords):
#             print(f"\n{'='*60}")
#             print(f"🔍 [{idx+1}/{total_keywords}] Keyword: {keyword}")
#             print(f"{'='*60}")

#             # Phase 1: collect job IDs for this keyword
#             raw_jobs = self.search_all_jobs(keyword, location, hours_old=24)

#             keyword_search_results = []
#             for job in raw_jobs:
#                 if job["job_id"] not in seen_global_ids:
#                     seen_global_ids.add(job["job_id"])
#                     job["keyword"] = keyword
#                     keyword_search_results.append(job)

#             print(f"   📋 {len(keyword_search_results)} unique new jobs to fetch for '{keyword}'")

#             if not keyword_search_results:
#                 print(f"   ⏭️  No new jobs — skipping to next keyword")
#                 if idx < total_keywords - 1:
#                     delay = random.uniform(3, 6)
#                     print(f"   ⏱️  Waiting {delay:.1f}s before next keyword...")
#                     time.sleep(delay)
#                 continue

#             # Phase 2: fetch details for this keyword's jobs in parallel
#             print(f"   🔗 Fetching details ({actual_workers} workers)...")

#             keyword_jobs = []
#             keyword_job_dicts = []
#             external_count = 0
#             salary_count = 0
#             exp_count = 0
#             completed = 0
#             kw_total = len(keyword_search_results)

#             with ThreadPoolExecutor(max_workers=actual_workers) as executor:
#                 future_to_job = {
#                     executor.submit(self.get_job_details, job["job_id"], job): job
#                     for job in keyword_search_results
#                 }

#                 for future in as_completed(future_to_job):
#                     completed += 1
#                     job = future_to_job[future]

#                     if completed % 25 == 0 or completed == 1 or completed == kw_total:
#                         pct = completed / kw_total * 100
#                         print(f"   Progress: {completed}/{kw_total} ({pct:.1f}%) | "
#                               f"external={external_count} salary={salary_count}")

#                     try:
#                         job_post = future.result(timeout=15)
#                         if job_post:
#                             keyword_jobs.append(job_post)
#                             all_jobs.append(job_post)

#                             if job_post.apply_url:
#                                 external_count += 1
#                             if job_post.compensation and job_post.compensation.min_amount:
#                                 salary_count += 1
#                             if job_post.experience:
#                                 exp_count += 1

#                             job_dict = job_post.to_supabase_dict()
#                             keyword_job_dicts.append(job_dict)
#                             all_job_dicts.append(job_dict)

#                     except Exception as e:
#                         print(f"   ✗ Error processing job {job['job_id']}: {e}")

#             # Phase 3: save this keyword's jobs to DB immediately
#             _flush_to_db(keyword_job_dicts, keyword)

#             # Accumulate grand totals
#             grand_external += external_count
#             grand_salary += salary_count
#             grand_exp += exp_count

#             print(f"   ✅ [{idx+1}/{total_keywords}] '{keyword}' done | "
#                   f"jobs={len(keyword_jobs)} external={external_count} | "
#                   f"running total={len(all_jobs)}")

#             # Delay between keywords (skip after last one)
#             if idx < total_keywords - 1:
#                 delay = random.uniform(3, 6)
#                 print(f"   ⏱️  Waiting {delay:.1f}s before next keyword...")
#                 time.sleep(delay)

#         # ── Final summary ────────────────────────────────────────────────────
#         print(f"\n{'='*60}")
#         print("✅ SCRAPE COMPLETE")
#         print(f"{'='*60}")
#         if all_jobs:
#             print(f"📊 Total jobs processed : {len(all_jobs)}")
#             print(f"🔗 External links found : {grand_external} ({grand_external/len(all_jobs)*100:.1f}%)")
#             print(f"💰 Jobs with salary info: {grand_salary} ({grand_salary/len(all_jobs)*100:.1f}%)")
#             print(f"📝 Jobs with experience : {grand_exp} ({grand_exp/len(all_jobs)*100:.1f}%)")
#             print(f"💾 Total saved to DB    : {total_saved_to_db}")

#         return all_jobs

#     def save_to_csv(self, jobs: List[JobPost], filename: str = None):
#         """Save jobs to CSV file with enhanced fields"""
#         if not filename:
#             filename = f"linkedin_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

#         import csv
#         with open(filename, 'w', newline='', encoding='utf-8') as f:
#             writer = csv.writer(f)
#             writer.writerow([
#                 'Job ID', 'Title', 'Company', 'Company Logo', 'Location', 'Date Posted',
#                 'Job URL', 'External Apply URL', 'Is Remote', 'Is Easy Apply',
#                 'Job Type', 'Job Level', 'Industry', 'Search Keyword',
#                 'Salary Min', 'Salary Max', 'Salary Text', 'Experience Required',
#                 'Description Preview'
#             ])

#             for job in jobs:
#                 writer.writerow([
#                     job.job_id,
#                     job.title,
#                     job.company_name,
#                     job.company_logo or '',
#                     job.location.display_location(),
#                     job.date_posted,
#                     job.job_url,
#                     job.apply_url or '',
#                     job.is_remote,
#                     job.is_easy_apply,
#                     ', '.join([jt.value for jt in job.job_type]) if job.job_type else '',
#                     job.job_level or '',
#                     job.company_industry or '',
#                     job.search_keyword or '',
#                     job.compensation.min_amount if job.compensation else '',
#                     job.compensation.max_amount if job.compensation else '',
#                     getattr(job, 'salary_text', ''),
#                     getattr(job, 'experience', ''),
#                     job.description[:200] + '...' if job.description and len(job.description) > 200 else (job.description or '')
#                 ])

#         print(f"💾 Saved {len(jobs)} jobs to {filename}")














































"""Main LinkedIn scraper class - optimized for external link extraction with Supabase"""

import time
import random
import re
import json
import threading
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
from urllib.parse import urlparse, unquote, parse_qs, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

from .models import JobPost, Location, Compensation, Country, JobType
from .constant import headers
from .util import (
    job_type_code,
    parse_job_type,
    parse_job_level,
    parse_company_industry,
    is_job_remote,
    extract_external_url_from_html,
    extract_emails_from_text,
    currency_parser,
    parse_relative_date,
    create_session,
    remove_attributes,
    parse_salary_from_text,
    parse_experience_from_text,
    extract_company_logo,
)
from .database import SupabaseManager


# ─────────────────────────────────────────────────────────────────────────────
# Every field name LinkedIn has ever used for the external apply URL.
# Ordered by how commonly they appear in production.
# ─────────────────────────────────────────────────────────────────────────────
_APPLY_FIELDS = [
    "offsiteApplyUrl",
    "companyApplyUrl",
    "applyUrl",
    "externalApplyUrl",
    "applyLink",
    "apply_url",
    "applicationUrl",
]


def _clean(raw: str) -> str:
    """
    Decode every escape format LinkedIn uses inside HTML/JS:
      \\u0026  →  &
      \\u002F  →  /
      \\/      →  /
      %xx      →  decoded (handles double-encoding too)
    """
    if not raw:
        return ""
    s = raw
    try:
        # decode unicode escapes like \u0026
        s = s.encode("raw_unicode_escape").decode("unicode_escape")
    except Exception:
        pass
    s = s.replace("\\/", "/")
    prev = None
    while s != prev:
        prev = s
        s = unquote(s)
    return s.strip()


def _is_external(url: str) -> bool:
    """True only for real third-party URLs that are not LinkedIn."""
    if not url or not url.startswith("http"):
        return False
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return False
    return (
        "linkedin.com" not in host
        and "lnkd.in" not in host
        and host != ""
    )


def _scrape_apply_url(html: str) -> Optional[str]:
    """
    Search raw HTML string for all known LinkedIn apply-URL patterns.
    Returns the first valid external URL found, or None.

    Covers every encoding context seen in LinkedIn responses:
      1. Plain JSON          "offsiteApplyUrl":"https://..."
      2. Escaped-quote JSON  \"offsiteApplyUrl\":\"https://...\"
      3. Unicode-escaped     \\u0026 inside the value
      4. Percent-encoded     %2F inside the value
      5. <code id="applyUrl"> comment block
      6. Voyager OffsiteApply blob
      7. externalApply redirect query string
    """

    for field in _APPLY_FIELDS:
        ef = re.escape(field)

        # ── Pattern 1: plain JSON  "field":"value" ────────────────────────
        for m in re.finditer(rf'"{ef}"\s*:\s*"((?:[^"\\]|\\.)*)"', html):
            url = _clean(m.group(1))
            if _is_external(url):
                return url

        # ── Pattern 2: escaped-quote  \"field\":\"value\" ─────────────────
        for m in re.finditer(rf'\\"{{0}}\\":\\"((?:[^\\"]|\\[^"])*?)\\"'.format(ef), html):
            url = _clean(m.group(1))
            if _is_external(url):
                return url

        # ── Pattern 3: single-quoted  'field':'value' ─────────────────────
        for m in re.finditer(rf"'{ef}'\s*:\s*'([^']*)'", html):
            url = _clean(m.group(1))
            if _is_external(url):
                return url

    # ── Pattern 4: <code id="applyUrl"> HTML-comment block ───────────────
    # Content: <!-- "https://linkedin.com/...externalApply/ID?url=ENCODED" -->
    code_m = re.search(r'<code[^>]+id=["\']applyUrl["\'][^>]*>(.*?)</code>',
                       html, re.IGNORECASE | re.DOTALL)
    if code_m:
        inner = code_m.group(1)
        # extract the url= query param
        qm = re.search(r'[?&]url=([^&"\s>]+)', inner)
        if qm:
            url = _clean(qm.group(1))
            if _is_external(url):
                return url
        # fallback: grab any http URL inside the block
        for m in re.finditer(r'https?://[^\s"\'<>\\]+', _clean(inner)):
            url = m.group(0).rstrip(".,;)")
            if _is_external(url):
                return url

    # ── Pattern 5: Voyager OffsiteApply blob ─────────────────────────────
    # "com.linkedin.voyager.jobs.OffsiteApply":{"companyApplyUrl":"https://..."}
    for m in re.finditer(r'"companyApplyUrl"\s*:\s*"((?:[^"\\]|\\.)*)"', html):
        url = _clean(m.group(1))
        if _is_external(url):
            return url

    # ── Pattern 6: externalApply redirect  ?url=ENCODED  in any href ─────
    for m in re.finditer(r'externalApply[^"\']*[?&]url=([^&"\'>\s]+)', html, re.IGNORECASE):
        url = _clean(m.group(1))
        if _is_external(url):
            return url

    # ── Pattern 7: any bare external http URL next to apply-related key ──
    for m in re.finditer(
        r'(?:apply|offsite|external)[^"\']{0,40}(https?://[^\s"\'<>\\]{10,})',
        html, re.IGNORECASE
    ):
        url = _clean(m.group(1)).rstrip(".,;),\"'")
        if _is_external(url):
            return url

    return None


class LinkedInScraper:
    """High-performance LinkedIn scraper focused on external links with Supabase storage"""

    def __init__(self, proxies=None, ca_cert=None, user_agent=None, use_database=True):
        self.base_url = "https://www.linkedin.com"
        self.session = create_session(proxies=proxies, ca_cert=ca_cert)
        self.session.headers.update(headers)

        self.min_delay = 1.0
        self.max_delay = 3.0
        self.current_delay = self.min_delay
        self.consecutive_errors = 0
        self.max_consecutive_errors = 3
        self.error_backoff = 1.5

        self._lock = threading.Lock()
        self._extracted_links = set()

        self.use_database = use_database
        self.db = SupabaseManager() if use_database else None
        if use_database:
            self.db.initialize()

    def _throttle(self):
        with self._lock:
            time.sleep(self.current_delay + random.uniform(0, 0.5))

    def _handle_error(self):
        with self._lock:
            self.consecutive_errors += 1
            if self.consecutive_errors >= self.max_consecutive_errors:
                self.current_delay = min(self.current_delay * self.error_backoff, self.max_delay)
                self.consecutive_errors = 0
                print(f"⚠️ Increasing delay to {self.current_delay:.1f}s due to errors")

    def _handle_success(self):
        with self._lock:
            self.consecutive_errors = 0
            if self.current_delay > self.min_delay:
                self.current_delay = max(self.current_delay / self.error_backoff, self.min_delay)

    # ─────────────────────────────────────────────────────────────────────────
    # SEARCH
    # ─────────────────────────────────────────────────────────────────────────

    def search_all_jobs(self, keyword: str, location: str = "United States",
                        hours_old: int = 24) -> List[Dict]:
        jobs = []
        seen_job_ids = set()
        start = 0
        page = 1
        max_pages = 200
        empty_page_retries = 2
        consecutive_empty = 0

        print(f"\n   📍 Searching all pages for: {keyword}")

        while page <= max_pages:
            params = {
                "keywords": keyword,
                "location": location,
                "distance": "100",
                "f_TPR": f"r{hours_old * 3600}",
                "start": start,
                "refresh": True,
            }
            url = f"{self.base_url}/jobs-guest/jobs/api/seeMoreJobPostings/search"

            try:
                self._throttle()
                response = self.session.get(url, params=params, timeout=15)

                if response.status_code == 429:
                    wait = random.uniform(10, 20)
                    print(f"   ⚠️ Rate limited. Waiting {wait:.0f}s...")
                    time.sleep(wait)
                    continue

                if response.status_code != 200:
                    print(f"   ❌ Search failed: HTTP {response.status_code}")
                    self._handle_error()
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                job_cards = soup.find_all("div", class_="base-card")

                if not job_cards:
                    consecutive_empty += 1
                    if consecutive_empty <= empty_page_retries:
                        print(f"   ⚠️ Empty page at start={start} ({consecutive_empty}/{empty_page_retries}), retrying...")
                        time.sleep(random.uniform(3, 6))
                        continue
                    else:
                        print(f"   ✅ End of results after {len(jobs)} jobs")
                        break
                consecutive_empty = 0

                page_jobs = 0
                for card in job_cards:
                    try:
                        link_tag = card.find("a", class_="base-card__full-link")
                        if not link_tag or not link_tag.get("href"):
                            continue
                        href = link_tag["href"]
                        job_id = href.split("?")[0].split("-")[-1]
                        if job_id in seen_job_ids:
                            continue
                        seen_job_ids.add(job_id)

                        title_tag = card.find("h3", class_="base-search-card__title")
                        title = title_tag.get_text(strip=True) if title_tag else "Unknown"
                        company_tag = card.find("h4", class_="base-search-card__subtitle")
                        company = company_tag.get_text(strip=True) if company_tag else "Unknown"
                        location_tag = card.find("span", class_="job-search-card__location")
                        location_str = location_tag.get_text(strip=True) if location_tag else ""

                        jobs.append({
                            "job_id": job_id,
                            "title": title,
                            "company": company,
                            "location": location_str,
                            "link": f"{self.base_url}/jobs/view/{job_id}",
                        })
                        page_jobs += 1
                    except Exception as e:
                        print(f"   ⚠️ Card parse error: {e}")
                        continue

                print(f"   📄 Page {page} (start={start}): {page_jobs} jobs | total={len(jobs)}")
                start += 25
                page += 1
                self._handle_success()
                time.sleep(random.uniform(1.0, 2.5))

            except Exception as e:
                print(f"   ❌ Search error page {page}: {e}")
                self._handle_error()
                time.sleep(5)
                break

        print(f"   📊 Total unique jobs for '{keyword}': {len(jobs)}")
        return jobs

    # ─────────────────────────────────────────────────────────────────────────
    # JOB DETAILS  +  EXTERNAL URL EXTRACTION
    # ─────────────────────────────────────────────────────────────────────────

    def _fetch_external_url(self, job_id: str,
                            api_html: str, view_html: str) -> Optional[str]:
        """
        Try every source in priority order and return the first external URL found.

        Priority:
          1. view page raw HTML   (offsiteApplyUrl lives here per screenshot)
          2. API page raw HTML    (sometimes has applyUrl / companyApplyUrl)
          3. JSON-LD blocks       (structured data on both pages)
          4. <a> anchor tags      (external hrefs with apply-related context)
        """

        # ── 1 & 2: raw HTML search on both pages ─────────────────────────────
        for label, html in [("view", view_html), ("api", api_html)]:
            if not html:
                continue
            url = _scrape_apply_url(html)
            if url:
                print(f"      ✅ [{label}] {url[:80]}")
                return url

        # ── 3: JSON-LD blocks ─────────────────────────────────────────────────
        for label, html in [("view", view_html), ("api", api_html)]:
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            for script in soup.find_all("script", {"type": "application/ld+json"}):
                try:
                    data = json.loads(script.string or "")
                    nodes = [data] + (data.get("@graph") or [])
                    for node in nodes:
                        if not isinstance(node, dict):
                            continue
                        for key in _APPLY_FIELDS + ["sameAs"]:
                            val = node.get(key)
                            if isinstance(val, str):
                                url = _clean(val)
                                if _is_external(url):
                                    print(f"      ✅ [JSON-LD/{label}/{key}] {url[:80]}")
                                    return url
                except Exception:
                    pass

        # ── 4: <a> anchors with external href + apply context ─────────────────
        apply_kw = {"apply", "application", "submit", "external", "offsite", "job"}
        for label, html in [("view", view_html), ("api", api_html)]:
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = _clean(a["href"])
                if not _is_external(href):
                    continue
                ctx = (
                    a.get_text(strip=True).lower()
                    + " ".join(a.get("class", [])).lower()
                    + (a.get("aria-label") or "").lower()
                )
                if any(k in ctx for k in apply_kw):
                    print(f"      ✅ [anchor/{label}] {href[:80]}")
                    return href

        print(f"      ℹ️  No external URL found for {job_id} — Easy Apply")
        return None

    def get_job_details(self, job_id: str, job_data: Dict = None) -> Optional[JobPost]:
        job_view_url = f"{self.base_url}/jobs/view/{job_id}"
        api_url      = f"{self.base_url}/jobs-guest/jobs/api/jobPosting/{job_id}"

        try:
            # ── fetch API page ────────────────────────────────────────────────
            self._throttle()
            api_resp = self.session.get(api_url, timeout=10)
            if api_resp.status_code == 429:
                print(f"      Rate limited for {job_id}")
                return None
            if api_resp.status_code != 200:
                print(f"      API fetch failed {job_id}: {api_resp.status_code}")
                return None
            api_html = api_resp.text

            # ── fetch view page ───────────────────────────────────────────────
            self._throttle()
            view_resp = self.session.get(job_view_url, timeout=10)
            view_html = view_resp.text if view_resp.status_code == 200 else ""
            soup = BeautifulSoup(view_html or api_html, "html.parser")

            # ── extract external URL ──────────────────────────────────────────
            external_url = self._fetch_external_url(job_id, api_html, view_html)

            # ── metadata ──────────────────────────────────────────────────────
            title = (job_data or {}).get("title", "")
            if not title:
                t = soup.find("h1", class_="top-card-layout__title")
                title = t.get_text(strip=True) if t else "Unknown"

            company = (job_data or {}).get("company", "")
            if not company:
                c = soup.find("a", class_="topcard__org-name-link")
                company = c.get_text(strip=True) if c else "Unknown"

            company_logo = extract_company_logo(soup)

            description = ""
            for sel in ["div.show-more-less-html__markup",
                        "div.description__text",
                        "div.jobs-description__content"]:
                d = soup.select_one(sel)
                if d:
                    description = d.get_text(strip=True)
                    break

            location_str = (job_data or {}).get("location", "")
            if not location_str:
                lt = soup.find("span", class_="topcard__flavor--bullet")
                location_str = lt.get_text(strip=True) if lt else ""
            location = Location.from_string(location_str) if location_str else Location()

            date_posted = None
            tt = soup.find("span", class_="posted-time-ago__text")
            if tt:
                date_posted = parse_relative_date(tt.get_text(strip=True))

            job_type        = parse_job_type(soup)
            job_level       = parse_job_level(soup)
            company_industry = parse_company_industry(soup)

            salary_min, salary_max, salary_text = parse_salary_from_text(
                description, view_html or api_html)
            experience = parse_experience_from_text(description, view_html or api_html)
            is_remote  = is_job_remote(title, description, location)

            compensation = None
            if salary_min or salary_max:
                compensation = Compensation(
                    min_amount=salary_min,
                    max_amount=salary_max,
                    currency="USD",
                    interval="yearly",
                )

            job = JobPost(
                job_id=job_id,
                title=title,
                company_name=company,
                company_logo=company_logo,
                location=location,
                description=description[:10000] if description else None,
                date_posted=date_posted,
                job_url=job_view_url,
                apply_url=external_url,
                job_url_direct=external_url,
                job_type=job_type,
                job_level=job_level,
                company_industry=company_industry,
                is_remote=is_remote,
                is_easy_apply=not external_url,
                compensation=compensation,
                emails=extract_emails_from_text(description or ""),
                search_keyword=(job_data or {}).get("keyword"),
                experience=experience,
                salary_text=salary_text,
            )

            self._handle_success()
            return job

        except Exception as e:
            print(f"❌ Error fetching job {job_id}: {e}")
            self._handle_error()
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # BATCH SCRAPE
    # ─────────────────────────────────────────────────────────────────────────

    def scrape_all_jobs_batch(self, keywords: List[str],
                              location: str = "United States",
                              max_workers: int = 5,
                              save_to_db: bool = True) -> List[JobPost]:

        all_jobs: List[JobPost] = []
        all_job_dicts: List[dict] = []
        seen_global_ids: set = set()
        total_keywords = len(keywords)
        actual_workers = min(max_workers, 5)   # hard cap at 5
        total_saved_to_db = 0
        grand_external = 0
        grand_salary = 0
        grand_exp = 0

        def _flush_to_db(batch: list, keyword: str):
            nonlocal total_saved_to_db
            if not (save_to_db and self.db and self.db.initialized and batch):
                return
            try:
                self.db.save_jobs_batch(batch)
                total_saved_to_db += len(batch)
                print(f"   💾 [{keyword}] Saved {len(batch)} jobs "
                      f"(total={total_saved_to_db})")
            except Exception as e:
                print(f"   ⚠️ DB save error [{keyword}]: {e}")

        if save_to_db and not (self.db and self.db.initialized):
            print("\n⚠️ Supabase not initialised — DB saves skipped")

        for idx, keyword in enumerate(keywords):
            print(f"\n{'='*60}")
            print(f"🔍 [{idx+1}/{total_keywords}] Keyword: {keyword}")
            print(f"{'='*60}")

            raw_jobs = self.search_all_jobs(keyword, location, hours_old=24)

            keyword_results = []
            for job in raw_jobs:
                if job["job_id"] not in seen_global_ids:
                    seen_global_ids.add(job["job_id"])
                    job["keyword"] = keyword
                    keyword_results.append(job)

            print(f"   📋 {len(keyword_results)} unique new jobs for '{keyword}'")

            if not keyword_results:
                if idx < total_keywords - 1:
                    delay = random.uniform(3, 6)
                    print(f"   ⏱️  Waiting {delay:.1f}s...")
                    time.sleep(delay)
                continue

            print(f"   🔗 Fetching details ({actual_workers} workers)...")

            keyword_jobs: List[JobPost] = []
            keyword_dicts: List[dict] = []
            external_count = salary_count = exp_count = completed = 0
            kw_total = len(keyword_results)

            with ThreadPoolExecutor(max_workers=actual_workers) as executor:
                future_to_job = {
                    executor.submit(self.get_job_details, j["job_id"], j): j
                    for j in keyword_results
                }
                for future in as_completed(future_to_job):
                    completed += 1
                    src_job = future_to_job[future]

                    if completed % 25 == 0 or completed == 1 or completed == kw_total:
                        print(f"   Progress: {completed}/{kw_total} "
                              f"({completed/kw_total*100:.0f}%) | "
                              f"external={external_count}")

                    try:
                        job_post = future.result(timeout=15)
                        if job_post:
                            keyword_jobs.append(job_post)
                            all_jobs.append(job_post)
                            if job_post.apply_url:
                                external_count += 1
                            if job_post.compensation and job_post.compensation.min_amount:
                                salary_count += 1
                            if job_post.experience:
                                exp_count += 1
                            d = job_post.to_supabase_dict()
                            keyword_dicts.append(d)
                            all_job_dicts.append(d)
                    except Exception as e:
                        print(f"   ✗ {src_job['job_id']}: {e}")

            _flush_to_db(keyword_dicts, keyword)
            grand_external += external_count
            grand_salary   += salary_count
            grand_exp      += exp_count

            print(f"   ✅ '{keyword}': {len(keyword_jobs)} jobs, "
                  f"{external_count} external links")

            if idx < total_keywords - 1:
                delay = random.uniform(3, 6)
                print(f"   ⏱️  Waiting {delay:.1f}s before next keyword...")
                time.sleep(delay)

        print(f"\n{'='*60}")
        print("✅ SCRAPE COMPLETE")
        print(f"{'='*60}")
        if all_jobs:
            pct = grand_external / len(all_jobs) * 100
            print(f"📊 Total jobs      : {len(all_jobs)}")
            print(f"🔗 External links  : {grand_external} ({pct:.1f}%)")
            print(f"💰 With salary     : {grand_salary}")
            print(f"📝 With experience : {grand_exp}")
            print(f"💾 Saved to DB     : {total_saved_to_db}")

        return all_jobs

    def save_to_csv(self, jobs: List[JobPost], filename: str = None):
        if not filename:
            filename = f"linkedin_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        import csv
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Job ID", "Title", "Company", "Company Logo", "Location",
                "Date Posted", "Job URL", "External Apply URL", "Is Remote",
                "Is Easy Apply", "Job Type", "Job Level", "Industry",
                "Search Keyword", "Salary Min", "Salary Max", "Salary Text",
                "Experience Required", "Description Preview",
            ])
            for job in jobs:
                writer.writerow([
                    job.job_id, job.title, job.company_name,
                    job.company_logo or "",
                    job.location.display_location(),
                    job.date_posted, job.job_url, job.apply_url or "",
                    job.is_remote, job.is_easy_apply,
                    ", ".join(jt.value for jt in job.job_type) if job.job_type else "",
                    job.job_level or "", job.company_industry or "",
                    job.search_keyword or "",
                    job.compensation.min_amount if job.compensation else "",
                    job.compensation.max_amount if job.compensation else "",
                    getattr(job, "salary_text", "") or "",
                    getattr(job, "experience", "") or "",
                    (job.description or "")[:200],
                ])
        print(f"💾 Saved {len(jobs)} jobs to {filename}")
