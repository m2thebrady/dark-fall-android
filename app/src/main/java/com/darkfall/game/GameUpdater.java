package com.darkfall.game;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import androidx.core.content.FileProvider;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.File;
import java.util.regex.Pattern;

/** Native updater. Never blocks the offline HTML game. */
public final class GameUpdater {
    private static final String API = "https://api.github.com/repos/m2thebrady/dark-fall-android/releases/latest";
    private static final String ASSET = "dark-fall.apk";
    private final Activity activity;
    private long downloadId = -1;
    private File downloadedFile;
    private BroadcastReceiver receiver;
    private boolean prompted = false;
    private boolean permissionPending = false;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private boolean checkingDownload = false;
    private int downloadChecks = 0;
    private DownloadManager activeManager;
    private final Runnable pollDownload = new Runnable() {
        @Override public void run() {
            if (!checkingDownload || activeManager == null || downloadId < 0) return;
            try (android.database.Cursor cursor = activeManager.query(new DownloadManager.Query().setFilterById(downloadId))) {
                if (cursor != null && cursor.moveToFirst()) {
                    int status = cursor.getInt(cursor.getColumnIndexOrThrow(DownloadManager.COLUMN_STATUS));
                    if (status == DownloadManager.STATUS_SUCCESSFUL) {
                        checkingDownload = false;
                        if (downloadedFile != null && downloadedFile.isFile() && downloadedFile.length() > 0) install();
                        else message("Update downloaded but the APK could not be found.");
                        return;
                    }
                    if (status == DownloadManager.STATUS_FAILED) {
                        int reason = cursor.getInt(cursor.getColumnIndexOrThrow(DownloadManager.COLUMN_REASON));
                        checkingDownload = false;
                        message("Update download failed (Android code " + reason + ").");
                        return;
                    }
                }
            } catch (Exception e) {
                checkingDownload = false;
                message("Could not check the update download: " + e.getClass().getSimpleName());
                return;
            }
            if (++downloadChecks >= 180) {
                checkingDownload = false;
                message("The update is taking too long. Check your internet connection and try again.");
            } else handler.postDelayed(this, 1000);
        }
    };

    public GameUpdater(Activity activity) { this.activity = activity; }

    public void check() {
        new Thread(() -> {
            HttpURLConnection connection = null;
            try {
                connection = (HttpURLConnection) new URL(API).openConnection();
                connection.setConnectTimeout(7000);
                connection.setReadTimeout(7000);
                connection.setRequestProperty("Accept", "application/vnd.github+json");
                connection.setRequestProperty("User-Agent", "DarkFall-Android-Updater");
                if (connection.getResponseCode() != 200) return;
                StringBuilder json = new StringBuilder();
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        json.append(line);
                        if (json.length() > 100000) return;
                    }
                }
                JSONObject release = new JSONObject(json.toString());
                String tag = release.optString("tag_name", "");
                if (!Pattern.matches("[vV][0-9]{1,9}", tag)) return;
                int remote = Integer.parseInt(tag.substring(1));
                int installed = activity.getPackageManager().getPackageInfo(activity.getPackageName(), 0).versionCode;
                if (remote <= installed || release.optBoolean("draft") || release.optBoolean("prerelease")) return;
                JSONArray assets = release.optJSONArray("assets");
                if (assets == null) return;
                for (int i = 0; i < assets.length(); i++) {
                    JSONObject asset = assets.optJSONObject(i);
                    if (asset == null || !ASSET.equals(asset.optString("name"))) continue;
                    String url = asset.optString("browser_download_url", "");
                    if (!url.startsWith("https://github.com/m2thebrady/dark-fall-android/releases/download/")) continue;
                    activity.runOnUiThread(() -> prompt(remote, url));
                    return;
                }
            } catch (Exception ignored) {
                // Offline or rate-limited: gameplay continues normally.
            } finally {
                if (connection != null) connection.disconnect();
            }
        }, "DarkFallUpdateCheck").start();
    }

    private void prompt(int version, String url) {
        if (activity.isFinishing() || prompted) return;
        prompted = true;
        new AlertDialog.Builder(activity)
            .setTitle("Dark Fall update available")
            .setMessage("Version " + version + " is ready. Download and install now?")
            .setNegativeButton("Later", (d, w) -> {})
            .setPositiveButton("Update", (d, w) -> download(url, version))
            .show();
    }

    private void download(String url, int version) {
        try {
            File dir = activity.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
            if (dir == null) throw new IllegalStateException("No download directory");
            downloadedFile = new File(dir, "dark-fall-" + version + ".apk");
            if (downloadedFile.exists()) downloadedFile.delete();
            DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
            request.setTitle("Dark Fall " + version);
            request.setDescription("Downloading game update");
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            request.setDestinationUri(Uri.fromFile(downloadedFile));
            DownloadManager manager = (DownloadManager) activity.getSystemService(Context.DOWNLOAD_SERVICE);
            downloadId = manager.enqueue(request);
            activeManager = manager;
            downloadChecks = 0;
            checkingDownload = true;
            handler.removeCallbacks(pollDownload);
            handler.postDelayed(pollDownload, 1000);
            message("Downloading Dark Fall " + version + ". Android will open the installer when ready.");
        } catch (Exception e) {
            message("Unable to download update.");
        }
    }

    private void install() {
        if (Build.VERSION.SDK_INT >= 26 && !activity.getPackageManager().canRequestPackageInstalls()) {
            permissionPending = true;
            new AlertDialog.Builder(activity)
                .setTitle("Allow Dark Fall updates")
                .setMessage("Android needs permission to install updates from Dark Fall. Enable 'Allow from this source', then return to the game.")
                .setPositiveButton("Settings", (d, w) -> {
                    Intent intent = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                        Uri.parse("package:" + activity.getPackageName()));
                    activity.startActivity(intent);
                })
                .setNegativeButton("Later", (d, w) -> {})
                .show();
            return;
        }
        try {
            Uri uri = FileProvider.getUriForFile(activity,
                activity.getPackageName() + ".updateprovider", downloadedFile);
            Intent intent = new Intent(Intent.ACTION_VIEW);
            intent.setDataAndType(uri, "application/vnd.android.package-archive");
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
            activity.startActivity(intent);
            permissionPending = false;
        } catch (Exception e) {
            message("Android could not open the installer.");
        }
    }

    public void onResume() {
        if (permissionPending && (Build.VERSION.SDK_INT < 26 ||
            activity.getPackageManager().canRequestPackageInstalls())) install();
    }

    public void close() { checkingDownload = false; handler.removeCallbacks(pollDownload); stopReceiver(); }

    private void stopReceiver() {
        if (receiver == null) return;
        try { activity.unregisterReceiver(receiver); } catch (Exception ignored) {}
        receiver = null;
    }

    private void message(String text) {
        new AlertDialog.Builder(activity).setTitle("Dark Fall").setMessage(text)
            .setPositiveButton("OK", null).show();
    }
}
