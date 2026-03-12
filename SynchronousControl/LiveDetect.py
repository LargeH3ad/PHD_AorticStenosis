import time
import mss
import numpy as np
import cv2
import pytesseract
import re
import csv
from datetime import datetime

# ====== CONFIGURATION ======
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

ROI = {
    "top": 500,
    "left": 800,
    "width": 300,
    "height": 400
}

# OCR config: PSM 6 for block of text
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.'

# The order of keys you want in your dictionary
lvot_keys = [
    "LVOT Diam",
    "LVOT Vmax",
    "LVOT Vmean",
    "LVOT PGmean",
    "LVOT PGMax",
    "LVOT VTI",
    "LVOT HR",
    "LVOT SV"
]

# Create a CSV filename with current date and time
current_time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_file = f"US_Data_{current_time_str}.csv"

# Create CSV file and write header
with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["Timestamp"] + lvot_keys)
    writer.writeheader()

print(f"Starting LVOT monitor and logging to CSV: {csv_file}\n")

with mss.mss() as sct:
    while True:
        start_time = time.time()

        # Capture ROI
        screenshot = sct.grab(ROI)
        img = np.array(screenshot)

        # Grayscale + threshold
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # OCR
        text = pytesseract.image_to_string(thresh, config=custom_config)

        # Show ROI
        cv2.imshow("ROI Capture", thresh)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Extract numeric values, ignore lone '.'
        numbers = [num for num in re.findall(r"[0-9.]+", text) if num != '.']

        # Create dictionary
        lvot_dict = {}
        for i, key in enumerate(lvot_keys):
            lvot_dict[key] = numbers[i] if i < len(numbers) else None

        # Add timestamp
        lvot_dict["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Print dictionary
        print(lvot_dict)

        # Append row to CSV
        with open(csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Timestamp"] + lvot_keys)
            writer.writerow(lvot_dict)

        # Maintain sampling rate (~5 Hz)
        elapsed = time.time() - start_time
        sleep_time = max(0, 0.2 - elapsed)
        time.sleep(sleep_time)

cv2.destroyAllWindows()