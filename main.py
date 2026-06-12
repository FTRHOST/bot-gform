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
LINK = 'https://docs.google.com/forms/d/e/1FAIpQLSecQJHZWuwk6ogbXeSypBVhJ5uZIZuAMS-kt7hdAldNYd-xDA/viewform?usp=dialog'
RESPONSE_COUNT = 30 # Jumlah total responden yang diinginkan
THREADS_MAX = 3    # Jumlah browser yang berjalan simultan (jangan terlalu banyak agar tidak berat)

# REALISTIC INDONESIAN DATA
NAMES = [
    "Ahmad Fauzi", "Siti Aminah", "Budi Santoso", "Dewi Lestari", "Rizky Ramadhan",
    "Putri Handayani", "Aditya Wijaya", "Lani Nuraini", "Hendra Saputra", "Maya Sari",
    "Fajar Nugroho", "Anisa Rahmawati", "Bambang Hermawan", "Ratna Dwi", "Eko Prasetyo",
    "Dian Safitri", "Agus Setiawan", "Rina Marlina", "Taufik Hidayat", "Indah Permata",
    "Guntur Pratama", "Siska Amelia", "Dimas Anggara", "Novianti Putri", "Reza Alfian",
    "Linda Wahyuni", "Zulham Syah", "Mega Utami", "Aris Munandar", "Yulia Fitri",
    "Muhammad Ihsan", "Nurul Hidayah", "Bayu Segara", "Fitriani Handayani", "Wahyu Hidayat"
]

CITIES = [
    "Salatiga", "Semarang", "Boyolali", "Solo", "Magelang", "Ambarawa", "Ungaran",
    "Kendal", "Demak", "Grobogan", "Sragen", "Karanganyar", "Klaten", "Sukoharjo",
    "Purwodadi", "Temanggung", "Wonosobo"
]

PROGRAMS = [
    "Tarbiyah - Pendidikan Agama Islam", "Tarbiyah - Pendidikan Bahasa Arab", "Tarbiyah - Pendidikan Guru MI",
    "Dakwah - Komunikasi Penyiaran Islam", "Dakwah - Manajemen Dakwah", "Dakwah - Bimbingan Konseling Islam",
    "Syariah - Hukum Keluarga Islam", "Syariah - Hukum Ekonomi Syariah", "Syariah - Hukum Tata Negara",
    "FEBI - Perbankan Syariah", "FEBI - Ekonomi Syariah", "FEBI - Akuntansi Syariah",
    "FUAD - Psikologi Islam", "FUAD - Ilmu Al-Qur'an dan Tafsir"
]

# KONSEP QUANTUM UNCERTAINTY (Probabilitas Jawaban)
# Menggunakan distribusi bobot agar hasil tidak flat/palsu.
# Mayoritas di 3, 4, 5 (Netral, Setuju, Sangat Setuju), tapi ada 'noise' di 1-2.
LIKERT_WEIGHTS = [2, 8, 25, 40, 25] # Persentase: [STS, TS, N, S, SS]

count = 0
count_lock = threading.Lock()

firefox_options = FirefoxOptions()
firefox_options.add_argument("--headless")
firefox_options.add_argument("--incognito")

def get_weighted_choice():
    # Mengembalikan index 0-4 berdasarkan bobot quantum
    return random.choices([0, 1, 2, 3, 4], weights=LIKERT_WEIGHTS)[0]

def fillForm():
    global count
    driver = None
    try:
        # Generate Identity
        full_name = random.choice(NAMES)
        age = str(random.randint(18, 23))
        city = random.choice(CITIES)
        program = random.choice(PROGRAMS)
        gender_idx = 1 if any(x in full_name.upper() for x in ["SITI", "PUTRI", "MAYA", "ANI", "RINA", "LINDA"]) else 0
        
        driver = webdriver.Firefox(options=firefox_options)
        driver.set_page_load_timeout(45)
        
        with count_lock:
            resp_id = count + 1
            count += 1
        
        logger.info(f"Resp {resp_id} - Memulai sesi: {full_name} ({city})")
        driver.get(LINK)
        
        current_page = 1
        while current_page <= 6: # Antisipasi multi-page
            time.sleep(random.uniform(2, 4)) # Jeda manusiawi
            
            # Cari semua pertanyaan di halaman ini
            items = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"], .Qr7Oae, .geS5v')
            
            if items:
                logger.info(f"Resp {resp_id} - Mengisi Halaman {current_page} ({len(items)} pertanyaan)")
                for item in items:
                    text = item.text.upper()
                    inputs = item.find_elements(By.CSS_SELECTOR, 'input[type="text"], textarea')
                    choices = item.find_elements(By.CSS_SELECTOR, '[role="radio"]')
                    
                    # 1. INPUT TEXT (Bagian Identitas)
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
                    
                    # 2. PILIHAN GANDA
                    elif choices:
                        label = text.split('\n')[0]
                        target_idx = -1
                        
                        # Mapping Identitas Pilihan Ganda
                        if "JENIS KELAMIN" in label:
                            target_idx = gender_idx
                        elif "SEMESTER" in label:
                            target_idx = random.choices([0,1,2,3,4], weights=[10, 30, 40, 15, 5])[0]
                        elif "JARAK TEMPUH" in label:
                            target_idx = random.randint(0, len(choices)-1)
                        elif "UANG SAKU" in label:
                            target_idx = random.randint(0, len(choices)-1)
                        elif "STATUS" in label:
                            target_idx = random.choices([0, 1], weights=[80, 20])[0] # 80% santri biasa
                        elif "LAMA MENYANTRI" in label:
                            target_idx = random.randint(0, len(choices)-1)
                        else:
                            # KUANTUM UNCERTAINTY untuk Kuesioner (Likert 1-5)
                            target_idx = get_weighted_choice()
                        
                        if target_idx != -1 and target_idx < len(choices):
                            driver.execute_script("arguments[0].click();", choices[target_idx])
                            time.sleep(random.uniform(0.3, 0.8))

            # CARI TOMBOL NAVIGASI
            buttons = driver.find_elements(By.CSS_SELECTOR, 'div[role="button"]')
            next_btn = None
            submit_btn = None
            for b in buttons:
                b_text = b.text.lower()
                if "berikutnya" in b_text or "next" in b_text: next_btn = b
                elif "kirim" in b_text or "submit" in b_text: submit_btn = b
            
            if submit_btn:
                # Jangan klik submit jika masih ada tombol 'Berikutnya' (Double check)
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
        time.sleep(random.uniform(3, 7)) # Staggering start

    for t in threads:
        t.join()
    logger.info("--- SEMUA RESPONDEN SELESAI ---")

if __name__ == "__main__":
    run()
