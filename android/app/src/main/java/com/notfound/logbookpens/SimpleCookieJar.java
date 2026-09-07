package com.notfound.logbookpens;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import okhttp3.Cookie;
import okhttp3.CookieJar;
import okhttp3.HttpUrl;

public class SimpleCookieJar implements CookieJar {
    private final Map<String, List<Cookie>> cookieStore = new HashMap<>();

    @Override
    public synchronized void saveFromResponse(HttpUrl url, List<Cookie> cookies) {
        List<Cookie> existing = cookieStore.get(url.host());
        if (existing == null) {
            existing = new ArrayList<>();
            cookieStore.put(url.host(), existing);
        }
        for (Cookie newCookie : cookies) {
            existing.removeIf(c -> c.name().equals(newCookie.name()));
            existing.add(newCookie);
        }
    }

    @Override
    public synchronized List<Cookie> loadForRequest(HttpUrl url) {
        List<Cookie> cookies = cookieStore.get(url.host());
        return cookies != null ? new ArrayList<>(cookies) : new ArrayList<>();
    }
}
