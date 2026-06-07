# Folder Structure

```text
project-name/
|-- run_server.py
|-- config.json
|-- requirements.txt
|-- Dockerfile
|-- manifest.yaml
|-- README.md
|-- readme_setup.md
|-- readme_test.md
|-- readme_folder_structure.md
`-- app/
    |-- main.py
    |-- core/
    |   |-- config.py
    |   |-- dependencies.py
    |   |-- sqldbconnection.py
    |   `-- exceptions.py
    |-- api/
    |   |-- routes/
    |   |   |-- auth_routes.py
    |   |   |-- health_routes.py
    |   |   |-- customer_routes.py
    |   |   `-- sample_routes.py
    |   `-- middleware/
    |       |-- auth_middleware.py
    |       |-- logging_middleware.py
    |       |-- correlation_middleware.py
    |       `-- exception_middleware.py
    |-- models/
    |   |-- request_models.py
    |   |-- response_models.py
    |   `-- db_models.py
    |-- service/
    |   |-- customer_service.py
    |   |-- external_api_service.py
    |   |-- token_service.py
    |   `-- sample_service.py
    |-- repository/
    |   |-- customer_repository.py
    |   `-- sample_repository.py
    `-- utils/
        |-- constants.py
        |-- pii_utils.py
        `-- response_builder.py
```

## Responsibilities

`app/main.py`
: Creates the FastAPI app, registers middleware, routers, and lifecycle events.

`app/core`
: Owns configuration, reusable dependencies, and application exceptions.

`app/api/middleware`
: Owns centralized NFR behavior for authentication, logging, correlation, and exceptions.

`app/api/routes`
: Defines API contracts and delegates work to services.

`app/service`
: Contains business logic and orchestration.

`app/repository`
: Contains database and external persistence logic.

`app/models`
: Contains Pydantic request and response models plus DB-facing models.

`app/utils`
: Contains reusable constants, PII helpers, and response envelope builders.
