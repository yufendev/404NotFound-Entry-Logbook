#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PENS COMPANION // BY 404WORKSHOP
Aplikasi Otomatisasi Logbook KP & SPPA/PA + Portal Akademik Mahasiswa PENS
Theme: Modern White / Clean Light SaaS x Pink Neon Accent (Zero Emoticons)
Created by: Mohammad Putra Maulana Yufen (MEKATRONIKA 23) | IG: @yufenxyz | 404Workshop
"""

import sys
import os
import re
import json
import random
import time
import threading
from datetime import datetime, timedelta, date

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
    QDateEdit, QSpinBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QSplitter, QProgressBar, QMessageBox,
    QFrame, QScrollArea, QStackedWidget, QSizePolicy, QFileDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDate, QUrl, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QDesktopServices

import requests

def resource_path(relative_path):
    """Mendapatkan path file absolut, kompatibel dengan PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_config_paths():
    """Mengembalikan daftar path config untuk prioritas load dan multi-save permanen."""
    paths = []
    # 1. Folder EXE lokal / script
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        paths.append(os.path.join(exe_dir, "config_logbook.json"))
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        paths.append(os.path.join(script_dir, "config_logbook.json"))

    # 2. Folder AppData permanen agar kredensial survive meski EXE dipindah/diupdate
    appdata = os.environ.get('LOCALAPPDATA') or os.environ.get('APPDATA')
    if appdata:
        fixed_dir = os.path.join(appdata, "404NotFound_Logbook")
        paths.append(os.path.join(fixed_dir, "config_logbook.json"))

    # 3. Folder project default jika ada
    proj_dir = "C:/DATA/404NOTFOUND/01_LOGBOOK_PENS"
    if os.path.exists(proj_dir):
        paths.append(os.path.join(proj_dir, "config_logbook.json"))

    return paths

CONFIG_FILE = get_config_paths()[0]

# Preset Template untuk Mahasiswa PENS
PRESET_TEMPLATES = {
    "Hardware / IoT / Mekatronika": [
        "Mempelajari dan melakukan telaah dokumen spesifikasi teknis sistem instrumentasi dan hardware di lokasi magang.",
        "Melakukan analisis integrasi sensor dan modul komunikasi data untuk pemantauan parameter operasional sistem.",
        "Mempelajari skema instalasi kelistrikan, diagram proteksi daya, serta perancangan jalur wiring kendali.",
        "Melakukan riset dan komparasi komponen modul mikrokontroler serta transmisi telemetri nirkabel.",
        "Melakukan perancangan awal diagram pengkabelan (wiring diagram) dan tata letak sensor pada unit kerja.",
        "Melakukan pengujian fungsional modul akuisisi data sensor serta kalibrasi pembacaan parameter analog.",
        "Melakukan simulasi komunikasi serial antar perangkat pengontrol dengan modul periferal utama.",
        "Melakukan troubleshooting dan optimasi protokol transmisi data pada pengujian modul komunikasi.",
        "Melakukan studi literatur dan asistensi terkait sistem efisiensi konsumsi daya pada unit kendali.",
        "Menyusun dokumentasi teknis harian, rekapitulasi data hasil pengujian instrumentasi, dan evaluasi berkala."
    ],
    "Software / Web / Mobile / IT": [
        "Mempelajari arsitektur sistem perangkat lunak, alur kerja repositori kode, dan spesifikasi kebutuhan modul.",
        "Melakukan analisis alur data (data flow) serta pemetaan struktur antarmuka pengguna pada modul aplikasi.",
        "Mengembangkan dan menyempurnakan implementasi logika modul backend serta integrasi antarmuka API.",
        "Melakukan perancangan komponen antarmuka pengguna (UI/UX) berbasis desain responsif dan interaktif.",
        "Melakukan pengujian kode fungsional (unit testing) dan verifikasi respon endpoint layanan aplikasi.",
        "Melakukan pembersihan bug (debugging) dan optimalisasi penanganan pengecualian pada alur pemrosesan data.",
        "Melakukan sinkronisasi repositori git, penelaahan kode (code review), dan validasi integrasi berkelanjutan.",
        "Mempelajari dokumentasi struktur basis data relasional serta optimasi indeks relasi data.",
        "Melakukan simulasi deployment aplikasi ke lingkungan staging serta pengujian performa pemuatan laman.",
        "Menyusun dokumentasi teknis kode sumber (API documentation) dan pelaporan hasil progres sprint harian."
    ],
    "Umum Teknik / Telekomunikasi": [
        "Mempelajari Standard Operating Procedure (SOP) operasional teknis serta pengenalan regulasi keselamatan kerja.",
        "Melakukan survei lapangan dan inspeksi kondisi perangkat keras jaringan transmisi serta instrumentasi pendukung.",
        "Melakukan pengecekan kestabilan daya dan kontinuitas jalur transmisi sinyal pada perangkat operasional.",
        "Melakukan monitoring performa jaringan telekomunikasi dan pencatatan parameter metrik kualitas layanan harian.",
        "Melakukan asistensi teknis bersama mentor pembimbing terkait pemecahan kendala operasional lapangan.",
        "Melakukan pencatatan log historis gangguan serta analisis akar penyebab permasalahan teknis sistem.",
        "Melakukan kalibrasi berkala pada instrumen pengukuran sinyal dan parameter fisika lapangan.",
        "Mempelajari topologi jaringan transmisi serta manajemen alokasi frekuensi pada stasiun kerja.",
        "Melakukan pengujian redaman jalur kabel dan verifikasi kelayakan komponen interkoneksi perangkat.",
        "Menyusun rekapitulasi laporan logbook harian, dokumentasi foto kegiatan, dan rencana kerja teknis berikutnya."
    ]
}

PRESET_TEMPLATES_TA = {
    "Robotika / Mekatronika / Embedded": [
        "Melakukan studi literatur terkait pemodelan kinematika robot mobil diferensial dan metode kendali gerak berbasis high-level control.",
        "Menyusun kerangka modul praktikum sistem robot otonom beserta tujuan pembelajaran, alat, dan prosedur pengujian.",
        "Merancang skema wiring dan integrasi sensor jarak, encoder roda, serta modul komunikasi pada platform robot.",
        "Melakukan pengujian pergerakan robot lurus dan belok berdasarkan model kinematika serta koreksi error odometri.",
        "Mengembangkan algoritma navigasi waypoint dan pengujian akurasi posisi pada lintasan uji terkontrol.",
        "Melakukan kalibrasi parameter kontroler PID kecepatan roda dan evaluasi respon transien sistem.",
        "Menyusun dokumentasi teknis bab metode penelitian dan menyempurnakan diagram blok sistem kendali.",
        "Melakukan analisis data eksperimen, penyusunan tabel hasil uji, dan interpretasi grafik performa sistem.",
        "Melakukan revisi modul praktikum berdasarkan hasil evaluasi pengujian dan masukan pembimbing.",
        "Menyusun laporan kemajuan Proyek Akhir, slide presentasi, dan daftar pustaka sesuai panduan penulisan ilmiah."
    ],
    "Software / IoT / Sistem Cerdas": [
        "Melakukan studi literatur terkait arsitektur sistem cerdas, algoritma machine learning, dan dataset yang digunakan.",
        "Merancang dan mengimplementasikan pipeline preprocessing data serta ekstraksi fitur untuk model yang dikembangkan.",
        "Mengembangkan prototipe awal model dan melakukan eksperimen training pada dataset uji coba.",
        "Melakukan evaluasi performa model menggunakan metrik akurasi, presisi, recall, dan F1-score.",
        "Melakukan optimasi hyperparameter model dan komparasi hasil dengan baseline yang ada di literatur.",
        "Merancang antarmuka aplikasi dan integrasi model inference ke sistem backend atau embedded platform.",
        "Melakukan pengujian end-to-end sistem pada skenario nyata dan pencatatan hasil pengukuran performa.",
        "Menyusun dokumentasi teknis bab implementasi dan hasil pengujian beserta analisis statistiknya.",
        "Melakukan revisi dan penyempurnaan sistem berdasarkan masukan dan evaluasi pembimbing PA.",
        "Menyusun laporan akhir Proyek Akhir, abstrak, dan poster ilmiah sesuai format yang ditentukan jurusan."
    ],
    "Umum Teknik / Telekomunikasi": [
        "Melakukan studi literatur dan pengumpulan referensi terkait topik Proyek Akhir dari jurnal dan prosiding ilmiah.",
        "Merancang arsitektur sistem dan menyusun diagram blok keseluruhan komponen yang akan dikembangkan.",
        "Melakukan pengadaan dan uji kelayakan komponen hardware yang digunakan dalam implementasi sistem.",
        "Mengimplementasikan rancangan sistem dan melakukan pengujian unit pada masing-masing subsistem.",
        "Melakukan integrasi seluruh subsistem dan pengujian fungsional sistem secara keseluruhan.",
        "Menganalisis hasil pengujian dan menyusun tabel data serta grafik performa berdasarkan parameter ukur.",
        "Melakukan iterasi perbaikan sistem berdasarkan hasil analisis dan masukan dari pembimbing.",
        "Menyusun dokumentasi bab implementasi dan hasil pengujian beserta pembahasan yang komprehensif.",
        "Melakukan finalisasi sistem dan persiapan demo serta presentasi Proyek Akhir.",
        "Menyusun laporan Proyek Akhir lengkap, mempersiapkan slide sidang, dan revisi dokumen akhir."
    ]
}

DEFAULT_CONFIG = {
    "netid": "",
    "password": "",
    "remember_me": True,
    "presets": PRESET_TEMPLATES["Hardware / IoT / Mekatronika"],
    "last_used_preset_idx": 0,
    "presets_ta": PRESET_TEMPLATES_TA["Robotika / Mekatronika / Embedded"],
    "last_used_preset_ta_idx": 0
}

INDONESIAN_MONTHS = {
    'januari': 1, 'februari': 2, 'maret': 3, 'april': 4,
    'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8,
    'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
}

