# #!/usr/bin/env python3
# """Main entry point for LinkedIn scraper with Supabase storage"""

# import sys
# import os
# import time
# from datetime import datetime
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# from src.linkedin_scraper import LinkedInScraper


# def main():
#     """Main function"""
    
#     print("=" * 70)
#     print("🚀 LINKEDIN EXTERNAL LINK SCRAPER WITH SUPABASE")
#     print("=" * 70)
    
#     # Configuration from environment variables
#     keywords = [
#         "Python Developer",
#         "Java Developer", 
#         "JavaScript Developer",
#         "React Developer",
#         "DevOps Engineer",
#     ]
    
#     location = os.getenv("LOCATION", "United States")
#     jobs_per_keyword = int(os.getenv("MAX_JOBS_PER_KEYWORD", "15"))
#     max_workers = int(os.getenv("MAX_WORKERS", "5"))
    
#     print(f"\n📋 Configuration:")
#     print(f"   Keywords: {', '.join(keywords[:3])}...")
#     print(f"   Location: {location}")
#     print(f"   Jobs per keyword: {jobs_per_keyword}")
#     print(f"   Parallel workers: {max_workers}")
#     print(f"   Supabase: Enabled")
    
#     # Initialize scraper with database
#     scraper = LinkedInScraper(use_database=True)
    
#     start_time = time.time()
    
#     try:
#         # Run scrape
#         jobs = scraper.scrape_batch(
#             keywords=keywords,
#             location=location,
#             jobs_per_keyword=jobs_per_keyword,
#             max_workers=max_workers,
#             save_to_db=True
#         )
        
#         # Save to CSV as backup
#         if jobs:
#             scraper.save_to_csv(jobs)
        
#         # Summary
#         elapsed = time.time() - start_time
#         external_count = sum(1 for j in jobs if j.apply_url)
        
#         print("\n" + "=" * 70)
#         print("✅ SCRAPE COMPLETE")
#         print("=" * 70)
#         print(f"📊 Total jobs: {len(jobs)}")
#         print(f"🔗 External links: {external_count}")
#         print(f"⏱️  Time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
#         print(f"⚡ Speed: {len(jobs)/elapsed:.1f} jobs/sec")
        
#         # Get database statistics if available
#         if scraper.db and scraper.db.initialized:
#             stats = scraper.db.get_statistics()
#             if stats:
#                 print("\n📊 Database Statistics:")
#                 print(f"   Total jobs in DB: {stats.get('total_jobs', 0)}")
#                 print(f"   External links in DB: {stats.get('external_links', 0)}")
#                 print(f"   Unique companies: {stats.get('unique_companies', 0)}")
#                 print(f"   Remote jobs: {stats.get('remote_jobs', 0)}")
        
#     except KeyboardInterrupt:
#         print("\n\n⚠️ Interrupted by user")
#     except Exception as e:
#         print(f"\n❌ Error: {e}")
#         import traceback
#         traceback.print_exc()


# if __name__ == "__main__":
#     main()




























# #!/usr/bin/env python3
# """Main entry point for LinkedIn scraper with Supabase storage"""

# import sys
# import os
# import time
# from datetime import datetime
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# from src.linkedin_scraper import LinkedInScraper


# def main():
#     """Main function"""
    
#     print("=" * 70)
#     print("🚀 LINKEDIN EXTERNAL LINK SCRAPER WITH SUPABASE")
#     print("=" * 70)
    
