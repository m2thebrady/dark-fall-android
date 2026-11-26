# Dark Fall V1509 — Royal Haven Craft and Arcane Interiors

The Android app now bundles the original V1509 HTML, reconstructed from individually compressed, checksummed files in `game-bundle/`. The original HTML is over GitHub's per-file limit, so it is generated locally, not tracked directly.

## Build and update
- Install Python 3.11+ and Java 17. For Android Studio, use **Build APK**; Gradle runs the bundle materialization task automatically. Set `DARKFALL_PYTHON` if a custom Python executable is needed.
- To reconstruct the browser game or run source audits, execute `python3 scripts/materialize_game.py` from the repository root.
- Android versionCode: **1509** / versionName: **0.1509**; application ID and signing configuration are unchanged.
- The GitHub Actions publish workflow creates `v1509` with `dark-fall.apk` once the signed build succeeds. Verify gameplay and upgrade on a real Android device before treating this build as production-ready.
- See [UPDATER_SETUP.md](UPDATER_SETUP.md) for the existing signing and update setup.

## Historical notes
### V988 — first APK build verification milestone

**This ZIP is an Android Studio / GitHub Actions project, not an APK.** The game asset is identical to the V987 project (which retains V983 gameplay); no fire repairs were imported.

## What changed
- Android app versionCode 988 and versionName 0.988.
- Automated pre-build checks verify bundled game, application ID, landscape configuration and version alignment.
- GitHub Actions now checks that the resulting debug/release APK exists, passes ZIP integrity checks and contains `assets/index.html` before publishing artifacts.
- Preserves the same application ID and optional persistent signing configuration.

## Compile the first APK
1. Create a **private** GitHub repository and upload the *contents* of this project ZIP, including the hidden `.github` directory.
2. Open **Actions → Build Dark Fall Android APK → Run workflow**.
3. When successful, download the `Dark-Fall-V988-Debug-APK` artifact and extract `app-debug.apk`.
4. Install it on an Android phone to test launch, class selection, combat, touchscreen controls, sound and pause/resume.

**Important:** The debug APK is only for first testing. To preserve app installation and WebView storage across future releases, generate your own private keystore and configure the four `DARKFALL_*` GitHub Actions secrets described below, then install the consistently signed release APK from the start. A debug APK generally cannot be upgraded to a release APK without uninstalling.

## Release signing secrets
`DARKFALL_KEYSTORE_BASE64`, `DARKFALL_STORE_PASSWORD`, `DARKFALL_KEY_ALIAS`, `DARKFALL_KEY_PASSWORD`. Never upload keystores or passwords to the repository or chat. Keep an offline backup. To create a keystore locally with a JDK:

```sh
keytool -genkeypair -v -keystore darkfall-release.jks -alias darkfall -keyalg RSA -keysize 3072 -validity 10000
```

The build workflow decodes the secret keystore in the GitHub runner and produces `Dark-Fall-V988-Signed-APK` when configured. Maintain the same application ID and signing key for subsequent updates; increase `versionCode`.

## Build status
Project static validation completed locally. The APK build and phone installation are **not yet verified** because the Android SDK and Gradle are unavailable in this environment. The next real milestone is running the workflow and reviewing its build log or installing the APK. Do not treat this ZIP as an installable APK.
