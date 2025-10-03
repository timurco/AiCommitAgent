#!/bin/bash

# AI Commit Agent - Global Installation Script

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
AGENT_SCRIPT="$SCRIPT_DIR/git_commit_agent.py"

echo "🤖 Installing AI Commit Agent..."

# Check if script exists
if [ ! -f "$AGENT_SCRIPT" ]; then
    echo "❌ Error: $AGENT_SCRIPT not found"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip3 install -q -r "$SCRIPT_DIR/requirements.txt"
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found, installing manually..."
    pip3 install -q google-genai python-dotenv
fi

# Make script executable
chmod +x "$AGENT_SCRIPT"

# Create wrapper script in ~/.local/bin
INSTALL_BIN="$HOME/.local/bin"
WRAPPER_SCRIPT="$INSTALL_BIN/aicommit"

# Create ~/.local/bin if it doesn't exist
mkdir -p "$INSTALL_BIN"

# Create wrapper script
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash

# AI Commit Agent Wrapper
# Automatically loads GEMINI_API_KEY from ~/.config/aicommit/config or from environment

# Check for API key in environment first
if [ -z "\$GEMINI_API_KEY" ]; then
    # Try to load from global config
    CONFIG_FILE="\$HOME/.config/aicommit/config"
    if [ -f "\$CONFIG_FILE" ]; then
        export \$(grep -v '^#' "\$CONFIG_FILE" | xargs)
    fi
fi

# Run the agent with Python
python3 "$AGENT_SCRIPT" "\$@"
EOF

chmod +x "$WRAPPER_SCRIPT"

# Create config directory and example config
CONFIG_DIR="$HOME/.config/aicommit"
mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_DIR/config" ]; then
    cat > "$CONFIG_DIR/config" << 'EOF'
# AI Commit Agent Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# Gemini Model (optional, default: gemini-2.5-pro)
# Available models: gemini-2.5-pro, gemini-2.5-flash, gemini-1.5-pro, gemini-1.5-flash
GEMINI_MODEL=gemini-2.5-pro
EOF
    echo "📝 Created config file: $CONFIG_DIR/config"
    echo "   Please edit it (\`aicommit config\`) and add your GEMINI_API_KEY"
fi

# Detect shell and update PATH if needed
SHELL_NAME=$(basename "$SHELL")

case "$SHELL_NAME" in
    zsh)
        SHELL_RC="$HOME/.zshrc"
        ;;
    bash)
        SHELL_RC="$HOME/.bashrc"
        ;;
    fish)
        SHELL_RC="$HOME/.config/fish/config.fish"
        ;;
    *)
        echo "⚠️  Unknown shell: $SHELL_NAME"
        echo "Please add ~/.local/bin to your PATH manually"
        exit 0
        ;;
esac

# Check if ~/.local/bin is already in PATH configuration
if grep -q '\.local/bin' "$SHELL_RC" 2>/dev/null; then
    echo "✅ ~/.local/bin already in PATH in $SHELL_RC"
else
    echo "" >> "$SHELL_RC"
    echo "# Add ~/.local/bin to PATH" >> "$SHELL_RC"
    if [ "$SHELL_NAME" = "fish" ]; then
        echo 'set -gx PATH $HOME/.local/bin $PATH' >> "$SHELL_RC"
    else
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    fi
    echo "✅ Added ~/.local/bin to PATH in $SHELL_RC"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "📍 Installed to: $WRAPPER_SCRIPT"
echo "⚙️  Config file: $CONFIG_DIR/config"
echo ""
echo "Next steps:"
echo "1. Edit config file and add your GEMINI_API_KEY:"
echo "   aicommit config"
echo ""
echo "2. Reload your shell:"
echo "   source $SHELL_RC"
echo ""
echo "3. Use anywhere:"
echo "   aicommit              # In current directory"
echo "   aicommit /path/to/repo  # In specific repository"
