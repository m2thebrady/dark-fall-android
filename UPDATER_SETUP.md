# Dark Fall V989 Android updater

This branch preserves the existing bundled game and sensorLandscape orientation. It adds a native update checker using the public GitHub Releases API for `m2thebrady/dark-fall-android`. The app offers to download `dark-fall.apk` when the latest published `vNNN` release has a higher version code. Offline play continues normally.

## One-time release signing setup (required before publishing)
Generate a permanent Android signing keystore locally and back it up securely. Never commit it to GitHub or share its passwords in chat. In repository Settings → Secrets and variables → Actions, configure:
- `DARKFALL_KEYSTORE_BASE64`: base64-encoded keystore file
- `DARKFALL_STORE_PASSWORD`
- `DARKFALL_KEY_ALIAS`
- `DARKFALL_KEY_PASSWORD`

After this branch is tested and merged to main, open Actions → **Publish signed Dark Fall update** → Run workflow on main. The workflow builds a signed APK and publishes it as release `v989` with asset `dark-fall.apk`. Repository Actions permissions must permit writing contents (the workflow declares `contents: write`; organization policy may restrict this).

**Important:** The existing debug-signed app likely cannot update directly to this release-signed APK. Back up local progress if applicable; you may need to uninstall the debug version **once** before installing the release APK. Afterward, all releases must use the **same keystore, alias, package ID, and increasing versionCode**.

For future releases, increment versionCode/versionName, adjust `scripts/validate_project.py`, update the game HTML if needed, then run the publish workflow. Do not reuse an existing release version.

Android still requires user approval for each APK installation and may request one-time permission to install from Dark Fall. The app never silently installs updates.

Security: only publish trusted signed APKs. The Android installer enforces signing continuity, but this initial updater does not independently verify downloaded APK hashes. Public repositories expose their source code and history; never commit credentials or keystores.

Testing: GitHub Actions must successfully compile the branch and the APK must be tested on an Android device before merging.