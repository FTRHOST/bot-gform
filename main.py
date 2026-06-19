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
LINK = 'https://docs.google.com/forms/d/e/1FAIpQLScs4MvtoMoI2o5xflzU-UbBWogzr0uEksAmWBeFuBlf9pcYPA/viewform?usp=publish-editor'
RESPONSE_COUNT = 1 # Jumlah total responden yang diinginkan
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

def is_empty_value(val):
    if val is None:
        return True
    import math
    try:
        if isinstance(val, float) and math.isnan(val):
            return True
    except:
        pass
    val_str = str(val).strip()
    if val_str == "" or val_str.lower() == "nan":
        return True
    return False

def is_question_required(item):
    try:
        # Check if the question text or any label inside the item contains a red asterisk '*'
        text = (item.text or "").strip()
        if '*' in text:
            return True
            
        # Check if any input/textarea element has the 'required' or 'aria-required="true"' attribute
        inputs = item.find_elements(By.CSS_SELECTOR, 'input, textarea, [role="radiogroup"], [role="list"]')
        for inp in inputs:
            if inp.get_attribute("aria-required") == "true" or inp.get_attribute("required") is not None:
                return True
    except:
        pass
    return False

def find_matching_choice_index(choices, target_value):
    import difflib
    
    if is_empty_value(target_value):
        return -1
    target_str = str(target_value).strip().lower()
    
    # Try exact match first on choice text / attributes
    for idx, choice in enumerate(choices):
        text = choice.text or ""
        val = choice.get_attribute("data-value") or ""
        aria = choice.get_attribute("aria-label") or ""
        
        all_texts = [t.strip().lower() for t in [text, val, aria] if t]
        for t in all_texts:
            if target_str == t:
                return idx
                
    # Try numeric representation for Likert scales or general index
    try:
        num_val = int(float(target_value))
        # Likert options map: 1 -> STS, 2 -> TS, 3 -> N, 4 -> S, 5 -> SS
        if len(choices) == 5 and 1 <= num_val <= 5:
            return num_val - 1
            
        if 0 <= num_val < len(choices):
            return num_val
    except ValueError:
        pass
        
    # Try fuzzy matching using difflib for string similarity (handles typos like 'sanngat setuj')
    best_idx = -1
    highest_ratio = 0.0
    for idx, choice in enumerate(choices):
        text = choice.text or ""
        val = choice.get_attribute("data-value") or ""
        aria = choice.get_attribute("aria-label") or ""
        
        all_texts = [t.strip().lower() for t in [text, val, aria] if t]
        for t in all_texts:
            ratio = difflib.SequenceMatcher(None, target_str, t).ratio()
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_idx = idx
                
    # Use fuzzy match if similarity is high enough (threshold 0.6)
    if highest_ratio > 0.6:
        return best_idx
        
    return -1

