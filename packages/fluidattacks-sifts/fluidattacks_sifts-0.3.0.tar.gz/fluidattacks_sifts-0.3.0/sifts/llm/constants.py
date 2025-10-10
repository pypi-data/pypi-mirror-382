LLM_MODELS = [
    {
        "model_name": "o3-mini",
        "litellm_params": {
            "model": "o3-mini",
            "caching": True,
        },
    },
    {
        "model_name": "gpt-4o-mini",
        "litellm_params": {
            "model": "gpt-4o-mini",
            "caching": True,
        },
    },
    {
        "model_name": "nova-pro",
        "litellm_params": {
            "model": "bedrock/us.amazon.nova-pro-v1:0",
            "caching": True,
            "user_continue_message": {"role": "user", "content": "Please continue"},
        },
    },
    {
        "model_name": "voyage-3",
        "litellm_params": {
            "model": "voyage/voyage-3",
            "caching": True,
        },
    },
]


MAX_TOKEN_COUNT_FUNCTION = 3000
