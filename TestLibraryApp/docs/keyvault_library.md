# KeyVault Library Test

## Library

Installed from:

```text
../libraries-dist/Keyvault_library/keyvault_library-0.1.0-py3-none-any.whl
```

Import package:

```python
from keyvault_library import KeyVaultManager
```

## Test File

```text
TestLibraryApp/library_tests/test_keyvault_library.py
```

## What It Tests

The test loads `TestLibraryApp/config.json` through `KeyVaultManager.from_file()`, then prints the configured vault URL, secret count, and key count.

## Why This Matters

It proves the library reads the parent application's config file, not a package-internal config file.

## Run Only This Test

```powershell
cd C:\Projects\Python-Library\TestLibraryApp
.\.venv\Scripts\python.exe .\library_tests\test_keyvault_library.py
```

Expected output:

```text
PASS keyvault_library: url=... secrets=1 keys=1
```