#     # Complete domain list from your requirements
#     keywords = [
#         "Actimize Developer",
#         "Active Directory",
#         "Agronomy Operations",
#         "AI/ML Engineer",
#         "Anti Money Laundering (AML)",
#         "Atlassian Engineer / Jira",
#         "Big Data Engineer",
#         "Bioinformatics",
#         "Bioinformatics for UK",
#         "Biotechnology",
#         "Biotechnology Internship",
#         "Business Analyst",
#         "Business Analyst for Canada",
#         "Business Intelligence Engineer",
#         "Business Intelligence Engineer Internships",
#         "Chemical Engineer",
#         "CLINICAL DATA ANALYST",
#         "Clinical Research Coordinator",
#         "Cloud Engineer",
#         "Cloud Engineer for Ireland",
#         "Computer Science",
#         "Computer Science Internship",
#         "Construction Management",
#         "Credit controller for UK",
#         "CRM Sales",
#         "CRM Specialist",
#         "Cyber security",
#         "Cybersecurity for Ireland",
#         "Cybersecurity for UK",
#         "Data Analyst",
#         "Data Analyst for Canada",
#         "Data Analyst for UK",
#         "Data Analyst Internship for Ireland",
#         "Data Analyst Internships",
#         "Database Administration",
#         "Data Center Technician",
#         "Data Engineer",
#         "Data Engineer (citizen/h4ead)",
#         "Data Engineer for UK",
#         "Data Science for Germany",
#         "Data Scientist",
#         "Design Verification Engineer",
#         "DevOps",
#         "DevOps for India",
#         "DevOps for Ireland",
#         "DevOps for UK",
#         "DevOps Internships",
#         "Dynamics 365",
#         "Electrical Engineer",
#         "Electrical Project",
#         "Electronic Health Records (EHR)",
#         "Embedded Software Engineer",
#         "Environmental Health and Safety (EHS)",
#         "Epic Analyst",
#         "ERP",
#         "Financial analyst",
#         "Financial analyst for Ireland",
#         "Frontend Engineering",
#         "Full Stack",
#         "Game Developer",
#         "Game UI / Interactive UI Designer",
#         "Generative AI",
#         "GRC Analyst",
#         "Healthcare Data Analyst",
#         "Healthcare data analyst, Health care business analyst,HeHalthcare data engineer",
#         "HR Recruiter",
#         "ITSM/ITIL",
#         "Java Developer",
#         "Java Full Stack",
#         "Manufacturing engineer (Mechanical)",
#         "Manufacturing engineer (Mechanical) for Canada",
#         "Marketing Automation Specialist",
#         "Mechanical Engineer",
#         "Medical Affairs",
#         "Medical Coding",
#         "MLOps Engineer",
#         ".Net",
#         ".Net for Ireland",
#         "Netsuite",
#         "Network Engineer",
#         "Network Security Engineer",
#         "Payroll Analyst",
#         "Pharmacovigilance",
#         "Photography",
#         "Product Manager",
#         "Project Coordinator for Canada",
#         "Project Management for Ireland",
#         "Project Management Internship",
#         "Project Manager",
#         "python developer",
#         "QA Automation Engineer",
#         "Quality Analyst",
#         "Quality Analyst for UK",
#         "Quality Assurance Engineer",
#         "Quality Engineer",
#         "Regulatory Affairs",
#         "RTL Design Engineer",
#         "Safety Analyst",
#         "Sailpoint",
#         "Sales executive for UK",
#         "Salesforce Developer",
#         "Salesforce Developer for UK",
#         "SAP",
#         "Sap basis and security",
#         "SAP FICO",
#         "SAP MM",
#         "Scrum Master",
#         "Security Engineer",
#         "ServiceNow Developer",
#         "Software Developer",
#         "Software Engineer",
#         "Software Engineer for Ireland",
#         "Software/Hardware Asset Management Analyst",
#         "Structural Engineer for Canada",
#         "Supply Chain",
#         "Supply Chain (citizen/h4ead)",
#         "Supply Chain for Ireland",
#         "Sustainability analyst for Ireland",
#         "System Infrastructure Engineer",
#         "Tax analyst",
#         "Technical program Management (citizen/h4ead)",
#         "Tosca Test Automation Engineer",
#         "UX Designer",
#         "Workday Analyst"
#     ]
    
#     location = os.getenv("LOCATION", "United States")
#     jobs_per_keyword = int(os.getenv("MAX_JOBS_PER_KEYWORD", "5"))  # Reduced to 5 since you have many keywords
#     max_workers = int(os.getenv("MAX_WORKERS", "5"))
    
#     print(f"\n📋 Configuration:")
#     print(f"   Keywords: {len(keywords)} domains to scrape")
#     print(f"   Location: {location}")
#     print(f"   Jobs per keyword: {jobs_per_keyword}")
#     print(f"   Parallel workers: {max_workers}")
#     print(f"   Supabase: {'Enabled' if os.getenv('SUPABASE_URL') else 'Disabled (CSV only)'}")
    
#     # Initialize scraper with database
#     scraper = LinkedInScraper(use_database=bool(os.getenv('SUPABASE_URL')))
    
#     start_time = time.time()
    
#     try:
#         # Run scrape
#         jobs = scraper.scrape_batch(
#             keywords=keywords,
#             location=location,
#             jobs_per_keyword=jobs_per_keyword,
#             max_workers=max_workers,
#             save_to_db=True
#         )
        
#         # Save to CSV as backup
#         if jobs:
#             scraper.save_to_csv(jobs)
        
#         # Summary
#         elapsed = time.time() - start_time
#         external_count = sum(1 for j in jobs if j.apply_url)
#         salary_count = sum(1 for j in jobs if j.compensation and j.compensation.min_amount)
#         exp_count = sum(1 for j in jobs if j.experience)
#         logo_count = sum(1 for j in jobs if j.company_logo)
        
#         print("\n" + "=" * 70)
#         print("✅ SCRAPE COMPLETE")
#         print("=" * 70)
#         print(f"📊 Total jobs: {len(jobs)}")
#         print(f"🔗 External links: {external_count}")
#         print(f"💰 Jobs with salary: {salary_count}")
#         print(f"📝 Jobs with experience: {exp_count}")
#         print(f"🖼️  Jobs with logo: {logo_count}")
#         print(f"⏱️  Time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
#         print(f"⚡ Speed: {len(jobs)/elapsed:.1f} jobs/sec")
        
