# AI Commit Agent 🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Gemini API](https://img.shields.io/badge/Gemini-2.5-orange.svg)](https://ai.google.dev/)

AI-powered git commit assistant using Google Gemini API. Analyzes your staged changes and generates structured, meaningful commit messages following conventional commits with emojis.

## 🎬 Demo

https://github.com/user-attachments/assets/845ad9d9-42e9-42ac-a364-69cd411af4ca

## Features

- 🔍 Analyzes staged files and diffs
- 🤖 Generates commit messages using Gemini AI
- 📝 Follows conventional commits format with emojis
- 📚 Learns from your recent commits
- ✅ Interactive confirmation before committing
- ⚡ Auto-commit mode with `-y` flag
- 💬 Add context with `-m` flag (supports any language)
- ⚙️ Easy config management with `aicommit config`
- 🎯 Smart: only calls AI if there are staged files

## Installation

```bash
# Clone the repository
git clone https://github.com/timurco/AiCommitAgent.git
cd AiCommitAgent

# Run installation script (installs dependencies and sets up global command)
./install.sh
```

The script will:
- Install Python dependencies globally
- Create `aicommit` command in `~/.local/bin`
- Generate config file at `~/.config/aicommit/config`

Then reload your shell:

```bash
source ~/.zshrc  # or ~/.bashrc for bash, or ~/.config/fish/config.fish for fish
```

Configure your API key:

```bash
aicommit config
```

Add your Gemini API key and preferred model:

```env
GEMINI_API_KEY=your_api_key_here

# Optional: Choose Gemini model (default: gemini-2.5-pro)
GEMINI_MODEL=gemini-2.5-flash
```

## Usage

### Global Command

After installation, use anywhere:

```bash
# Interactive mode (asks for confirmation)
aicommit

# Auto-commit mode (no confirmation)
aicommit -y

# Provide context/description for better commit message
aicommit -m "Added bunch of books and fixed headers"
aicommit -m "Добавил кучу книг, и исправил там заголовки"

# Combine flags
aicommit -y -m "Quick fix for typos"

# Specify repository path
aicommit /path/to/repo

# Open config in vim
aicommit config
```

## Commit Message Format

The agent follows this structure:

```
<emoji> <type>: <short description>

- Detailed point 1
- Detailed point 2
- Detailed point 3
```

### Types with Emojis

- ✨ `feat:` - New features
- 🐛 `fix:` - Bug fixes
- 📚 `docs:` - Documentation changes
- 🎨 `style:` - Code style/formatting
- ♻️ `refactor:` - Code refactoring
- 🧪 `test:` - Tests
- 🔧 `chore:` - Maintenance tasks
- 🏗️ `build:` - Build system changes
- ⚙️ `ci:` - CI/CD changes

## Examples

```
✨ feat: add MapConverter for URL conversion

- Add Node.js project structure
- Implement clipboard support for macOS
```

```
🐛 fix: correct gitignore corrupted entries

- Fix first line corruption
- Add Node.js patterns
- Remove duplicates
```

## How It Works

1. Checks if there are staged files (exits early if none)
2. Gets the diff (`git diff --cached`)
3. Analyzes recent commits for style reference
4. Sends context to Gemini AI only if there are changes
5. Generates commit message following the rules
6. Shows preview and asks for confirmation (unless `-y` flag)
7. Creates the commit

## Requirements

- Python 3.7+
- Git repository
- Google Gemini API key

## Troubleshooting

### "Not a git repository" error
Make sure you're in a git repository or provide a valid path.

### "No staged files to commit" warning
Stage your changes first with `git add`.

### API key not found
Make sure global config exists: `aicommit config` and add your `GEMINI_API_KEY`.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: [github.com/timurco/AiCommitAgent](https://github.com/timurco/AiCommitAgent)
- **Issues**: [github.com/timurco/AiCommitAgent/issues](https://github.com/timurco/AiCommitAgent/issues)
- **Gemini API**: [aistudio.google.com/api-keys](https://aistudio.google.com/api-keys)

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.
