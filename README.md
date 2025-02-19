# Recursive Intelligence Loop

A Python-based tool for conducting recursive intelligence self-optimization loops using AI language models. The system maintains structured conversations with AI models while preserving context and iteration history.

## Features

- Interactive conversations with AI models via OpenRouter API
- Automatic conversation logging with both XML and human-readable formats
- Session persistence and resumption
- Iterative conversation tracking
- Atomic file operations for reliable chat storage
- Support for external text editor integration

## Requirements

- Python 3.8 or higher
- OpenRouter API key
- Text editor (default: kwrite)

## Installation

This project uses [rye](https://rye-up.com/) for dependency management:

```bash
# Clone the repository
git clone https://github.com/wizzardx/recursive-intelligence-loop.git
cd recursive-intelligence-loop

# Install dependencies
rye sync
```

## Configuration

1. Create a `.env` file in the project root:
```env
OPENROUTER_API_KEY=your_api_key_here
```

2. (Optional) Modify the default editor in `loop.py` if you don't use kwrite:
```python
EDITOR = "your_preferred_editor"
```

## Usage

Run the main script:

```bash
./run.sh
```

This will:
1. Sync dependencies
2. Format code with black
3. Run type checking
4. Start the intelligence loop

The system will either:
- Start a new conversation session, or
- Allow you to resume one of up to 5 most recent sessions

Chat logs are stored in the `chat_logs` directory in markdown format with embedded XML data.

## Project Structure

- `loop.py`: Main application logic
- `run.sh`: Convenience script for running the application
- `chat_logs/`: Directory containing conversation history
- `.env`: Configuration file for API keys

## Development

Type checking enforced with:
- mypy (strict mode)
- typeguard runtime checking

Code formatting using:
- black

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

