# Default model mappings
MODELS = {
    'v3': {
        'openrouter': 'deepseek/deepseek-v3.2-exp',
        'deepinfra': 'deepseek-ai/DeepSeek-V3-0324-Turbo'
    },
    'devstral': {
        'openrouter': 'mistralai/devstral-medium',
        'deepinfra': 'mistralai/Devstral-Small-2507'
    },
    'default': {
        'deepinfra': 'Qwen/Qwen3-Coder-480B-A35B-Instruct-Turbo',
        'openrouter': 'anthropic/claude-sonnet-4.5'
    },
    'qwen': {
        'deepinfra': 'Qwen/Qwen3-Coder-480B-A35B-Instruct-Turbo',
        'openrouter': 'qwen/qwen3-coder'
    },
    'morph_fast': {
        'openrouter': 'morph/morph-v3-fast'
    },
    'morph_large': {
        'openrouter': 'morph/morph-v3-large'
    }
}