#     except KeyboardInterrupt:
#         print("\n\n⚠️ Interrupted by user")
#     except Exception as e:
#         print(f"\n❌ Error: {e}")
#         import traceback
#         traceback.print_exc()


# if __name__ == "__main__":
#     main()






















































# #!/usr/bin/env python3
# """Main entry point for LinkedIn scraper - Scrapes ALL jobs from last 24 hours"""

# import sys
# import os
# import time
# from datetime import datetime
# from dotenv import load_dotenv

# load_dotenv()

# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# from src.linkedin_scraper import LinkedInScraper


# def main():
#     print("=" * 70)
#     print("🚀 LINKEDIN SCRAPER - ALL JOBS FROM LAST 24 HOURS")
#     print("=" * 70)

#     keywords = [
#         "Actimize Developer",
#         "Active Directory",
#         "Agronomy Operations",
#         "AI/ML Engineer",
#         "Anti Money Laundering (AML)",
#         "Atlassian Engineer / Jira",
#         "Big Data Engineer",
#         "Bioinformatics",
#         "Bioinformatics for UK",
#         "Biotechnology",
#         "Biotechnology Internship",
#         "Business Analyst",
#         "Business Analyst for Canada",
#         "Business Intelligence Engineer",
#         "Business Intelligence Engineer Internships",
#         "Chemical Engineer",
#         "CLINICAL DATA ANALYST",
#         "Clinical Research Coordinator",
#         "Cloud Engineer",
#         "Cloud Engineer for Ireland",
#         "Computer Science",
#         "Computer Science Internship",
#         "Construction Management",
#         "Credit controller for UK",
#         "CRM Sales",
#         "CRM Specialist",
#         "Cyber security",
#         "Cybersecurity for Ireland",
#         "Cybersecurity for UK",
#         "Data Analyst",
#         "Data Analyst for Canada",
#         "Data Analyst for UK",
#         "Data Analyst Internship for Ireland",
#         "Data Analyst Internships",
#         "Database Administration",
#         "Data Center Technician",
#         "Data Engineer",
#         "Data Engineer (citizen/h4ead)",
#         "Data Engineer for UK",
#         "Data Science for Germany",
#         "Data Scientist",
#         "Design Verification Engineer",
#         "DevOps",
#         "DevOps for India",
#         "DevOps for Ireland",
#         "DevOps for UK",
#         "DevOps Internships",
#         "Dynamics 365",
#         "Electrical Engineer",
#         "Electrical Project",
#         "Electronic Health Records (EHR)",
#         "Embedded Software Engineer",
#         "Environmental Health and Safety (EHS)",
#         "Epic Analyst",
#         "ERP",
#         "Financial analyst",
#         "Financial analyst for Ireland",
#         "Frontend Engineering",
#         "Full Stack",
#         "Game Developer",
#         "Game UI / Interactive UI Designer",
#         "Generative AI",
#         "GRC Analyst",
#         "Healthcare Data Analyst",
#         "Healthcare data analyst, Health care business analyst,HeHalthcare data engineer",
#         "HR Recruiter",
#         "ITSM/ITIL",
#         "Java Developer",
#         "Java Full Stack",
#         "Manufacturing engineer (Mechanical)",
#         "Manufacturing engineer (Mechanical) for Canada",
#         "Marketing Automation Specialist",
#         "Mechanical Engineer",
#         "Medical Affairs",
#         "Medical Coding",
#         "MLOps Engineer",
#         ".Net",
#         ".Net for Ireland",
#         "Netsuite",
#         "Network Engineer",
#         "Network Security Engineer",
#         "Payroll Analyst",
#         "Pharmacovigilance",
#         "Photography",
#         "Product Manager",
#         "Project Coordinator for Canada",
#         "Project Management for Ireland",
#         "Project Management Internship",
#         "Project Manager",
#         "python developer",
#         "QA Automation Engineer",
#         "Quality Analyst",
#         "Quality Analyst for UK",
#         "Quality Assurance Engineer",
#         "Quality Engineer",
#         "Regulatory Affairs",
#         "RTL Design Engineer",
#         "Safety Analyst",
#         "Sailpoint",
#         "Sales executive for UK",
#         "Salesforce Developer",
#         "Salesforce Developer for UK",
#         "SAP",
#         "Sap basis and security",
#         "SAP FICO",
#         "SAP MM",
#         "Scrum Master",
#         "Security Engineer",
#         "ServiceNow Developer",
#         "Software Developer",
#         "Software Engineer",
#         "Software Engineer for Ireland",
#         "Software/Hardware Asset Management Analyst",
#         "Structural Engineer for Canada",
#         "Supply Chain",
#         "Supply Chain (citizen/h4ead)",
#         "Supply Chain for Ireland",
#         "Sustainability analyst for Ireland",
#         "System Infrastructure Engineer",
#         "Tax analyst",
#         "Technical program Management (citizen/h4ead)",
#         "Tosca Test Automation Engineer",
#         "UX Designer",
#         "Workday Analyst"
#     ]

#     location    = os.getenv("LOCATION", "United States")
#     max_workers = int(os.getenv("MAX_WORKERS", "5"))