def get_value_from_row(row, label_or_text, likert_idx=None):
    if row is None:
        return None
    # Normalize label_or_text
    norm_label = label_or_text.upper().strip()
    
    # Get all column keys
    keys = row.index if hasattr(row, 'index') else list(row.keys())
    
    # Try direct key match
    for col in keys:
        norm_col = str(col).upper().strip()
        if norm_col == norm_label:
            return row[col]
            
    # Try fuzzy matches for identity questions
    if "NAMA" in norm_label:
        for col in keys:
            c = str(col).upper()
            if "NAMA" in c or c == "NAME":
                return row[col]
    if "USIA" in norm_label or "UMUR" in norm_label:
        for col in keys:
            c = str(col).upper()
            if "USIA" in c or "UMUR" in c or "AGE" in c:
                return row[col]
    if "KELAMIN" in norm_label or "GENDER" in norm_label:
        for col in keys:
            c = str(col).upper()
            if "KELAMIN" in c or "GENDER" in c or "SEX" in c:
                return row[col]
    if "FAKULTAS" in norm_label or "PROGRAM STUDI" in norm_label or "PRODI" in norm_label:
        for col in keys:
            c = str(col).upper()
            if "FAKULTAS" in c or "PRODI" in c or "STUDI" in c or "JURUSAN" in c or "PROGRAM" in c:
                return row[col]
    if "SEMESTER" in norm_label:
        for col in keys:
            c = str(col).upper()
            if "SEMESTER" in c:
                return row[col]
    if "KOTA" in norm_label or "KABUPATEN" in norm_label:
        for col in keys:
            c = str(col).upper()
            if "KOTA" in c or "KABUPATEN" in c or "ASAL" in c:
                return row[col]
    if "JARAK" in norm_label:
        for col in keys:
            c = str(col).upper()
            if "JARAK" in c:
                return row[col]
    if "UANG SAKU" in norm_label:
        for col in keys:
            c = str(col).upper()
            if "UANG" in c or "SAKU" in c:
                return row[col]
    if "STATUS" in norm_label:
        for col in keys:
            c = str(col).upper()
            if "STATUS" in c:
                return row[col]
    if "LAMA MENYANTRI" in norm_label:
        for col in keys:
            c = str(col).upper()
            if "LAMA" in c or "MENYANTRI" in c:
                return row[col]

    # Try mapping using likert_idx if provided (e.g. Q1, Q2, ..., Q31 or Q01, Q02, ...)
    if likert_idx is not None:
        patterns = [
            f"Q{likert_idx}", f"P{likert_idx}", f"Y{likert_idx}", f"X{likert_idx}",
            f"Q{likert_idx:02d}", f"P{likert_idx:02d}", f"Y{likert_idx:02d}", f"X{likert_idx:02d}",
            f"PERTANYAAN {likert_idx}", f"PERTANYAAN_{likert_idx}",
            f"QUESTION {likert_idx}", f"QUESTION_{likert_idx}",
            f"K{likert_idx}", f"K{likert_idx:02d}"
        ]
        for col in keys:
            c = str(col).upper().strip()
            if c in patterns:
                return row[col]
                
    # Fallback to substring matching on all keys
    for col in keys:
        c = str(col).upper().strip()
        if c in norm_label or norm_label in c:
            return row[col]
            
    return None

def choose_mode():
    import os
    global LINK
    
    # 1. Determine Google Form Link
    # Check if a URL argument was passed in command line
    cli_url = None
    for arg in sys.argv[1:]:
        if arg.startswith(('http://', 'https://')) and "viewform" in arg:
            cli_url = arg
            break
            
    if cli_url:
        LINK = cli_url
        logger.info(f"Menggunakan Link Google Form dari CLI: {LINK}")
    else:
        print("=" * 60)
        print("                KONFIGURASI LINK GOOGLE FORM")
        print("=" * 60)
        while True:
            try:
                link_input = input("Masukkan Link Google Form Anda: ").strip()
                if link_input.startswith(('http://', 'https://')):
                    LINK = link_input
                    break
                print("Link tidak valid! Harus dimulai dengan http:// atau https://")
            except KeyboardInterrupt:
                print("\nKeluar...")
                sys.exit(0)
                
    # 2. Choose Mode
    # Check command-line arguments for mode
    cli_mode = None
    file_path = None
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg == '--random':
                cli_mode = 'random'
            elif arg == '--fetch-template':
                cli_mode = 'fetch_template'
            elif os.path.exists(arg) and arg != sys.argv[0]:
                cli_mode = 'file'
                file_path = arg
                
    if cli_mode:
        if cli_mode == 'random':
            resp_count = RESPONSE_COUNT
            print(f"Menggunakan Mode Random dari CLI. Jumlah responden default: {resp_count}")
            return 'random', None, resp_count
        elif cli_mode == 'fetch_template':
            return 'fetch_template', None, 1
        else:
            return 'file', file_path, None
            
    print("=" * 60)
    print("               BOT GOOGLE FORM - PILIH MODE")
    print("=" * 60)
    print("1. Mode Random (Mengisi form dengan data acak realistis)")
    print("2. Mode File Lokal (Mengisi form dari data CSV / Excel Lokal)")
    print("3. Mode Scan Template (Membuat template CSV otomatis dari Google Form)")
    print("=" * 60)
    
    while True:
        try:
            choice = input("Pilih mode (1/2/3): ").strip()
            if choice in ('1', '2', '3'):
                break
            print("Pilihan tidak valid. Silakan pilih 1, 2, atau 3.")
        except KeyboardInterrupt:
            print("\nKeluar...")
            sys.exit(0)
            
    if choice == '1':
        while True:
            try:
                count_input = input("Masukkan jumlah responden yang diinginkan (angka): ").strip()
                if count_input.isdigit() and int(count_input) > 0:
                    resp_count = int(count_input)
                    break
                print("Masukkan jumlah yang valid (angka bulat positif).")
            except KeyboardInterrupt:
                print("\nKeluar...")
                sys.exit(0)
        return 'random', None, resp_count
    elif choice == '2':
        while True:
            try:
                f_path = input("Masukkan path file CSV/Excel lokal (misal: data.xlsx atau data.csv): ").strip()
                if not f_path:
                    continue
                if os.path.exists(f_path):
                    return 'file', f_path, None
                print(f"File '{f_path}' tidak ditemukan. Silakan masukkan path yang benar.")
            except KeyboardInterrupt:
                print("\nKeluar...")
                sys.exit(0)
    else:
        return 'fetch_template', None, None

