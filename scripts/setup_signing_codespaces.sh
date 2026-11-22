#!/usr/bin/env bash
set -euo pipefail
REPO="m2thebrady/dark-fall-android"
KEYDIR="$PWD/.private-signing"
KEYFILE="$KEYDIR/darkfall-release.jks"
ALIAS="darkfall"
umask 077
command -v keytool >/dev/null || { echo "Java keytool is required."; exit 1; }
command -v gh >/dev/null || { echo "GitHub CLI is required."; exit 1; }
gh auth status >/dev/null || { echo "Sign in to GitHub CLI first: gh auth login"; exit 1; }
mkdir -p "$KEYDIR"
if [ -e "$KEYFILE" ]; then
  echo "Keystore already exists at $KEYFILE. Refusing to replace it."
  exit 1
fi
echo "Creating your permanent signing key. Use a strong password and remember it."
echo "Keytool will ask for keystore and key passwords; choose the SAME password for both."
keytool -genkeypair -v -keystore "$KEYFILE" -alias "$ALIAS" -keyalg RSA -keysize 3072 -validity 10000 -dname "CN=Dark Fall, OU=Android, O=Dark Fall, C=US"
echo
echo "IMPORTANT: Back up $KEYFILE using the Codespaces file explorer BEFORE deleting the Codespace."
echo "Never commit or share this file. Without this key, installed releases cannot be updated."
read -r -p "Have you downloaded a secure backup of the keystore? Type BACKED-UP to continue: " confirm
[ "$confirm" = "BACKED-UP" ] || { echo "Stopped. Back up the keystore and rerun the secret-upload step manually."; exit 1; }
read -r -s -p "Enter the keystore password again to store in GitHub Secrets: " pass
echo
[ -n "$pass" ] || { echo "Empty password not allowed."; exit 1; }
echo "Saving encrypted GitHub Actions secrets..."
base64 < "$KEYFILE" | tr -d '\n' | gh secret set DARKFALL_KEYSTORE_BASE64 --repo "$REPO"
printf '%s' "$pass" | gh secret set DARKFALL_STORE_PASSWORD --repo "$REPO"
printf '%s' "$pass" | gh secret set DARKFALL_KEY_PASSWORD --repo "$REPO"
printf '%s' "$ALIAS" | gh secret set DARKFALL_KEY_ALIAS --repo "$REPO"
unset pass
echo "Signing secrets configured. Keep your downloaded keystore backup safe."
