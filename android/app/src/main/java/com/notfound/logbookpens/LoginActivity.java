package com.notfound.logbookpens;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class LoginActivity extends AppCompatActivity {

    private EditText etNetId, etPassword;
    private CheckBox cbRemember;
    private TextView tvStatus;
    private Button btnLogin;
    private SharedPreferences prefs;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        prefs = getSharedPreferences("404_pens_prefs", MODE_PRIVATE);

        etNetId = findViewById(R.id.etNetId);
        etPassword = findViewById(R.id.etPassword);
        cbRemember = findViewById(R.id.cbRemember);
        tvStatus = findViewById(R.id.tvStatus);
        btnLogin = findViewById(R.id.btnLogin);

        boolean remember = prefs.getBoolean("remember", true);
        cbRemember.setChecked(remember);
        if (remember) {
            etNetId.setText(prefs.getString("netid", ""));
            etPassword.setText(prefs.getString("password", ""));
        }

        btnLogin.setOnClickListener(v -> doLogin());
    }

    private void doLogin() {
        String netId = etNetId.getText().toString().trim();
        String password = etPassword.getText().toString().trim();

        if (netId.isEmpty() || password.isEmpty()) {
            Toast.makeText(this, "NetID dan Password wajib diisi!", Toast.LENGTH_SHORT).show();
            return;
        }

        btnLogin.setEnabled(false);
        btnLogin.setText("Menghubungkan CAS PENS...");
        tvStatus.setText("Memverifikasi kredensial...");
        tvStatus.setTextColor(getResources().getColor(R.color.primary, null));

        new Thread(() -> {
            boolean success = NetworkManager.getInstance().login(netId, password);
            runOnUiThread(() -> {
                btnLogin.setEnabled(true);
                btnLogin.setText("MASUK CAS PENS");

                if (success) {
                    if (cbRemember.isChecked()) {
                        prefs.edit()
                                .putString("netid", netId)
                                .putString("password", password)
                                .putBoolean("remember", true)
                                .apply();
                    } else {
                        prefs.edit().clear().apply();
                    }

                    Intent intent = new Intent(LoginActivity.this, MainActivity.class);
                    startActivity(intent);
                    finish();
                } else {
                    tvStatus.setText("Gagal: NetID atau Password salah / CAS ditolak");
                    tvStatus.setTextColor(getResources().getColor(R.color.primary_dark, null));
                }
            });
        }).start();
    }
}
