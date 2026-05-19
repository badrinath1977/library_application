# LLM Platform Library Test

## Library

Installed from:

```text
../libraries-dist/llm_platform_library/llm_platform_library-0.1.0-py3-none-any.whl
```

Import package:

```python
from llm_platform_library import CostTracker, DepartmentRouter, PromptManager
```

## Test File

```text
TestLibraryApp/library_tests/test_llm_platform_library.py
```

## What It Tests

The test routes a sample query to a department, renders a prompt template, records token usage, and prints the calculated cost.

## Why This Matters

It verifies the core local utilities without calling an external LLM provider.

## Run Only This Test

```powershell
cd C:\Projects\Python-Library\TestLibraryApp
.\.venv\Scripts\python.exe .\library_tests\test_llm_platform_library.py
```

Expected output:

```text
PASS llm_platform_library: department=Finance prompt='Hello Badri, route=Finance' cost=0.0020
```