def load_config():
    for p in get_config_paths():
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in DEFAULT_CONFIG.items():
                        if k not in data:
                            data[k] = v
                    return data
            except Exception:
                pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    for p in get_config_paths():
        try:
            d = os.path.dirname(p)
            if d:
                os.makedirs(d, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Gagal save config ke {p}: {e}")

def sanitize_pens_sql(text):
    """Filter kata SELECT, INSERT, UPDATE, DELETE sesuai WAF resmi MIS PENS."""
    replacements = {
        r'\bselect\b': 'memilih',
        r'\bSELECT\b': 'MEMILIH',
        r'\binsert\b': 'memasukkan',
        r'\bINSERT\b': 'MEMASUKKAN',
        r'\bupdate\b': 'memperbarui',
        r'\bUPDATE\b': 'MEMPERBARUI',
        r'\bdelete\b': 'menghapus',
        r'\bDELETE\b': 'MENGHAPUS',
    }
    cleaned = text
    found = []
    for pattern, rep in replacements.items():
        if re.search(pattern, cleaned, re.IGNORECASE):
            found.append(pattern.replace(r'\b', ''))
            cleaned = re.sub(pattern, rep, cleaned, flags=re.IGNORECASE)
    return cleaned.replace("&", "dan"), found

def parse_start_date(tgl_kp_str):
    try:
        m = re.search(r'(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})', tgl_kp_str)
        if m:
            day = int(m.group(1))
            mon_name = m.group(2).lower()
            year = int(m.group(3))
            month = INDONESIAN_MONTHS.get(mon_name, 8)
            return date(year, month, day)
    except Exception:
        pass
    return date(2026, 8, 24)

def calculate_week_from_date(target_date, start_date):
    diff = (target_date - start_date).days
    if diff < 0:
        return 1
    w = (diff // 7) + 1
    return min(max(w, 1), 24)

def generate_random_times():
    mulai_min_pool = ["00", "10", "15", "20", "30", "40", "45"]
    selesai_min_pool = ["00", "10", "15", "20", "30", "45", "50"]
    
    jam_mulai_hour = random.choice([8, 9, 10])
    jam_mulai_min = "00" if jam_mulai_hour == 10 else random.choice(mulai_min_pool)
    jam_mulai = f"{jam_mulai_hour:02d}:{jam_mulai_min}"

    jam_selesai_hour = random.choice([14, 15, 16])
    jam_selesai_min = "00" if jam_selesai_hour == 16 else random.choice(selesai_min_pool)
    jam_selesai = f"{jam_selesai_hour:02d}:{jam_selesai_min}"

    return jam_mulai, jam_selesai

# ================= ASYNC WORKER THREAD =================

class PensWorker(QThread):
    log_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal(bool, str, object)
    progress_signal = pyqtSignal(int, int)

    def __init__(self, action, payload=None, user_context=None):
        super().__init__()
        self.action = action
        self.payload = payload or {}
        self.ctx = user_context or {}

    def run(self):
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        })

        if self.action == "login_cas":
            netid = self.payload.get("netid", "").strip()
            password = self.payload.get("password", "").strip()

            self.log_signal.emit(f"[INFO] Menghubungi CAS EEPIS PENS untuk {netid}...", "#e11d48")
            ok, msg, scraped = self._do_full_login(s, netid, password)
            if ok:
                self.log_signal.emit(f"[SUCCESS] Login Berhasil! User: {scraped['nama']} ({scraped['nrp']})", "#059669")
                self.finished_signal.emit(True, "login_cas", scraped)
            else:
                self.log_signal.emit(f"[ERROR] Login CAS Gagal: {msg}", "#e11d48")
                self.finished_signal.emit(False, "login_cas", msg)

        elif self.action == "fetch_entries":
            week = self.payload.get("week", 3)
            self.log_signal.emit(f"[INFO] Mengambil data logbook Minggu {week} dari MIS PENS...", "#0284c7")
            ok, msg, scraped = self._do_full_login(s, self.ctx['netid'], self.ctx['password'])
            if not ok:
                self.log_signal.emit(f"[ERROR] Gagal sesi login: {msg}", "#e11d48")
                self.finished_signal.emit(False, "fetch_entries", msg)
                return

            try:
                url = f"https://online.mis.pens.ac.id/entry_logbook_kp1.php?valTahun={self.ctx['tahun']}&valSemester={self.ctx['semester']}&valMinggu={week}"
                r = s.get(url, timeout=15)
                matches = re.findall(r'<tr>\s*<td align=["\']center["\']>(\d+)</td>\s*<td align=["\']center["\']>([^<]+)</td>\s*<td align=["\']center["\']>([^<]+)</td>\s*<td align=["\']center["\']>([^<]+)</td>\s*<td>([^<]*)</td>', r.text)
                entries = []
                for m in matches:
                    entries.append({
                        "no": m[0],
                        "tanggal": m[1],
                        "jam_mulai": m[2],
                        "jam_selesai": m[3],
                        "kegiatan": m[4].strip()
                    })
                self.log_signal.emit(f"[SUCCESS] Ditemukan {len(entries)} entri di Minggu {week}", "#059669")
                self.finished_signal.emit(True, "fetch_entries", {"week": week, "entries": entries})
            except Exception as e:
                self.log_signal.emit(f"[ERROR] Gagal parse data PENS: {str(e)}", "#e11d48")
                self.finished_signal.emit(False, "fetch_entries", str(e))

        elif self.action == "submit_single":
            tgl = self.payload.get("tanggal")
            minggu = self.payload.get("minggu")
            jm = self.payload.get("jam_mulai")
            js = self.payload.get("jam_selesai")
            keg = self.payload.get("kegiatan")

            self.log_signal.emit(f"[SUBMIT] Menembak logbook tanggal {tgl} (Minggu {minggu})...", "#e11d48")
            ok, msg, scraped = self._do_full_login(s, self.ctx['netid'], self.ctx['password'])
            if not ok:
                self.log_signal.emit(f"[ERROR] Gagal login: {msg}", "#e11d48")
                self.finished_signal.emit(False, "submit_single", msg)
                return

            res_ok, res_msg = self._submit_post(s, tgl, minggu, jm, js, keg)
            if res_ok:
                self.log_signal.emit(f"[SUCCESS] SUKSES TERKIRIM: {tgl} | {jm}-{js} | {keg[:40]}...", "#059669")
                self.finished_signal.emit(True, "submit_single", {"tanggal": tgl, "minggu": minggu})
            else:
                self.log_signal.emit(f"[ERROR] GAGAL SUBMIT: {res_msg}", "#e11d48")
                self.finished_signal.emit(False, "submit_single", res_msg)

        elif self.action == "submit_batch":
            dates = self.payload.get("dates", [])
            mode_pilih = self.payload.get("mode_pilih", "random")
            presets = self.payload.get("presets", [])
            start_kp_date = self.ctx.get("start_kp_date", date(2026, 8, 24))

            self.log_signal.emit(f"[SUBMIT] Memulai batch submit {len(dates)} hari kerja...", "#e11d48")
            ok, msg, scraped = self._do_full_login(s, self.ctx['netid'], self.ctx['password'])
            if not ok:
                self.log_signal.emit(f"[ERROR] Login gagal: {msg}", "#e11d48")
                self.finished_signal.emit(False, "submit_batch", msg)
                return

            total = len(dates)
            success_count = 0
            curr_idx = self.payload.get("last_idx", 0)

            for i, target_date in enumerate(dates):
                tgl_str = target_date.strftime("%Y-%m-%d")
                minggu = calculate_week_from_date(target_date, start_kp_date)
                jm, js = generate_random_times()

                if mode_pilih == "sequence":
                    keg = presets[curr_idx % len(presets)]
                    curr_idx += 1
                else:
                    keg = random.choice(presets)

                self.log_signal.emit(f"[{i+1}/{total}] Tembak {tgl_str} ({jm}-{js}) Minggu {minggu}...", "#e11d48")
                res_ok, res_msg = self._submit_post(s, tgl_str, minggu, jm, js, keg)
                if res_ok:
                    success_count += 1
                    self.log_signal.emit(f"  -> Sukses tersimpan.", "#059669")
                else:
                    self.log_signal.emit(f"  -> Gagal: {res_msg}", "#e11d48")

                self.progress_signal.emit(i + 1, total)
                time.sleep(1.2)

            self.log_signal.emit(f"[SUCCESS] BATCH SELESAI: {success_count}/{total} entri sukses tersimpan di MIS PENS.", "#059669")
            self.finished_signal.emit(True, "submit_batch", {"success_count": success_count, "total": total, "last_idx": curr_idx})

        elif self.action == "fetch_ta":
            week = self.payload.get("week", 1)
            self.log_signal.emit(f"[INFO] Mengambil data logbook SPPA Minggu {week} dari MIS PENS...", "#7c3aed")
            ok, msg, scraped = self._do_full_login(s, self.ctx['netid'], self.ctx['password'])
            if not ok:
                self.log_signal.emit(f"[ERROR] Gagal sesi login: {msg}", "#e11d48")
                self.finished_signal.emit(False, "fetch_ta", msg)
                return
            try:
                url = f"https://online.mis.pens.ac.id/entry_logbook_ta.php?valTahun={self.ctx['tahun']}&valSemester={self.ctx['semester']}&valMinguLihat={week}&sid={random.random()}"
                r = s.get(url, timeout=15)
                matches = re.findall(
                    r'<tr>\s*<td align=["\']center["\']>(\d+)</td>\s*<td align=["\']center["\']>([^<]+)</td>\s*<td align=["\']center["\']>([^<]+)</td>\s*<td align=["\']center["\']>([^<]+)</td>\s*<td[^>]*>([^<]*)</td>',
                    r.text)
                entries = []
                for m in matches:
                    entries.append({"no": m[0], "tanggal": m[1], "jam_mulai": m[2], "jam_selesai": m[3], "kegiatan": m[4].strip()})
                self.log_signal.emit(f"[SUCCESS] Ditemukan {len(entries)} entri SPPA di Minggu {week}", "#059669")
                self.finished_signal.emit(True, "fetch_ta", {"week": week, "entries": entries})
            except Exception as e:
                self.log_signal.emit(f"[ERROR] Gagal parse data SPPA: {str(e)}", "#e11d48")
                self.finished_signal.emit(False, "fetch_ta", str(e))

        elif self.action == "submit_ta_single":
            tgl_py = self.payload.get("tanggal_py")   # date object
            minggu = self.payload.get("minggu")
            jm = self.payload.get("jam_mulai")
            js = self.payload.get("jam_selesai")
            keg = self.payload.get("kegiatan")
            tgl_str = tgl_py.strftime("%d-%m-%Y")     # SPPA butuh d-m-Y!

            self.log_signal.emit(f"[SUBMIT] Tembak SPPA {tgl_str} (Minggu {minggu})...", "#7c3aed")
            ok, msg, scraped = self._do_full_login(s, self.ctx['netid'], self.ctx['password'])
            if not ok:
                self.log_signal.emit(f"[ERROR] Login gagal: {msg}", "#e11d48")
                self.finished_signal.emit(False, "submit_ta_single", msg)
                return
            res_ok, res_msg = self._submit_ta_post(s, tgl_str, minggu, jm, js, keg)
            if res_ok:
                self.log_signal.emit(f"[SUCCESS] SPPA TERKIRIM: {tgl_str} | {jm}-{js}", "#059669")
                self.finished_signal.emit(True, "submit_ta_single", {"tanggal": tgl_str})
            else:
                self.log_signal.emit(f"[ERROR] GAGAL: {res_msg}", "#e11d48")
                self.finished_signal.emit(False, "submit_ta_single", res_msg)

        elif self.action == "submit_ta_batch":
            dates = self.payload.get("dates", [])
            mode_pilih = self.payload.get("mode_pilih", "random")
            presets = self.payload.get("presets", [])
            start_pa_date = self.ctx.get("start_kp_date", date.today())

            self.log_signal.emit(f"[SUBMIT] Batch SPPA {len(dates)} hari kerja...", "#7c3aed")
            ok, msg, scraped = self._do_full_login(s, self.ctx['netid'], self.ctx['password'])
            if not ok:
                self.log_signal.emit(f"[ERROR] Login gagal: {msg}", "#e11d48")
                self.finished_signal.emit(False, "submit_ta_batch", msg)
                return

            total = len(dates)
            success_count = 0
            curr_idx = self.payload.get("last_idx", 0)

            for i, target_date in enumerate(dates):
                tgl_str = target_date.strftime("%d-%m-%Y")
                minggu = calculate_week_from_date(target_date, start_pa_date)
                jm, js = generate_random_times()
                if mode_pilih == "sequence":
                    keg = presets[curr_idx % len(presets)]
                    curr_idx += 1
                else:
                    keg = random.choice(presets)

                self.log_signal.emit(f"[{i+1}/{total}] SPPA {tgl_str} ({jm}-{js}) Minggu {minggu}...", "#7c3aed")
                res_ok, res_msg = self._submit_ta_post(s, tgl_str, minggu, jm, js, keg)
                if res_ok:
                    success_count += 1
                    self.log_signal.emit(f"  -> Sukses.", "#059669")
                else:
                    self.log_signal.emit(f"  -> Gagal: {res_msg}", "#e11d48")

                self.progress_signal.emit(i + 1, total)
                time.sleep(1.2)

            self.log_signal.emit(f"[SUCCESS] BATCH SPPA SELESAI: {success_count}/{total} entri tersimpan.", "#059669")
            self.finished_signal.emit(True, "submit_ta_batch", {"success_count": success_count, "total": total, "last_idx": curr_idx})

        elif self.action == "fetch_academic":
            self.log_signal.emit("[INFO] Mengambil data Akademik, Jadwal & Presensi dari MIS PENS...", "#0284c7")
            ok, msg, scraped = self._do_full_login(s, self.ctx['netid'], self.ctx['password'])
            if not ok:
                self.log_signal.emit(f"[ERROR] Gagal login untuk data akademik: {msg}", "#e11d48")
                self.finished_signal.emit(False, "fetch_academic", msg)
                return

            try:
                # 1. Transkrip: IPK, SKS, Dosen Wali
                r_trans = s.get("https://online.mis.pens.ac.id/cetak_transkripSemMBKM.php", timeout=20)
                m_ipk = re.search(r'Indeks Prestasi[\s\S]*?<td[^>]*>:\s*</td>[\s\S]*?<td[^>]*>([\d\.,]+)</td>', r_trans.text)
                ipk = m_ipk.group(1).strip() if m_ipk else "-"

                m_sks = re.search(r'Jumlah SKS[^\n<]*<br>[^\n<]*Total Credits</td><td>\s*:\s*(\d+)\s*sks</td>', r_trans.text)
                sks = m_sks.group(1).strip() if m_sks else "-"

                m_wali = re.search(r'Dosen Wali[^\n<]*</td>[\s\S]*?<td[^>]*>:\s*</td>[\s\S]*?<td[^>]*>([^<]+)</td>', r_trans.text)
                if not m_wali:
                    m_wali = re.search(r'<td>\s*(Novian[^\n<]+)<br>', r_trans.text)
                dosen_wali = m_wali.group(1).strip() if m_wali else "-"

                # 2. Jadwal Kuliah
                thn = self.ctx.get("tahun", "2026")
                smt = self.ctx.get("semester", "1")
                r_jad = s.get(f"https://online.mis.pens.ac.id/jadwal_kul.php?valTahun={thn}&valSemester={smt}&sid={random.random()}", timeout=20)
                days = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']
                jadwal = {}
                for i, d in enumerate(days):
                    idx_d = r_jad.text.find(f'>{d}')
                    if idx_d == -1:
                        continue
                    next_idx = len(r_jad.text)
                    for nd in days[i+1:]:
                        pos = r_jad.text.find(f'>{nd}', idx_d + len(d))
                        if pos != -1 and pos < next_idx:
                            next_idx = pos
                            break
                    chunk = r_jad.text[idx_d:next_idx]
                    cells = re.findall(r'<td[^>]*width=[\"\']475[\"\'][^>]*>([\s\S]*?)</td>', chunk)
                    entries = []
                    for c in cells:
                        clean = re.sub(r'</?(?:div|center)[^>]*>', '', c)
                        parts = [p.strip() for p in clean.split('<br>') if p.strip()]
                        if len(parts) >= 3:
                            entries.append({'matkul': parts[0], 'dosen_jam': parts[1], 'ruang': parts[2]})
                        elif len(parts) == 2:
                            entries.append({'matkul': parts[0], 'dosen_jam': parts[1], 'ruang': '-'})
                        elif len(parts) == 1:
                            entries.append({'matkul': parts[0], 'dosen_jam': '-', 'ruang': '-'})
                    if entries:
                        jadwal[d] = entries

                # 3. Presensi Kehadiran
                nrp = self.ctx.get("nrp", "")
                r_abs = s.get(f"https://online.mis.pens.ac.id/absen.php?valTahun={thn}&valSemester={smt}&valnrp={nrp}&sid={random.random()}", timeout=20)
                absen_rows = re.findall(r'<tr>\s*<td[^>]*>([A-Z0-9]+)</td>\s*<td[^>]*>([^<]+)</td>([\s\S]*?)<td[^>]*>(\d+\s*%)</td>', r_abs.text)
                presensi = []
                for kode, mk, _, pct in absen_rows:
                    pct_clean = pct.strip()
                    digits = re.sub(r'[^\d]', '', pct_clean)
                    num = int(digits) if digits else 0
                    presensi.append({
                        'kode': kode.strip(),
                        'matkul': mk.strip(),
                        'persen': pct_clean,
                        'persen_num': num
                    })

                self.log_signal.emit(f"[SUCCESS] Data Akademik: IPK {ipk} | Total {sks} SKS | Dosen Wali: {dosen_wali}", "#059669")
                self.finished_signal.emit(True, "fetch_academic", {
                    "ipk": ipk,
                    "sks": sks,
                    "dosen_wali": dosen_wali,
                    "jadwal": jadwal,
                    "presensi": presensi
                })
            except Exception as e:
                self.log_signal.emit(f"[ERROR] Gagal memuat data akademik: {str(e)}", "#e11d48")
                self.finished_signal.emit(False, "fetch_academic", str(e))

        elif self.action == "upload_file":
            target = self.payload.get("target", "kp")
            file_path = self.payload.get("file_path", "")
            file_type = self.payload.get("file_type", "pdf")

            if not file_path or not os.path.exists(file_path):
                self.log_signal.emit("[ERROR] File yang akan diunggah tidak ditemukan di komputer!", "#e11d48")
                self.finished_signal.emit(False, "upload_file", "File tidak ditemukan di disk.")
                return

            fname = os.path.basename(file_path)
            self.log_signal.emit(f"[UPLOAD] Mengunggah {fname} ke server MIS PENS ({target.upper()})...", "#0284c7")
            ok, msg, scraped = self._do_full_login(s, self.ctx['netid'], self.ctx['password'])
            if not ok:
                self.log_signal.emit(f"[ERROR] Sesi login gagal untuk unggah: {msg}", "#e11d48")
                self.finished_signal.emit(False, "upload_file", msg)
                return

            try:
                url = "https://online.mis.pens.ac.id/mEntry_Logbook_KP1.php" if target == "kp" else "https://online.mis.pens.ac.id/mEntry_Logbook_TA.php"
                field_flag = "kirimfile1" if file_type == "pdf" else "kirimfile2"
                file_field = "fileupload" if file_type == "pdf" else "fileupload2"
                mime = "application/pdf" if file_type == "pdf" else "image/jpeg"

                with open(file_path, 'rb') as fp:
                    files = {file_field: (fname, fp.read(), mime)}
                data = {field_flag: '1'}

                r = s.post(url, data=data, files=files, timeout=30)
                if r.status_code == 200:
                    self.log_signal.emit(f"[SUCCESS] Berhasil mengunggah berkas: {fname}!", "#059669")
                    self.finished_signal.emit(True, "upload_file", {"filename": fname, "target": target, "file_type": file_type})
                else:
                    self.log_signal.emit(f"[ERROR] Gagal unggah berkas: HTTP {r.status_code}", "#e11d48")
                    self.finished_signal.emit(False, "upload_file", f"HTTP {r.status_code}")
            except Exception as e:
                self.log_signal.emit(f"[ERROR] Kendala jaringan saat unggah berkas: {str(e)}", "#e11d48")
                self.finished_signal.emit(False, "upload_file", str(e))

    def _do_full_login(self, s, netid, password):
        try:
            r1 = s.get('https://login.pens.ac.id/cas/login?service=https%3A%2F%2Fonline.mis.pens.ac.id%2Findex.php%3FLogin%3D1%26halAwal%3D1', timeout=15)
            lt_match = re.search(r'name=["\']lt["\']\s+value=["\']([^"\']+)["\']', r1.text)
            action_match = re.search(r'action=["\']([^"\']+)["\']', r1.text)
            if not lt_match:
                return False, "Tidak menemukan token keamanan LT dari CAS", {}
            
            lt = lt_match.group(1)
            action = action_match.group(1) if action_match else '/cas/login'
            if not action.startswith('http'):
                action = 'https://login.pens.ac.id' + action

            data = {
                'username': netid,
                'password': password,
                'lt': lt,
                '_eventId': 'submit',
                'submit': 'LOGIN'
            }
            r2 = s.post(action, data=data, timeout=15, allow_redirects=True)
            if not ('online.mis.pens.ac.id' in r2.url or 'mEntry_Logbook_KP1.php' in r2.text or 'Logout' in r2.text):
                return False, "NetID atau Password CAS salah / ditolak server PENS", {}

            m_user = re.search(r'USER\s*:\s*([^(\n\r<]+)\s*\(([0-9]+)\)', r2.text)
            nama = m_user.group(1).strip() if m_user else netid
            nrp = m_user.group(2).strip() if m_user else "-"

            r3 = s.get('https://online.mis.pens.ac.id/mEntry_Logbook_KP1.php', timeout=15)
            m_load = re.search(r'showEntry_Logbook_KP1\((\d+),\s*(\d+),\s*(\d+)\)', r3.text)
            tahun = m_load.group(1) if m_load else '2026'
            semester = m_load.group(2) if m_load else '1'
            minggu_default = int(m_load.group(3)) if m_load else 3

            r4 = s.get(f'https://online.mis.pens.ac.id/entry_logbook_kp1.php?valTahun={tahun}&valSemester={semester}&valMinggu={minggu_default}', timeout=15)
            
            m_kp = re.search(r'name=["\']kp_daftar["\'][^>]*value=["\']([^"\']+)["\']', r4.text)
            m_mhs = re.search(r'name=["\']mahasiswa["\'][^>]*value=["\']([^"\']+)["\']', r4.text)
            kp_daftar = m_kp.group(1) if m_kp else "0"
            mahasiswa = m_mhs.group(1) if m_mhs else "0"

            m_tempat = re.search(r'Tempat KP\s*</td>\s*<td[^>]*>\s*:\s*([^<]+)</td>', r4.text)
            tempat_kp = m_tempat.group(1).strip() if m_tempat else "Tempat KP"

            m_tgl = re.search(r'Tanggal KP\s*</td>\s*<td[^>]*>\s*:\s*([^<]+)</td>', r4.text)
            tgl_kp_str = m_tgl.group(1).strip() if m_tgl else "24 Agustus 2026 sd 05 Februari 2027"

            scraped = {
                "netid": netid,
                "password": password,
                "nama": nama,
                "nrp": nrp,
                "tahun": tahun,
                "semester": semester,
                "minggu_default": minggu_default,
                "kp_daftar": kp_daftar,
                "mahasiswa": mahasiswa,
                "tempat_kp": tempat_kp,
                "tgl_kp_str": tgl_kp_str,
                "start_kp_date": parse_start_date(tgl_kp_str)
            }

            # Scrape ta_mahasiswa dari halaman TA (id yg beda dari KP)
            try:
                r_ta = s.get(f'https://online.mis.pens.ac.id/entry_logbook_ta.php?valTahun={tahun}&valSemester={semester}&valMinggu=1', timeout=15)
                m_ta_mhs = re.search(r'name=["\']mahasiswa["\'][^>]*value=["\']([^"\']+)["\']', r_ta.text)
                scraped["ta_mahasiswa"] = m_ta_mhs.group(1) if m_ta_mhs else mahasiswa
                m_judul = re.search(r'Judul PA</td><td colspan="3">:\s*([^<]+)</td>', r_ta.text)
                scraped["judul_pa"] = m_judul.group(1).strip() if m_judul else ""
            except Exception:
                scraped["ta_mahasiswa"] = mahasiswa
                scraped["judul_pa"] = ""

            return True, "OK", scraped
        except Exception as e:
            return False, f"Koneksi CAS Error: {str(e)}", {}

    def _submit_post(self, s, tgl, minggu, jm, js, keg):
        clean_keg, _ = sanitize_pens_sql(keg)
        payload = {
            'valnrpMahasiswa': self.ctx["nrp"],
            'valTahun': self.ctx["tahun"],
            'valSemester': self.ctx["semester"],
            'valMinggu': str(minggu),
            'Simpan': '1',
            'tanggal': tgl,
            'jam_mulai': jm,
            'jam_selesai': js,
            'kegiatan': clean_keg,
            'sesuai_kuliah': '2',
            'matakuliah': '',
            'kp_daftar': self.ctx["kp_daftar"],
            'mahasiswa': self.ctx["mahasiswa"],
            'Setuju': '1',
            'sid': str(random.random())
        }
        try:
            r = s.post('https://online.mis.pens.ac.id/entry_logbook_kp1.php', data=payload, timeout=20)
            if r.status_code == 200:
                return True, "OK"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    def _submit_ta_post(self, s, tgl_str, minggu, jm, js, keg):
        """Submit entri logbook SPPA/PPA/PA.
        Beda dari KP:
        - tanggal format d-m-Y (bukan Y-m-d)
        - field: mahasiswa (bukan kp_daftar)
        - TIDAK ada sesuai_kuliah / matakuliah
        - endpoint: entry_logbook_ta.php
        """
        clean_keg, _ = sanitize_pens_sql(keg)
        payload = {
            'valnrpMahasiswa': self.ctx["nrp"],
            'valTahun': self.ctx["tahun"],
            'valSemester': self.ctx["semester"],
            'valMinggu': str(minggu),
            'Simpan': '1',
            'tanggal': tgl_str,     # d-m-Y
            'jam_mulai': jm,
            'jam_selesai': js,
            'kegiatan': clean_keg,
            'mahasiswa': self.ctx.get("ta_mahasiswa", self.ctx.get("mahasiswa", "0")),
            'Setuju': '1',
            'sid': str(random.random()),
        }
        try:
            r = s.post('https://online.mis.pens.ac.id/entry_logbook_ta.php', data=payload, timeout=20)
            if r.status_code == 200:
                return True, "OK"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)


