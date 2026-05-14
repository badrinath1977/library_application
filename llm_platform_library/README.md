# llm-platform-library

`llm-platform-library` is a reusable enterprise Python 3.11+ library for LLM calls, RAG orchestration, prompt management, cost tracking, and department routing.

The current provider is a safe mock provider only. No real external API calls are made, no API keys are stored, and prompts are not logged in full.

## Features

- Mock LLM client with provider abstraction
- RAG prompt construction and source tracking
- Prompt template registration and safe rendering
- Token usage and estimated cost aggregation
- Rule-based department routing with confidence scores
- Structured logging to `llm_platform_library_YYYYMMDD.log`
- Custom exceptions rooted at `LLMPlatformLibraryError`

## Installation

```powershell
python -m pip install .
```

Editable install:

```powershell
python -m pip install -e ".[dev]"
```

## Config Format

```json
{
  "Provider": "mock",
  "DefaultModel": "gpt-4.1-mini",
  "LogLocation": "C:/Logs/llm_platform_library",
  "PromptFolder": "prompts",
  "Departments": {
    "HR": ["leave", "salary", "benefits", "policy"],
    "Finance": ["invoice", "budget", "expense", "payment"],
    "IT": ["password", "access", "laptop", "vpn"],
    "Legal": ["contract", "agreement", "compliance"],
    "Sales": ["lead", "customer", "pricing", "proposal"],
    "General": []
  },
  "ModelPricing": {
    "gpt-4.1-mini": {
      "InputPer1KTokens": 0.00015,
      "OutputPer1KTokens": 0.0006
    }
  }
}
```

## Usage Examples

```python
from llm_platform_library import LLMClient
from llm_platform_library.exceptions import LLMPlatformLibraryError

try:
    client = LLMClient("config.json")
    response = client.generate_response("Summarize the policy.", department="HR")
except LLMPlatformLibraryError as ex:
    print(f"LLM platform error: {ex}")
```

```python
from llm_platform_library import DepartmentRouter

router = DepartmentRouter({"IT": ["password", "vpn"], "General": []})
route = router.route("I need VPN access")
```

## Quality Commands

```powershell
pytest
ruff check .
mypy llm_platform_library
pip-audit
pytest --cov=llm_platform_library
python -m build
```

## build_library.py Usage

```powershell
python build_library.py
```

