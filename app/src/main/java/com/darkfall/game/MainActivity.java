package com.darkfall.game;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.ConsoleMessage;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.TextView;
import android.view.Gravity;

/** V988 Android shell. Embedded V983 game remains unchanged. */
public class MainActivity extends Activity {
    private WebView gameView;
    private TextView errorView;
    private static final String GAME_URL = "file:///android_asset/index.html";

    private void immersive() {
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
            View.SYSTEM_UI_FLAG_FULLSCREEN |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
            View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
            View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        immersive();

        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.BLACK);
        gameView = new WebView(this);
        gameView.setBackgroundColor(Color.BLACK);
        gameView.setOverScrollMode(View.OVER_SCROLL_NEVER);
        gameView.setVerticalScrollBarEnabled(false);
        gameView.setHorizontalScrollBarEnabled(false);
        gameView.setLayerType(View.LAYER_TYPE_HARDWARE, null);

        WebSettings settings = gameView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true); // Required for packaged index.html.
        settings.setAllowContentAccess(false);
        settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setSupportZoom(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setDefaultTextEncodingName("UTF-8");

        errorView = new TextView(this);
        errorView.setTextColor(Color.WHITE);
        errorView.setBackgroundColor(0xDD200C0C);
        errorView.setGravity(Gravity.CENTER);
        errorView.setPadding(30, 24, 30, 24);
        errorView.setVisibility(View.GONE);
        root.addView(gameView, new FrameLayout.LayoutParams(-1, -1));
        root.addView(errorView, new FrameLayout.LayoutParams(-1, -1));

        gameView.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                // The game is an offline application; never navigate to external pages.
                return !GAME_URL.equals(request.getUrl().toString());
            }
            @Override public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    errorView.setText("Dark Fall could not load its local game file.\n" + error.getDescription());
                    errorView.setVisibility(View.VISIBLE);
                }
            }
            @Override public void onPageFinished(WebView view, String url) {
                if (GAME_URL.equals(url)) errorView.setVisibility(View.GONE);
            }
        });
        gameView.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onConsoleMessage(ConsoleMessage message) {
                // Console output is available through Android Studio Logcat during testing.
                android.util.Log.d("DarkFallWeb", message.messageLevel() + ": " + message.message()
                    + " (" + message.sourceId() + ":" + message.lineNumber() + ")");
                return true;
            }
        });
        setContentView(root);
        gameView.loadUrl(GAME_URL);
    }

    @Override public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) immersive();
    }
    @Override protected void onPause() {
        if (gameView != null) gameView.onPause();
        super.onPause();
    }
    @Override protected void onResume() {
        super.onResume();
        if (gameView != null) gameView.onResume();
        immersive();
    }
    @Override public void onBackPressed() {
        // Preserve gameplay state; back is intentionally ignored in the prototype.
        // The Android system can still close the app via overview / app settings.
    }
    @Override protected void onDestroy() {
        if (gameView != null) {
            gameView.stopLoading();
            gameView.destroy();
            gameView = null;
        }
        super.onDestroy();
    }
}