# ================= CLEAN MODERN WHITE THEME STYLESHEET =================

CLEAN_WHITE_QSS = """
/* Global Base */
QWidget {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* Explicitly remove all borders and background on labels */
QLabel {
    border: none;
    background: transparent;
    padding: 0px;
    margin: 0px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
    border-radius: 12px;
    top: -1px;
}
QTabBar::tab {
    background-color: #f1f5f9;
    color: #64748b;
    border: 1px solid #e2e8f0;
    padding: 10px 18px;
    min-width: 140px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 6px;
    font-weight: 700;
}
QTabBar::tab:selected {
    background-color: #ffffff;
    color: #e11d48;
    border-top: 3px solid #e11d48;
    border-bottom: 1px solid #ffffff;
}
QTabBar::tab:hover {
    color: #e11d48;
    background-color: #ffffff;
}

/* Clean GroupBox */
QGroupBox {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-top: 14px;
    padding-top: 20px;
    background-color: #ffffff;
    font-weight: 800;
    color: #0f172a;
    font-size: 13px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    background-color: #f8fafc;
    color: #e11d48;
    font-weight: bold;
}

/* Only form controls get borders */
QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 12px;
    color: #0f172a;
    selection-background-color: #ffe4e6;
    selection-color: #9f1239;
    font-size: 13px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus, QTextEdit:focus {
    border: 1.5px solid #e11d48;
    background-color: #ffffff;
}

/* Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e11d48, stop:1 #f43f5e);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 700;
    font-size: 13px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #be123c, stop:1 #e11d48);
}
QPushButton:pressed {
    background-color: #9f1239;
}
QPushButton#btnSuccess {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
    color: #ffffff;
}
QPushButton#btnSuccess:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #047857, stop:1 #059669);
}
QPushButton#btnSecondary {
    background-color: #f1f5f9;
    color: #334155;
    border: 1px solid #cbd5e1;
}
QPushButton#btnSecondary:hover {
    background-color: #e2e8f0;
    color: #e11d48;
    border-color: #e11d48;
}

/* Clean Table */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f1f5f9;
    color: #0f172a;
}
QHeaderView::section {
    background-color: #f8fafc;
    color: #0f172a;
    padding: 10px 8px;
    border: 1px solid #e2e8f0;
    font-weight: 700;
}
QTableWidget::item:selected {
    background-color: #ffe4e6;
    color: #9f1239;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    text-align: center;
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: bold;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e11d48, stop:1 #fb7185);
    border-radius: 5px;
}

/* Scrollbar */
QScrollBar:vertical {
    background: #f8fafc;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #e11d48;
}

/* Card ID Selectors (prevents style bleeding to children) */
#loginCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 34px;
}
#headerCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 12px 20px;
}
#userCard {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 6px 14px;
}
#creditBox {
    background-color: #fff1f2;
    border: 1px solid #fecdd3;
    border-radius: 12px;
    padding: 14px 18px;
}
#aboutCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 30px;
}
#batchPreviewBox {
    background-color: #fff1f2;
    border: 1px solid #fecdd3;
    border-radius: 10px;
    padding: 12px;
}
#slotRow {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 4px;
}
#attachmentBox {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 8px 12px;
}
#chipBtn {
    background-color: #ffffff;
    border: 1px dashed #cbd5e1;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    text-align: center;
}
#chipBtn:hover {
    border-color: #e11d48;
    color: #e11d48;
    background-color: #fff1f2;
}
#chipBtnSelectedKP {
    background-color: #fff1f2;
    border: 1px solid #fecdd3;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: 800;
    color: #be123c;
    text-align: center;
}
#chipBtnSelectedTA {
    background-color: #f5f3ff;
    border: 1px solid #ddd6fe;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: 800;
    color: #6d28d9;
    text-align: center;
}
#chipClearBtn {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    color: #64748b;
    font-weight: 900;
    font-size: 11px;
    border-radius: 6px;
    padding: 0px;
}
#chipClearBtn:hover {
    background-color: #fee2e2;
    border-color: #fecdd3;
    color: #e11d48;
}
"""