def load_data(file_path):
    import pandas as pd
    try:
        if file_path.endswith('.csv'):
            # Try comma first
            df = pd.read_csv(file_path)
            # If it only has 1 column, it might be separated by semicolon or tab (Indonesian Excel standard)
            if df.shape[1] <= 1:
                df_sep = pd.read_csv(file_path, sep=';')
                if df_sep.shape[1] > df.shape[1]:
                    df = df_sep
            return df
        elif file_path.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file_path)
        else:
            raise ValueError("Format file tidak didukung. Harus .csv atau .xlsx / .xls")
    except Exception as e:
        logger.error(f"Error membaca file {file_path}: {e}")
        sys.exit(1)

def fillForm(row_data=None):
    global count
    driver = None
    resp_id = 0
    try:
        # Generate or Extract Identity
        if row_data is not None:
            # Mode CSV/Excel
            name_val = get_value_from_row(row_data, "NAMA")
            full_name = str(name_val).strip() if not is_empty_value(name_val) else "Responden Tanpa Nama"
            
            age_val = get_value_from_row(row_data, "USIA")
            age = str(age_val).strip() if not is_empty_value(age_val) else None
            
            city_val = get_value_from_row(row_data, "KOTA")
            city = str(city_val).strip() if not is_empty_value(city_val) else None
            
            program_val = get_value_from_row(row_data, "FAKULTAS")
            program = str(program_val).strip() if not is_empty_value(program_val) else None
            
            gender_val = get_value_from_row(row_data, "JENIS KELAMIN")
            if not is_empty_value(gender_val):
                g_str = str(gender_val).strip().lower()
                is_female = ("wanita" in g_str or "perempuan" in g_str or g_str.startswith("p") or g_str.startswith("f"))
                gender_idx = 1 if is_female else 0
            else:
                gender_idx = None
        else:
            # Mode Random
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
        
        logger.info(f"Resp {resp_id} - Memulai sesi: {full_name} ({city or 'Tanpa Kota'})")
        driver.get(LINK)
        
        current_page = 1
        likert_counter = 0
        while current_page <= 6:
            time.sleep(random.uniform(2, 4))
            
            items = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"], .Qr7Oae, .geS5v')
            
            if items:
                logger.info(f"Resp {resp_id} - Mengisi Halaman {current_page} ({len(items)} pertanyaan)")
                for item in items:
                    text = item.text.upper()
                    inputs = item.find_elements(By.CSS_SELECTOR, 'input[type="text"], textarea')
                    choices = item.find_elements(By.CSS_SELECTOR, '[role="radio"]')
                    label = text.split('\n')[0]
                    
                    is_required = is_question_required(item)
                    
                    if inputs:
                        val = ""
                        source = "Acak"
                        if "NAMA" in text:
                            val = full_name if full_name != "Responden Tanpa Nama" else ""
                            source = "CSV" if row_data is not None else "Acak"
                        elif "USIA" in text:
                            val = age or ""
                            source = "CSV" if row_data is not None else "Acak"
                        elif "FAKULTAS" in text:
                            val = program or ""
                            source = "CSV" if row_data is not None else "Acak"
                        elif "KOTA" in text:
                            val = city or ""
                            source = "CSV" if row_data is not None else "Acak"
                        elif row_data is not None:
                            row_val = get_value_from_row(row_data, label)
                            if not is_empty_value(row_val):
                                val = str(row_val).strip()
                            source = "CSV"
                        
                        if not val:
                            if is_required:
                                raise ValueError(f"Pertanyaan wajib '{label}' kosong di file CSV/Excel!")
                            else:
                                logger.info(f"Resp {resp_id} - Melewati pertanyaan opsional '{label}' karena kosong di CSV/Excel.")
                                continue
                        
                        inputs[0].clear()
                        inputs[0].send_keys(val)
                        logger.info(f"Resp {resp_id} - Mengisi teks '{label}' = '{val}' ({source})")
                        time.sleep(random.uniform(0.5, 1.2))
                    
                    elif choices:
                        target_idx = -1
                        source = "Acak"
                        
                        is_identity = False
                        for id_keyword in ["JENIS KELAMIN", "SEMESTER", "JARAK TEMPUH", "UANG SAKU", "STATUS", "LAMA MENYANTRI"]:
                            if id_keyword in label:
                                is_identity = True
                                break
                        
                        if not is_identity:
                            likert_counter += 1
                            row_val = get_value_from_row(row_data, label, likert_idx=likert_counter) if row_data is not None else None
                        else:
                            row_val = get_value_from_row(row_data, label) if row_data is not None else None
                        
                        if row_data is not None:
                            # Strict validation for CSV/Excel mode
                            if is_empty_value(row_val):
                                if is_required:
                                    raise ValueError(f"Data untuk pertanyaan pilihan wajib '{label}' kosong atau tidak ditemukan di CSV/Excel!")
                                else:
                                    logger.info(f"Resp {resp_id} - Melewati pertanyaan pilihan opsional '{label}' karena kosong di CSV/Excel.")
                                    continue
                            
                            target_idx = find_matching_choice_index(choices, row_val)
                            if target_idx == -1:
                                available_options = [c.get_attribute("data-value") or c.text for c in choices]
                                raise ValueError(f"Nilai '{row_val}' untuk pertanyaan '{label}' tidak cocok dengan opsi apa pun di form! Pilihan tersedia: {available_options}")
                            source = "CSV"
                        else:
                            # Mode Random (original logic)
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
                                if target_idx >= len(choices): target_idx = len(choices) - 1
                        
                        if target_idx != -1 and target_idx < len(choices):
                            chosen_option = choices[target_idx].get_attribute("data-value") or choices[target_idx].text or str(target_idx)
                            logger.info(f"Resp {resp_id} - Memilih '{label}' = '{chosen_option}' ({source})")
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
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

