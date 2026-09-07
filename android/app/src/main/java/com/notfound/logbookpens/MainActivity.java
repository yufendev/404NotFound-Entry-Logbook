package com.notfound.logbookpens;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;

import com.google.android.material.bottomnavigation.BottomNavigationView;

public class MainActivity extends AppCompatActivity {

    private TextView tvHeaderUser, tvHeaderKp;
    private Button btnLogout;
    private BottomNavigationView bottomNav;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        tvHeaderUser = findViewById(R.id.tvHeaderUser);
        tvHeaderKp = findViewById(R.id.tvHeaderKp);
        btnLogout = findViewById(R.id.btnLogout);
        bottomNav = findViewById(R.id.bottomNav);

        NetworkManager nm = NetworkManager.getInstance();
        tvHeaderUser.setText(nm.studentName + " (" + nm.studentNrp + ")");
        tvHeaderKp.setText(nm.tempatKp.isEmpty() ? "Politeknik Elektronika Negeri Surabaya" : nm.tempatKp);

        btnLogout.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, LoginActivity.class);
            startActivity(intent);
            finish();
        });

        bottomNav.setOnItemSelectedListener(item -> {
            Fragment selected = null;
            int id = item.getItemId();
            if (id == R.id.nav_tembak) {
                selected = new TembakFragment();
            } else if (id == R.id.nav_presets) {
                selected = new PresetsFragment();
            } else if (id == R.id.nav_monitor) {
                selected = new MonitorFragment();
            } else if (id == R.id.nav_about) {
                selected = new AboutFragment();
            }

            if (selected != null) {
                getSupportFragmentManager().beginTransaction()
                        .replace(R.id.fragmentContainer, selected)
                        .commit();
                return true;
            }
            return false;
        });

        // Default to Tembak Fragment
        getSupportFragmentManager().beginTransaction()
                .replace(R.id.fragmentContainer, new TembakFragment())
                .commit();
    }
}