#     print(f"\n📋 Configuration:")
#     print(f"   📊 Keywords  : {len(keywords)} domains")
#     print(f"   🌎 Location  : {location}")
#     print(f"   ⏰ Time filter: Last 24 hours (ALL pages until empty)")
#     print(f"   🔄 Workers   : {max_workers}")
#     print(f"   📦 Supabase  : {'Enabled' if os.getenv('SUPABASE_URL') else 'Disabled (CSV only)'}")
#     print(f"\n   ℹ️  Pagination stops only when LinkedIn returns an empty page,")
#     print(f"   so every job posted in the last 24 hours will be collected.\n")

#     scraper = LinkedInScraper(use_database=bool(os.getenv('SUPABASE_URL')))
#     start_time = time.time()

#     try:
#         jobs = scraper.scrape_all_jobs_batch(
#             keywords=keywords,
#             location=location,
#             max_workers=max_workers,
#             save_to_db=True,
#         )

#         if jobs:
#             scraper.save_to_csv(jobs)

#         elapsed = time.time() - start_time
#         print("\n" + "=" * 70)
#         print("✅ FINAL SUMMARY")
#         print("=" * 70)
#         print(f"📊 Total jobs scraped : {len(jobs)}")
#         print(f"⏱️  Total time         : {elapsed:.1f}s  ({elapsed/60:.1f} min)")
#         if jobs:
#             print(f"⚡ Average speed      : {len(jobs)/elapsed:.1f} jobs/sec")

#     except KeyboardInterrupt:
#         print("\n\n⚠️ Interrupted by user")
#         if 'jobs' in locals() and jobs:
#             fname = f"linkedin_jobs_interrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#             print(f"💾 Saving {len(jobs)} jobs collected so far → {fname}")
#             scraper.save_to_csv(jobs, fname)

#     except Exception as e:
#         print(f"\n❌ Error: {e}")
#         import traceback
#         traceback.print_exc()


# if __name__ == "__main__":
#     main()










































































# #!/usr/bin/env python3
# """Main entry point for LinkedIn scraper - Scrapes ALL jobs from last 24 hours"""

# import sys
# import os
# import time
# from datetime import datetime
# from dotenv import load_dotenv

# load_dotenv()

# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# from src.linkedin_scraper import LinkedInScraper


# def main():
#     print("=" * 70)
#     print("🚀 LINKEDIN SCRAPER - ALL JOBS FROM LAST 24 HOURS")
#     print("=" * 70)

#     keywords = [
#         "Actimize Developer",
#         "Active Directory",
#         "Agronomy Operations",
#         "AI/ML Engineer",
#         "Anti Money Laundering (AML)",
#         "Atlassian Engineer / Jira",
#         "Big Data Engineer",
#         "Bioinformatics",
#         "Bioinformatics for UK",
#         "Biotechnology",
#         "Biotechnology Internship",
#         "Business Analyst",
#         "Business Analyst for Canada",
#         "Business Intelligence Engineer",
#         "Business Intelligence Engineer Internships",
#         "Chemical Engineer",
#         "CLINICAL DATA ANALYST",
#         "Clinical Research Coordinator",
#         "Cloud Engineer",
#         "Cloud Engineer for Ireland",
#         "Computer Science",
#         "Computer Science Internship",
#         "Construction Management",
#         "Credit controller for UK",
#         "CRM Sales",
#         "CRM Specialist",
#         "Cyber security",
#         "Cybersecurity for Ireland",
#         "Cybersecurity for UK",
#         "Data Analyst",
#         "Data Analyst for Canada",
#         "Data Analyst for UK",
#         "Data Analyst Internship for Ireland",
#         "Data Analyst Internships",
#         "Database Administration",
#         "Data Center Technician",
#         "Data Engineer",
#         "Data Engineer (citizen/h4ead)",
#         "Data Engineer for UK",
#         "Data Science for Germany",
#         "Data Scientist",
#         "Design Verification Engineer",
#         "DevOps",
#         "DevOps for India",
#         "DevOps for Ireland",
#         "DevOps for UK",
#         "DevOps Internships",
#         "Dynamics 365",
#         "Electrical Engineer",
#         "Electrical Project",
#         "Electronic Health Records (EHR)",
#         "Embedded Software Engineer",
#         "Environmental Health and Safety (EHS)",
#         "Epic Analyst",
#         "ERP",
#         "Financial analyst",
#         "Financial analyst for Ireland",
#         "Frontend Engineering",
#         "Full Stack",
#         "Game Developer",
#         "Game UI / Interactive UI Designer",
#         "Generative AI",
#         "GRC Analyst",
#         "Healthcare Data Analyst",
#         "Healthcare data analyst, Health care business analyst,HeHalthcare data engineer",
#         "HR Recruiter",
#         "ITSM/ITIL",
#         "Java Developer",
#         "Java Full Stack",
#         "Manufacturing engineer (Mechanical)",
#         "Manufacturing engineer (Mechanical) for Canada",
#         "Marketing Automation Specialist",
#         "Mechanical Engineer",
#         "Medical Affairs",
#         "Medical Coding",
#         "MLOps Engineer",
#         ".Net",
#         ".Net for Ireland",
#         "Netsuite",
#         "Network Engineer",
#         "Network Security Engineer",
#         "Payroll Analyst",
#         "Pharmacovigilance",
#         "Photography",
#         "Product Manager",
#         "Project Coordinator for Canada",
#         "Project Management for Ireland",
#         "Project Management Internship",
#         "Project Manager",
#         "python developer",
#         "QA Automation Engineer",
#         "Quality Analyst",
#         "Quality Analyst for UK",
#         "Quality Assurance Engineer",
#         "Quality Engineer",
#         "Regulatory Affairs",
#         "RTL Design Engineer",
#         "Safety Analyst",
#         "Sailpoint",
#         "Sales executive for UK",
#         "Salesforce Developer",
#         "Salesforce Developer for UK",
#         "SAP",
#         "Sap basis and security",
#         "SAP FICO",
#         "SAP MM",
#         "Scrum Master",
#         "Security Engineer",
#         "ServiceNow Developer",
#         "Software Developer",
#         "Software Engineer",
#         "Software Engineer for Ireland",
#         "Software/Hardware Asset Management Analyst",
#         "Structural Engineer for Canada",
#         "Supply Chain",
#         "Supply Chain (citizen/h4ead)",
#         "Supply Chain for Ireland",
#         "Sustainability analyst for Ireland",
#         "System Infrastructure Engineer",
#         "Tax analyst",
#         "Technical program Management (citizen/h4ead)",
#         "Tosca Test Automation Engineer",
#         "UX Designer",
#         "Workday Analyst"
#     ]

