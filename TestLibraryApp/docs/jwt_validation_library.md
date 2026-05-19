# JWT Validation Library Test

## Library

Installed from:

```text
../libraries-dist/jwt_validation_library/jwt_validation_library-1.0.0-py3-none-any.whl
```

Import package:

```python
from jwt_validation import JwtValidator, JwtValidatorConfig
```

## Test File

```text
TestLibraryApp/library_tests/test_jwt_validation_library.py
```

## What It Tests

The test creates a local HS256 JWT, validates issuer, audience, required scope, allowed algorithm, and returns the configured `sub` claim.

## Why This Matters

It verifies that a parent application can configure token validation and receive a structured success result without contacting an external identity provider.

## Run Only This Test

```powershell
cd C:\Projects\Python-Library\TestLibraryApp
.\.venv\Scripts\python.exe .\library_tests\test_jwt_validation_library.py
```

Expected output:

```text
PASS jwt_validation: return_claim=user-123
```
