#!/bin/bash

###############################################################################
# DevOS Installation Script
# Cross-platform AI-Native Developer Operating Layer
###############################################################################

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BOLD}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║   ██████╗ ███████╗██╗   ██╗ ██████╗ ███████╗           ║"
echo "║   ██╔══██╗██╔════╝██║   ██║██╔═══██╗██╔════╝           ║"
echo "║   ██║  ██║█████╗  ██║   ██║██║   ██║███████╗           ║"
echo "║   ██║  ██║██╔══╝  ╚██╗ ██╔╝██║   ██║╚════██║           ║"
echo "║   ██████╔╝███████╗ ╚████╔╝ ╚██████╔╝███████║           ║"
echo "║   ╚═════╝ ╚══════╝  ╚═══╝   ╚═════╝ ╚══════╝           ║"
echo "║                                                          ║"
echo "║   AI-Native Developer Operating Layer                   ║"
echo "║   Installer v0.1.0                                      ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Detect OS
OS=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo -e "${RED}Error: Unsupported operating system${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Detected OS: $OS${NC}"

# Check Python
echo ""
echo -e "${BOLD}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "  Please install Python 3.8 or higher from https://www.python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check Go
if ! command -v go &> /dev/null; then
    echo -e "${YELLOW}⚠ Go is not installed (optional for CLI)${NC}"
    echo "  You can install it from https://golang.org"
else
    GO_VERSION=$(go version | cut -d' ' -f3)
    echo -e "${GREEN}✓ Go $GO_VERSION found${NC}"
fi

# Check for Ollama (optional)
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama found (local LLM support enabled)${NC}"
else
    echo -e "${YELLOW}⚠ Ollama not found (install for local LLM support)${NC}"
    echo "  Install from: https://ollama.ai"
fi

# Install Python dependencies
echo ""
echo -e "${BOLD}Installing Python dependencies...${NC}"
pip3 install --upgrade pip
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install Python dependencies${NC}"
    exit 1
fi

# Build Go CLI (if Go is available)
if command -v go &> /dev/null; then
    echo ""
    echo -e "${BOLD}Building Go CLI...${NC}"
    cd core-cli
    go mod download
    go build -o ../bin/devos .
    cd ..
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Go CLI built successfully${NC}"
        
        # Add to PATH
        INSTALL_DIR="$HOME/.devos"
        mkdir -p "$INSTALL_DIR/bin"
        cp bin/devos "$INSTALL_DIR/bin/"
        
        # Add to shell profile
        SHELL_PROFILE=""
        if [ "$OS" = "macos" ]; then
            SHELL_PROFILE="$HOME/.zshrc"
        else
            SHELL_PROFILE="$HOME/.bashrc"
        fi
        
        if ! grep -q "export PATH=\$PATH:\$HOME/.devos/bin" "$SHELL_PROFILE"; then
            echo "" >> "$SHELL_PROFILE"
            echo "# DevOS CLI" >> "$SHELL_PROFILE"
            echo "export PATH=\$PATH:\$HOME/.devos/bin" >> "$SHELL_PROFILE"
            echo -e "${GREEN}✓ Added DevOS to PATH in $SHELL_PROFILE${NC}"
        fi
    else
        echo -e "${RED}✗ Failed to build Go CLI${NC}"
        echo "  Continuing with Python-only installation..."
    fi
fi

# Create config directory
echo ""
echo -e "${BOLD}Setting up configuration...${NC}"
if [ "$OS" = "macos" ]; then
    CONFIG_DIR="$HOME/Library/Application Support/devos"
else
    CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/devos"
fi

mkdir -p "$CONFIG_DIR"
mkdir -p "$CONFIG_DIR/plugins"
mkdir -p "$CONFIG_DIR/logs"

echo -e "${GREEN}✓ Configuration directory created: $CONFIG_DIR${NC}"

# Installation complete
echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║                                                          ║${NC}"
echo -e "${BOLD}${GREEN}║   ✓ Installation Complete!                              ║${NC}"
echo -e "${BOLD}${GREEN}║                                                          ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BOLD}Quick Start:${NC}"
echo "  1. Restart your terminal or run:"
echo "     source $SHELL_PROFILE"
echo ""
echo "  2. (Optional) Configure AI provider:"
echo "     Edit: $CONFIG_DIR/config.json"
echo "     Set your API key for OpenAI, Anthropic, or Gemini"
echo "     OR use local Ollama (default)"
echo ""
echo "  3. Run DevOS:"
echo "     devos"
echo ""
echo -e "${BOLD}Examples:${NC}"
echo "  devos> setup fastapi project with docker"
echo "  devos> analyze system performance"
echo "  devos> fix build error"
echo ""
echo -e "${YELLOW}Documentation: https://docs.devos.ai${NC}"
echo -e "${YELLOW}GitHub: https://github.com/devos-ai/devos${NC}"
echo ""
