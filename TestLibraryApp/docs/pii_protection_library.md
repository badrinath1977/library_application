# PII Protection Library Test

## Library

Installed from:

```text
../libraries-dist/pii_protection_library/pii_protection-1.0.0-py3-none-any.whl
```

Import package:

```python
from pii_protection import PiiProtectionService, InMemoryPiiMappingStore
```

## Test File

```text
TestLibraryApp/library_tests/test_pii_protection_library.py
```

## What It Tests

The test tokenizes an email address, simulates an LLM output that preserves the token, and restores the original value using the same correlation ID.

## Why This Matters

For LLM workflows, raw PII should not be sent to the model. Tokenization lets the model preserve placeholders while the library restores approved values afterward.

## Run Only This Test

```powershell
cd C:\Projects\Python-Library\TestLibraryApp
.\.venv\Scripts\python.exe .\library_tests\test_pii_protection_library.py
```

Expected output:

```text
PASS pii_protection: protected={{PII_EMAIL_001}} restored='LLM returned badri@gmail.com'
```
