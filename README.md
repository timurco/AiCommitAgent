# AI Commit Agent 🤖

AI-powered git commit assistant using Google Gemini API. Analyzes your staged changes and generates structured, meaningful commit messages following conventional commits with emojis.

## Features

- 🔍 Analyzes staged files and diffs
- 🤖 Generates commit messages using Gemini AI
- 📝 Follows conventional commits format with emojis
- 📚 Learns from your recent commits
- ✅ Interactive confirmation before committing

## Installation

### 1. Install Dependencies

```bash
cd /Users/timurko/Code/_bots/02_AiCommitAgent
pip install -r requirements.txt
```

### 2. Set Up API Key

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here

# Optional: Choose Gemini model (default: gemini-2.5-pro)
GEMINI_MODEL=gemini-2.5-flash
```

### 3. Install Global Alias

```bash
./install.sh
```

Then reload your shell:

```bash
# For zsh
source ~/.zshrc

# For bash
source ~/.bashrc

# For fish
source ~/.config/fish/config.fish
```

## Usage

### Global Command

After installation, use anywhere:

```bash
# In any git repository
aicommit

# Or specify a repository path
aicommit /path/to/repo
```

### Direct Python

```bash
python git_commit_agent.py
python git_commit_agent.py /path/to/repo
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

1. Checks your staged files (`git status --porcelain`)
2. Gets the diff (`git diff --cached`)
3. Analyzes recent commits for style reference
4. Sends context to Gemini AI
5. Generates commit message following the rules
6. Shows preview and asks for confirmation
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
Make sure `.env` file exists and contains `GEMINI_API_KEY`.

## License

MIT
