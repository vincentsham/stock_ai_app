import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
from datetime import datetime
from database.utils import connect_to_db
import json
from etl.utils import hash_dict, hash_text, get_calendar_year_quarter, filter_complete_years
import numpy as np
from pathlib import Path
import pandas as pd
from database.utils import insert_records

def create_chrome_driver() -> webdriver.Chrome:
    """Create a Chrome driver with fallbacks to avoid macOS chromedriver crashes."""

    chrome_options = Options()
    # Prefer Chrome's modern headless mode where available
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # 1) Prefer Selenium Manager (bundled with Selenium) to avoid webdriver-manager path bugs.
    try:
        return webdriver.Chrome(options=chrome_options)
    except Exception as selenium_manager_error:
        print(f"Selenium Manager failed, falling back to webdriver-manager: {selenium_manager_error}")

    # 2) Fallback: webdriver-manager. Some versions can return a non-executable notices file.
    installed_path = Path(ChromeDriverManager().install())
    candidate_paths: list[Path]

    if installed_path.is_file() and installed_path.name.startswith("chromedriver"):
        candidate_paths = [installed_path]
    else:
        search_root = installed_path.parent if installed_path.is_file() else installed_path
        candidate_paths = sorted(search_root.glob("**/chromedriver*"))

    chromedriver_path = None
    for candidate in candidate_paths:
        name = candidate.name.lower()
        if "third_party" in name or "notice" in name or "notices" in name:
            continue
        if candidate.is_file() and candidate.stat().st_size > 0:
            chromedriver_path = candidate
            break

    if not chromedriver_path:
        raise RuntimeError(
            f"Could not locate chromedriver binary. webdriver-manager returned: {installed_path}"
        )

    service = Service(str(chromedriver_path))
    return webdriver.Chrome(service=service, options=chrome_options)


def get_html_content(driver, url) -> BeautifulSoup:
    print(f"Fetching {url}...")
    driver.get(url)
    
    # Wait specifically for the speech bubble content class "p-4" to load
    # This ensures the dynamic content (HTMX) has finished rendering
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ai-insights-modal-button")))
    
    # Add a small buffer to ensure all blocks render
    time.sleep(np.random.uniform(0.5, 5.0)) 
    
    # Get the fully rendered HTML
    html_content = driver.page_source

    return BeautifulSoup(html_content, "html.parser")

def extract_latest_fyfq(soup: BeautifulSoup) -> tuple:
    """
    Extracts the latest Fiscal Year and Quarter directly from the HTML structure.
    Target: div#transcriptList -> ul -> first h2 (FY) and first a (Quarter)
    """
    transcript_list_div = soup.find("div", id="transcriptList")
    
    if transcript_list_div:
        # 1. Get the Fiscal Year from the first <h2> inside the list
        # Structure: <li> <h2 class="menu-title">FY 2025</h2> </li>
        fy_header = transcript_list_div.find("h2", class_="menu-title")
        fiscal_year = "Unknown"
        if fy_header:
            # Text is "FY 2025", we split to get "2025"
            fiscal_year_text = fy_header.get_text(strip=True)
            if "FY" in fiscal_year_text:
                fiscal_year = fiscal_year_text.replace("FY", "").strip()

        # 2. Get the Quarter from the first <a> tag following the header
        # The HTML shows the quarters are listed immediately after the FY header
        # Structure: <li> <a ...> Q3 <small>... </small> </a> </li>
        # We just find the first <a> tag in this container, as the list is ordered descending
        latest_q_link = transcript_list_div.find("a", class_="list-group-item")
        fiscal_quarter = "Unknown"
        if latest_q_link:
            # The text inside <a> is likely "Q3\nNov 05". 
            # We want the part before the <small> tag.
            # get_text() will return "Q3Nov 05", so we might need to parse children or just split.
            # A safer way using BS4 is to get the text node directly or strip the small tag.
            
            # Remove the <small> tag temporarily to get clean "Q3"
            if latest_q_link.find("small"):
                latest_q_link.find("small").decompose()
            
            quarter_text = latest_q_link.get_text(strip=True)
            if "Q" in quarter_text:
                fiscal_quarter = quarter_text.replace("Q", "").strip()
        total_quarters = transcript_list_div.find_all("a", class_="list-group-item")

        return int(fiscal_year), int(fiscal_quarter), len(total_quarters)
    return None, None, 0

def extract_earnings_date(soup: BeautifulSoup):
    container = soup.find("ul", id="transcriptsContent")
    if not container:
        return None
    header_card = container.find("div", class_="flex flex-wrap justify-between bg-base-200 rounded-box p-4")
    if header_card:
        date_spans = header_card.find_all("span", class_="text-xs")
        for span in date_spans:
            date_pattern = r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\b"
            match = re.search(date_pattern, span.get_text())
            if match:
                # Convert the date to yyyy-mm-dd format
                date_str = match.group()
                parsed_date = datetime.strptime(date_str, "%B %d, %Y")
                return parsed_date.strftime("%Y-%m-%d")
    return None
    



