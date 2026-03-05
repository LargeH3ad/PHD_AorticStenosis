import time
import mss
import numpy as np
import cv2
import pytesseract
import re
import sqlite3
from datetime import datetime

# ====== CONFIGURATION ======
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

ROI = {
    "top": 500,
    "left": 800,
    "width": 300,
    "height": 400
}

custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.'

lvot_keys = [
    "LVOT_Diam",
    "LVOT_Vmax",
    "LVOT_Vmean",
    "LVOT_PGmean",
    "LVOT_PGmax",
    "LVOT_VTI",
    "LVOT_HR",
    "LVOT_SV"
]

# ====== DATABASE ======

current_time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# db_file = f"US_Data_{current_time_str}.db"
db_file = "LiveData.db"

conn = sqlite3.connect(r"C:\Users\pat\OneDrive - UNSW\ValveNN\PressureUltrasoundData.db")
cursor = conn.cursor()

# ====== MAIN LOOP ======

with mss.mss() as sct:
    while True:
        start_time = time.time()
        Timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        screenshot = sct.grab(ROI)
        img = np.array(screenshot)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        text = pytesseract.image_to_string(thresh, config=custom_config)

        cv2.imshow("ROI Capture", thresh)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        numbers = [num for num in re.findall(r"[0-9.]+", text) if num != '.']

        lvot_dict = {}
        for i, key in enumerate(lvot_keys):
            lvot_dict[key] = int(float(numbers[i])) if i < len(numbers) else None

        print(lvot_dict)

        # Insert row (P1,P2,P3 left NULL)
        cursor.execute("""
            INSERT INTO LiveData (
                Timestamp,
                P1, P2, P3,
                LVOT_Diam, LVOT_Vmax, LVOT_Vmean,
                LVOT_PGmean, LVOT_PGmax,
                LVOT_VTI, LVOT_HR, LVOT_SV
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            Timestamp,
            None, None, None,
            lvot_dict.get("LVOT_Diam"),
            lvot_dict.get("LVOT_Vmax"),
            lvot_dict.get("LVOT_Vmean"),
            lvot_dict.get("LVOT_PGmean"),
            lvot_dict.get("LVOT_PGmax"),
            lvot_dict.get("LVOT_VTI"),
            lvot_dict.get("LVOT_HR"),
            lvot_dict.get("LVOT_SV")
        ))

        conn.commit()

        elapsed = time.time() - start_time
        sleep_time = max(0, 0.2 - elapsed)
        time.sleep(sleep_time)

cv2.destroyAllWindows()
conn.close()