# ================= MAIN APPLICATION WINDOW =================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.user_ctx = {}
        self._workers = []

        self.setWindowTitle("PENS Companion by 404Workshop")
        self.resize(1260, 840)
        self.setMinimumSize(1100, 740)
        self.setStyleSheet(CLEAN_WHITE_QSS)

        # Set Icon
        icon_path = resource_path("app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Root Stacked Widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.page_login = QWidget()
        self.page_dashboard = QWidget()

        self.selected_file_kp_pdf = ""
        self.selected_file_kp_jpg = ""
        self.selected_file_ta_pdf = ""
        self.selected_file_ta_jpg = ""

        self.stack.addWidget(self.page_login)     # Index 0
        self.stack.addWidget(self.page_dashboard) # Index 1

        self.init_login_page()
        self.init_dashboard_page()

        # Check remember me
        if self.cfg.get("remember_me") and self.cfg.get("netid") and self.cfg.get("password"):
            self.txt_login_user.setText(self.cfg["netid"])
            self.txt_login_pass.setText(self.cfg["password"])
            self.do_cas_login()

    def start_worker(self, worker, on_finished=None):
        """Menjalankan QThread worker dengan aman tanpa bahaya garbage-collection crash."""
        self._workers.append(worker)
        worker.finished.connect(lambda: self._workers.remove(worker) if worker in self._workers else None)
        worker.log_signal.connect(self.log)
        if on_finished:
            worker.finished_signal.connect(on_finished)
        else:
            worker.finished_signal.connect(self.on_worker_finished)
        if hasattr(worker, 'progress_signal'):
            worker.progress_signal.connect(self.on_progress)
        worker.start()
        return worker

    def refresh_style(self, widget):
        """Me-refresh stylesheet runtime saat objectName widget berubah."""
        try:
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()
        except Exception:
            pass

    # ---------------- PAGE 0: LOGIN SCREEN ----------------
    def init_login_page(self):
        root_lay = QVBoxLayout(self.page_login)
        root_lay.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(500)
        c_lay = QVBoxLayout(card)
        c_lay.setSpacing(14)

        # Top Bar: Logo & Version
        top_h = QHBoxLayout()
        logo_label = QLabel()
        logo_path = resource_path("logo_login.png")
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path)
            logo_label.setPixmap(pm)
        else:
            logo_label.setText("404 NOTFOUND")
            logo_label.setStyleSheet("color: #e11d48; font-weight: 900; font-size: 20px;")
        top_h.addWidget(logo_label)
        top_h.addStretch()

        ver_tag = QLabel("v3.0 COMPANION")
        ver_tag.setStyleSheet("color: #e11d48; font-size: 11px; font-weight: bold; border: 1px solid #fecdd3; padding: 4px 10px; border-radius: 10px; background: #fff1f2;")
        top_h.addWidget(ver_tag)
        c_lay.addLayout(top_h)

        # Headings: Clean plain text without any boxes
        t_title = QLabel("PENS Companion")
        t_title.setStyleSheet("font-size: 22px; font-weight: 900; color: #0f172a; margin-top: 4px;")
        c_lay.addWidget(t_title)

        t_sub = QLabel("by 404Workshop // Otomatisasi Logbook KP, SPPA & Portal Akademik PENS")
        t_sub.setStyleSheet("font-size: 12px; color: #64748b;")
        t_sub.setWordWrap(True)
        c_lay.addWidget(t_sub)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("border-top: 1px solid #e2e8f0; margin: 4px 0;")
        c_lay.addWidget(sep)

        # Form Inputs
        lbl_user = QLabel("NetID / Email Mahasiswa PENS:")
        lbl_user.setStyleSheet("font-weight: 600; color: #334155;")
        c_lay.addWidget(lbl_user)

        self.txt_login_user = QLineEdit()
        self.txt_login_user.setFixedHeight(40)
        self.txt_login_user.setPlaceholderText("contoh: putra@me.student.pens.ac.id")
        c_lay.addWidget(self.txt_login_user)

        lbl_pass = QLabel("Password CAS EEPIS:")
        lbl_pass.setStyleSheet("font-weight: 600; color: #334155;")
        c_lay.addWidget(lbl_pass)

        self.txt_login_pass = QLineEdit()
        self.txt_login_pass.setFixedHeight(40)
        self.txt_login_pass.setEchoMode(QLineEdit.Password)
        self.txt_login_pass.setPlaceholderText("Password akun CAS PENS kamu")
        c_lay.addWidget(self.txt_login_pass)

        self.chk_remember = QCheckBox("Ingat Kredensial di Komputer Ini")
        self.chk_remember.setChecked(self.cfg.get("remember_me", True))
        c_lay.addWidget(self.chk_remember)

        self.lbl_login_status = QLabel("")
        self.lbl_login_status.setStyleSheet("font-size: 12px; min-height: 18px; font-weight: bold;")
        self.lbl_login_status.setAlignment(Qt.AlignCenter)
        c_lay.addWidget(self.lbl_login_status)

        self.btn_login = QPushButton("MASUK CAS PENS")
        self.btn_login.setFixedHeight(46)
        self.btn_login.setStyleSheet("font-size: 14px; font-weight: 800; border-radius: 8px;")
        self.btn_login.clicked.connect(self.do_cas_login)
        c_lay.addWidget(self.btn_login)

        # Developer Credit Card (Mohammad Putra Maulana Yufen)
        credit_box = QFrame()
        credit_box.setObjectName("creditBox")
        cr_lay = QVBoxLayout(credit_box)
        cr_lay.setSpacing(3)

        c1 = QLabel("CRAFTED BY")
        c1.setStyleSheet("font-size: 10px; color: #be123c; font-weight: 800; letter-spacing: 0.5px;")
        c1.setAlignment(Qt.AlignCenter)
        cr_lay.addWidget(c1)

        c2 = QLabel("Mohammad Putra Maulana Yufen")
        c2.setStyleSheet("font-size: 14px; font-weight: 900; color: #0f172a;")
        c2.setAlignment(Qt.AlignCenter)
        cr_lay.addWidget(c2)

        c3 = QLabel("MEKATRONIKA 23 - Instagram: @yufenxyz")
        c3.setStyleSheet("font-size: 12px; font-weight: bold; color: #e11d48;")
        c3.setAlignment(Qt.AlignCenter)
        cr_lay.addWidget(c3)

        c_lay.addWidget(credit_box)

        root_lay.addWidget(card)

    def do_cas_login(self):
        user = self.txt_login_user.text().strip()
        pwd = self.txt_login_pass.text().strip()

        if not user or not pwd:
            self.lbl_login_status.setText("NetID dan Password wajib diisi!")
            self.lbl_login_status.setStyleSheet("color: #e11d48;")
            return

        self.btn_login.setEnabled(False)
        self.btn_login.setText("Menghubungkan ke CAS PENS...")
        self.lbl_login_status.setText("Memverifikasi kredensial di server PENS...")
        self.lbl_login_status.setStyleSheet("color: #0284c7;")

        worker = PensWorker("login_cas", payload={"netid": user, "password": pwd})
        self.start_worker(worker, on_finished=self.on_login_finished)

    def on_login_finished(self, success, action, data):
        self.btn_login.setEnabled(True)
        self.btn_login.setText("MASUK CAS PENS")

        if success:
            self.user_ctx = data
            if self.chk_remember.isChecked():
                self.cfg["netid"] = self.user_ctx["netid"]
                self.cfg["password"] = self.user_ctx["password"]
                self.cfg["remember_me"] = True
            else:
                self.cfg["netid"] = ""
                self.cfg["password"] = ""
                self.cfg["remember_me"] = False
            save_config(self.cfg)

            self.lbl_dash_user.setText(f"{self.user_ctx['nama']} ({self.user_ctx['nrp']})")
            self.lbl_dash_kp.setText(f"Tempat KP: {self.user_ctx['tempat_kp']} | Periode: {self.user_ctx['tgl_kp_str']}")

            w = calculate_week_from_date(date.today(), self.user_ctx['start_kp_date'])
            self.combo_view_week.blockSignals(True)
            self.combo_view_week.setCurrentIndex(min(max(w - 1, 0), 23))
            self.combo_view_week.blockSignals(False)
            self.lbl_week_single.setText(f"Minggu ke-{w}")
            self.lbl_week_single_ta.setText(f"Minggu ke-{w}")

            # update info judul PA di tab SPPA
            judul = self.user_ctx.get("judul_pa", "")
            if judul:
                self.lbl_judul_pa.setText(f"Judul PA: {judul[:80]}{'...' if len(judul) > 80 else ''}")
            else:
                self.lbl_judul_pa.setText("Judul PA: (belum terdaftar / belum disetujui)")

            self.stack.setCurrentIndex(1)
            self.log(f"[INFO] Selamat datang, {self.user_ctx['nama']}!", "#059669")
            self.log(f"[INFO] Tempat KP: {self.user_ctx['tempat_kp']}", "#e11d48")

            self.do_fetch_entries()
            QTimer.singleShot(1200, self.do_fetch_academic)
        else:
            self.lbl_login_status.setText(f"Gagal: {data}")
            self.lbl_login_status.setStyleSheet("color: #e11d48;")

    def do_logout(self):
        reply = QMessageBox.question(self, "Konfirmasi Logout", "Apakah kamu yakin ingin keluar dan berganti akun?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.user_ctx = {}
            self.txt_login_pass.clear()
            self.lbl_login_status.clear()
            self.stack.setCurrentIndex(0)

    # ---------------- PAGE 1: MAIN DASHBOARD ----------------
    def init_dashboard_page(self):
        root_lay = QVBoxLayout(self.page_dashboard)
        root_lay.setContentsMargins(20, 16, 20, 16)
        root_lay.setSpacing(14)

        # Header Bar - Clean White Card
        header_frame = QFrame()
        header_frame.setObjectName("headerCard")
        header = QHBoxLayout(header_frame)
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(16)

        # Logo Image
        logo_label = QLabel()
        logo_path = resource_path("logo_header.png")
        if os.path.exists(logo_path):
            logo_label.setPixmap(QPixmap(logo_path))
        else:
            logo_label.setText("404")
            logo_label.setStyleSheet("color: #e11d48; font-weight: 900; font-size: 18px;")
        header.addWidget(logo_label)

        # App Title & Subtitle (Plain text without any box)
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        app_name = QLabel("PENS Companion")
        app_name.setStyleSheet("font-size: 17px; font-weight: 900; color: #0f172a;")
        sub_name = QLabel("by 404Workshop // MIS Portal Automation Suite")
        sub_name.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 600;")
        title_box.addWidget(app_name)
        title_box.addWidget(sub_name)
        header.addLayout(title_box)

        header.addStretch()

        # Student Profile Card
        user_card = QFrame()
        user_card.setObjectName("userCard")
        u_lay = QVBoxLayout(user_card)
        u_lay.setSpacing(2)
        self.lbl_dash_user = QLabel("Mahasiswa PENS")
        self.lbl_dash_user.setStyleSheet("font-size: 12px; font-weight: 800; color: #0f172a;")
        self.lbl_dash_kp = QLabel("Memuat data...")
        self.lbl_dash_kp.setStyleSheet("font-size: 11px; color: #64748b;")
        self.lbl_dash_akademik = QLabel("IPK: - | Total SKS: -")
        self.lbl_dash_akademik.setStyleSheet("font-size: 11px; font-weight: 700; color: #0284c7;")
        u_lay.addWidget(self.lbl_dash_user)
        u_lay.addWidget(self.lbl_dash_kp)
        u_lay.addWidget(self.lbl_dash_akademik)
        header.addWidget(user_card)

        # Creator Tag
        dev_badge = QLabel("404Workshop | Dev: Putra Yufen (MEKATRONIKA 23) - @yufenxyz")
        dev_badge.setStyleSheet("color: #be123c; font-size: 11px; font-weight: bold; background: #fff1f2; border: 1px solid #fecdd3; padding: 6px 12px; border-radius: 8px;")
        header.addWidget(dev_badge)

        # Logout Button
        btn_logout = QPushButton("Logout")
        btn_logout.setObjectName("btnSecondary")
        btn_logout.setFixedHeight(38)
        btn_logout.clicked.connect(self.do_logout)
        header.addWidget(btn_logout)

        root_lay.addWidget(header_frame)

        # Tabs
        self.tabs = QTabWidget()
        root_lay.addWidget(self.tabs, stretch=1)

        self.tab_tembak = QWidget()
        self.tab_presets = QWidget()
        self.tab_sppa = QWidget()
        self.tab_presets_ta = QWidget()
        self.tab_jadwal = QWidget()
        self.tab_monitor = QWidget()
        self.tab_about = QWidget()

        self.tabs.addTab(self.tab_tembak, "Logbook KP")
        self.tabs.addTab(self.tab_presets, "Preset KP")
        self.tabs.addTab(self.tab_sppa, "Logbook SPPA")
        self.tabs.addTab(self.tab_presets_ta, "Preset SPPA")
        self.tabs.addTab(self.tab_jadwal, "Jadwal & Presensi")
        self.tabs.addTab(self.tab_monitor, "Monitoring MIS")
        self.tabs.addTab(self.tab_about, "Developer & Kredit")

        self.setup_tab_tembak()
        self.setup_tab_presets()
        self.setup_tab_sppa()
        self.setup_tab_presets_ta()
        self.setup_tab_jadwal()
        self.setup_tab_monitor()
        self.setup_tab_about()

        # Log & Progress Footer
        footer_box = QVBoxLayout()
        footer_box.setSpacing(6)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        footer_box.addWidget(self.progress_bar)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFixedHeight(115)
        self.log_console.setStyleSheet("""
            background-color: #0f172a;
            color: #f8fafc;
            border: 1px solid #334155;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            border-radius: 8px;
            padding: 8px;
        """)
        footer_box.addWidget(self.log_console)

        root_lay.addLayout(footer_box)

    # ---------------- TAB 1: EKSEKUSI TEMBAK ----------------
    def setup_tab_tembak(self):
        layout = QHBoxLayout(self.tab_tembak)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(20)

        # Left Column: Single Day Submit
        box_single = QGroupBox("Tembak Hari Ini / Tanggal Spesifik")
        l_single = QVBoxLayout(box_single)
        l_single.setSpacing(14)

        # Tanggal & Week row
        h_tgl = QHBoxLayout()
        h_tgl.setSpacing(10)
        lbl_t = QLabel("Tanggal:")
        lbl_t.setStyleSheet("font-weight: 600;")
        h_tgl.addWidget(lbl_t)

        self.date_single = QDateEdit()
        self.date_single.setDate(QDate.currentDate())
        self.date_single.setCalendarPopup(True)
        self.date_single.setFixedHeight(38)
        self.date_single.dateChanged.connect(self.on_single_date_changed)
        h_tgl.addWidget(self.date_single, stretch=1)

        self.lbl_week_single = QLabel("Minggu ke-3")
        self.lbl_week_single.setStyleSheet("background-color: #fff1f2; color: #e11d48; border: 1px solid #fecdd3; padding: 8px 12px; border-radius: 8px; font-weight: 800;")
        h_tgl.addWidget(self.lbl_week_single)
        l_single.addLayout(h_tgl)

        # Jam Kerja row
        h_time = QHBoxLayout()
        h_time.setSpacing(10)
        lbl_w = QLabel("Jam Kerja:")
        lbl_w.setStyleSheet("font-weight: 600;")
        h_time.addWidget(lbl_w)

        self.txt_jam_mulai = QLineEdit("08:15")
        self.txt_jam_mulai.setFixedHeight(38)
        self.txt_jam_mulai.setFixedWidth(75)
        h_time.addWidget(self.txt_jam_mulai)

        lbl_sd = QLabel("sd")
        lbl_sd.setStyleSheet("color: #64748b; font-weight: 600;")
        h_time.addWidget(lbl_sd)

        self.txt_jam_selesai = QLineEdit("15:30")
        self.txt_jam_selesai.setFixedHeight(38)
        self.txt_jam_selesai.setFixedWidth(75)
        h_time.addWidget(self.txt_jam_selesai)

        btn_reroll = QPushButton("Acak Jam")
        btn_reroll.setObjectName("btnSecondary")
        btn_reroll.setFixedHeight(38)
        btn_reroll.clicked.connect(self.reroll_single_times)
        h_time.addWidget(btn_reroll)
        l_single.addLayout(h_time)

        # Preset selection
        lbl_k = QLabel("Kegiatan (Pilih Preset atau Ketik Bebas):")
        lbl_k.setStyleSheet("font-weight: 600;")
        l_single.addWidget(lbl_k)

        self.combo_presets_single = QComboBox()
        self.combo_presets_single.setFixedHeight(38)
        self.reload_preset_dropdown()
        self.combo_presets_single.currentIndexChanged.connect(self.on_preset_dropdown_changed)
        l_single.addWidget(self.combo_presets_single)

        self.txt_kegiatan_single = QTextEdit()
        self.txt_kegiatan_single.setFixedHeight(105)
        if self.cfg["presets"]:
            self.txt_kegiatan_single.setPlainText(self.cfg["presets"][0])
        l_single.addWidget(self.txt_kegiatan_single)

        info_fix = QLabel("Matakuliah otomatis diset 'Tidak'. Sanitasi kata SQL aktif otomatis.")
        info_fix.setStyleSheet("color: #64748b; font-size: 11px;")
        l_single.addWidget(info_fix)

        # Modern SaaS Attachment Bar (Zero Emoticons, Clean Light)
        box_file_kp = QFrame()
        box_file_kp.setObjectName("attachmentBox")
        l_fkp = QVBoxLayout(box_file_kp)
        l_fkp.setContentsMargins(10, 8, 10, 8)
        l_fkp.setSpacing(6)

        h_bar_top = QHBoxLayout()
        lbl_att_title = QLabel("Lampiran Berkas (Opsional)")
        lbl_att_title.setStyleSheet("font-size: 11px; font-weight: 700; color: #475569;")
        h_bar_top.addWidget(lbl_att_title)
        h_bar_top.addStretch()

        self.btn_up_kp = QPushButton("Unggah Berkas Saja")
        self.btn_up_kp.setObjectName("btnSecondary")
        self.btn_up_kp.setFixedHeight(24)
        self.btn_up_kp.setStyleSheet("font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 6px;")
        self.btn_up_kp.clicked.connect(lambda: self.do_upload_now("kp"))
        h_bar_top.addWidget(self.btn_up_kp)
        l_fkp.addLayout(h_bar_top)

        h_chips = QHBoxLayout()
        h_chips.setSpacing(8)

        self.chip_pdf_kp = QPushButton("+ Lampirkan PDF Laporan")
        self.chip_pdf_kp.setObjectName("chipBtn")
        self.chip_pdf_kp.setFixedHeight(34)
        self.chip_pdf_kp.clicked.connect(lambda: self.pick_file_dialog("kp", "pdf"))
        h_chips.addWidget(self.chip_pdf_kp, stretch=1)

        self.btn_clear_pdf_kp = QPushButton("X")
        self.btn_clear_pdf_kp.setObjectName("chipClearBtn")
        self.btn_clear_pdf_kp.setFixedSize(24, 24)
        self.btn_clear_pdf_kp.setToolTip("Hapus lampiran PDF")
        self.btn_clear_pdf_kp.clicked.connect(lambda: self.clear_file("kp", "pdf"))
        self.btn_clear_pdf_kp.hide()
        h_chips.addWidget(self.btn_clear_pdf_kp)

        self.chip_jpg_kp = QPushButton("+ Lampirkan Foto")
        self.chip_jpg_kp.setObjectName("chipBtn")
        self.chip_jpg_kp.setFixedHeight(34)
        self.chip_jpg_kp.clicked.connect(lambda: self.pick_file_dialog("kp", "jpg"))
        h_chips.addWidget(self.chip_jpg_kp, stretch=1)

        self.btn_clear_jpg_kp = QPushButton("X")
        self.btn_clear_jpg_kp.setObjectName("chipClearBtn")
        self.btn_clear_jpg_kp.setFixedSize(24, 24)
        self.btn_clear_jpg_kp.setToolTip("Hapus lampiran Foto")
        self.btn_clear_jpg_kp.clicked.connect(lambda: self.clear_file("kp", "jpg"))
        self.btn_clear_jpg_kp.hide()
        h_chips.addWidget(self.btn_clear_jpg_kp)

        l_fkp.addLayout(h_chips)
        l_single.addWidget(box_file_kp)

        l_single.addStretch()

        self.btn_submit_single = QPushButton("TEMBAK KE MIS PENS")
        self.btn_submit_single.setFixedHeight(46)
        self.btn_submit_single.setStyleSheet("font-size: 14px; font-weight: 800; border-radius: 8px;")
        self.btn_submit_single.clicked.connect(self.do_submit_single)
        l_single.addWidget(self.btn_submit_single)

        layout.addWidget(box_single, stretch=1)

        # Right Column: Batch Range Submit
        box_batch = QGroupBox("Tembak Rentang Tanggal (Batch Auto-Fill)")
        l_batch = QVBoxLayout(box_batch)
        l_batch.setSpacing(14)

        desc_b = QLabel("Otomatis isi hari kerja sekaligus (Senin - Jumat) dengan jam acak:")
        desc_b.setStyleSheet("color: #64748b;")
        l_batch.addWidget(desc_b)

        h_range = QHBoxLayout()
        h_range.setSpacing(10)
        lbl_dr = QLabel("Dari:")
        lbl_dr.setStyleSheet("font-weight: 600;")
        h_range.addWidget(lbl_dr)

        self.date_batch_start = QDateEdit()
        self.date_batch_start.setDate(QDate.currentDate().addDays(-7))
        self.date_batch_start.setCalendarPopup(True)
        self.date_batch_start.setFixedHeight(38)
        h_range.addWidget(self.date_batch_start)

        lbl_sp = QLabel("Sampai:")
        lbl_sp.setStyleSheet("font-weight: 600;")
        h_range.addWidget(lbl_sp)

        self.date_batch_end = QDateEdit()
        self.date_batch_end.setDate(QDate.currentDate())
        self.date_batch_end.setCalendarPopup(True)
        self.date_batch_end.setFixedHeight(38)
        h_range.addWidget(self.date_batch_end)
        l_batch.addLayout(h_range)

        self.chk_skip_weekend = QCheckBox("Lewati Hari Libur (Hanya Senin - Jumat)")
        self.chk_skip_weekend.setChecked(True)
        self.chk_skip_weekend.setStyleSheet("font-weight: 600; color: #334155;")
        l_batch.addWidget(self.chk_skip_weekend)

        lbl_m = QLabel("Mode Pengambilan dari 10 Preset:")
        lbl_m.setStyleSheet("font-weight: 600;")
        l_batch.addWidget(lbl_m)

        self.combo_batch_mode = QComboBox()
        self.combo_batch_mode.setFixedHeight(38)
        self.combo_batch_mode.addItem("Acak Penuh dari 10 Preset", "random")
        self.combo_batch_mode.addItem("Berurutan (Slot 1, Slot 2, dst bergantian)", "sequence")
        l_batch.addWidget(self.combo_batch_mode)

        # Batch Preview Box
        box_batch_preview = QFrame()
        box_batch_preview.setObjectName("batchPreviewBox")
        l_prev = QVBoxLayout(box_batch_preview)
        self.lbl_batch_summary = QLabel("Menghitung estimasi hari kerja...")
        self.lbl_batch_summary.setStyleSheet("color: #e11d48; font-size: 13px; font-weight: 800;")
        l_prev.addWidget(self.lbl_batch_summary)
        l_batch.addWidget(box_batch_preview)

        l_batch.addStretch()

        # Create submit batch button before connecting signals
        self.btn_submit_batch = QPushButton("MULAI BATCH TEMBAK OTOMATIS")
        self.btn_submit_batch.setFixedHeight(46)
        self.btn_submit_batch.setObjectName("btnSuccess")
        self.btn_submit_batch.setStyleSheet("font-size: 14px; font-weight: 800; border-radius: 8px;")
        self.btn_submit_batch.clicked.connect(self.do_submit_batch)
        l_batch.addWidget(self.btn_submit_batch)

        self.date_batch_start.dateChanged.connect(self.update_batch_summary)
        self.date_batch_end.dateChanged.connect(self.update_batch_summary)
        self.chk_skip_weekend.stateChanged.connect(self.update_batch_summary)
        self.update_batch_summary()

        layout.addWidget(box_batch, stretch=1)

    # ---------------- TAB 2: 10 PRESET KEGIATAN ----------------
    def setup_tab_presets(self):
        layout = QVBoxLayout(self.tab_presets)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        top_bar = QHBoxLayout()
        lbl_tpl = QLabel("Muat Template Kegiatan:")
        lbl_tpl.setStyleSheet("font-weight: 700; color: #0f172a;")
        top_bar.addWidget(lbl_tpl)
        
        for name in PRESET_TEMPLATES.keys():
            btn = QPushButton(name)
            btn.setObjectName("btnSecondary")
            btn.setFixedHeight(36)
            btn.clicked.connect(lambda chk, n=name: self.apply_template(n))
            top_bar.addWidget(btn)
        
        top_bar.addStretch()
        btn_save = QPushButton("Simpan Semua Preset")
        btn_save.setObjectName("btnSuccess")
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self.save_presets_from_ui)
        top_bar.addWidget(btn_save)
        layout.addLayout(top_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 10px; background-color: #ffffff;")

        container = QWidget()
        container.setStyleSheet("background-color: #ffffff;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(12, 12, 12, 12)
        c_layout.setSpacing(8)

        self.preset_inputs = []
        for i in range(10):
            row_box = QFrame()
            row_box.setObjectName("slotRow")
            r_lay = QHBoxLayout(row_box)
            r_lay.setContentsMargins(8, 6, 8, 6)

            lbl_num = QLabel(f"Slot {i+1:02d}:")
            lbl_num.setStyleSheet("color: #e11d48; font-weight: 800; min-width: 58px;")
            r_lay.addWidget(lbl_num)

            inp = QLineEdit()
            inp.setFixedHeight(34)
            val = self.cfg["presets"][i] if i < len(self.cfg["presets"]) else ""
            inp.setText(val)
            inp.setPlaceholderText(f"Tulis uraian kegiatan Slot {i+1}...")
            r_lay.addWidget(inp)
            self.preset_inputs.append(inp)

            c_layout.addWidget(row_box)

        scroll.setWidget(container)
        layout.addWidget(scroll)

    # ---------------- TAB 5: JADWAL & PRESENSI ----------------
    def setup_tab_jadwal(self):
        layout = QVBoxLayout(self.tab_jadwal)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Top control bar
        top_bar = QHBoxLayout()
        lbl_info = QLabel("Jadwal Kuliah & Rekap Kehadiran Presensi Mahasiswa")
        lbl_info.setStyleSheet("font-weight: 800; font-size: 15px; color: #0f172a;")
        top_bar.addWidget(lbl_info)
        top_bar.addStretch()

        self.btn_refresh_academic = QPushButton("Tarik Data dari Portal MIS")
        self.btn_refresh_academic.setObjectName("btnSecondary")
        self.btn_refresh_academic.setFixedHeight(36)
        self.btn_refresh_academic.clicked.connect(self.do_fetch_academic)
        top_bar.addWidget(self.btn_refresh_academic)
        layout.addLayout(top_bar)

        splitter = QSplitter(Qt.Vertical)

        # Section 1: Jadwal Kuliah Mingguan
        box_jadwal = QGroupBox("Jadwal Kuliah Mingguan (Semester Aktif)")
        l_j = QVBoxLayout(box_jadwal)
        self.table_jadwal = QTableWidget()
        self.table_jadwal.setColumnCount(5)
        self.table_jadwal.setHorizontalHeaderLabels(["Hari", "Jam Kuliah", "Mata Kuliah", "Dosen Pengajar", "Ruang"])
        self.table_jadwal.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_jadwal.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_jadwal.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_jadwal.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_jadwal.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_jadwal.verticalHeader().setVisible(False)
        l_j.addWidget(self.table_jadwal)
        splitter.addWidget(box_jadwal)

        # Section 2: Presensi & Kehadiran
        box_presensi = QGroupBox("Rekap Presensi & Batas Minimal Kehadiran (Min. 85%)")
        l_p = QVBoxLayout(box_presensi)
        self.table_presensi = QTableWidget()
        self.table_presensi.setColumnCount(4)
        self.table_presensi.setHorizontalHeaderLabels(["Kode MK", "Mata Kuliah", "Kehadiran (%)", "Status Kelayakan"])
        self.table_presensi.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_presensi.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_presensi.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_presensi.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_presensi.verticalHeader().setVisible(False)
        l_p.addWidget(self.table_presensi)
        splitter.addWidget(box_presensi)

        layout.addWidget(splitter, stretch=1)

    # ---------------- TAB 6: MONITORING MIS PENS ----------------
    def setup_tab_monitor(self):
        layout = QVBoxLayout(self.tab_monitor)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)

        lbl_cat = QLabel("Kategori:")
        lbl_cat.setStyleSheet("font-weight: 700; color: #0f172a;")
        ctrl.addWidget(lbl_cat)

        self.combo_monitor_mode = QComboBox()
        self.combo_monitor_mode.setFixedHeight(38)
        self.combo_monitor_mode.addItem("Kerja Praktek (KP)", "kp")
        self.combo_monitor_mode.addItem("Proyek Akhir (SPPA)", "sppa")
        self.combo_monitor_mode.currentIndexChanged.connect(self.do_fetch_entries)
        ctrl.addWidget(self.combo_monitor_mode)

        lbl_wk = QLabel("Minggu Ke:")
        lbl_wk.setStyleSheet("font-weight: 700; color: #0f172a;")
        ctrl.addWidget(lbl_wk)

        self.combo_view_week = QComboBox()
        self.combo_view_week.setFixedHeight(38)
        for i in range(1, 25):
            self.combo_view_week.addItem(f"Minggu {i}", i)
        self.combo_view_week.setCurrentIndex(2)
        self.combo_view_week.currentIndexChanged.connect(self.do_fetch_entries)
        ctrl.addWidget(self.combo_view_week)

        btn_refresh = QPushButton("Tarik Data Web PENS")
        btn_refresh.setFixedHeight(38)
        btn_refresh.clicked.connect(self.do_fetch_entries)
        ctrl.addWidget(btn_refresh)
        ctrl.addStretch()

        layout.addLayout(ctrl)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["No", "Tanggal", "Jam Mulai", "Jam Selesai", "Kegiatan"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    # ---------------- TAB 4: DEVELOPER DAN KREDIT ----------------
    def setup_tab_about(self):
        layout = QVBoxLayout(self.tab_about)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setAlignment(Qt.AlignCenter)

        box = QFrame()
        box.setObjectName("aboutCard")
        box.setFixedWidth(660)
        b_lay = QVBoxLayout(box)
        b_lay.setSpacing(14)

        # Logo in About
        top_a = QHBoxLayout()
        l_about = QLabel()
        logo_path = resource_path("logo_login.png")
        if os.path.exists(logo_path):
            l_about.setPixmap(QPixmap(logo_path))
        top_a.addWidget(l_about)
        top_a.addStretch()
        b_lay.addLayout(top_a)

        t_title = QLabel("PENS Companion by 404Workshop")
        t_title.setStyleSheet("font-size: 22px; font-weight: 900; color: #0f172a;")
        b_lay.addWidget(t_title)

        t_desc = QLabel("Aplikasi pendamping dan otomatisasi terpadu mahasiswa Politeknik Elektronika Negeri Surabaya (PENS) untuk pengisian logbook Kerja Praktek (KP), Seminar/Progres Proyek Akhir (SPPA/PA), jadwal kuliah, presensi kehadiran, transkrip nilai, dan upload berkas lampiran langsung ke database Online MIS PENS.")
        t_desc.setStyleSheet("font-size: 13px; color: #64748b; line-height: 1.5;")
        t_desc.setWordWrap(True)
        b_lay.addWidget(t_desc)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("border-top: 1px solid #e2e8f0; margin: 4px 0;")
        b_lay.addWidget(sep)

        # Developer Info Box
        dev_card = QFrame()
        dev_card.setObjectName("creditBox")
        d_lay = QVBoxLayout(dev_card)
        d_lay.setSpacing(4)

        d1 = QLabel("DEVELOPER AND WORKSHOP")
        d1.setStyleSheet("font-size: 11px; font-weight: 800; color: #be123c; letter-spacing: 0.5px;")
        d_lay.addWidget(d1)

        d2 = QLabel("Mohammad Putra Maulana Yufen (404Workshop)")
        d2.setStyleSheet("font-size: 18px; font-weight: 900; color: #0f172a;")
        d_lay.addWidget(d2)

        d3 = QLabel("MEKATRONIKA 23 - Politeknik Elektronika Negeri Surabaya")
        d3.setStyleSheet("font-size: 13px; color: #475569; font-weight: 600;")
        d_lay.addWidget(d3)

        d4 = QLabel("Instagram: @yufenxyz | GitHub: yufendev")
        d4.setStyleSheet("font-size: 14px; font-weight: 800; color: #e11d48; margin-top: 4px;")
        d_lay.addWidget(d4)

        b_lay.addWidget(dev_card)

        # Update Info Box (v3.0.0)
        upd_card = QFrame()
        upd_card.setStyleSheet("background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px;")
        u_box = QVBoxLayout(upd_card)
        u_box.setSpacing(4)

        u_title = QLabel("INFO UPDATE // v3.0.0 (COMPANION RELEASE)")
        u_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #0284c7; letter-spacing: 0.5px;")
        u_box.addWidget(u_title)

        u_list = QLabel(
            "• Rebranding resmi: PENS Companion by 404Workshop (Clean Light SaaS)\n"
            "• Logbook SPPA/PPA/PA: Tembak single & batch hari kerja, kalkulasi minggu otomatis\n"
            "• Preset 10 Slot SPPA: Robotika/Mekatronika, Software/IoT, Umum Teknik\n"
            "• Modul Akademik: Auto-scrape Transkrip (IPK, SKS, Dosen Wali), Jadwal & Presensi (%)\n"
            "• Direct File Uploader: Unggah PDF Laporan & Foto Dokumentasi JPG ke MIS PENS\n"
            "• Multi-Path Config Persistence: Simpan akun & preset permanen (AppData & portable EXE)\n"
            "• Full Client-Side Security: Kredensial lokal, HTTPS langsung ke server PENS, bebas telemetry"
        )
        u_list.setStyleSheet("font-size: 12px; color: #334155; line-height: 1.5;")
        u_list.setWordWrap(True)
        u_box.addWidget(u_list)

        b_lay.addWidget(upd_card)

        info_sec = QLabel("Keamanan: Kredensial akun CAS hanya disimpan secara lokal di laptop pribadimu. Data dikirim langsung melalui koneksi terenkripsi HTTPS ke server online.mis.pens.ac.id.")
        info_sec.setStyleSheet("font-size: 11px; color: #64748b; line-height: 1.4;")
        info_sec.setWordWrap(True)
        b_lay.addWidget(info_sec)

        layout.addWidget(box)

    # ---------------- TAB LOGBOOK SPPA ----------------
    def setup_tab_sppa(self):
        layout = QHBoxLayout(self.tab_sppa)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(20)

        # ---- LEFT: Single Day ----
        box_single = QGroupBox("Tembak Hari Ini / Tanggal Spesifik (SPPA)")
        l_single = QVBoxLayout(box_single)
        l_single.setSpacing(14)

        self.lbl_judul_pa = QLabel("Judul PA: (login dulu untuk muat data)")
        self.lbl_judul_pa.setStyleSheet("font-size: 11px; color: #7c3aed; font-weight: 600; background: #f5f3ff; border: 1px solid #ddd6fe; padding: 6px 10px; border-radius: 8px;")
        self.lbl_judul_pa.setWordWrap(True)
        l_single.addWidget(self.lbl_judul_pa)

        # Tanggal & Week
        h_tgl = QHBoxLayout(); h_tgl.setSpacing(10)
        lbl_t = QLabel("Tanggal:"); lbl_t.setStyleSheet("font-weight: 600;")
        h_tgl.addWidget(lbl_t)
        self.date_single_ta = QDateEdit()
        self.date_single_ta.setDate(QDate.currentDate())
        self.date_single_ta.setCalendarPopup(True)
        self.date_single_ta.setFixedHeight(38)
        self.date_single_ta.dateChanged.connect(self.on_single_date_ta_changed)
        h_tgl.addWidget(self.date_single_ta, stretch=1)
        self.lbl_week_single_ta = QLabel("Minggu ke-1")
        self.lbl_week_single_ta.setStyleSheet("background-color: #f5f3ff; color: #7c3aed; border: 1px solid #ddd6fe; padding: 8px 12px; border-radius: 8px; font-weight: 800;")
        h_tgl.addWidget(self.lbl_week_single_ta)
        l_single.addLayout(h_tgl)

        # Jam
        h_time = QHBoxLayout(); h_time.setSpacing(10)
        lbl_w = QLabel("Jam Kerja:"); lbl_w.setStyleSheet("font-weight: 600;")
        h_time.addWidget(lbl_w)
        self.txt_jam_mulai_ta = QLineEdit("08:15")
        self.txt_jam_mulai_ta.setFixedHeight(38); self.txt_jam_mulai_ta.setFixedWidth(75)
        h_time.addWidget(self.txt_jam_mulai_ta)
        lbl_sd = QLabel("sd"); lbl_sd.setStyleSheet("color: #64748b; font-weight: 600;")
        h_time.addWidget(lbl_sd)
        self.txt_jam_selesai_ta = QLineEdit("15:30")
        self.txt_jam_selesai_ta.setFixedHeight(38); self.txt_jam_selesai_ta.setFixedWidth(75)
        h_time.addWidget(self.txt_jam_selesai_ta)
        btn_reroll_ta = QPushButton("Acak Jam")
        btn_reroll_ta.setObjectName("btnSecondary"); btn_reroll_ta.setFixedHeight(38)
        btn_reroll_ta.clicked.connect(self.reroll_ta_times)
        h_time.addWidget(btn_reroll_ta)
        l_single.addLayout(h_time)

        # Preset dropdown
        lbl_k = QLabel("Kegiatan (Pilih Preset atau Ketik Bebas):"); lbl_k.setStyleSheet("font-weight: 600;")
        l_single.addWidget(lbl_k)
        self.combo_presets_ta_single = QComboBox()
        self.combo_presets_ta_single.setFixedHeight(38)
        self.reload_preset_ta_dropdown()
        self.combo_presets_ta_single.currentIndexChanged.connect(self.on_preset_ta_dropdown_changed)
        l_single.addWidget(self.combo_presets_ta_single)
        self.txt_kegiatan_ta = QTextEdit()
        self.txt_kegiatan_ta.setFixedHeight(105)
        if self.cfg.get("presets_ta"):
            self.txt_kegiatan_ta.setPlainText(self.cfg["presets_ta"][0])
        l_single.addWidget(self.txt_kegiatan_ta)

        info_fix = QLabel("Format tanggal otomatis d-m-Y (sesuai form SPPA). Sanitasi kata SQL aktif.")
        info_fix.setStyleSheet("color: #64748b; font-size: 11px;")
        l_single.addWidget(info_fix)

        # Modern SaaS Attachment Bar SPPA (Zero Emoticons, Clean Light)
        box_file_ta = QFrame()
        box_file_ta.setObjectName("attachmentBox")
        l_fta = QVBoxLayout(box_file_ta)
        l_fta.setContentsMargins(10, 8, 10, 8)
        l_fta.setSpacing(6)

        h_bar_ta_top = QHBoxLayout()
        lbl_att_ta_title = QLabel("Lampiran Berkas SPPA (Opsional)")
        lbl_att_ta_title.setStyleSheet("font-size: 11px; font-weight: 700; color: #475569;")
        h_bar_ta_top.addWidget(lbl_att_ta_title)
        h_bar_ta_top.addStretch()

        self.btn_up_ta = QPushButton("Unggah Berkas Saja")
        self.btn_up_ta.setObjectName("btnSecondary")
        self.btn_up_ta.setFixedHeight(24)
        self.btn_up_ta.setStyleSheet("font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 6px; color: #7c3aed;")
        self.btn_up_ta.clicked.connect(lambda: self.do_upload_now("ta"))
        h_bar_ta_top.addWidget(self.btn_up_ta)
        l_fta.addLayout(h_bar_ta_top)

        h_chips_ta = QHBoxLayout()
        h_chips_ta.setSpacing(8)

        self.chip_pdf_ta = QPushButton("+ Lampirkan PDF Laporan")
        self.chip_pdf_ta.setObjectName("chipBtn")
        self.chip_pdf_ta.setFixedHeight(34)
        self.chip_pdf_ta.clicked.connect(lambda: self.pick_file_dialog("ta", "pdf"))
        h_chips_ta.addWidget(self.chip_pdf_ta, stretch=1)

        self.btn_clear_pdf_ta = QPushButton("X")
        self.btn_clear_pdf_ta.setObjectName("chipClearBtn")
        self.btn_clear_pdf_ta.setFixedSize(24, 24)
        self.btn_clear_pdf_ta.setToolTip("Hapus lampiran PDF")
        self.btn_clear_pdf_ta.clicked.connect(lambda: self.clear_file("ta", "pdf"))
        self.btn_clear_pdf_ta.hide()
        h_chips_ta.addWidget(self.btn_clear_pdf_ta)

        self.chip_jpg_ta = QPushButton("+ Lampirkan Foto")
        self.chip_jpg_ta.setObjectName("chipBtn")
        self.chip_jpg_ta.setFixedHeight(34)
        self.chip_jpg_ta.clicked.connect(lambda: self.pick_file_dialog("ta", "jpg"))
        h_chips_ta.addWidget(self.chip_jpg_ta, stretch=1)

        self.btn_clear_jpg_ta = QPushButton("X")
        self.btn_clear_jpg_ta.setObjectName("chipClearBtn")
        self.btn_clear_jpg_ta.setFixedSize(24, 24)
        self.btn_clear_jpg_ta.setToolTip("Hapus lampiran Foto")
        self.btn_clear_jpg_ta.clicked.connect(lambda: self.clear_file("ta", "jpg"))
        self.btn_clear_jpg_ta.hide()
        h_chips_ta.addWidget(self.btn_clear_jpg_ta)

        l_fta.addLayout(h_chips_ta)
        l_single.addWidget(box_file_ta)

        l_single.addStretch()

        self.btn_submit_ta_single = QPushButton("TEMBAK KE LOGBOOK SPPA")
        self.btn_submit_ta_single.setFixedHeight(46)
        self.btn_submit_ta_single.setStyleSheet(
            "font-size: 14px; font-weight: 800; border-radius: 8px;"
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7c3aed,stop:1 #a78bfa); color: #fff;")
        self.btn_submit_ta_single.clicked.connect(self.do_submit_ta_single)
        l_single.addWidget(self.btn_submit_ta_single)
        layout.addWidget(box_single, stretch=1)

        # ---- RIGHT: Batch ----
        box_batch = QGroupBox("Tembak Rentang Tanggal SPPA (Batch Auto-Fill)")
        l_batch = QVBoxLayout(box_batch); l_batch.setSpacing(14)

        desc_b = QLabel("Otomatis isi hari kerja SPPA (Senin-Jumat) dengan jam acak:")
        desc_b.setStyleSheet("color: #64748b;"); l_batch.addWidget(desc_b)

        h_range = QHBoxLayout(); h_range.setSpacing(10)
        lbl_dr = QLabel("Dari:"); lbl_dr.setStyleSheet("font-weight: 600;"); h_range.addWidget(lbl_dr)
        self.date_ta_batch_start = QDateEdit()
        self.date_ta_batch_start.setDate(QDate.currentDate().addDays(-7))
        self.date_ta_batch_start.setCalendarPopup(True); self.date_ta_batch_start.setFixedHeight(38)
        h_range.addWidget(self.date_ta_batch_start)
        lbl_sp = QLabel("Sampai:"); lbl_sp.setStyleSheet("font-weight: 600;"); h_range.addWidget(lbl_sp)
        self.date_ta_batch_end = QDateEdit()
        self.date_ta_batch_end.setDate(QDate.currentDate())
        self.date_ta_batch_end.setCalendarPopup(True); self.date_ta_batch_end.setFixedHeight(38)
        h_range.addWidget(self.date_ta_batch_end)
        l_batch.addLayout(h_range)

        self.chk_skip_weekend_ta = QCheckBox("Lewati Hari Libur (Hanya Senin - Jumat)")
        self.chk_skip_weekend_ta.setChecked(True)
        self.chk_skip_weekend_ta.setStyleSheet("font-weight: 600; color: #334155;")
        l_batch.addWidget(self.chk_skip_weekend_ta)

        lbl_m = QLabel("Mode Pengambilan dari 10 Preset SPPA:"); lbl_m.setStyleSheet("font-weight: 600;")
        l_batch.addWidget(lbl_m)
        self.combo_ta_batch_mode = QComboBox(); self.combo_ta_batch_mode.setFixedHeight(38)
        self.combo_ta_batch_mode.addItem("Acak Penuh dari 10 Preset", "random")
        self.combo_ta_batch_mode.addItem("Berurutan (Slot 1, Slot 2, dst)", "sequence")
        l_batch.addWidget(self.combo_ta_batch_mode)

        box_prev = QFrame(); box_prev.setObjectName("batchPreviewBox")
        l_prev = QVBoxLayout(box_prev)
        self.lbl_ta_batch_summary = QLabel("Menghitung estimasi hari kerja SPPA...")
        self.lbl_ta_batch_summary.setStyleSheet("color: #7c3aed; font-size: 13px; font-weight: 800;")
        l_prev.addWidget(self.lbl_ta_batch_summary)
        l_batch.addWidget(box_prev)
        l_batch.addStretch()

        self.btn_submit_ta_batch = QPushButton("MULAI BATCH TEMBAK SPPA")
        self.btn_submit_ta_batch.setFixedHeight(46)
        self.btn_submit_ta_batch.setStyleSheet(
            "font-size: 14px; font-weight: 800; border-radius: 8px;"
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #059669,stop:1 #10b981); color: #fff;")
        self.btn_submit_ta_batch.clicked.connect(self.do_submit_ta_batch)
        l_batch.addWidget(self.btn_submit_ta_batch)

        self.date_ta_batch_start.dateChanged.connect(self.update_ta_batch_summary)
        self.date_ta_batch_end.dateChanged.connect(self.update_ta_batch_summary)
        self.chk_skip_weekend_ta.stateChanged.connect(self.update_ta_batch_summary)
        self.update_ta_batch_summary()
        layout.addWidget(box_batch, stretch=1)

    # ---------------- TAB PRESET SPPA ----------------
    def setup_tab_presets_ta(self):
        layout = QVBoxLayout(self.tab_presets_ta)
        layout.setContentsMargins(18, 18, 18, 18); layout.setSpacing(14)

        top_bar = QHBoxLayout()
        lbl_tpl = QLabel("Muat Template Kegiatan SPPA/PA:")
        lbl_tpl.setStyleSheet("font-weight: 700; color: #0f172a;"); top_bar.addWidget(lbl_tpl)
        for name in PRESET_TEMPLATES_TA.keys():
            btn = QPushButton(name); btn.setObjectName("btnSecondary"); btn.setFixedHeight(36)
            btn.clicked.connect(lambda chk, n=name: self.apply_template_ta(n))
            top_bar.addWidget(btn)
        top_bar.addStretch()
        btn_save = QPushButton("Simpan Semua Preset SPPA"); btn_save.setObjectName("btnSuccess")
        btn_save.setFixedHeight(38); btn_save.clicked.connect(self.save_presets_ta_from_ui)
        top_bar.addWidget(btn_save)
        layout.addLayout(top_bar)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: 1px solid #e2e8f0; border-radius: 10px; background-color: #ffffff;")
        container = QWidget(); container.setStyleSheet("background-color: #ffffff;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(12, 12, 12, 12); c_layout.setSpacing(8)

        self.preset_ta_inputs = []
        for i in range(10):
            row_box = QFrame(); row_box.setObjectName("slotRow")
            r_lay = QHBoxLayout(row_box); r_lay.setContentsMargins(8, 6, 8, 6)
            lbl_num = QLabel(f"Slot {i+1:02d}:")
            lbl_num.setStyleSheet("color: #7c3aed; font-weight: 800; min-width: 58px;")
            r_lay.addWidget(lbl_num)
            inp = QLineEdit(); inp.setFixedHeight(34)
            val = self.cfg.get("presets_ta", [])[i] if i < len(self.cfg.get("presets_ta", [])) else ""
            inp.setText(val); inp.setPlaceholderText(f"Tulis uraian kegiatan PA Slot {i+1}...")
            r_lay.addWidget(inp); self.preset_ta_inputs.append(inp)
            c_layout.addWidget(row_box)
        scroll.setWidget(container); layout.addWidget(scroll)

    # ---------------- LOGIC SPPA ----------------
    def on_single_date_ta_changed(self, qdate):
        tgl = qdate.toPyDate()
        start = self.user_ctx.get("start_kp_date", date.today())
        w = calculate_week_from_date(tgl, start)
        self.lbl_week_single_ta.setText(f"Minggu ke-{w}")

    def reroll_ta_times(self):
        jm, js = generate_random_times()
        self.txt_jam_mulai_ta.setText(jm); self.txt_jam_selesai_ta.setText(js)
        self.log(f"[INFO] Acak jam SPPA: {jm} - {js}", "#7c3aed")

    def reload_preset_ta_dropdown(self):
        self.combo_presets_ta_single.clear()
        for i, p in enumerate(self.cfg.get("presets_ta", [])):
            short_p = (p[:70] + "...") if len(p) > 70 else p
            self.combo_presets_ta_single.addItem(f"Slot {i+1:02d}: {short_p}", i)

    def on_preset_ta_dropdown_changed(self, idx):
        pts = self.cfg.get("presets_ta", [])
        if 0 <= idx < len(pts):
            self.txt_kegiatan_ta.setPlainText(pts[idx])

    def apply_template_ta(self, name):
        tpl = PRESET_TEMPLATES_TA.get(name, [])
        for i in range(10):
            if i < len(tpl): self.preset_ta_inputs[i].setText(tpl[i])
        self.save_presets_ta_from_ui()
        self.log(f"[SUCCESS] Template SPPA '{name}' dimuat!", "#059669")

    def save_presets_ta_from_ui(self):
        new_presets = [inp.text().strip() for inp in self.preset_ta_inputs if inp.text().strip()]
        while len(new_presets) < 10:
            new_presets.append(f"Melaksanakan kegiatan Proyek Akhir slot {len(new_presets)+1}")
        self.cfg["presets_ta"] = new_presets
        save_config(self.cfg)
        self.reload_preset_ta_dropdown()
        self.log("[SUCCESS] 10 Slot preset SPPA tersimpan.", "#059669")
        QMessageBox.information(self, "Tersimpan", "10 Slot preset kegiatan SPPA berhasil disimpan!")

    def update_ta_batch_summary(self):
        d_start = self.date_ta_batch_start.date().toPyDate()
        d_end = self.date_ta_batch_end.date().toPyDate()
        skip_wk = self.chk_skip_weekend_ta.isChecked()
        if d_start > d_end:
            self.lbl_ta_batch_summary.setText("Tanggal mulai lebih besar dari tanggal selesai!")
            if hasattr(self, 'btn_submit_ta_batch'): self.btn_submit_ta_batch.setEnabled(False)
            return
        curr = d_start; total_days = 0
        while curr <= d_end:
            if not (skip_wk and curr.weekday() >= 5): total_days += 1
            curr += timedelta(days=1)
        self.lbl_ta_batch_summary.setText(f"Target pengisian: {total_days} hari kerja SPPA (jam acak).")
        if hasattr(self, 'btn_submit_ta_batch'): self.btn_submit_ta_batch.setEnabled(total_days > 0)

    def do_submit_ta_single(self):
        tgl_py = self.date_single_ta.date().toPyDate()
        start = self.user_ctx.get("start_kp_date", date.today())
        w = calculate_week_from_date(tgl_py, start)
        jm = self.txt_jam_mulai_ta.text().strip() or "08:00"
        js = self.txt_jam_selesai_ta.text().strip() or "14:00"
        keg = self.txt_kegiatan_ta.toPlainText().strip()
        if not keg:
            QMessageBox.warning(self, "Peringatan", "Kolom kegiatan SPPA tidak boleh kosong!")
            return
        if not self.user_ctx:
            QMessageBox.warning(self, "Peringatan", "Login dulu sebelum tembak SPPA!")
            return
        self.btn_submit_ta_single.setEnabled(False)
        payload = {"tanggal_py": tgl_py, "minggu": w, "jam_mulai": jm, "jam_selesai": js, "kegiatan": keg}
        worker = PensWorker("submit_ta_single", payload=payload, user_context=self.user_ctx)
        self.start_worker(worker)

    def do_submit_ta_batch(self):
        d_start = self.date_ta_batch_start.date().toPyDate()
        d_end = self.date_ta_batch_end.date().toPyDate()
        skip_wk = self.chk_skip_weekend_ta.isChecked()
        if not self.user_ctx:
            QMessageBox.warning(self, "Peringatan", "Login dulu sebelum batch tembak SPPA!"); return
        target_dates = []
        curr = d_start
        while curr <= d_end:
            if not (skip_wk and curr.weekday() >= 5): target_dates.append(curr)
            curr += timedelta(days=1)
        if not target_dates:
            QMessageBox.information(self, "Info", "Tidak ada hari kerja di rentang tersebut."); return
        reply = QMessageBox.question(
            self, "Konfirmasi Batch SPPA",
            f"Tembak otomatis {len(target_dates)} hari ke Logbook SPPA?\nJam & kegiatan diacak dari 10 preset.\n\nLanjutkan?",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes: return
        self.btn_submit_ta_batch.setEnabled(False)
        self.progress_bar.setValue(0)
        mode = self.combo_ta_batch_mode.currentData()
        payload = {
            "dates": target_dates, "mode_pilih": mode,
            "presets": self.cfg.get("presets_ta", []),
            "last_idx": self.cfg.get("last_used_preset_ta_idx", 0)
        }
        worker = PensWorker("submit_ta_batch", payload=payload, user_context=self.user_ctx)
        self.start_worker(worker)

    # ---------------- LOGIC & EVENTS ----------------

    def log(self, msg, color="#0f172a"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_console.append(f'<span style="color:#64748b;">[{ts}]</span> <span style="color:{color};">{msg}</span>')

    def do_fetch_entries(self):
        if not self.user_ctx:
            return
        mode = getattr(self, 'combo_monitor_mode', None)
        is_sppa = mode and mode.currentData() == "sppa"
        week = self.combo_view_week.currentData() or (self.combo_view_week.currentIndex() + 1)
        action = "fetch_ta" if is_sppa else "fetch_entries"
        worker = PensWorker(action, payload={"week": week}, user_context=self.user_ctx)
        self.start_worker(worker)

    def do_fetch_academic(self):
        if not self.user_ctx:
            return
        self.btn_refresh_academic.setEnabled(False)
        worker = PensWorker("fetch_academic", user_context=self.user_ctx)
        self.start_worker(worker)

    def update_academic_ui(self, data):
        self.btn_refresh_academic.setEnabled(True)
        ipk = data.get("ipk", "-")
        sks = data.get("sks", "-")
        wali = data.get("dosen_wali", "-")

        # Update header badge
        self.lbl_dash_akademik.setText(f"IPK: {ipk} | Total SKS: {sks} | Wali: {wali}")

        # Update Jadwal table
        jadwal = data.get("jadwal", {})
        total_rows = sum(len(v) for v in jadwal.values())
        self.table_jadwal.setRowCount(total_rows)

        r_idx = 0
        days_order = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
        for d in days_order:
            if d not in jadwal:
                continue
            for item in jadwal[d]:
                self.table_jadwal.setItem(r_idx, 0, QTableWidgetItem(d))
                self.table_jadwal.item(r_idx, 0).setTextAlignment(Qt.AlignCenter)

                raw_dj = item.get("dosen_jam", "-")
                parts = raw_dj.split(" - ")
                if len(parts) >= 2:
                    dosen = parts[0].strip()
                    jam = parts[1].strip()
                else:
                    dosen = raw_dj
                    jam = "-"
                self.table_jadwal.setItem(r_idx, 1, QTableWidgetItem(jam))
                self.table_jadwal.item(r_idx, 1).setTextAlignment(Qt.AlignCenter)
                self.table_jadwal.setItem(r_idx, 2, QTableWidgetItem(item.get("matkul", "-")))
                self.table_jadwal.setItem(r_idx, 3, QTableWidgetItem(dosen))
                self.table_jadwal.setItem(r_idx, 4, QTableWidgetItem(item.get("ruang", "-")))
                self.table_jadwal.item(r_idx, 4).setTextAlignment(Qt.AlignCenter)
                r_idx += 1

        # Update Presensi table
        presensi = data.get("presensi", [])
        self.table_presensi.setRowCount(len(presensi))
        for r, p in enumerate(presensi):
            self.table_presensi.setItem(r, 0, QTableWidgetItem(p.get("kode", "")))
            self.table_presensi.item(r, 0).setTextAlignment(Qt.AlignCenter)
            self.table_presensi.setItem(r, 1, QTableWidgetItem(p.get("matkul", "")))

            pct_item = QTableWidgetItem(p.get("persen", ""))
            pct_item.setTextAlignment(Qt.AlignCenter)
            pct_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table_presensi.setItem(r, 2, pct_item)

            num = p.get("persen_num", 0)
            mk_lower = p.get("matkul", "").lower()
            if "magang" in mk_lower or "proyek akhir" in mk_lower:
                status_str = "Kegiatan Luar / PA"
                color = QColor("#64748b")
            elif num >= 85:
                status_str = "Aman (Bisa UAS)"
                color = QColor("#059669")
            elif num >= 75:
                status_str = "Waspada"
                color = QColor("#d97706")
            else:
                status_str = "Bahaya (< 85%)"
                color = QColor("#e11d48")

            status_item = QTableWidgetItem(status_str)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(color)
            status_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table_presensi.setItem(r, 3, status_item)

    def pick_file_dialog(self, target, file_type):
        if file_type == "pdf":
            filt = "Dokumen PDF (*.pdf);;Semua File (*.*)"
            title = f"Pilih File Laporan Progres ({target.upper()})"
        else:
            filt = "Gambar JPG (*.jpg *.jpeg);;Semua File (*.*)"
            title = f"Pilih Foto Dokumentasi ({target.upper()})"

        fname, _ = QFileDialog.getOpenFileName(self, title, "", filt)
        if fname:
            base = os.path.basename(fname)
            short = (base[:18] + "...") if len(base) > 21 else base
            if target == "kp":
                if file_type == "pdf":
                    self.selected_file_kp_pdf = fname
                    self.chip_pdf_kp.setText(f"PDF: {short}")
                    self.chip_pdf_kp.setObjectName("chipBtnSelectedKP")
                    self.chip_pdf_kp.setToolTip(fname)
                    self.refresh_style(self.chip_pdf_kp)
                    self.btn_clear_pdf_kp.show()
                else:
                    self.selected_file_kp_jpg = fname
                    self.chip_jpg_kp.setText(f"Foto: {short}")
                    self.chip_jpg_kp.setObjectName("chipBtnSelectedKP")
                    self.chip_jpg_kp.setToolTip(fname)
                    self.refresh_style(self.chip_jpg_kp)
                    self.btn_clear_jpg_kp.show()
            else:
                if file_type == "pdf":
                    self.selected_file_ta_pdf = fname
                    self.chip_pdf_ta.setText(f"PDF: {short}")
                    self.chip_pdf_ta.setObjectName("chipBtnSelectedTA")
                    self.chip_pdf_ta.setToolTip(fname)
                    self.refresh_style(self.chip_pdf_ta)
                    self.btn_clear_pdf_ta.show()
                else:
                    self.selected_file_ta_jpg = fname
                    self.chip_jpg_ta.setText(f"Foto: {short}")
                    self.chip_jpg_ta.setObjectName("chipBtnSelectedTA")
                    self.chip_jpg_ta.setToolTip(fname)
                    self.refresh_style(self.chip_jpg_ta)
                    self.btn_clear_jpg_ta.show()
            self.log(f"[INFO] Berkas dipilih ({target.upper()} - {file_type.upper()}): {os.path.basename(fname)}", "#0284c7")

    def clear_file(self, target, file_type):
        if target == "kp":
            if file_type == "pdf":
                self.selected_file_kp_pdf = ""
                self.chip_pdf_kp.setText("+ Lampirkan PDF Laporan")
                self.chip_pdf_kp.setObjectName("chipBtn")
                self.chip_pdf_kp.setToolTip("")
                self.refresh_style(self.chip_pdf_kp)
                self.btn_clear_pdf_kp.hide()
            else:
                self.selected_file_kp_jpg = ""
                self.chip_jpg_kp.setText("+ Lampirkan Foto")
                self.chip_jpg_kp.setObjectName("chipBtn")
                self.chip_jpg_kp.setToolTip("")
                self.refresh_style(self.chip_jpg_kp)
                self.btn_clear_jpg_kp.hide()
        else:
            if file_type == "pdf":
                self.selected_file_ta_pdf = ""
                self.chip_pdf_ta.setText("+ Lampirkan PDF Laporan")
                self.chip_pdf_ta.setObjectName("chipBtn")
                self.chip_pdf_ta.setToolTip("")
                self.refresh_style(self.chip_pdf_ta)
                self.btn_clear_pdf_ta.hide()
            else:
                self.selected_file_ta_jpg = ""
                self.chip_jpg_ta.setText("+ Lampirkan Foto")
                self.chip_jpg_ta.setObjectName("chipBtn")
                self.chip_jpg_ta.setToolTip("")
                self.refresh_style(self.chip_jpg_ta)
                self.btn_clear_jpg_ta.hide()

    def do_upload_now(self, target):
        if not self.user_ctx:
            QMessageBox.warning(self, "Peringatan", "Silakan login terlebih dahulu!")
            return

        pdf_path = getattr(self, f"selected_file_{target}_pdf", "")
        jpg_path = getattr(self, f"selected_file_{target}_jpg", "")

        if not pdf_path and not jpg_path:
            QMessageBox.information(self, "Info", "Belum ada berkas PDF atau Foto yang dipilih untuk diunggah.")
            return

        if pdf_path:
            worker1 = PensWorker("upload_file", payload={"target": target, "file_path": pdf_path, "file_type": "pdf"}, user_context=self.user_ctx)
            self.start_worker(worker1)

        if jpg_path:
            worker2 = PensWorker("upload_file", payload={"target": target, "file_path": jpg_path, "file_type": "jpg"}, user_context=self.user_ctx)
            self.start_worker(worker2)

    def reroll_single_times(self):
        jm, js = generate_random_times()
        self.txt_jam_mulai.setText(jm)
        self.txt_jam_selesai.setText(js)
        self.log(f"[INFO] Acak jam kerja: {jm} - {js}", "#e11d48")

    def on_single_date_changed(self, qdate):
        tgl = qdate.toPyDate()
        start = self.user_ctx.get("start_kp_date", date(2026, 8, 24))
        w = calculate_week_from_date(tgl, start)
        self.lbl_week_single.setText(f"Minggu ke-{w}")

    def reload_preset_dropdown(self):
        self.combo_presets_single.clear()
        for i, p in enumerate(self.cfg["presets"]):
            short_p = (p[:70] + "...") if len(p) > 70 else p
            self.combo_presets_single.addItem(f"Slot {i+1:02d}: {short_p}", i)

    def on_preset_dropdown_changed(self, idx):
        if 0 <= idx < len(self.cfg["presets"]):
            self.txt_kegiatan_single.setPlainText(self.cfg["presets"][idx])

    def apply_template(self, name):
        tpl = PRESET_TEMPLATES.get(name, [])
        for i in range(10):
            if i < len(tpl):
                self.preset_inputs[i].setText(tpl[i])
        self.save_presets_from_ui()
        self.log(f"[SUCCESS] Berhasil memuat template {name}!", "#059669")

    def save_presets_from_ui(self):
        new_presets = [inp.text().strip() for inp in self.preset_inputs if inp.text().strip()]
        while len(new_presets) < 10:
            new_presets.append(f"Melaksanakan tugas teknis harian slot {len(new_presets)+1}")
        self.cfg["presets"] = new_presets
        save_config(self.cfg)
        self.reload_preset_dropdown()
        self.log("[SUCCESS] 10 Slot preset kegiatan tersimpan.", "#059669")
        QMessageBox.information(self, "Tersimpan", "10 Slot preset kegiatan berhasil disimpan!")

    def do_submit_single(self):
        tgl = self.date_single.date().toString("yyyy-MM-dd")
        start = self.user_ctx.get("start_kp_date", date(2026, 8, 24))
        w = calculate_week_from_date(self.date_single.date().toPyDate(), start)
        jm = self.txt_jam_mulai.text().strip() or "08:00"
        js = self.txt_jam_selesai.text().strip() or "14:00"
        keg = self.txt_kegiatan_single.toPlainText().strip()

        if not keg:
            QMessageBox.warning(self, "Peringatan", "Kolom kegiatan tidak boleh kosong!")
            return

        self.btn_submit_single.setEnabled(False)
        payload = {
            "tanggal": tgl,
            "minggu": w,
            "jam_mulai": jm,
            "jam_selesai": js,
            "kegiatan": keg
        }
        worker = PensWorker("submit_single", payload=payload, user_context=self.user_ctx)
        self.start_worker(worker)

    def update_batch_summary(self):
        d_start = self.date_batch_start.date().toPyDate()
        d_end = self.date_batch_end.date().toPyDate()
        skip_wk = self.chk_skip_weekend.isChecked()

        if d_start > d_end:
            self.lbl_batch_summary.setText("Tanggal mulai lebih besar dari tanggal selesai!")
            if hasattr(self, 'btn_submit_batch'):
                self.btn_submit_batch.setEnabled(False)
            return

        curr = d_start
        total_days = 0
        while curr <= d_end:
            if skip_wk and curr.weekday() >= 5:
                pass
            else:
                total_days += 1
            curr += timedelta(days=1)

        self.lbl_batch_summary.setText(f"Target pengisian: {total_days} hari kerja (Senin-Jumat dengan jam acak).")
        if hasattr(self, 'btn_submit_batch'):
            self.btn_submit_batch.setEnabled(total_days > 0)

    def do_submit_batch(self):
        d_start = self.date_batch_start.date().toPyDate()
        d_end = self.date_batch_end.date().toPyDate()
        skip_wk = self.chk_skip_weekend.isChecked()

        target_dates = []
        curr = d_start
        while curr <= d_end:
            if skip_wk and curr.weekday() >= 5:
                pass
            else:
                target_dates.append(curr)
            curr += timedelta(days=1)

        if not target_dates:
            QMessageBox.information(self, "Info", "Tidak ada hari kerja pada rentang tanggal tersebut.")
            return

        reply = QMessageBox.question(
            self, "Konfirmasi Batch Submit",
            f"Kamu akan menembak otomatis {len(target_dates)} hari kerja ke MIS PENS.\\nJam masuk/pulang dan kegiatan akan diacak dari 10 preset.\\n\\nLanjutkan?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self.btn_submit_batch.setEnabled(False)
        self.progress_bar.setValue(0)
        mode = self.combo_batch_mode.currentData()

        payload = {
            "dates": target_dates,
            "mode_pilih": mode,
            "presets": self.cfg["presets"],
            "last_idx": self.cfg.get("last_used_preset_idx", 0)
        }
        worker = PensWorker("submit_batch", payload=payload, user_context=self.user_ctx)
        self.start_worker(worker)

    def on_progress(self, curr, total):
        pct = int((curr / total) * 100)
        self.progress_bar.setValue(pct)

    def on_worker_finished(self, success, action, data):
        self.btn_submit_single.setEnabled(True)
        self.btn_submit_batch.setEnabled(True)
        if hasattr(self, 'btn_submit_ta_single'):
            self.btn_submit_ta_single.setEnabled(True)
        if hasattr(self, 'btn_submit_ta_batch'):
            self.btn_submit_ta_batch.setEnabled(True)

        if action in ("fetch_entries", "fetch_ta"):
            if success:
                entries = data.get("entries", [])
                self.table.setRowCount(len(entries))
                for row, e in enumerate(entries):
                    self.table.setItem(row, 0, QTableWidgetItem(str(e["no"])))
                    self.table.setItem(row, 1, QTableWidgetItem(e["tanggal"]))
                    self.table.setItem(row, 2, QTableWidgetItem(e["jam_mulai"]))
                    self.table.setItem(row, 3, QTableWidgetItem(e["jam_selesai"]))
                    self.table.setItem(row, 4, QTableWidgetItem(e["kegiatan"]))
                    for col in range(4):
                        self.table.item(row, col).setTextAlignment(Qt.AlignCenter)

        elif action == "submit_single":
            if success:
                QMessageBox.information(self, "Sukses", "Entri logbook berhasil ditembak dan tersimpan di MIS PENS!")
                if self.selected_file_kp_pdf or self.selected_file_kp_jpg:
                    self.do_upload_now("kp")
                self.reroll_single_times()
                self.do_fetch_entries()
            else:
                QMessageBox.critical(self, "Gagal", f"Gagal submit ke PENS: {data}")

        elif action == "submit_batch":
            if success:
                self.progress_bar.setValue(100)
                self.cfg["last_used_preset_idx"] = data.get("last_idx", 0)
                save_config(self.cfg)
                QMessageBox.information(self, "Batch Selesai", f"Selesai! {data.get('success_count')} entri berhasil ditembak ke MIS PENS!")
                self.do_fetch_entries()

        elif action == "submit_ta_single":
            if success:
                QMessageBox.information(self, "Sukses SPPA", f"Entri logbook SPPA berhasil tersimpan di MIS PENS!\n{data.get('tanggal', '')}")
                if self.selected_file_ta_pdf or self.selected_file_ta_jpg:
                    self.do_upload_now("ta")
                self.reroll_ta_times()
                self.do_fetch_entries()
            else:
                QMessageBox.critical(self, "Gagal SPPA", f"Gagal submit ke SPPA: {data}")

        elif action == "submit_ta_batch":
            if success:
                self.progress_bar.setValue(100)
                self.cfg["last_used_preset_ta_idx"] = data.get("last_idx", 0)
                save_config(self.cfg)
                QMessageBox.information(self, "Batch SPPA Selesai", f"Selesai! {data.get('success_count')} entri SPPA berhasil ditembak ke MIS PENS!")
                self.do_fetch_entries()

        elif action == "fetch_academic":
            if success:
                self.update_academic_ui(data)

        elif action == "upload_file":
            if success:
                fn = data.get("filename", "berkas")
                tgt = data.get("target", "KP").upper()
                ftype = data.get("file_type", "pdf")
                self.clear_file(data.get("target", "kp"), ftype)
                QMessageBox.information(self, "Unggah Berhasil", f"Berkas '{fn}' berhasil terunggah ke portal MIS PENS ({tgt})!")
            else:
                QMessageBox.critical(self, "Unggah Gagal", f"Gagal mengunggah berkas: {data}")


def excepthook(type, value, tb):
    import traceback
    err_str = "".join(traceback.format_exception(type, value, tb))
    print(err_str, file=sys.stderr)
    try:
        log_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
        log_path = os.path.join(log_dir, "crash_error.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] Uncaught Exception:\n{err_str}\n\n")
    except Exception:
        pass

def main():
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