#     location    = os.getenv("LOCATION", "United States")
#     max_workers = int(os.getenv("MAX_WORKERS", "20"))

#     print(f"\n📋 Configuration:")
#     print(f"   📊 Keywords  : {len(keywords)} domains")
#     print(f"   🌎 Location  : {location}")
#     print(f"   ⏰ Time filter: Last 24 hours (ALL pages until empty)")
#     print(f"   🔄 Workers   : {max_workers}")
#     print(f"   📦 Supabase  : {'Enabled' if os.getenv('SUPABASE_URL') else 'Disabled (CSV only)'}")
#     print(f"\n   ℹ️  Pagination stops only when LinkedIn returns an empty page,")
#     print(f"   so every job posted in the last 24 hours will be collected.\n")

#     scraper = LinkedInScraper(use_database=bool(os.getenv('SUPABASE_URL')))
#     start_time = time.time()

#     try:
#         jobs = scraper.scrape_all_jobs_batch(
#             keywords=keywords,
#             location=location,
#             max_workers=max_workers,
#             save_to_db=True,
#         )

#         if jobs:
#             scraper.save_to_csv(jobs)

#         elapsed = time.time() - start_time
#         print("\n" + "=" * 70)
#         print("✅ FINAL SUMMARY")
#         print("=" * 70)
#         print(f"📊 Total jobs scraped : {len(jobs)}")
#         print(f"⏱️  Total time         : {elapsed:.1f}s  ({elapsed/60:.1f} min)")
#         if jobs:
#             print(f"⚡ Average speed      : {len(jobs)/elapsed:.1f} jobs/sec")

#     except KeyboardInterrupt:
#         print("\n\n⚠️ Interrupted by user")
#         if 'jobs' in locals() and jobs:
#             fname = f"linkedin_jobs_interrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#             print(f"💾 Saving {len(jobs)} jobs collected so far → {fname}")
#             scraper.save_to_csv(jobs, fname)

#     except Exception as e:
#         print(f"\n❌ Error: {e}")
#         import traceback
#         traceback.print_exc()


# if __name__ == "__main__":
#     main()




































# #!/usr/bin/env python3
# """Main entry point for LinkedIn scraper with keyword batching"""

# import sys
# import os
# import time
# import requests
# from datetime import datetime
# from dotenv import load_dotenv

# load_dotenv()

# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# from src.linkedin_scraper import LinkedInScraper


# # how many keywords per run
# BATCH_SIZE = 41


# def get_progress():
#     """Get last keyword index from Supabase"""
#     url = os.getenv("SUPABASE_URL") + "/rest/v1/scraper_progress?id=eq.1"
#     headers = {
#         "apikey": os.getenv("SUPABASE_KEY"),
#         "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
#     }

#     r = requests.get(url, headers=headers)

#     if r.status_code == 200 and r.json():
#         return r.json()[0]["last_index"]

#     return 0


# def update_progress(new_index):
#     """Update keyword index in Supabase"""

#     url = os.getenv("SUPABASE_URL") + "/rest/v1/scraper_progress?id=eq.1"

#     headers = {
#         "apikey": os.getenv("SUPABASE_KEY"),
#         "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
#         "Content-Type": "application/json",
#         "Prefer": "return=minimal",
#     }

