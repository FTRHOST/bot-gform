import random
import threading
import math
import logging
import traceback
from flask import Flask, request, render_template
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import json
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

count = 106
count_lock = threading.Lock() # Added lock for thread safety
ml = False
tf = False
val = 1
firefox_options = FirefoxOptions()
firefox_options.add_argument("--disable-extensions")
firefox_options.add_argument("--incognito")
firefox_options.add_argument("--headless") 
firefox_options.add_argument("--start-maximized")

app = Flask(__name__)
total = 250 # Increased to accommodate count starting at 106
percents = [(34.9, 55.6, 4.5, 5), (22.2, 9.5, 12.7, 6, 7.9, 14.3, 25.4, 2), (73, 11.1, 15.9), (76.2, 15.9, 7.9),
            (11.1, 17.5, 71.4), (12.7, 42.9, 6, 20.6, 5, 9.5, 3.3), (69.8, 23.8, 3, 3.4), (42.9, 46, 11.1),
            (11.1, 14.3, 74.6), (90.5, 9.5), (92.1, 7.9), (4, 41.3, 49.2, 5.5), (71.4, 4.8, 23.8), (45, 35, 20),
            (52.4, 47.6), (76.2, 6.4, 9.5, 7.9), (15.9, 76.2, 7.9), (33.3, 50.8, 15.9), (14.3, 57.1, 17.5, 11.1),
            (74.6, 14.3, 11.1)]
persons = {}
response = 10
link = 'https://docs.google.com/forms/d/e/1FAIpQLSfIwKNe3Kw042nSHJr_mu-f6PXQLudiUX2EETBnIHUjsYGodQ/viewform?usp=dialog'


def fillForm(link_):
    global tf
    global count
    global val
    global ml
    driver = None
    try:
        logger.info("Starting browser instance...")
        driver = webdriver.Firefox(options=firefox_options)
        driver.set_page_load_timeout(30)
        
        if not ml:
            val = 1
            
        for m in range(val):
            with count_lock:
                temp = count
                count += 1
            
            logger.info(f"Respondent {temp}: Navigating to form")
            driver.get(link_)
            
            current_question_global_idx = 0
            max_pages = 5
            for page_num in range(max_pages):
                time.sleep(1)
                # Check if we are on a page with questions or identity
                wait = WebDriverWait(driver, 10)
                
                # Check if there is a "Berikutnya" (Next) or "Submit" (Kirim) button
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, 'div[role="button"]')
                    next_btn = None
                    submit_btn = None
                    for b in buttons:
                        btn_text = b.text.lower()
                        if "berikutnya" in btn_text or "next" in btn_text:
                            next_btn = b
                        elif "kirim" in btn_text or "submit" in btn_text:
                            submit_btn = b
                    
                    # Find all items that could be questions or headers
                    items = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"], .Qr7Oae, .geS5v')
                    logger.info(f"Page {page_num + 1}: Found {len(items)} items")

                    if not items and next_btn:
                        logger.info("No items found, clicking Next/Berikutnya (likely landing page)")
                        driver.execute_script("arguments[0].click();", next_btn)
                        continue

                    for item in items:
                        # Skip if it's just a header (no radio/text)
                        inputs = item.find_elements(By.CSS_SELECTOR, 'input[type="text"], textarea')
                        choices = item.find_elements(By.CSS_SELECTOR, '[role="radio"], [role="checkbox"], [jscontroller="EcW08c"]')
                        
                        if inputs:
                            # Identity page usually
                            label = item.text.upper()
                            val_to_fill = "Bot User"
                            if "NAMA" in label:
                                val_to_fill = random.choice(["Andi", "Budi", "Cici", "Dedi", "Eka"]) + f" {temp}"
                            elif "KELAS" in label:
                                val_to_fill = random.choice(["X-A", "XI-B", "XII-C"])
                            elif "NO HP" in label or "TELEPON" in label:
                                val_to_fill = "08" + "".join([str(random.randint(0,9)) for _ in range(10)])
                            
                            inputs[0].send_keys(val_to_fill)
                            logger.info(f"Filled text field: {val_to_fill}")
                        
                        elif choices:
                            # Question page
                            try:
                                if f'{temp}' in persons and current_question_global_idx < len(persons[f'{temp}']):
                                    num = persons[f'{temp}'][current_question_global_idx]
                                    if num < len(choices):
                                        driver.execute_script("arguments[0].click();", choices[num])
                                        logger.info(f"Q{current_question_global_idx+1}: Clicked option {num}")
                                    current_question_global_idx += 1
                                else:
                                    # Just pick a random one if no data
                                    rand_choice = random.randint(0, len(choices)-1)
                                    driver.execute_script("arguments[0].click();", choices[rand_choice])
                                    current_question_global_idx += 1
                            except Exception as e:
                                logger.error(f"Error clicking choice: {e}")

                    if submit_btn:
                        driver.execute_script("arguments[0].click();", submit_btn)
                        logger.info(f"Respondent {temp}: Form submitted!")
                        break
                    elif next_btn:
                        driver.execute_script("arguments[0].click();", next_btn)
                        logger.info(f"Moving to next page...")
                    else:
                        logger.warning("No Next or Submit button found. Breaking loop.")
                        break
                
                except Exception as e:
                    logger.error(f"Error processing page {page_num + 1}: {e}")
                    break

            time.sleep(2)
            
        tf = True
        ml = False
        val = 1
    except Exception as e:
        logger.error(f"Fatal error in fillForm: {e}")
        logger.error(traceback.format_exc())
    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")


def multiRun(key1, key2):
    global tf
    global ml
    global val
    tf = False
    count_to_run = int(key2)
    if count_to_run > 4:
        ml = True
        val = math.ceil(count_to_run / 4)
        count_to_run = 4
    
    threads = []
    for i in range(count_to_run):
        t = threading.Thread(target=fillForm, args=(key1,))
        t.start()
        threads.append(t)
        time.sleep(1) # Small delay between starting threads
    
    return threads


def formFill(key1, key2):
    try:
        threads = multiRun(key1, key2)
        # Wait for all threads to finish instead of busy wait
        for t in threads:
            t.join()
        logger.info(f"All {key2} form fills attempted.")
    except Exception as e:
        logger.error(f"Error in formFill: {e}")


for n in range(total):
    persons[f"{n + 1}"] = []

mno = 1
for question in percents:
    for option in question:
        respondent_count = (math.floor(option * 1.5))
        for ko in range(respondent_count):
            if f'{mno}' in persons:
                persons['{}'.format(mno)].append(question.index(option))
            mno += 1
    mno = 1

if __name__ == "__main__":
    logger.info("Starting Google Forms Bot")
    formFill(link, response)
