# AriAI

A flexible chatbot framework that supports multiple AI providers (OpenAI and Hugging Face).

## Features

- Support for both OpenAI (GPT-3.5/4) and Hugging Face models
- Custom system prompts / personalities
- Conversation memory
- Rich terminal UI with colored output
- Easy to use and extend

## Installation

1. Clone this repository:
```bash
git clone https://github.com/username/ariai.git
cd ariai
```

2. Build and install the package:
```bash
python setup.py sdist bdist_wheel
pip install ./dist/ariai-0.1-py3-none-any.whl
```

## Usage

Here's a basic example:

```python
from ariai import AriAI

# Using OpenAI
bot = AriAI(
    provider="openai",
    api_key="YOUR_OPENAI_API_KEY",
    system_prompt="You are a helpful AI assistant."
)

# Or using Hugging Face
bot = AriAI(
    provider="huggingface",
    hf_model="google/flan-t5-base",
    system_prompt="You are a helpful AI assistant."
)

# Start the interactive chat UI
bot.start_ui()
```

You can also use the chat method directly:

```python
response = bot.chat("Hello, how are you?")
print(response)
```

## Configuration

### OpenAI

For OpenAI, you'll need to set your API key. You can either:
1. Pass it directly to the constructor
2. Set it as an environment variable: `OPENAI_API_KEY`

### Hugging Face

For Hugging Face, you can specify any model that supports text generation. The default is "google/flan-t5-base".

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.