#     data = {"last_index": new_index}

#     requests.patch(url, headers=headers, json=data)


# def main():

#     print("=" * 70)
#     print("🚀 LINKEDIN SCRAPER - BATCH MODE")
#     print("=" * 70)

#     all_keywords = [
#         "Actimize Developer",
#         "Active Directory",
#         "Agronomy Operations",
#         "AI/ML Engineer",
#         "Anti Money Laundering (AML)",
#         "Atlassian Engineer / Jira",
#         "Big Data Engineer",
#         "Bioinformatics",
#         "Bioinformatics for UK",
#         "Biotechnology",
#         "Biotechnology Internship",
#         "Business Analyst",
#         "Business Analyst for Canada",
#         "Business Intelligence Engineer",
#         "Business Intelligence Engineer Internships",
#         "Chemical Engineer",
#         "CLINICAL DATA ANALYST",
#         "Clinical Research Coordinator",
#         "Cloud Engineer",
#         "Cloud Engineer for Ireland",
#         "Computer Science",
#         "Computer Science Internship",
#         "Construction Management",
#         "Credit controller for UK",
#         "CRM Sales",
#         "CRM Specialist",
#         "Cyber security",
#         "Cybersecurity for Ireland",
#         "Cybersecurity for UK",
#         "Data Analyst",
#         "Data Analyst for Canada",
#         "Data Analyst for UK",
#         "Data Analyst Internship for Ireland",
#         "Data Analyst Internships",
#         "Database Administration",
#         "Data Center Technician",
#         "Data Engineer",
#         "Data Engineer (citizen/h4ead)",
#         "Data Engineer for UK",
#         "Data Science for Germany",
#         "Data Scientist",
#         "Design Verification Engineer",
#         "DevOps",
#         "DevOps for India",
#         "DevOps for Ireland",
#         "DevOps for UK",
#         "DevOps Internships",
#         "Dynamics 365",
#         "Electrical Engineer",
#         "Electrical Project",
#         "Electronic Health Records (EHR)",
#         "Embedded Software Engineer",
#         "Environmental Health and Safety (EHS)",
#         "Epic Analyst",
#         "ERP",
#         "Financial analyst",
#         "Financial analyst for Ireland",
#         "Frontend Engineering",
#         "Full Stack",
#         "Game Developer",
#         "Game UI / Interactive UI Designer",
#         "Generative AI",
#         "GRC Analyst",
#         "Healthcare Data Analyst",
#         "HR Recruiter",
#         "ITSM/ITIL",
#         "Java Developer",
#         "Java Full Stack",
#         "Marketing Automation Specialist",
#         "Mechanical Engineer",
#         "Medical Coding",
#         "MLOps Engineer",
#         ".Net",
#         ".Net for Ireland",
#         "Network Engineer",
#         "Network Security Engineer",
#         "Product Manager",
#         "Project Manager",
#         "python developer",
#         "QA Automation Engineer",
#         "Quality Analyst",
#         "Quality Assurance Engineer",
#         "Regulatory Affairs",
#         "RTL Design Engineer",
#         "Salesforce Developer",
#         "SAP",
#         "SAP FICO",
#         "Scrum Master",
#         "Security Engineer",
#         "ServiceNow Developer",
#         "Software Developer",
#         "Software Engineer",
#         "Supply Chain",
#         "System Infrastructure Engineer",
#         "Technical program Management (citizen/h4ead)",
#         "UX Designer",
#         "Workday Analyst",
#     ]

#     location = os.getenv("LOCATION", "United States")
#     max_workers = int(os.getenv("MAX_WORKERS", "8"))

#     start_index = get_progress()

#     end_index = start_index + BATCH_SIZE

#     keywords = all_keywords[start_index:end_index]

#     print(f"\n📊 Total keywords: {len(all_keywords)}")
#     print(f"▶ Starting from keyword index: {start_index}")
#     print(f"⏹ Ending index: {end_index}")
#     print(f"📦 Processing {len(keywords)} keywords this run\n")

#     scraper = LinkedInScraper(use_database=True)

#     start_time = time.time()

#     jobs = scraper.scrape_all_jobs_batch(
#         keywords=keywords,
#         location=location,
#         max_workers=max_workers,
#         save_to_db=True,
#     )

#     if jobs:
#         scraper.save_to_csv(jobs)

#     new_index = end_index

#     if new_index >= len(all_keywords):
#         new_index = 0

#     update_progress(new_index)

#     elapsed = time.time() - start_time

#     print("\n" + "=" * 70)
#     print("✅ RUN COMPLETE")
#     print("=" * 70)
#     print(f"Jobs scraped: {len(jobs)}")
#     print(f"Next run will start from index: {new_index}")
#     print(f"Total runtime: {elapsed/60:.1f} minutes")


# if __name__ == "__main__":
#     main()






















































# #!/usr/bin/env python3
# """LinkedIn scraper with resume support"""

# import sys
# import os
# import time
# import requests
# from datetime import datetime
# from dotenv import load_dotenv

