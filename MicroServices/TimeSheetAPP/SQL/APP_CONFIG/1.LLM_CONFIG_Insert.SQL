-- OpenAI
INSERT INTO GenAI.AppConfig (ConfigKey, ConfigValue, ConfigType, ApplicationName, EnvironmentName, IsSensitive, IsActive, Description, CreatedBy)
VALUES (
    'LLM_CONFIG',
    '{
        "provider": "openai",
        "model": "gpt-4o",
        "api_key": "sk-xxxx",
        "base_url": "[api.openai.com](https://api.openai.com/v1)",
        "temperature": 0.3,
        "max_tokens": 2048,
        "timeout": 30,
        "streaming": false
    }',
    'LLM', 'GenAI-HRApp', 'DEV', 1, 1, 'OpenAI LLM Configuration', 'admin@xyz.com'
);

-- Azure OpenAI
INSERT INTO GenAI.AppConfig (ConfigKey, ConfigValue, ConfigType, ApplicationName, EnvironmentName, IsSensitive, IsActive, Description, CreatedBy)
VALUES (
    'LLM_CONFIG',
    '{
        "provider": "azure_openai",
        "model": "gpt-4o",
        "api_key": "xxxx",
        "base_url": "https://<resource>.openai.azure.com/",
        "api_version": "2024-02-01",
        "deployment_name": "gpt-4o-deployment",
        "temperature": 0.3,
        "max_tokens": 2048,
        "timeout": 30,
        "streaming": false
    }',
    'LLM', 'GenAI-HRApp', 'PROD', 1, 1, 'Azure OpenAI Configuration', 'admin@xyz.com'
);

-- Ollama (Local)
INSERT INTO GenAI.AppConfig (ConfigKey, ConfigValue, ConfigType, ApplicationName, EnvironmentName, IsSensitive, IsActive, Description, CreatedBy)
VALUES (
    'LLM_CONFIG',
    '{
        "provider": "ollama",
        "model": "llama3",
        "base_url": "[localhost](http://localhost:11434)",
        "temperature": 0.3,
        "max_tokens": 2048,
        "timeout": 60,
        "streaming": false
    }',
    'LLM', 'GenAI-HRApp', 'LOCAL', 0, 1, 'Ollama Local LLM Configuration', 'admin@xyz.com'
);

-- Custom / Any Future Provider
INSERT INTO GenAI.AppConfig (ConfigKey, ConfigValue, ConfigType, ApplicationName, EnvironmentName, IsSensitive, IsActive, Description, CreatedBy)
VALUES (
    'LLM_CONFIG',
    '{
        "provider": "custom",
        "model": "custom-model-v1",
        "api_key": "xxxx",
        "base_url": "[your-custom-llm.com](https://your-custom-llm.com/v1)",
        "headers": {
            "x-custom-header": "value"
        },
        "temperature": 0.3,
        "max_tokens": 2048,
        "timeout": 30,
        "streaming": false
    }',
    'LLM', 'GenAI-HRApp', 'UAT', 1, 1, 'Custom LLM Provider Configuration', 'admin@xyz.com'
);