def extract_earnings_transcript(soup: BeautifulSoup) -> str:
    # Based on your HTML: Each speech block is in a div with class "flex flex-col my-5"
    # We look for all such divs
    container = soup.find("ul", id="transcriptsContent")
    if not container:
        return ""
    speech_blocks = soup.find_all("div", class_="flex flex-col my-5")
    
    formatted_transcript = []
    
    for block in speech_blocks:
        # 1. Extract Speaker Name
        # Structure: <div class="text-primary ..."> ... <span>Name</span> </div>
        speaker_div = block.find("div", class_="text-primary")
        speaker_name = "Unknown Speaker"
        if speaker_div:
            # Usually the name is in the span
            span = speaker_div.find("span")
            if span:
                speaker_name = span.get_text(strip=True)
            else:
                speaker_name = speaker_div.get_text(strip=True)
        
        # 2. Extract Text
        # Structure: <div class="p-4"> ... text ... </div>
        text_div = block.find("div", class_="p-4")
        if text_div:
            text_content = text_div.get_text(strip=True)
            
            # Append to our list
            formatted_transcript.append(f"{speaker_name}: {text_content}")
    
    # Combine into a single string
    full_text = "\n".join(formatted_transcript)
    
    if not full_text:
        return ""
    else:
        return full_text
    



def extract_all_earnings_transcripts(tic: str, num_transcripts: int = 4) -> list:
    url = f"https://discountingcashflows.com/company/{tic}/transcripts/"

    # Initialize the driver (with fallbacks to avoid chromedriver crashes)
    driver = create_chrome_driver()
    transcripts = []
    try:
        # List page does not contain transcript text bubbles; wait for transcript list to render.
        soup = get_html_content(driver, url)
        fy, fq, total_quarters = extract_latest_fyfq(soup)

        if fy is None or fq is None:
            raise ValueError(f"Could not extract fiscal year and quarter for {tic} from {url}")

        while len(transcripts) < min(num_transcripts, total_quarters):
            url = f"https://discountingcashflows.com/company/{tic}/transcripts/{fy}/{fq}/"
            soup = get_html_content(driver, url)
            transcript_text = extract_earnings_transcript(soup)
            earnings_date = extract_earnings_date(soup)

            if transcript_text != "":
                transcripts.append({
                    "ticker": tic.upper(),
                    "year": fy,
                    "quarter": f"Q{fq}",
                    "date": earnings_date,
                    "transcript": transcript_text,
                    "url": url,
                    "source": "discountingcashflows"
                })
            fq = fq - 1
            if fq == 0:
                fq = 4
                fy = fy - 1
               
    except Exception as e:
        print(f"Error during scraping: {e} for {tic}")
    finally:
        driver.quit()
        return transcripts 


def main():
    # Example usage
    tic = "AAPL"
    transcripts = extract_all_earnings_transcripts(tic, num_transcripts=2)
    for transcript in transcripts:
        print(f"Symbol: {transcript['symbol']}, Year: {transcript['year']}, Period: {transcript['period']}, Date: {transcript['date']}")
        print(f"Content:\n{transcript['content'][:500]}...")
        print("\n" + "="*80 + "\n")



if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tic FROM core.stock_profiles;")
        tics = cursor.fetchall()
        tics = [tic[0] for tic in tics]
        # tics = [tic[0] if tic[0] not in ['NVDA', 'AAPL', 'TSLA'] else None for tic in tics]
        # tics = ["SOFI"]
        

        for tic in tics:
            if tic is None:
                continue
            total_records = 0
            transcripts = extract_all_earnings_transcripts(tic, num_transcripts=8)
            transcripts_list = []
            for transcript in transcripts:
                earnings_date = transcript.get("date")
                source = transcript.get("source")
                url = transcript.get("url")
                transcripts_list.append({
                    "tic": tic.upper(),
                    "earnings_date": earnings_date,
                    "url": url,
                    "transcript_sha256": hash_text(transcript.get("transcript")),
                    "raw_json": json.dumps(transcript),
                    "raw_json_sha256": hash_dict(transcript),
                    "source": source
                })
            df_transcripts = pd.DataFrame(transcripts_list)
            df_transcripts['earnings_date'] = pd.to_datetime(df_transcripts['earnings_date'])
            df_transcripts = df_transcripts.sort_values(by='earnings_date', ascending=False)
            df_transcripts = filter_complete_years(df_transcripts, tic)
            calendar_year, calendar_quarter = zip(*[get_calendar_year_quarter(date) for date in df_transcripts['earnings_date']])
            df_transcripts.loc[:, 'calendar_year'] = calendar_year
            df_transcripts.loc[:, 'calendar_quarter'] = calendar_quarter

            total_inserted = insert_records(conn, df_transcripts, "raw.earnings_transcripts", ["tic", "calendar_year", "calendar_quarter"], where=["raw_json_sha256"])
            print(f"For {tic}: Total records processed = {total_inserted}")  
        conn.close()
