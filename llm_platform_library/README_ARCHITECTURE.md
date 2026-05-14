# llm-platform-library Architecture

## Module Architecture

- `client.py`: configuration loading, validation, mock LLM provider abstraction.
- `rag.py`: RAG context construction and answer generation orchestration.
- `prompts.py`: prompt registration, lookup, and safe rendering.
- `cost_tracker.py`: token usage recording and cost aggregation.
- `department_router.py`: keyword-based routing to enterprise departments.
- `models.py`: immutable dataclass contracts.
- `logger.py`: structured file logging.
- `exceptions.py`: custom exception hierarchy.

## Data Flow

Applications provide configuration to `LLMClient`. The client validates provider, model, departments, log path, prompt folder, and model pricing. Services use dataclass models for typed inputs and outputs.

## RAG Flow

1. Application retrieves documents using its own search/vector system.
2. Application passes `RAGDocument` values to `RAGService`.
3. `RAGService` builds context and a grounded prompt.
4. `LLMClient` generates a mock response.
5. `RAGResponse` returns answer text and source document IDs.

## Cost Tracking Flow

`CostTracker` receives `TokenUsage`, department, and model. It uses configured `ModelPricing` to estimate cost and aggregate totals by department and model.

## Department Routing Flow

`DepartmentRouter` evaluates keyword rules. The best matching department is returned with a confidence score. If no match exists, it logs a warning and falls back to `General`.

## Future Provider Integration

Future provider adapters can be added for Azure OpenAI, OpenAI-compatible APIs, Managed Identity, and enterprise gateways. Provider adapters should never log API keys, full prompts, or secrets.

## Security Principles

- No API keys in code.
- No real external API calls in this version.
- No secrets or full sensitive prompts in logs.
- Consumers catch `LLMPlatformLibraryError`.
- No bare `except` or `sys.exit()` in library modules.

