#!/usr/bin/env python3
"""
Git Commit Agent - AI-powered git commit assistant using Gemini API
Analyzes staged files and creates structured commit messages
"""

import os
import sys
import re
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        # Set console to UTF-8 mode
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass  # Fallback to default encoding if UTF-8 setup fails

# Load environment variables from .env file
load_dotenv()

# Also load from global config if not set in environment
if not os.environ.get("GEMINI_API_KEY"):
    config_file = Path.home() / ".config" / "aicommit" / "config"
    if config_file.exists():
        load_dotenv(config_file)

# Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")


class GitCommitAgent:
    """Agent for creating structured git commits using Gemini AI"""

    @staticmethod
    def _get_default_instruction() -> str:
        """
        Load default instruction from template file

        Returns:
            Default instruction text
        """
        template_file = Path(__file__).parent / "instruction_template.txt"
        if template_file.exists():
            try:
                return template_file.read_text(encoding='utf-8')
            except Exception:
                pass

        # Fallback if template file doesn't exist
        return """You are a Git commit message expert assistant.
Your task is to analyze staged changes and create structured, meaningful commit messages.
Follow conventional commits format with emojis."""

    def __init__(self, repo_path: str):
        """
        Initialize the Git Commit Agent

        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = Path(repo_path)
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = GEMINI_MODEL
        self.system_instruction = self._load_system_instruction()

        # Validate repository
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {repo_path}")

    def _load_system_instruction(self) -> str:
        """
        Load system instruction from config file or use default

        Returns:
            System instruction text
        """
        config_file = Path.home() / ".config" / "aicommit" / "instruction.txt"

        if config_file.exists():
            try:
                return config_file.read_text(encoding='utf-8')
            except Exception as e:
                print(f"⚠️  Warning: Could not load instruction from {config_file}: {e}")
                print("Using default instruction...")

        return self._get_default_instruction()

    def has_staged_files(self) -> bool:
        """
        Check if there are any staged files

        Returns:
            True if there are staged files, False otherwise
        """
        try:
            # Use git diff --cached --quiet - exits with 1 if there are differences
            result = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=self.repo_path,
                capture_output=True
            )
            # Exit code 0 = no differences (nothing staged)
            # Exit code 1 = there are differences (files staged)
            return result.returncode == 1
        except subprocess.CalledProcessError:
            return False

    def get_git_status(self) -> dict:
        """
        Get current git status

        Returns:
            Dict with status information
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
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

                # First character = staged area status
                if status[0] in ['M', 'A', 'D', 'R', 'C'] and status[0] != ' ':
                    staged.append({'status': status[0], 'file': filepath})
                # Second character = working tree status
                if status[1] in ['M', 'D'] and status[1] != ' ':
                    unstaged.append({'status': status[1], 'file': filepath})
                # Untracked files
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
                encoding='utf-8',
                errors='replace',
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
                encoding='utf-8',
                errors='replace',
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
                encoding='utf-8',
                errors='replace',
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

    def process_commit(self, auto_confirm: bool = False, user_message: str = None) -> str:
        """
        Process staged files and create commit using Gemini AI

        Args:
            auto_confirm: If True, skip confirmation prompt
            user_message: Optional user-provided context/description

        Returns:
            Response message
        """

        # Early check for staged files - don't call AI if nothing to commit
        print("📊 Checking for staged files...")
        if not self.has_staged_files():
            return "⚠️  No staged files to commit"

        # Get detailed status
        status = self.get_git_status()
        if 'error' in status:
            return f"❌ Error getting git status: {status['error']}"

        # Get git information (status already checked above)
        diff = self.get_staged_diff()
        recent = self.get_recent_commits()

        # Prepare context for Gemini
        context_parts = []

        if user_message:
            context_parts.append(f"""## User's Context/Description:
{user_message}

IMPORTANT: The user provided this context to help you understand their intent. Use it to write a better commit message, but the final message must be in ENGLISH following the conventional commits format.
""")

        context_parts.append(f"""## Staged Files ({len(status['staged'])}):
{json.dumps(status['staged'], indent=2)}

## Diff:
{diff.get('diff', 'No diff available')[:5000]}

## Recent Commits (for style reference):
{json.dumps(recent.get('commits', []), indent=2)}

Based on this information, generate a commit message following the rules.""")

        context = "\n".join(context_parts)

        print("\n🤖 Analyzing changes with Gemini AI...")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=context,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.3,
                )
            )

            commit_message = response.text.strip()

            # Remove markdown code blocks if present
            if commit_message.startswith('```'):
                lines = commit_message.split('\n')
                commit_message = '\n'.join(lines[1:-1])

            # Remove <<MSG ... MSG>>, <<COMMIT_MSG ... COM>>, etc. wrappers
            # (Windows-specific Gemini API artifact)
            # Remove opening markers like <<MSG, <<COMMIT_MSG, etc.
            commit_message = re.sub(r'^<<[A-Z_]+\s*\n?', '', commit_message)
            # Remove closing markers like MSG>>, COM>>, COMMIT_MSG, etc.
            # Match optional whitespace, then uppercase/underscore word, optional >>, optional whitespace at end
            commit_message = re.sub(r'\n?[A-Z_]+>>?\s*$', '', commit_message)
            commit_message = commit_message.strip()

            print("\n📝 Generated commit message:")
            print("-" * 60)
            print(commit_message)
            print("-" * 60)

            # Ask for confirmation unless auto-confirm is enabled
            if not auto_confirm:
                print("\n❓ Create this commit? (y/n): ", end='')
                confirmation = input().strip().lower()
                if confirmation != 'y':
                    return "❌ Commit cancelled by user"

            result = self.create_commit(commit_message)
            if result.get('success'):
                return f"✅ Commit created successfully!\n{result['output']}"
            else:
                return f"❌ Failed to create commit:\n{result.get('error')}\n{result.get('output')}"

        except Exception as e:
            return f"❌ Error generating commit message: {str(e)}"