# load_dotenv()

# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# from src.linkedin_scraper import LinkedInScraper


# # --------------------------------------------------
# # Progress functions (Supabase)
# # --------------------------------------------------

# def get_progress():

#     url = os.getenv("SUPABASE_URL") + "/rest/v1/scraper_progress?id=eq.1"

#     headers = {
#         "apikey": os.getenv("SUPABASE_KEY"),
#         "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
#     }

#     r = requests.get(url, headers=headers)

#     if r.status_code == 200 and r.json():
#         return r.json()[0]["last_index"]

#     return 0


# def update_progress(index):

#     url = os.getenv("SUPABASE_URL") + "/rest/v1/scraper_progress?id=eq.1"

#     headers = {
#         "apikey": os.getenv("SUPABASE_KEY"),
#         "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
#         "Content-Type": "application/json",
#         "Prefer": "return=minimal",
#     }

#     data = {"last_index": index}

#     requests.patch(url, headers=headers, json=data)


# # --------------------------------------------------
# # Main scraper
# # --------------------------------------------------

# def main():

#     print("=" * 70)
#     print("🚀 LINKEDIN SCRAPER WITH AUTO RESUME")
#     print("=" * 70)

#     # all_keywords = [

#     #     "Actimize Developer",
#     #     "Active Directory",
#     #     "Agronomy Operations",
#     #     "AI/ML Engineer",
#     #     "Anti Money Laundering (AML)",
#     #     "Atlassian Engineer / Jira",
#     #     "Big Data Engineer",
#     #     "Bioinformatics",
#     #     "Bioinformatics for UK",
#     #     "Biotechnology",
#     #     "Biotechnology Internship",
#     #     "Business Analyst",
#     #     "Business Analyst for Canada",
#     #     "Business Intelligence Engineer",
#     #     "Business Intelligence Engineer Internships",
#     #     "Chemical Engineer",
#     #     "CLINICAL DATA ANALYST",
#     #     "Clinical Research Coordinator",
#     #     "Cloud Engineer",
#     #     "Cloud Engineer for Ireland",
#     #     "Computer Science",
#     #     "Computer Science Internship",
#     #     "Construction Management",
#     #     "Credit controller for UK",
#     #     "CRM Sales",
#     #     "CRM Specialist",
#     #     "Cyber security",
#     #     "Cybersecurity for Ireland",
#     #     "Cybersecurity for UK",
#     #     "Data Analyst",
#     #     "Data Analyst for Canada",
#     #     "Data Analyst for UK",
#     #     "Data Analyst Internship for Ireland",
#     #     "Data Analyst Internships",
#     #     "Database Administration",
#     #     "Data Center Technician",
#     #     "Data Engineer",
#     #     "Data Engineer (citizen/h4ead)",
#     #     "Data Engineer for UK",
#     #     "Data Science for Germany",
#     #     "Data Scientist",
#     #     "Design Verification Engineer",
#     #     "DevOps",
#     #     "DevOps for India",
#     #     "DevOps for Ireland",
#     #     "DevOps for UK",
#     #     "DevOps Internships",
#     #     "Dynamics 365",
#     #     "Electrical Engineer",
#     #     "Electrical Project",
#     #     "Electronic Health Records (EHR)",
#     #     "Embedded Software Engineer",
#     #     "Environmental Health and Safety (EHS)",
#     #     "Epic Analyst",
#     #     "ERP",
#     #     "Financial analyst",
#     #     "Financial analyst for Ireland",
#     #     "Frontend Engineering",
#     #     "Full Stack",
#     #     "Game Developer",
#     #     "Game UI / Interactive UI Designer",
#     #     "Generative AI",
#     #     "GRC Analyst",
#     #     "Healthcare Data Analyst",
#     #     "HR Recruiter",
#     #     "ITSM/ITIL",
#     #     "Java Developer",
#     #     "Java Full Stack",
#     #     "Manufacturing engineer (Mechanical)",
#     #     "Marketing Automation Specialist",
#     #     "Mechanical Engineer",
#     #     "Medical Coding",
#     #     "MLOps Engineer",
#     #     ".Net",
#     #     ".Net for Ireland",
#     #     "Network Engineer",
#     #     "Network Security Engineer",
#     #     "Product Manager",
#     #     "Project Manager",
#     #     "python developer",
#     #     "QA Automation Engineer",
#     #     "Quality Analyst",
#     #     "Quality Assurance Engineer",
#     #     "Regulatory Affairs",
#     #     "RTL Design Engineer",
#     #     "Salesforce Developer",
#     #     "SAP",
#     #     "SAP FICO",
#     #     "Scrum Master",
#     #     "Security Engineer",
#     #     "ServiceNow Developer",
#     #     "Software Developer",
#     #     "Software Engineer",
#     #     "Supply Chain",
#     #     "System Infrastructure Engineer",
#     #     "Technical program Management (citizen/h4ead)",
#     #     "UX Designer",
#     #     "Workday Analyst"

