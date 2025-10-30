"""
linkedin_scraper.py
-------------------

This script demonstrates two things:

1️⃣ LinkedIn Login Automation (demo-only)
    - Uses Selenium & ChromeDriver to show login flow.
    - Does NOT scrape any data from LinkedIn (to remain ToS compliant).

2️⃣ Public Profile Scraper
    - Reads URLs from `profile_urls.txt`
    - Visits public pages (e.g., GitHub, Clutch, Medium, company 'team' pages)
    - Extracts name, title, location, about, experience
    - Saves results to `profiles.csv`

Run:
    python linkedin_scraper.py

Author: Ratish Oberoi
"""

import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
HEADLESS = False
MIN_DELAY = 4
MAX_DELAY = 8
MAX_RETRIES = 3


# ---------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------
def random_delay():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


def create_driver():
    """Create and return a Chrome WebDriver with random headers."""
    ua = UserAgent()
    user_agent = ua.random
    chrome_options = Options()
    if HEADLESS:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument("--window-size=1200,900")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def safe_get(driver, url):
    """Safely open a URL with retries."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            driver.get(url)
            random_delay()
            return driver.page_source
        except Exception as e:
            print(f"Attempt {attempt} failed for {url}: {e}")
            time.sleep(2 * attempt)
    return None


# ---------------------------------------------------------------------
# PART 1 - LINKEDIN LOGIN DEMONSTRATION
# ---------------------------------------------------------------------
def demo_linkedin_login():
    """
    Demonstration-only: Automate login flow safely.
    This does NOT scrape or store any LinkedIn data.
    """
    print("\n--- LinkedIn Login Demonstration (Safe) ---")
    driver = create_driver()
    try:
        driver.get("https://www.linkedin.com/login")
        time.sleep(3)

        print("Filling login form (demo account)...")
        email = driver.find_element(By.ID, "username")
        password = driver.find_element(By.ID, "password")

        # Demo credentials (replace with dummy test account)
        email.send_keys("your_test_email@example.com")
        password.send_keys("your_test_password")

        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print("Login attempted. Waiting 5 seconds...")
        time.sleep(5)

        print("Login flow demonstrated successfully.")
        print("NOTE: No data scraped. This is demonstration only.")
    except Exception as e:
        print("Login demo error:", e)
    finally:
        driver.quit()


# ---------------------------------------------------------------------
# PART 2 - PUBLIC PROFILE SCRAPER
# ---------------------------------------------------------------------
def parse_generic_profile(html, url=None):
    def parse_generic_profile(html, url=None):
        """Improved parser for GitHub-style public profiles."""
    soup = BeautifulSoup(html, "html.parser")

    data = {
        "url": url,
        "name": None,
        "title": None,
        "location": None,
        "about": None,
        "experiences": None,
    }

    # 🧩 1. Name (display name)
    full_name_tag = soup.find("span", attrs={"itemprop": "name"})
    if full_name_tag:
        data["name"] = full_name_tag.get_text(strip=True)

    # 🧩 2. Username / handle
    user_tag = soup.find("span", attrs={"itemprop": "additionalName"})
    if user_tag:
        data["title"] = user_tag.get_text(strip=True)

    # 🧩 3. Bio / about
    bio_tag = soup.find("div", class_="p-note")
    if bio_tag:
        data["about"] = bio_tag.get_text(strip=True)

    # 🧩 4. Location
    loc_tag = soup.find("li", attrs={"itemprop": "homeLocation"})
    if loc_tag:
        data["location"] = loc_tag.get_text(strip=True)

    # 🧩 5. Stats (followers, following, repos)
    stats = []
    for stat in soup.select("a.UnderlineNav-item .Counter"):
        txt = stat.get_text(strip=True)
        if txt:
            stats.append(txt + " items")
    # Followers / following info
    follow_section = soup.find("div", class_="flex-order-1")
    if follow_section:
        follow_text = " ".join(follow_section.get_text(" ", strip=True).split())
        stats.append(follow_text)
    if stats:
        data["experiences"] = " | ".join(stats)

    return data



def scrape_public_profiles():
    """Scrape data from public profile URLs listed in profile_urls.txt."""
    print("\n--- Public Profile Scraper ---")
    driver = create_driver()
    profiles = []
    try:
        with open("profile_urls.txt", "r", encoding="utf-8") as f:
            links = [l.strip() for l in f if l.strip()]
        print(f"Loaded {len(links)} URLs from profile_urls.txt\n")

        for link in tqdm(links, desc="Profiles"):
            print("Visiting:", link)
            html = safe_get(driver, link)
            if not html:
                profiles.append({"url": link})
                continue
            data = parse_generic_profile(html, link)
            profiles.append(data)
            random_delay()

        df = pd.DataFrame(profiles)
        df.to_csv("profiles.csv", index=False)
        print("\n✅ Saved extracted data to profiles.csv\n")
    except Exception as e:
        print("Scraper error:", e)
    finally:
        driver.quit()


# ---------------------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("========= AeroLeads Assignment: LinkedIn Scraper =========\n")
    print("This script has two safe demo parts:")
    print("  1. LinkedIn login demonstration (no data scraped)")
    print("  2. Public profile scraper (ethical & functional)\n")

    choice = input("Enter 1 to run LinkedIn login demo, or 2 to run public scraper: ")

    if choice.strip() == "1":
        demo_linkedin_login()
    elif choice.strip() == "2":
        scrape_public_profiles()
    else:
        print("Invalid choice. Please run again and choose 1 or 2.")
