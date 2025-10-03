#!/usr/bin/env python3
"""
Git Commit Agent - AI-powered git commit assistant using Gemini API
Analyzes staged files and creates structured commit messages
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")


class GitCommitAgent:
    """Agent for creating structured git commits using Gemini AI"""

    def __init__(self, repo_path: str):
        """
        Initialize the Git Commit Agent

        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = Path(repo_path)
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = GEMINI_MODEL

        # Validate repository
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {repo_path}")

    def get_git_status(self) -> dict:
        """
        Get current git status

        Returns:
            Dict with status information
        """
        print("📊 Checking git status...")
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            staged = []
            unstaged = []
            untracked = []

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                status = line[:2]
                filepath = line[3:]

                if status[0] in ['M', 'A', 'D', 'R', 'C']:
                    staged.append({'status': status[0], 'file': filepath})
                if status[1] in ['M', 'D']:
                    unstaged.append({'status': status[1], 'file': filepath})
                if status == '??':
                    untracked.append(filepath)

            return {
                'staged': staged,
                'unstaged': unstaged,
                'untracked': untracked
            }
        except subprocess.CalledProcessError as e:
            return {'error': str(e)}

    def get_staged_diff(self) -> dict:
        """
        Get diff of staged files

        Returns:
            Dict with diff information
        """
        print("🔍 Analyzing staged changes...")
        try:
            result = subprocess.run(
                ["git", "diff", "--cached"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            return {
                'diff': result.stdout,
                'lines': len(result.stdout.split('\n'))
            }
        except subprocess.CalledProcessError as e:
            return {'error': str(e)}

    def get_recent_commits(self, count: int = 2) -> dict:
        """
        Get recent commit messages for style reference

        Args:
            count: Number of recent commits to retrieve

        Returns:
            Dict with commit history
        """
        print(f"📚 Reading last {count} commits for style reference...")
        try:
            result = subprocess.run(
                ["git", "log", f"-{count}", "--pretty=format:%s%n%b%n---"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            commits = [c.strip() for c in result.stdout.split('---') if c.strip()]

            return {
                'commits': commits,
                'count': len(commits)
            }
        except subprocess.CalledProcessError as e:
            return {'error': str(e)}

    def create_commit(self, message: str) -> dict:
        """
        Create a git commit with the provided message

        Args:
            message: Commit message

        Returns:
            Dict with commit result
        """
        print("💾 Creating commit...")
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            return {
                'success': True,
                'output': result.stdout
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': str(e),
                'output': e.stderr
            }

    def process_commit(self) -> str:
        """
        Process staged files and create commit using Gemini AI

        Returns:
            Response message
        """

        system_instruction = """You are a Git commit message expert assistant.

Your task is to analyze staged changes and create structured, meaningful commit messages.

## Commit Message Rules:

### Format:
- Use heredoc format for multiline messages
- All messages MUST be in English
- Follow conventional commits with emojis

### Types with emojis:
- ✨ feat: - New features
- 🐛 fix: - Bug fixes
- 📚 docs: - Documentation changes
- 🎨 style: - Code style/formatting
- ♻️ refactor: - Code refactoring
- 🧪 test: - Tests
- 🔧 chore: - Maintenance tasks
- 🏗️ build: - Build system changes
- ⚙️ ci: - CI/CD changes

### Message Structure:
```
<emoji> <type>: <short description>

- Detailed point 1
- Detailed point 2
- Detailed point 3
```

### Examples:
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

## Analysis Strategy:
1. Review the diff carefully
2. Identify the main purpose of changes
3. List specific modifications
4. Choose appropriate type and emoji
5. Write clear, concise message

## CRITICAL:
- NEVER add "Generated with Claude Code" or similar AI attribution
- Focus on WHAT changed and WHY
- Be specific but concise
- Use bullet points for details
"""

        # Get git information
        status = self.get_git_status()
        diff = self.get_staged_diff()
        recent = self.get_recent_commits()

        if 'error' in status:
            return f"❌ Error getting git status: {status['error']}"

        if not status['staged']:
            return "⚠️  No staged files to commit"

        # Prepare context for Gemini
        context = f"""## Staged Files ({len(status['staged'])}):
{json.dumps(status['staged'], indent=2)}

## Diff:
{diff.get('diff', 'No diff available')[:5000]}

## Recent Commits (for style reference):
{json.dumps(recent.get('commits', []), indent=2)}

Based on this information, generate a commit message following the rules."""

        print("\n🤖 Analyzing changes with Gemini AI...")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=context,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                )
            )

            commit_message = response.text.strip()

            # Remove markdown code blocks if present
            if commit_message.startswith('```'):
                lines = commit_message.split('\n')
                commit_message = '\n'.join(lines[1:-1])

            print("\n📝 Generated commit message:")
            print("-" * 60)
            print(commit_message)
            print("-" * 60)

            # Ask for confirmation
            print("\n❓ Create this commit? (y/n): ", end='')
            confirmation = input().strip().lower()

            if confirmation == 'y':
                result = self.create_commit(commit_message)
                if result.get('success'):
                    return f"✅ Commit created successfully!\n{result['output']}"
                else:
                    return f"❌ Failed to create commit:\n{result.get('error')}\n{result.get('output')}"
            else:
                return "❌ Commit cancelled by user"

        except Exception as e:
            return f"❌ Error generating commit message: {str(e)}"


def main():
    """Main entry point"""
    import sys

    # Get repo path from command line or use current directory
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."

    try:
        agent = GitCommitAgent(repo_path)
        result = agent.process_commit()
        print(f"\n{result}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