#     # ]






#     all_keywords = [
# "GRC Analyst",
# "Healthcare Data Analyst",
# "Healthcare data analyst, Health care business analyst,HeHalthcare data engineer",
# "HR Recruiter",
# "ITSM/ITIL",
# "Java Developer",
# "Java Full Stack",
# "Manufacturing engineer (Mechanical)",
# "Manufacturing engineer (Mechanical) for Canada",
# "Marketing Automation Specialist",
# "Mechanical Engineer",
# "Medical Affairs",
# "Medical Coding",
# "MLOps Engineer",
# ".Net",
# ".Net for Ireland",
# "Netsuite",
# "Network Engineer",
# "Network Security Engineer",
# "Payroll Analyst",
# "Pharmacovigilance",
# "Photography",
# "Product Manager",
# "Project Coordinator for Canada",
# "Project Management for Ireland",
# "Project Management Internship",
# "Project Manager",
# "python developer",
# "QA Automation Engineer",
# "Quality Analyst",
# "Quality Analyst for UK",
# "Quality Assurance Engineer",
# "Quality Engineer",
# "Regulatory Affairs",
# "RTL Design Engineer",
# "Safety Analyst",
# "Sailpoint",
# "Sales executive for UK",
# "Salesforce Developer",
# "Salesforce Developer for UK",
# "SAP",
# "Sap basis and security",
# "SAP FICO",
# "SAP MM",
# "Scrum Master",
# "Security Engineer",
# "ServiceNow Developer",
# "Software Developer",
# "Software Engineer",
# "Software Engineer for Ireland",
# "Software/Hardware Asset Management Analyst",
# "Structural Engineer for Canada",
# "Supply Chain",
# "Supply Chain (citizen/h4ead)",
# "Supply Chain for Ireland",
# "Sustainability analyst for Ireland",
# "System Infrastructure Engineer",
# "Tax analyst",
# "Technical program Management (citizen/h4ead)",
# "Tosca Test Automation Engineer",
# "UX Designer",
# "Workday Analyst"
# ]
#     location = os.getenv("LOCATION", "United States")
#     max_workers = int(os.getenv("MAX_WORKERS", "5"))

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

import sys
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.linkedin_scraper import LinkedInScraper


def main():

    print("=" * 70)
    print("🚀 LINKEDIN SCRAPER - REPO B")
    print("=" * 70)

    keywords = [

        "GRC Analyst",
        "Healthcare Data Analyst",
        "Healthcare data analyst, Health care business analyst,HeHalthcare data engineer",
        "HR Recruiter",
        "ITSM/ITIL",
        "Java Developer",
        "Java Full Stack",
        "Manufacturing engineer (Mechanical)",
        "Manufacturing engineer (Mechanical) for Canada",
        "Marketing Automation Specialist",
        "Mechanical Engineer",
        "Medical Affairs",
        "Medical Coding",
        "MLOps Engineer",
        ".Net",
        ".Net for Ireland",
        "Netsuite",
        "Network Engineer",
        "Network Security Engineer",
        "Payroll Analyst",
        "Pharmacovigilance",
        "Photography",
        "Product Manager",
        "Project Coordinator for Canada",
        "Project Management for Ireland",
        "Project Management Internship",
        "Project Manager",
        "python developer",
        "QA Automation Engineer",
        "Quality Analyst",
        "Quality Analyst for UK",
        "Quality Assurance Engineer",
        "Quality Engineer",
        "Regulatory Affairs",
        "RTL Design Engineer",
        "Safety Analyst",
        "Sailpoint",
        "Sales executive for UK",
        "Salesforce Developer",
        "Salesforce Developer for UK",
        "SAP",
        "Sap basis and security",
        "SAP FICO",
        "SAP MM",
        "Scrum Master",
        "Security Engineer",
        "ServiceNow Developer",
        "Software Developer",
        "Software Engineer",
        "Software Engineer for Ireland",
        "Software/Hardware Asset Management Analyst",
        "Structural Engineer for Canada",
        "Supply Chain",
        "Supply Chain (citizen/h4ead)",
        "Supply Chain for Ireland",
        "Sustainability analyst for Ireland",
        "System Infrastructure Engineer",
        "Tax analyst",
        "Technical program Management (citizen/h4ead)",
        "Tosca Test Automation Engineer",
        "UX Designer",
        "Workday Analyst"
    ]

    location = os.getenv("LOCATION", "United States")
    max_workers = 6

    scraper = LinkedInScraper(use_database=True)

    start_time = time.time()

    jobs = scraper.scrape_all_jobs_batch(
        keywords=keywords,
        location=location,
        max_workers=max_workers,
        save_to_db=True
    )

    if jobs:
        scraper.save_to_csv(jobs)

    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print("✅ REPO B SCRAPE COMPLETE")
    print("=" * 70)
    print(f"Jobs scraped: {len(jobs)}")
    print(f"Runtime: {elapsed/60:.1f} minutes")


if __name__ == "__main__":
    main()