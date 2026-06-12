import random
import threading
import math
import logging
import traceback
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# CONFIGURATION
LINK = 'https://docs.google.com/forms/d/1SsQ_ta2Fmiu0lt0WNxDZoef-2_KeH4cMFOeQ4KoHgVg/preview'
RESPONSE_COUNT = 3 # Jumlah total responden yang diinginkan
THREADS_MAX = 3    # Jumlah browser yang berjalan simultan

# REALISTIC INDONESIAN DATA (Expanded)
FIRST_NAMES_MALE = [
    "Ahmad", "Budi", "Rizky", "Aditya", "Hendra", "Fajar", "Bambang", "Agus", "Taufik", "Guntur",
    "Dimas", "Reza", "Zulham", "Aris", "Muhammad", "Bayu", "Wahyu", "Eko", "Andi", "Dedi",
    "Fauzi", "Ihsan", "Pratama", "Setiawan", "Hidayat", "Saputra", "Nugroho", "Ramadhan", "Wijaya",
    "Alfian", "Munandar", "Segara", "Hermawan", "Prasetyo", "Santoso"
]

FIRST_NAMES_FEMALE = [
    "Siti", "Dewi", "Putri", "Lani", "Maya", "Anisa", "Ratna", "Dian", "Rina", "Indah",
    "Siska", "Novianti", "Linda", "Mega", "Yulia", "Nurul", "Fitriani", "Sri", "Lestari", "Aminah",
    "Nuraini", "Rahmawati", "Marlina", "Permata", "Amelia", "Wahyuni", "Utami", "Fitri", "Hidayah",
    "Handayani", "Safitri", "Sari", "Kusuma", "Aulia"
]

LAST_NAMES = [
    "Saputra", "Pratama", "Hidayat", "Setiawan", "Kusuma", "Wijaya", "Santoso", "Nugroho", "Wahyuni",
    "Lestari", "Sari", "Utami", "Hidayah", "Ramadhan", "Alfian", "Munandar", "Syah", "Putri",
    "Prasetyo", "Hermawan", "Gunawan", "Subagyo", "Wicaksono", "Purnomo", "Sutrisno", "Budiman",
    "Hartono", "Susanto", "Mulyono", "Sudirman"
]

CITIES = [
    "Salatiga", "Semarang", "Boyolali", "Solo", "Magelang", "Ambarawa", "Ungaran",
    "Kendal", "Demak", "Grobogan", "Sragen", "Karanganyar", "Klaten", "Sukoharjo",
    "Purwodadi", "Temanggung", "Wonosobo", "Jepara", "Kudus", "Pati", "Rembang", "Blora"
]

PROGRAMS = [
    "Tarbiyah - Pendidikan Agama Islam", "Tarbiyah - Pendidikan Bahasa Arab", "Tarbiyah - Pendidikan Guru MI",
    "Dakwah - Komunikasi Penyiaran Islam", "Dakwah - Manajemen Dakwah", "Dakwah - Bimbingan Konseling Islam",
    "Syariah - Hukum Keluarga Islam", "Syariah - Hukum Ekonomi Syariah", "Syariah - Hukum Tata Negara",
    "FEBI - Perbankan Syariah", "FEBI - Ekonomi Syariah", "FEBI - Akuntansi Syariah",
    "FUAD - Psikologi Islam", "FUAD - Ilmu Al-Qur'an dan Tafsir"
]

# KONSEP QUANTUM UNCERTAINTY (Probabilitas Jawaban)
LIKERT_WEIGHTS = [2, 8, 25, 40, 25] # Persentase: [STS, TS, N, S, SS]

# Track used names to ensure uniqueness
used_names = set()
names_lock = threading.Lock()
count = 0
count_lock = threading.Lock()

firefox_options = FirefoxOptions()
firefox_options.add_argument("--headless")
firefox_options.add_argument("--incognito")

def get_weighted_choice():
    return random.choices([0, 1, 2, 3, 4], weights=LIKERT_WEIGHTS)[0]

def generate_unique_name():
    global used_names
    with names_lock:
        for _ in range(1000): # Attempt to find a unique name
            is_female = random.choice([True, False])
            first = random.choice(FIRST_NAMES_FEMALE if is_female else FIRST_NAMES_MALE)
            last = random.choice(LAST_NAMES)
            full_name = f"{first} {last}"
            
            if full_name not in used_names:
                used_names.add(full_name)
                return full_name, is_female
        
        fallback_name = f"Responden {random.randint(1000, 9999)}"
        return fallback_name, random.choice([True, False])

