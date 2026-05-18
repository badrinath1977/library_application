# TestLibraryApp

`TestLibraryApp` is a separate consumer application used to validate that `keyvault-library` works like an installed third-party package.

It has its own `config.json` and explicitly passes that file to:

```python
KeyVaultManager.from_file("config.json")
```

The library must read this application's config file, not `Keyvault_library/config.json` and not any package-internal file.

## Build the Library

From the library project:

```powershell
cd C:\Projects\Python-Library\Keyvault_library
python build_library.py
```

If `pip-audit` fails because of unrelated packages in the shared Python environment, you can still build the wheel directly:

```powershell
python -m build
```

Expected wheel after collecting library distributions:

```text
C:\Projects\Python-Library\libraries-dist\Keyvault_library\keyvault_library-0.1.0-py3-none-any.whl
```

## Install the Wheel

From this test application:

```powershell
cd C:\Projects\Python-Library\TestLibraryApp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run the Test App

```powershell
python app.py
```

Or:

```powershell
python run_test_app.py
```

## Expected Output

```text
KeyVault Library Test Application Started
Config File Used: C:\Projects\Python-Library\TestLibraryApp\config.json
Configuration loaded successfully
KeyVault URL: https://testingkeyvalut.vault.azure.net/
Secrets Count: 3
Keys Count: 2
Log Location: logs/test_library_app
Test completed successfully
```

## Verify Logs

The test app config writes logs to:

```text
TestLibraryApp/logs/test_library_app
```

The log file name follows:

```text
keyvault_library_YYYYMMDD.log
```

## Confirm It Reads Its Own Config

The app prints:

```text
Config File Used: <absolute path to TestLibraryApp/config.json>
```

You can also temporarily change `TestLibraryApp/config.json`, for example change `KeyVaultURL`, then rerun `python app.py`. The printed value should match the app config file.

## Safe Failure Behavior

If `config.json` is missing, invalid, or unreadable, the app catches `KeyVaultLibraryError`, prints a safe configuration error message, and exits with a non-zero code.