def open_config(config_type: str = "config"):
    """
    Open config file in platform-specific editor

    Args:
        config_type: Type of config to open ('config' or 'instruction')
    """
    import platform

    config_dir = Path.home() / ".config" / "aicommit"
    config_dir.mkdir(parents=True, exist_ok=True)

    if config_type == "instruction":
        config_file = config_dir / "instruction.txt"

        if not config_file.exists():
            print("⚠️  Instruction file not found. Creating with defaults...")
            config_file.write_text(GitCommitAgent._get_default_instruction())
            print(f"✅ Created default instruction at: {config_file}")
    else:
        config_file = config_dir / "config"

        if not config_file.exists():
            print("⚠️  Config file not found. Creating...")
            config_file.write_text("""# AI Commit Agent Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# Gemini Model (optional, default: gemini-2.5-pro)
# Available models: gemini-2.5-pro, gemini-2.5-flash, gemini-1.5-pro, gemini-1.5-flash
GEMINI_MODEL=gemini-2.5-pro
""")

    print(f"📝 Opening {config_file}...")

    # Open in platform-specific editor
    if platform.system() == "Windows":
        # Use notepad on Windows
        subprocess.run(["notepad", str(config_file)])
    else:
        # Use vim on macOS/Linux
        subprocess.run(["vim", str(config_file)])


def main():
    """Main entry point"""
    # Handle 'config' subcommand
    if len(sys.argv) > 1 and sys.argv[1] == "config":
        # Check for second argument (instruction or default to config)
        config_type = sys.argv[2] if len(sys.argv) > 2 else "config"
        if config_type not in ["config", "instruction"]:
            print(f"❌ Unknown config type: {config_type}")
            print("Usage: aicommit config [instruction]")
            sys.exit(1)
        open_config(config_type)
        return

    # Parse arguments
    auto_confirm = False
    repo_path = "."
    user_message = None
    i = 1

    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg in ['-y', '--yes']:
            auto_confirm = True
        elif arg in ['-m', '--message']:
            # Next argument is the message
            if i + 1 < len(sys.argv):
                user_message = sys.argv[i + 1]
                i += 1  # Skip next arg
            else:
                print("❌ Error: -m requires a message argument")
                sys.exit(1)
        elif not arg.startswith('-'):
            repo_path = arg

        i += 1

    try:
        agent = GitCommitAgent(repo_path)
        result = agent.process_commit(auto_confirm=auto_confirm, user_message=user_message)
        print(f"\n{result}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
