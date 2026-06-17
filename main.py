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
LINK = 'masukan linknya disini'
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

def find_matching_choice_index(choices, target_value):
    if target_value is None or str(target_value).strip() == "":
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
                
    # Try substring match if exact match fails
    for idx, choice in enumerate(choices):
        text = choice.text or ""
        val = choice.get_attribute("data-value") or ""
        aria = choice.get_attribute("aria-label") or ""
        
        all_texts = [t.strip().lower() for t in [text, val, aria] if t]
        for t in all_texts:
            if target_str in t or t in target_str:
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
        
    return -1

def get_value_from_row(row, label_or_text):
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

    # Try Likert Scale question index matching: Q1/P1, Q2/P2, ..., Q15/P15
    likert_questions = [
        "Saya berusaha semaksimal mungkin untuk mencapai hasil maksimal dalam kegiatan pesantren",
        "Saya merasa bertanggung jawab sebagai santri",
        "Lingkungan dan teman di pesantren membuat saya lebih semangat dalam kegiatan",
        "Saya ingin meningkatkan kemampuan diri selama di pesantren",
        "Ibu Nyai memberikan arahan dan teladan yang baik dalam prilaku sehari-hari",
        "Ibu Nyai sering mengingatkan pentingnya tujuan belajar dan beribadah di pesantren",
        "Ibu Nyai mendorong santri untuk berpikir dan memahami pelajaran secara mendalam",
        "Ibu Nyai memberikan nasihat atau bimbingan secara pribadi ketika santri mengalami kesulitan",
        "Saya mematuhi peraturan yang berlaku di pesantren",
        "Saya berusaha mengikuti seluruh kegiatan pesantren sesuai jadwal yang ditentukan",
        "Saya menyelesaikan tugas yang diberikan oleh pengurus atau ustadz dengan baik",
        "Saya berusaha melaksanakan ibadah wajib secara konsisten",
        "Saya merasakan ketenangan batin ketika menjalankan ibadah",
        "Saya berusaha memahami ajaran agama yang diajarkan di pesantren",
        "Nilai-nilai agama mempengaruhi perilaku saya dalam kehidupan sehari-hari"
    ]
    
    matching_idx = -1
    for i, q in enumerate(likert_questions):
        if q.upper().strip() in norm_label or norm_label in q.upper().strip():
            matching_idx = i + 1
            break
            
    if matching_idx != -1:
        patterns = [
            f"Q{matching_idx}", f"P{matching_idx}", f"Y{matching_idx}", f"X{matching_idx}",
            f"PERTANYAAN {matching_idx}", f"PERTANYAAN_{matching_idx}",
            f"QUESTION {matching_idx}", f"QUESTION_{matching_idx}",
            f"PIR{matching_idx}", f"K{matching_idx}"
        ]
        for col in keys:
            c = str(col).upper().strip()
            if c in patterns:
                return row[col]
            if q.upper().strip() in c or c in q.upper().strip():
                return row[col]
                
    # Fallback to substring matching on all keys
    for col in keys:
        c = str(col).upper().strip()
        if c in norm_label or norm_label in c:
            return row[col]
            
    return None

def choose_mode():
    import os
    # Check command-line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == '--random':
            return 'random', None
        elif os.path.exists(arg):
            return 'file', arg
        else:
            logger.error(f"File '{arg}' tidak ditemukan. Menggunakan mode interaktif.")
            
    print("=" * 60)
    print("               BOT GOOGLE FORM - PILIH MODE")
    print("=" * 60)
    print("1. Mode Random (Mengisi form dengan data acak realistis)")
    print("2. Mode File (Mengisi form dari data CSV / Excel)")
    print("=" * 60)
    
    while True:
        try:
            choice = input("Pilih mode (1/2): ").strip()
            if choice in ('1', '2'):
                break
            print("Pilihan tidak valid. Silakan pilih 1 atau 2.")
        except KeyboardInterrupt:
            print("\nKeluar...")
            sys.exit(0)
            
    if choice == '1':
        return 'random', None
    else:
        while True:
            try:
                file_path = input("Masukkan path file CSV/Excel (misal: data.xlsx atau data.csv): ").strip()
                if not file_path:
                    continue
                if os.path.exists(file_path):
                    return 'file', file_path
                print(f"File '{file_path}' tidak ditemukan. Silakan masukkan path yang benar.")
            except KeyboardInterrupt:
                print("\nKeluar...")
                sys.exit(0)

def load_data(file_path):
    import pandas as pd
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
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
            full_name = str(name_val).strip() if name_val is not None else generate_unique_name()[0]
            
            age_val = get_value_from_row(row_data, "USIA")
            age = str(age_val).strip() if age_val is not None else str(random.randint(18, 23))
            
            city_val = get_value_from_row(row_data, "KOTA")
            city = str(city_val).strip() if city_val is not None else random.choice(CITIES)
            
            program_val = get_value_from_row(row_data, "FAKULTAS")
            program = str(program_val).strip() if program_val is not None else random.choice(PROGRAMS)
            
            gender_val = get_value_from_row(row_data, "JENIS KELAMIN")
            if gender_val is not None:
                g_str = str(gender_val).strip().lower()
                is_female = ("wanita" in g_str or "perempuan" in g_str or g_str.startswith("p") or g_str.startswith("f"))
            else:
                _, is_female = generate_unique_name()
            gender_idx = 1 if is_female else 0
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
                        elif row_data is not None:
                            # Check if the field text splits/labels match any key in row
                            row_val = get_value_from_row(row_data, text.split('\n')[0])
                            if row_val is not None:
                                val = str(row_val).strip()
                        
                        if val:
                            inputs[0].clear()
                            inputs[0].send_keys(val)
                            time.sleep(random.uniform(0.5, 1.2))
                    
                    elif choices:
                        label = text.split('\n')[0]
                        target_idx = -1
                        
                        row_val = get_value_from_row(row_data, label) if row_data is not None else None
                        
                        if row_val is not None:
                            target_idx = find_matching_choice_index(choices, row_val)
                            if target_idx == -1:
                                logger.warning(f"Resp {resp_id} - Pilihan '{row_val}' tidak ditemukan untuk '{label}'. Menggunakan pilihan acak.")
                        
                        if target_idx == -1:
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
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

def run():
    import pandas as pd
    
    # Choose mode and retrieve file path if applicable
    mode, file_path = choose_mode()
    
    rows_data = None
    resp_count = RESPONSE_COUNT
    
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
