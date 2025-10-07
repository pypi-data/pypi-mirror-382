# LLM Backend for Cowrie Honeypot

This module implements an LLM-powered backend for the Cowrie SSH/Telnet honeypot. Instead of emulating a real system with pre-defined command responses, this backend uses a Large Language Model to generate dynamic, context-aware responses to attackers' commands.

## Configuration

Configure the LLM backend in your `cowrie.cfg` file:

```ini
[honeypot]
backend = llm

[llm]
# LLM API Settings
# Default is for a local LLM server (like text-generation-webui)
LLM_HOST = http://127.0.0.1:5000
LLM_PATH = /api/v1/generate
LLM_PROMPT_KEYNAME = prompt
DEBUG = false

# For OpenAI-compatible APIs, set LLM_API_TYPE = openai
# LLM_API_TYPE = openai
# LLM_HOST = https://api.openai.com/v1
# LLM_PATH = /chat/completions
# LLM_PROMPT_KEYNAME = messages

# Request body sent to LLM API
LLM_REQUEST_BODY = {
    "max_new_tokens": 250,
    "temperature": 0.7,
    "stop": ["User:", "System:"]
}
```

## Supported LLM APIs

1. **Local LLM servers** (default): Works with [text-generation-webui](https://github.com/oobabooga/text-generation-webui) and other compatible APIs
2. **OpenAI API**: Set `LLM_API_TYPE = openai` to use GPT models from OpenAI or compatible APIs

## How It Works

The LLM backend:
1. Takes the user's input commands
2. Constructs a context-aware prompt including system information and command history
3. Calls the configured LLM API
4. Returns the LLM's response as if it were the output of the command

For each new session, the state is maintained between commands to provide consistent responses.

## Advantages

- Dynamic responses that adapt to attacker behavior
- Realistic command output even for uncommon commands
- Maintains consistent state and file paths throughout a session
- Can be adjusted to show various security levels and system configurations
- No need to implement all possible Unix commands or maintain a virtual filesystem

## Security Note

Ensure your LLM is set up to avoid providing actual harmful instructions to attackers. The system context provided to the LLM is designed to keep responses within the scope of simulating command output only.