package com.notfound.logbookpens;

import android.app.DatePickerDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;
import java.util.Locale;
import java.util.Random;

public class TembakFragment extends Fragment {

    private TextView tvDateDisplay;
    private Button btnPickDate, btnReroll, btnSubmitSingle;
    private EditText etJamMulai, etJamSelesai, etKegiatan;
    private Spinner spinnerPresets;
    private Calendar calendar;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_tembak, container, false);

        tvDateDisplay = v.findViewById(R.id.tvDateDisplay);
        btnPickDate = v.findViewById(R.id.btnPickDate);
        btnReroll = v.findViewById(R.id.btnReroll);
        btnSubmitSingle = v.findViewById(R.id.btnSubmitSingle);
        etJamMulai = v.findViewById(R.id.etJamMulai);
        etJamSelesai = v.findViewById(R.id.etJamSelesai);
        etKegiatan = v.findViewById(R.id.etKegiatan);
        spinnerPresets = v.findViewById(R.id.spinnerPresets);

        calendar = Calendar.getInstance();
        updateDateDisplay();

        btnPickDate.setOnClickListener(view -> {
            new DatePickerDialog(requireContext(), (datePicker, year, month, day) -> {
                calendar.set(Calendar.YEAR, year);
                calendar.set(Calendar.MONTH, month);
                calendar.set(Calendar.DAY_OF_MONTH, day);
                updateDateDisplay();
            }, calendar.get(Calendar.YEAR), calendar.get(Calendar.MONTH), calendar.get(Calendar.DAY_OF_MONTH)).show();
        });

        btnReroll.setOnClickListener(view -> rerollTimes());

        loadPresetsToSpinner();

        btnSubmitSingle.setOnClickListener(view -> doSubmit());

        return v;
    }

    private void updateDateDisplay() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault());
        tvDateDisplay.setText(sdf.format(calendar.getTime()));
    }

    private void rerollTimes() {
        String[] mulaiMin = {"00", "10", "15", "20", "30", "45"};
        String[] selesaiMin = {"00", "10", "15", "20", "30", "45", "50"};
        Random r = new Random();

        int hMulai = 8 + r.nextInt(3); // 8, 9, 10
        String mMulai = (hMulai == 10) ? "00" : mulaiMin[r.nextInt(mulaiMin.length)];
        etJamMulai.setText(String.format(Locale.getDefault(), "%02d:%s", hMulai, mMulai));

        int hSelesai = 14 + r.nextInt(3); // 14, 15, 16
        String mSelesai = (hSelesai == 16) ? "00" : selesaiMin[r.nextInt(selesaiMin.length)];
        etJamSelesai.setText(String.format(Locale.getDefault(), "%02d:%s", hSelesai, mSelesai));
    }

    private void loadPresetsToSpinner() {
        SharedPreferences prefs = requireContext().getSharedPreferences("404_presets", Context.MODE_PRIVATE);
        List<String> list = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            String val = prefs.getString("preset_" + i, "Melaksanakan tugas teknis harian slot " + (i + 1));
            list.add("Slot " + (i + 1) + ": " + (val.length() > 35 ? val.substring(0, 35) + "..." : val));
        }

        ArrayAdapter<String> adapter = new ArrayAdapter<>(requireContext(), android.R.layout.simple_spinner_dropdown_item, list);
        spinnerPresets.setAdapter(adapter);

        spinnerPresets.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(android.widget.AdapterView<?> adapterView, View view, int i, long l) {
                String full = prefs.getString("preset_" + i, "");
                if (!full.isEmpty()) etKegiatan.setText(full);
            }

            @Override
            public void onNothingSelected(android.widget.AdapterView<?> adapterView) {}
        });
    }

    private void doSubmit() {
        String tgl = tvDateDisplay.getText().toString();
        String jMulai = etJamMulai.getText().toString().trim();
        String jSelesai = etJamSelesai.getText().toString().trim();
        String keg = etKegiatan.getText().toString().trim();

        if (keg.isEmpty()) {
            Toast.makeText(requireContext(), "Kolom kegiatan wajib diisi!", Toast.LENGTH_SHORT).show();
            return;
        }

        btnSubmitSingle.setEnabled(false);
        btnSubmitSingle.setText("Menembak ke MIS PENS...");

        new Thread(() -> {
            NetworkManager nm = NetworkManager.getInstance();
            boolean ok = nm.submitLogbook(tgl, nm.currentWeek, jMulai, jSelesai, keg);
            requireActivity().runOnUiThread(() -> {
                btnSubmitSingle.setEnabled(true);
                btnSubmitSingle.setText("TEMBAK KE MIS PENS");
                if (ok) {
                    Toast.makeText(requireContext(), "Logbook berhasil tersimpan di MIS PENS!", Toast.LENGTH_LONG).show();
                    rerollTimes();
                } else {
                    Toast.makeText(requireContext(), "Gagal submit ke MIS PENS!", Toast.LENGTH_LONG).show();
                }
            });
        }).start();
    }
}
