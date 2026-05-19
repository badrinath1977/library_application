# Application Usage Guide

## Install Wheel

```powershell
pip install dist/llm_platform_library-0.1.0-py3-none-any.whl
```

## Sample Consumer App

```python
from llm_platform_library import LLMClient, RAGDocument, RAGService
from llm_platform_library.exceptions import LLMPlatformLibraryError

try:
    client = LLMClient("config.json")
    rag = RAGService(client)
    response = rag.generate_answer(
        "What is the leave policy?",
        [RAGDocument(document_id="hr-1", content="Leave policy allows PTO.")],
    )
    print(response.answer)
except LLMPlatformLibraryError as ex:
    print(f"LLM platform error: {ex}")
```

## Sample Config

Use the `config.json` format documented in `README.md`. Applications should own their config file and pass its path explicitly.

## LLMClient

```python
client = LLMClient("config.json")
response = client.generate_response("Summarize this request.", department="HR")
```

## RAGService

```python
rag = RAGService(client)
answer = rag.generate_answer("Question", documents)
```

## PromptManager

```python
from llm_platform_library import PromptManager

prompts = PromptManager()
prompts.register_prompt("summary", "Summarize: {text}")
rendered = prompts.render_prompt("summary", {"text": "content"})
```

## CostTracker

```python
from llm_platform_library import CostTracker, ModelPricing, TokenUsage

tracker = CostTracker({"gpt-4.1-mini": ModelPricing(0.00015, 0.0006)})
tracker.record_usage(TokenUsage(100, 50, 150), "HR", "gpt-4.1-mini")
```

## DepartmentRouter

```python
from llm_platform_library import DepartmentRouter

router = DepartmentRouter({"HR": ["leave"], "General": []})
route = router.route("leave balance question")
```