def fillForm():
    global count
    driver = None
    resp_id = 0
    try:
        # Generate Unique Identity
        full_name, is_female = generate_unique_name()
        age = str(random.randint(18, 23))
        city = random.choice(CITIES)
        program = random.choice(PROGRAMS)
        gender_idx = 1 if is_female else 0
        
        driver = webdriver.Firefox(options=firefox_options)
        driver.set_page_load_timeout(45)
        
        with count_lock:
            count += 1
            resp_id = count
        
        logger.info(f"Resp {resp_id} - Memulai sesi: {full_name} ({city})")
        driver.get(LINK)
        
        current_page = 1
        while current_page <= 6:
            time.sleep(random.uniform(2, 4))
            
            items = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"], .Qr7Oae, .geS5v')
            
            if items:
                logger.info(f"Resp {resp_id} - Mengisi Halaman {current_page} ({len(items)} pertanyaan)")
                for item in items:
                    text = item.text.upper()
                    inputs = item.find_elements(By.CSS_SELECTOR, 'input[type="text"], textarea')
                    choices = item.find_elements(By.CSS_SELECTOR, '[role="radio"]')
                    
                    if inputs:
                        val = ""
                        if "NAMA" in text: val = full_name
                        elif "USIA" in text: val = age
                        elif "FAKULTAS" in text: val = program
                        elif "KOTA" in text: val = city
                        
                        if val:
                            inputs[0].clear()
                            inputs[0].send_keys(val)
                            time.sleep(random.uniform(0.5, 1.2))
                    
                    elif choices:
                        label = text.split('\n')[0]
                        target_idx = -1
                        
                        if "JENIS KELAMIN" in label:
                            target_idx = gender_idx
                        elif "SEMESTER" in label:
                            target_idx = random.choices([0,1,2,3,4,5], weights=[5, 25, 40, 20, 5, 5])[0]
                            if target_idx >= len(choices): target_idx = len(choices) - 1
                        elif "JARAK TEMPUH" in label:
                            target_idx = random.randint(0, len(choices)-1)
                        elif "UANG SAKU" in label:
                            target_idx = random.randint(0, len(choices)-1)
                        elif "STATUS" in label:
                            target_idx = random.choices([0, 1], weights=[80, 20])[0]
                            if target_idx >= len(choices): target_idx = len(choices) - 1
                        elif "LAMA MENYANTRI" in label:
                            target_idx = random.randint(0, len(choices)-1)
                        else:
                            target_idx = get_weighted_choice()
                        
                        if target_idx != -1 and target_idx < len(choices):
                            driver.execute_script("arguments[0].click();", choices[target_idx])
                            time.sleep(random.uniform(0.3, 0.8))

            buttons = driver.find_elements(By.CSS_SELECTOR, 'div[role="button"]')
            next_btn = None
            submit_btn = None
            for b in buttons:
                b_text = b.text.lower()
                if "berikutnya" in b_text or "next" in b_text: next_btn = b
                elif "kirim" in b_text or "submit" in b_text: submit_btn = b
            
            if submit_btn:
                if not next_btn:
                    driver.execute_script("arguments[0].click();", submit_btn)
                    logger.info(f"Resp {resp_id} - FORM BERHASIL DISUBMIT!")
                    break
                else:
                    driver.execute_script("arguments[0].click();", next_btn)
                    current_page += 1
            elif next_btn:
                driver.execute_script("arguments[0].click();", next_btn)
                logger.info(f"Resp {resp_id} - Lanjut ke halaman berikutnya...")
                current_page += 1
            else:
                break
                
    except Exception as e:
        logger.error(f"Resp {resp_id} - Error: {e}")
    finally:
        if driver:
            driver.quit()

def run():
    logger.info(f"--- MEMULAI BOT QUANTUM RESPONDEN ({RESPONSE_COUNT} RESPONDEN) ---")
    threads = []
    for _ in range(RESPONSE_COUNT):
        while threading.active_count() > THREADS_MAX:
            time.sleep(1)
        t = threading.Thread(target=fillForm)
        t.start()
        threads.append(t)
        time.sleep(random.uniform(3, 7))

    for t in threads:
        t.join()
    logger.info("--- SEMUA RESPONDEN SELESAI ---")

if __name__ == "__main__":
    run()
