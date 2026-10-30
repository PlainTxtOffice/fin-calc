# Fin Calc for Android

Native Kotlin calculator with decimal arithmetic, reusable calculation history,
light/dark themes, display precision settings, and CSV export.

## Build and run

Open this directory in Android Studio. Install Android SDK Platform 37 and let
Gradle sync. Select the **app** configuration and an Android 8.0 (API 26) or
newer device or emulator, then click Run.

The project uses Android Gradle Plugin 9.4.1 and the included Gradle 9.6.0
wrapper. Use Android Studio's bundled JDK for Gradle. Set `ANDROID_HOME` to your
SDK directory, or let Android Studio create an ignored `local.properties` with
`sdk.dir`. Python is not required.

Open `platform/android/` itself rather than the repository root. Android
Studio's `.idea/` directories and `*.iml` files are ignored local IDE state; do
not move them between project roots. The Gradle project files and wrapper are
shared.

From this directory in PowerShell:

```powershell
.\gradlew.bat testDebugUnitTest lintDebug assembleDebug
.\gradlew.bat installDebug
```

The debug APK is `app/build/outputs/apk/debug/app-debug.apk`.

## Using the calculator

Enter an expression with the keypad and tap **=**. Tap a saved result to reuse
its full precision. **C** clears input; **⌫** deletes the last character.
Use **log**, parentheses, and a positive value for base-10 logarithms.

The **⋮** menu contains Settings, Export History, Clear History, Privacy
Policy, and About. Privacy Policy opens the Plain Text Office privacy policy
in a browser.
Settings provide full precision or 0–6 decimal places, light/dark appearance,
and a history limit of 1–10,000 entries or Unlimited. Export opens Android's
document picker and writes UTF-8 CSV with `timestamp,expression,result` columns.

History and settings are saved in app-private `calculator.json`. Uninstalling
or clearing app data removes them; export anything you want to retain first.
The app requests no network or storage permissions and disables Android backup.
Each platform keeps its own history; there is no cross-device synchronization.

## Arithmetic and validation

The engine uses `BigDecimal`, 28 significant digits, and half-even rounding.
Display rounding does not change stored results. Unary minus binds more tightly
than powers, and powers associate to the right, matching the Windows engine.

Inputs are limited to 128 tokens and 2,048 characters. The mobile engine bounds
decimal exponents to ±9,999 to keep calculations
responsive. These limits are narrower than Python Decimal's range. Logarithms
and fractional powers use decimal series with guard digits; their final digit
can differ from the Windows implementation.

Unit tests cover calculation errors, history reuse, settings, failed saves,
restart persistence, CSV escaping, and 59 reference calculations generated from
`platform/windows/fin_calc/domains/calc/evaluator.py`. The reference values live
in `app/src/test/resources/python-reference.json`.

## Release preparation

The application ID is `com.tripp.fincalc`; the initial version is
`0.1.0` with version code `1`. It compiles against API 37 and targets API 36.

```powershell
.\gradlew.bat bundleRelease
```

This creates an **unsigned** bundle at
`app/build/outputs/bundle/release/app-release.aab`. For distribution, use
Android Studio's **Build > Generate Signed App Bundle / APK**, create or select
your upload key, and keep the key and passwords outside version control.
Increment the version code before subsequent Play releases. This project does
not include store submission credentials or upload automation.

## Source layout

- `domains/calc/`: decimal arithmetic, expression input, history, formatting.
- `config/`: settings values.
- `adapters/`: JSON persistence and CSV output.
- `application/`: calculator sessions and background Android lifecycle state.
- `ui/`: keypad, tape, settings, and visual presentation.
- `MainActivity.kt`: activity lifecycle and document picker integration.

The repository's [MIT license](../../LICENSE) applies to this port.
