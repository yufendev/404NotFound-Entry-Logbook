package com.notfound.logbookpens;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import java.util.ArrayList;
import java.util.List;

public class PresetsFragment extends Fragment {

    private LinearLayout slotsContainer;
    private Button btnSavePresets;
    private final List<EditText> inputFields = new ArrayList<>();

    private static final String[] DEFAULT_SLOTS = {
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
    };

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_presets, container, false);

        slotsContainer = v.findViewById(R.id.slotsContainer);
        btnSavePresets = v.findViewById(R.id.btnSavePresets);

        loadSlotsUI();

        btnSavePresets.setOnClickListener(view -> saveSlots());

        return v;
    }

    private void loadSlotsUI() {
        slotsContainer.removeAllViews();
        inputFields.clear();

        SharedPreferences prefs = requireContext().getSharedPreferences("404_presets", Context.MODE_PRIVATE);

        for (int i = 0; i < 10; i++) {
            LinearLayout row = new LinearLayout(requireContext());
            row.setOrientation(LinearLayout.VERTICAL);
            row.setBackgroundResource(R.drawable.card_white);
            row.setPadding(20, 16, 20, 16);
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            lp.setMargins(0, 0, 0, 16);
            row.setLayoutParams(lp);

            TextView lbl = new TextView(requireContext());
            lbl.setText(String.format("Slot %02d", i + 1));
            lbl.setTextColor(getResources().getColor(R.color.primary, null));
            lbl.setTextSize(13);
            lbl.setTypeface(null, android.graphics.Typeface.BOLD);
            row.addView(lbl);

            EditText et = new EditText(requireContext());
            String saved = prefs.getString("preset_" + i, DEFAULT_SLOTS[i]);
            et.setText(saved);
            et.setTextSize(13);
            et.setBackground(null);
            et.setPadding(0, 8, 0, 4);
            row.addView(et);

            inputFields.add(et);
            slotsContainer.addView(row);
        }
    }

    private void saveSlots() {
        SharedPreferences.Editor ed = requireContext().getSharedPreferences("404_presets", Context.MODE_PRIVATE).edit();
        for (int i = 0; i < inputFields.size(); i++) {
            ed.putString("preset_" + i, inputFields.get(i).getText().toString().trim());
        }
        ed.apply();
        Toast.makeText(requireContext(), "10 Slot preset berhasil disimpan!", Toast.LENGTH_SHORT).show();
    }
}
