import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def scrape_hood_transcript_custom():
    url = "https://discountingcashflows.com/company/HOOD/transcripts/"
    
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print(f"Fetching {url}...")
        import pdb; pdb.set_trace()
        driver.get(url)
        
        # Wait specifically for the speech bubble content class "p-4" to load
        # This ensures the dynamic content (HTMX) has finished rendering
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "p-4")))
        
        # Add a small buffer to ensure all blocks render
        time.sleep(3) 
        
        # Get the fully rendered HTML
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        
        print("Page loaded. Parsing transcript blocks...\n")
        
        # Based on your HTML: Each speech block is in a div with class "flex flex-col my-5"
        # We look for all such divs
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
                formatted_transcript.append(f"**{speaker_name}:**\n{text_content}\n")
        
        # Combine into a single string
        full_text = "\n".join(formatted_transcript)
        
        if not full_text:
            print("No transcript text found. The selector might still be slightly off or login is required.")
        else:
            # Preview content
            print("--- Transcript Preview ---")
            print(full_text[:500] + "...\n")
            
            # Save to file
            filename = "hood_transcript_2025_q3_cleaned.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(full_text)
            print(f"Successfully saved full transcript to '{filename}'")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_hood_transcript_custom()