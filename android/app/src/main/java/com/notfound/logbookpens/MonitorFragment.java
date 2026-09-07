package com.notfound.logbookpens;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class MonitorFragment extends Fragment {

    private Spinner spinnerWeek;
    private Button btnRefreshEntries;
    private LinearLayout entriesContainer;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_monitor, container, false);

        spinnerWeek = v.findViewById(R.id.spinnerWeek);
        btnRefreshEntries = v.findViewById(R.id.btnRefreshEntries);
        entriesContainer = v.findViewById(R.id.entriesContainer);

        List<String> weeks = new ArrayList<>();
        for (int i = 1; i <= 24; i++) {
            weeks.add("Minggu " + i);
        }
        ArrayAdapter<String> adapter = new ArrayAdapter<>(requireContext(), android.R.layout.simple_spinner_dropdown_item, weeks);
        spinnerWeek.setAdapter(adapter);

        NetworkManager nm = NetworkManager.getInstance();
        int defWeek = Math.min(Math.max(nm.currentWeek - 1, 0), 23);
        spinnerWeek.setSelection(defWeek);

        btnRefreshEntries.setOnClickListener(view -> loadData());

        loadData();

        return v;
    }

    private void loadData() {
        int selectedWeek = spinnerWeek.getSelectedItemPosition() + 1;
        btnRefreshEntries.setEnabled(false);
        btnRefreshEntries.setText("Memuat...");

        new Thread(() -> {
            List<Map<String, String>> data = NetworkManager.getInstance().fetchEntries(selectedWeek);
            requireActivity().runOnUiThread(() -> {
                btnRefreshEntries.setEnabled(true);
                btnRefreshEntries.setText("Tarik Data");

                entriesContainer.removeAllViews();
                if (data.isEmpty()) {
                    TextView empty = new TextView(requireContext());
                    empty.setText("Belum ada data logbook untuk Minggu " + selectedWeek);
                    empty.setGravity(android.view.Gravity.CENTER);
                    empty.setPadding(0, 40, 0, 0);
                    empty.setTextColor(getResources().getColor(R.color.text_secondary, null));
                    entriesContainer.addView(empty);
                } else {
                    for (Map<String, String> item : data) {
                        LinearLayout card = new LinearLayout(requireContext());
                        card.setOrientation(LinearLayout.VERTICAL);
                        card.setBackgroundResource(R.drawable.card_white);
                        card.setPadding(20, 16, 20, 16);
                        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
                        lp.setMargins(0, 0, 0, 12);
                        card.setLayoutParams(lp);

                        TextView tgl = new TextView(requireContext());
                        tgl.setText(item.get("tanggal") + " (" + item.get("jam_mulai") + " - " + item.get("jam_selesai") + ")");
                        tgl.setTextColor(getResources().getColor(R.color.primary, null));
                        tgl.setTextSize(13);
                        tgl.setTypeface(null, android.graphics.Typeface.BOLD);
                        card.addView(tgl);

                        TextView keg = new TextView(requireContext());
                        keg.setText(item.get("kegiatan"));
                        keg.setTextColor(getResources().getColor(R.color.text_primary, null));
                        keg.setTextSize(13);
                        keg.setPadding(0, 6, 0, 0);
                        card.addView(keg);

                        entriesContainer.addView(card);
                    }
                }
            });
        }).start();
    }
}
