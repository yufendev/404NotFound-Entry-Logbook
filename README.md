# 404NotFound Entry Logbook // PENS Community Edition

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Android-blue.svg?style=flat-square)]()
[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat-square&logo=python&logoColor=white)]()
[![Framework](https://img.shields.io/badge/GUI-PyQt5-41CD52.svg?style=flat-square&logo=qt&logoColor=white)]()
[![Release](https://img.shields.io/badge/Release-v2.4.0--community-e11d48.svg?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-gray.svg?style=flat-square)]()

Desktop automation client for student daily internship (*Kerja Praktek / Magang*) logbook submissions on the **Politeknik Elektronika Negeri Surabaya (PENS)** Online MIS portal (`https://online.mis.pens.ac.id`).

Engineered by **Mohammad Putra Maulana Yufen** (MEKATRONIKA '23).

---

## Background & Problem Statement

Filling daily internship monitoring forms on the PENS Online MIS portal often involves:
1. **Frequent Session Expirations:** The EEPIS Apereo CAS authentication layer enforces aggressive timeouts, requiring students to manually authenticate multiple times daily.
2. **Repetitive Daily Entry:** Inputting repetitive hours, dates, and identical technical tasks every weekday is tedious and prone to missed deadlines.
3. **Silent WAF Rejections:** The backend portal implements an overzealous SQL keyword filter that silently discards submissions containing common technical words like `SELECT`, `INSERT`, `UPDATE`, or `DELETE`.
4. **Lack of Automated Work Hour Variation:** Submitting static identical hours (e.g. exactly 08:00 to 16:00 every day) appears unnatural and risks administrative scrutiny.

**404NotFound Entry Logbook** solves all of these challenges in a portable, single-executable desktop suite.

---

## Key Features

### 1. Reverse-Engineered CAS Authentication
* Implements direct HTTP session handshakes with the Apereo Central Authentication Service (`login.pens.ac.id`).
* Dynamically extracts one-time login tokens (`lt`) and session execution flows (`_eventId=submit`).
* Safely maintains session cookies across background worker threads without credential leakage.

### 2. Zero-Config Student Profile Scraping
* Automatically crawls student metadata directly upon login:
  * Full Student Name & NRP
  * Internship Location / Company (*Tempat KP*)
  * Academic Year & Active Semester
  * Internal database identifiers (`kp_daftar` & `mahasiswa`)
  * Starting date of internship and active week calculation (Weeks 1 to 24).
* Completely multi-user ready: any PENS student can log in with their own NetID credentials.

### 3. Smart Work Hours Randomizer
* **Start Time:** Randomized realistically between **08:00** and **10:00** (e.g., 08:15, 08:30, 09:20).
* **End Time:** Randomized realistically between **14:00** and **16:00** (e.g., 14:30, 15:15, 16:00).
* **Weekend Awareness:** Intelligent calendar engine automatically detects and excludes Saturdays and Sundays during batch execution.

### 4. 10-Slot Modular Preset Engine
* Persistent pool of 10 customizable activity descriptions stored locally in JSON format.
* Includes one-click domain presets tailored to PENS curricula:
  * **Hardware / IoT / Mekatronika:** Instrumentation, wiring diagrams, telemetry, sensor calibration.
  * **Software / Web / Mobile / IT:** Repository maintenance, API endpoints, UI/UX, debugging, sprint review.
  * **Umum Teknik / Telekomunikasi:** SOP compliance, network transmission, RF monitoring, cabling.
* Execution modes:
  * **Single-Day Submission:** One-click instant submit for the current date.
  * **Batch Range Submission:** Automated sequential or randomized multi-day submission across date intervals with polite request pacing.

### 5. Automated WAF SQL-Sanitization
* Automatically detects and sanitizes problematic keywords (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) into formal Indonesian technical terms, guaranteeing zero silent drops by the PENS server.
* Enforces standard administrative guidelines: Automatically locks course curriculum relevance (*"Sesuai Matakuliah"*) to **"Tidak"** (code `2`).

### 6. Live Portal Bidirectional Synchronization
* Integrated monitoring tab communicating directly with `entry_logbook_kp1.php`.
* Pulls live historical records across all 24 weeks with status verification.

---

## Tech Stack & Architecture

```
404NotFound_Entry_Logbook/
├── pens_logbook_app.py     # Main application codebase (PyQt5 GUI + Worker Threads)
├── config_logbook.json     # Local persistent configuration & custom user presets
├── app_icon.ico            # High-resolution multi-scale application icon
├── logo_login.png          # Cropped authentic 404 Project branding (Login view)
├── logo_header.png         # Cropped authentic 404 Project branding (Dashboard view)
└── dist/
    └── 404NotFound_Entry_Logbook.exe  # Standalone frozen executable (43 MB)
```

* **GUI Framework:** PyQt5 (Qt 5.15) utilizing an ultra-clean White / Light SaaS design language with Electric Neon Pink (`#e11d48`) brand accents.
* **HTTP Client:** Python `requests.Session` with custom User-Agent headers, connection pooling, and SSL verification.
* **Concurrency:** Dedicated `QThread` (Worker-Signal-Slot pattern) ensuring zero GUI freezing during network I/O.
* **Packaging:** PyInstaller 6.x single-file bundle with frozen binary assets.

---

## Installation & Usage

### Option A: Portable Standalone Executable (Recommended)
No Python installation or dependencies required.
1. Download **`404NotFound_Entry_Logbook.exe`** from the [Releases](https://github.com/yufendev/404NotFound-Entry-Logbook/releases) page.
2. Double-click the executable to launch.
3. Enter your EEPIS NetID (e.g. `user@me.student.pens.ac.id`) and Password.
4. Select your date, roll random hours, pick an activity preset, and click **TEMBAK KE MIS PENS**.

### Option B: Running from Source

```bash
# Clone the repository
git clone https://github.com/yufendev/404NotFound-Entry-Logbook.git
cd 404NotFound-Entry-Logbook

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required dependencies
pip install requests PyQt5 Pillow

# Run the application
python pens_logbook_app.py
```

### Compiling to Binary (.exe)

To compile your own standalone single-file binary with embedded assets:

```bash
pyinstaller --onefile --noconsole \
  --name "404NotFound_Entry_Logbook" \
  --icon "app_icon.ico" \
  --add-data "logo_header.png;." \
  --add-data "logo_login.png;." \
  --add-data "app_icon.ico;." \
  --clean pens_logbook_app.py
```

The output will be generated under the `dist/` directory.

---

## Security & Privacy Guarantee

* **100% Client-Side:** No middleman servers, cloud databases, or third-party webhooks are utilized.
* **Direct Encrypted Transport:** All communication occurs strictly between your local machine and official PENS servers (`https://login.pens.ac.id` and `https://online.mis.pens.ac.id`) over TLS/HTTPS.
* **Credential Safety:** If enabled, credentials are saved solely on your local storage in `config_logbook.json`.

---

## Developer & Credits

* **Developer:** Mohammad Putra Maulana Yufen
* **Department:** MEKATRONIKA 2023 - Politeknik Elektronika Negeri Surabaya
* **Instagram:** [@yufenxyz](https://instagram.com/yufenxyz)
* **GitHub:** [@yufendev](https://github.com/yufendev)

---

## License

This project is licensed under the MIT License. Developed for academic utility and workflow optimization among PENS engineering students.
