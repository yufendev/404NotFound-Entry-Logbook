package com.notfound.logbookpens;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Random;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import okhttp3.FormBody;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class NetworkManager {

    private static NetworkManager instance;
    private final OkHttpClient client;

    public String currentNetId = "";
    public String currentPassword = "";
    public String studentName = "";
    public String studentNrp = "";
    public String tempatKp = "";
    public String tglKpStr = "";
    public String tahun = "2026";
    public String semester = "1";
    public int currentWeek = 3;
    public String kpDaftar = "0";
    public String mahasiswaId = "0";

    private NetworkManager() {
        // OkHttpClient with cookie jar
        client = new OkHttpClient.Builder()
                .cookieJar(new SimpleCookieJar())
                .followRedirects(true)
                .followSslRedirects(true)
                .build();
    }

    public static synchronized NetworkManager getInstance() {
        if (instance == null) {
            instance = new NetworkManager();
        }
        return instance;
    }

    public static String sanitizePensSql(String input) {
        String cleaned = input;
        cleaned = cleaned.replaceAll("(?i)\\bselect\\b", "memilih");
        cleaned = cleaned.replaceAll("(?i)\\binsert\\b", "memasukkan");
        cleaned = cleaned.replaceAll("(?i)\\bupdate\\b", "memperbarui");
        cleaned = cleaned.replaceAll("(?i)\\bdelete\\b", "menghapus");
        return cleaned.replace("&", "dan");
    }

    public boolean login(String netId, String password) {
        try {
            this.currentNetId = netId;
            this.currentPassword = password;

            // 1. Get CAS login page for LT token
            Request r1 = new Request.Builder()
                    .url("https://login.pens.ac.id/cas/login?service=https%3A%2F%2Fonline.mis.pens.ac.id%2Findex.php%3FLogin%3D1%26halAwal%3D1")
                    .header("User-Agent", "Mozilla/5.0 (Linux; Android 10; Mobile)")
                    .build();
            Response resp1 = client.newCall(r1).execute();
            String html1 = resp1.body() != null ? resp1.body().string() : "";

            Pattern ltPattern = Pattern.compile("name=[\"']lt[\"']\\s+value=[\"']([^\"']+)[\"']");
            Matcher ltMatcher = ltPattern.matcher(html1);
            if (!ltMatcher.find()) return false;
            String lt = ltMatcher.group(1);

            Pattern actionPattern = Pattern.compile("action=[\"']([^\"']+)[\"']");
            Matcher actionMatcher = actionPattern.matcher(html1);
            String action = actionMatcher.find() ? actionMatcher.group(1) : "/cas/login";
            if (!action.startsWith("http")) action = "https://login.pens.ac.id" + action;

            // 2. Submit credentials
            RequestBody formBody = new FormBody.Builder()
                    .add("username", netId)
                    .add("password", password)
                    .add("lt", lt)
                    .add("_eventId", "submit")
                    .add("submit", "LOGIN")
                    .build();

            Request r2 = new Request.Builder()
                    .url(action)
                    .post(formBody)
                    .header("User-Agent", "Mozilla/5.0 (Linux; Android 10; Mobile)")
                    .build();
            Response resp2 = client.newCall(r2).execute();
            String html2 = resp2.body() != null ? resp2.body().string() : "";

            if (!html2.contains("online.mis.pens.ac.id") && !html2.contains("Logout") && !html2.contains("mEntry_Logbook_KP1.php")) {
                return false;
            }

            // Scrape Name & NRP
            Pattern userPattern = Pattern.compile("USER\\s*:\\s*([^(\n\r<]+)\\s*\\(([0-9]+)\\)");
            Matcher userMatcher = userPattern.matcher(html2);
            if (userMatcher.find()) {
                this.studentName = userMatcher.group(1).trim();
                this.studentNrp = userMatcher.group(2).trim();
            } else {
                this.studentName = netId;
                this.studentNrp = "-";
            }

            // 3. Scrape KP info from mEntry_Logbook_KP1.php
            Request r3 = new Request.Builder()
                    .url("https://online.mis.pens.ac.id/mEntry_Logbook_KP1.php")
                    .build();
            Response resp3 = client.newCall(r3).execute();
            String html3 = resp3.body() != null ? resp3.body().string() : "";

            Pattern loadPattern = Pattern.compile("showEntry_Logbook_KP1\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)");
            Matcher loadMatcher = loadPattern.matcher(html3);
            if (loadMatcher.find()) {
                this.tahun = loadMatcher.group(1);
                this.semester = loadMatcher.group(2);
                this.currentWeek = Integer.parseInt(loadMatcher.group(3));
            }

            // 4. Scrape entry details
            Request r4 = new Request.Builder()
                    .url("https://online.mis.pens.ac.id/entry_logbook_kp1.php?valTahun=" + tahun + "&valSemester=" + semester + "&valMinggu=" + currentWeek)
                    .build();
            Response resp4 = client.newCall(r4).execute();
            String html4 = resp4.body() != null ? resp4.body().string() : "";

            Pattern kpPat = Pattern.compile("name=[\"']kp_daftar[\"'][^>]*value=[\"']([^\"']+)[\"']");
            Matcher kpMat = kpPat.matcher(html4);
            if (kpMat.find()) this.kpDaftar = kpMat.group(1);

            Pattern mhsPat = Pattern.compile("name=[\"']mahasiswa[\"'][^>]*value=[\"']([^\"']+)[\"']");
            Matcher mhsMat = mhsPat.matcher(html4);
            if (mhsMat.find()) this.mahasiswaId = mhsMat.group(1);

            Pattern tmpPat = Pattern.compile("Tempat KP\\s*</td>\\s*<td[^>]*>\\s*:\\s*([^<]+)</td>");
            Matcher tmpMat = tmpPat.matcher(html4);
            if (tmpMat.find()) this.tempatKp = tmpMat.group(1).trim();

            Pattern tglPat = Pattern.compile("Tanggal KP\\s*</td>\\s*<td[^>]*>\\s*:\\s*([^<]+)</td>");
            Matcher tglMat = tglPat.matcher(html4);
            if (tglMat.find()) this.tglKpStr = tglMat.group(1).trim();

            return true;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean submitLogbook(String tanggal, int minggu, String jamMulai, String jamSelesai, String kegiatan) {
        try {
            String cleanKegiatan = sanitizePensSql(kegiatan);
            RequestBody formBody = new FormBody.Builder()
                    .add("valnrpMahasiswa", this.studentNrp)
                    .add("valTahun", this.tahun)
                    .add("valSemester", this.semester)
                    .add("valMinggu", String.valueOf(minggu))
                    .add("Simpan", "1")
                    .add("tanggal", tanggal)
                    .add("jam_mulai", jamMulai)
                    .add("jam_selesai", jamSelesai)
                    .add("kegiatan", cleanKegiatan)
                    .add("sesuai_kuliah", "2") // Always Tidak
                    .add("matakuliah", "")
                    .add("kp_daftar", this.kpDaftar)
                    .add("mahasiswa", this.mahasiswaId)
                    .add("Setuju", "1")
                    .add("sid", String.valueOf(Math.random()))
                    .build();

            Request req = new Request.Builder()
                    .url("https://online.mis.pens.ac.id/entry_logbook_kp1.php")
                    .post(formBody)
                    .build();

            Response resp = client.newCall(req).execute();
            return resp.isSuccessful();
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    public List<Map<String, String>> fetchEntries(int week) {
        List<Map<String, String>> list = new ArrayList<>();
        try {
            Request req = new Request.Builder()
                    .url("https://online.mis.pens.ac.id/entry_logbook_kp1.php?valTahun=" + tahun + "&valSemester=" + semester + "&valMinggu=" + week)
                    .build();
            Response resp = client.newCall(req).execute();
            String html = resp.body() != null ? resp.body().string() : "";

            Pattern rowPattern = Pattern.compile("<tr>\\s*<td align=[\"']center[\"']>(\\d+)</td>\\s*<td align=[\"']center[\"']>([^<]+)</td>\\s*<td align=[\"']center[\"']>([^<]+)</td>\\s*<td align=[\"']center[\"']>([^<]+)</td>\\s*<td>([^<]*)</td>");
            Matcher m = rowPattern.matcher(html);
            while (m.find()) {
                Map<String, String> item = new HashMap<>();
                item.put("no", m.group(1));
                item.put("tanggal", m.group(2));
                item.put("jam_mulai", m.group(3));
                item.put("jam_selesai", m.group(4));
                item.put("kegiatan", m.group(5).trim());
                list.add(item);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return list;
    }
}