def fetch_template_form():
    logger.info("--- MEMULAI PROSES SCAN GOOGLE FORM UNTUK MEMBUAT TEMPLATE CSV ---")
    driver = None
    headers = []
    
    try:
        driver = webdriver.Firefox(options=firefox_options)
        driver.set_page_load_timeout(45)
        
        logger.info(f"Membuka Google Form: {LINK}")
        driver.get(LINK)
        
        current_page = 1
        while current_page <= 10:
            time.sleep(random.uniform(2, 4))
            
            # Find all questions on the page
            items = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"], .Qr7Oae, .geS5v')
            
            if items:
                logger.info(f"Scan Halaman {current_page} ({len(items)} pertanyaan ditemukan)")
                for item in items:
                    text = item.text
                    # Extract the question label (first line of text)
                    label = text.split('\n')[0].strip()
                    if label and label not in headers:
                        # Clean up label if it contains required mark (*)
                        clean_label = label.replace(" *", "").strip()
                        headers.append(clean_label)
                        logger.info(f"  [+] Menemukan Pertanyaan: {clean_label}")
                    
                    # Fill the question with random/temporary data to proceed to next page
                    inputs = item.find_elements(By.CSS_SELECTOR, 'input[type="text"], textarea')
                    choices = item.find_elements(By.CSS_SELECTOR, '[role="radio"]')
                    
                    if inputs:
                        val = "Test Data"
                        text_upper = text.upper()
                        if "NAMA" in text_upper: val = "Nama Responden"
                        elif "USIA" in text_upper: val = "20"
                        elif "FAKULTAS" in text_upper: val = "Fakultas Dakwah"
                        elif "KOTA" in text_upper: val = "Salatiga"
                        
                        inputs[0].clear()
                        inputs[0].send_keys(val)
                    
                    elif choices:
                        # Click the first choice to proceed
                        driver.execute_script("arguments[0].click();", choices[0])
            
            # Find buttons
            buttons = driver.find_elements(By.CSS_SELECTOR, 'div[role="button"]')
            next_btn = None
            submit_btn = None
            for b in buttons:
                b_text = b.text.lower()
                if "berikutnya" in b_text or "next" in b_text: next_btn = b
                elif "kirim" in b_text or "submit" in b_text: submit_btn = b
            
            if submit_btn:
                # We reached the last page! Do NOT click submit!
                logger.info("Mencapai halaman akhir (tombol Kirim/Submit ditemukan). Scan selesai!")
                break
            elif next_btn:
                # Click Next to go to next page
                driver.execute_script("arguments[0].click();", next_btn)
                logger.info(f"Lanjut ke halaman berikutnya...")
                current_page += 1
            else:
                break
                
        # Write headers to CSV
        if headers:
            import pandas as pd
            # Create a DataFrame with these headers
            df = pd.DataFrame(columns=headers)
            # Add one empty row (filled with None)
            df.loc[0] = [None] * len(headers)
            
            file_name = "template_kuesioner.csv"
            df.to_csv(file_name, index=False)
            
            logger.info("=" * 60)
            logger.info(f"SUKSES: Template CSV berhasil dibuat!")
            logger.info(f"File disimpan di: {file_name}")
            logger.info(f"Total Kolom: {len(headers)}")
            logger.info("=" * 60)
        else:
            logger.error("Gagal mendeteksi pertanyaan di Google Form.")
            
    except Exception as e:
        logger.error(f"Error saat scan form: {e}")
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

def run():
    import pandas as pd
    
    # Choose mode and retrieve file path if applicable
    mode, file_path, resp_count = choose_mode()
    
    if mode == 'fetch_template':
        fetch_template_form()
        return
        
    rows_data = None
    
    if mode == 'file':
        df = load_data(file_path)
        # Convert NaN values to None so they are easier to handle
        df = df.where(pd.notnull(df), None)
        rows_data = [row for _, row in df.iterrows()]
        resp_count = len(rows_data)
        logger.info(f"--- MEMULAI BOT DENGAN DATA FILE ({resp_count} RESPONDEN DARI FILE) ---")
    else:
        logger.info(f"--- MEMULAI BOT QUANTUM RESPONDEN ({resp_count} RESPONDEN SECARA RANDOM) ---")
        
    threads = []
    for i in range(resp_count):
        while threading.active_count() > THREADS_MAX:
            time.sleep(1)
        
        row_data = rows_data[i] if mode == 'file' else None
        t = threading.Thread(target=fillForm, args=(row_data,))
        t.start()
        threads.append(t)
        time.sleep(random.uniform(3, 7))

    for t in threads:
        t.join()
    logger.info("--- SEMUA RESPONDEN SELESAI ---")

if __name__ == "__main__":
    run()
