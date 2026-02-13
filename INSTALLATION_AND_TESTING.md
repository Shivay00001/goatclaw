# DevOS - Complete Installation & Testing Guide

## 📋 Project Structure

Your DevOS installation contains:

```
devos/
├── core-cli/              # Go-based CLI (main entry point)
│   ├── main.go
│   ├── go.mod
│   └── internal/
│       ├── config/        # Configuration management
│       ├── executor/      # Command execution
│       └── logger/        # Logging system
│
├── ai-engine/             # Python AI reasoning core
│   ├── core/
│   │   └── processor.py   # Natural language processing
│   ├── adapters/
│   │   └── llm_adapter.py # Multi-LLM support
│   ├── security/
│   │   └── validator.py   # Security validation
│   └── plugins/
│       └── plugin_manager.py
│
├── adapters/              # OS-specific adapters
│   ├── windows/
│   ├── macos/
│   └── linux/
│
├── memory/                # Context persistence
│   └── store.py
│
├── plugins/               # Plugin system
│   └── community/
│       └── git-helper/    # Example plugin
│
├── installer/             # Installation scripts
│   ├── install.sh         # Unix/Linux/macOS
│   └── install.ps1        # Windows
│
├── docs/                  # Documentation
│   ├── EXAMPLES.md
│   ├── SECURITY.md
│   ├── ARCHITECTURE.md
│   └── QUICKSTART.md
│
├── setup.py               # Python package setup
├── requirements.txt       # Python dependencies
├── README.md              # Main documentation
└── LICENSE                # MIT License
```

## 🚀 Installation Instructions

### Step 1: Prerequisites

Install required software:

#### Python 3.8+ (Required)

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**macOS:**
```bash
brew install python3
```

**Windows:**
Download from https://www.python.org/downloads/

#### Go 1.21+ (Optional, for CLI)

**Linux:**
```bash
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
```

**macOS:**
```bash
brew install go
```

**Windows:**
Download from https://go.dev/dl/

#### Ollama (Optional, for local LLM)

**All Platforms:**
Visit https://ollama.ai and follow installation instructions.

Then pull a model:
```bash
ollama pull llama3.2
```

### Step 2: Install DevOS

Navigate to the devos directory and run the appropriate installer:

#### Linux/macOS:

```bash
cd devos
chmod +x installer/install.sh
./installer/install.sh
```

#### Windows:

```powershell
cd devos
PowerShell -ExecutionPolicy Bypass -File installer\install.ps1
```

#### Manual Installation:

If you prefer manual installation:

```bash
cd devos

# Install Python dependencies
pip3 install -r requirements.txt

# (Optional) Build Go CLI
cd core-cli
go mod download
go build -o devos .
cd ..

# Add to PATH
# Linux/macOS: Add to ~/.bashrc or ~/.zshrc
export PATH=$PATH:$PWD/core-cli

# Windows: Add to system PATH via Environment Variables
```

### Step 3: Configuration

After installation, edit the config file:

**Config File Locations:**
- Linux: `~/.config/devos/config.json`
- macOS: `~/Library/Application Support/devos/config.json`
- Windows: `%APPDATA%\devos\config.json`

**Default Configuration (Ollama):**
```json
{
  "os": "linux",
  "ai_provider": "ollama",
  "model": "llama3.2",
  "base_url": "http://localhost:11434",
  "confirmation_mode": true,
  "sandbox_mode": true,
  "log_level": "info",
  "max_tokens": 2048,
  "temperature": 0.7
}
```

**Cloud Provider Example (OpenAI):**
```json
{
  "os": "linux",
  "ai_provider": "openai",
  "model": "gpt-4",
  "api_key": "your-openai-api-key",
  "confirmation_mode": true,
  "sandbox_mode": true,
  "log_level": "info"
}
```

## 🧪 Testing DevOS

### Basic Functionality Tests

#### Test 1: Start DevOS

```bash
devos
```

Expected output:
```
╔══════════════════════════════════════════════════════════╗
║   DevOS Banner                                           ║
╚══════════════════════════════════════════════════════════╝

🚀 DevOS is ready. Type 'help' for commands or use natural language.

devos>
```

#### Test 2: Built-in Commands

```bash
devos> help
devos> version
devos> status
devos> config
```

Each should return appropriate information without errors.

#### Test 3: Natural Language Processing

**Test Project Setup:**
```bash
devos> setup fastapi project with docker
```

Expected behavior:
1. Shows execution plan
2. Lists commands to be executed
3. Asks for confirmation
4. Creates project structure

**Test System Analysis:**
```bash
devos> analyze system performance
```

Expected behavior:
1. Runs CPU, memory, disk checks
2. Displays formatted results

**Test Safe Operation:**
```bash
devos> show files in current directory
```

Expected behavior:
1. Lists directory contents
2. No confirmation needed (safe operation)

### Security Tests

#### Test 1: Blocked Command Detection

```bash
devos> delete everything from root
```

Expected behavior:
```
❌ Error: Blocked command pattern detected: rm -rf /
This command is not allowed for safety reasons.
```

#### Test 2: Confirmation Mode

```bash
devos> delete all log files
```

Expected behavior:
```
⚠️  This operation will delete files. Proceed? (yes/no):
```

#### Test 3: Risk Assessment

```bash
devos> create new file test.txt
```

Expected: No confirmation (safe operation)

```bash
devos> install system package
```

Expected: Confirmation required (high-risk operation)

### Plugin System Tests

#### Test Plugin Loading

```bash
# Should show git-helper plugin
devos> status
```

Look for: "Plugins Loaded: 1"

#### Test Plugin Execution

```bash
devos> git status
```

Expected: Git plugin provides enhanced status with analysis.

### Cross-Platform Tests

#### Windows-Specific

```powershell
devos> Get-Process
devos> check system info
devos> show environment variables
```

#### macOS-Specific

```bash
devos> show homebrew packages
devos> system profiler info
```

#### Linux-Specific

```bash
devos> show systemd services
devos> check package manager
devos> show network interfaces
```

## 🔧 Troubleshooting

### Issue: "Python module not found"

**Solution:**
```bash
pip3 install -r requirements.txt --force-reinstall
```

### Issue: "Cannot connect to Ollama"

**Solution:**
```bash
# Start Ollama server
ollama serve

# In another terminal, test:
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "test"
}'
```

### Issue: "Go build failed"

**Solution:**
```bash
cd core-cli
go mod tidy
go build -o devos .
```

### Issue: "Permission denied"

**Linux/macOS:**
```bash
chmod +x installer/install.sh
chmod +x core-cli/devos
```

**Windows:**
Run PowerShell as Administrator

### Issue: "Config file not found"

**Solution:**
```bash
# Create config directory
mkdir -p ~/.config/devos  # Linux
mkdir -p ~/Library/Application\ Support/devos  # macOS
mkdir %APPDATA%\devos  # Windows

# DevOS will create default config on first run
devos
```

## 🎯 Advanced Testing

### Load Testing

Create a test script:

```bash
#!/bin/bash
for i in {1..10}; do
  echo "Test iteration $i"
  echo "show files in current directory" | devos
done
```

### Memory Leak Testing

```bash
# Monitor DevOS memory usage
while true; do
  echo "show status" | devos
  ps aux | grep devos
  sleep 5
done
```

### Plugin Development Test

Create a test plugin in `~/.config/devos/plugins/test-plugin/`:

**manifest.json:**
```json
{
  "name": "test-plugin",
  "version": "0.1.0",
  "description": "Test plugin",
  "entry_point": "plugin.py",
  "permissions": ["execute_commands"]
}
```

**plugin.py:**
```python
from plugins.plugin_manager import PluginInterface

class Plugin(PluginInterface):
    @property
    def name(self): return "test-plugin"
    
    @property
    def version(self): return "0.1.0"
    
    @property
    def description(self): return "Test plugin"
    
    def initialize(self, config): pass
    
    def execute(self, context):
        return {
            'success': True,
            'output': 'Test plugin executed!',
            'commands': []
        }
    
    def get_commands(self):
        return ['test']
```

Test it:
```bash
devos> test plugin
```

## 📊 Performance Benchmarks

Expected performance on modern hardware:

| Operation | Expected Time |
|-----------|--------------|
| CLI Startup | < 50ms |
| Config Load | < 10ms |
| Command Parse | < 5ms |
| AI Query (Ollama) | < 2s |
| AI Query (Cloud) | 1-3s |
| File Operation | 10-100ms |

Test startup time:
```bash
time devos --version
```

## 🔐 Security Verification

### Verify Security Features

1. **Test Blocked Commands:**
```bash
devos> rm -rf /
# Should be blocked
```

2. **Test Confirmation Mode:**
```bash
devos> delete important file
# Should ask for confirmation
```

3. **Test Sandbox:**
```bash
devos> access system files
# Should be restricted
```

4. **Check Logs:**
```bash
tail -f ~/.local/share/devos/logs/devos-*.log
```

All commands should be logged.

## 📝 Development Workflow

### Making Changes

1. **Modify Python code:**
```bash
# Edit files in ai-engine/
nano ai-engine/core/processor.py

# No rebuild needed, changes take effect immediately
```

2. **Modify Go code:**
```bash
# Edit files in core-cli/
nano core-cli/main.go

# Rebuild:
cd core-cli
go build -o devos .
```

3. **Test changes:**
```bash
./core-cli/devos
```

### Running Tests

**Python tests (if you add them):**
```bash
pytest tests/
```

**Go tests:**
```bash
cd core-cli
go test ./...
```

## 🎓 Learning Resources

1. **Read Documentation:**
   - `docs/QUICKSTART.md` - Quick start guide
   - `docs/EXAMPLES.md` - Usage examples
   - `docs/SECURITY.md` - Security features
   - `docs/ARCHITECTURE.md` - System architecture

2. **Explore Code:**
   - Start with `core-cli/main.go`
   - Then `ai-engine/core/processor.py`
   - Check out OS adapters for platform-specific code

3. **Experiment:**
   - Try different natural language commands
   - Create custom plugins
   - Modify security rules

## 🤝 Contributing

To contribute to DevOS:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Getting Help

- 📖 Documentation: All docs in `docs/` folder
- 🐛 Issues: Report bugs via GitHub issues
- 💬 Community: Join Discord for discussions
- 📧 Email: support@devos.ai

## ✅ Final Checklist

Before using DevOS in production:

- [ ] Python 3.8+ installed
- [ ] Go 1.21+ installed (optional)
- [ ] Ollama installed and running (if using local LLM)
- [ ] DevOS installed successfully
- [ ] Config file created and edited
- [ ] Basic commands work
- [ ] Security features tested
- [ ] Logs are being created
- [ ] Documentation read

## 🎉 You're Ready!

DevOS is now installed and tested. Start with simple commands and gradually explore more features.

```bash
devos> Let's build something amazing!
```

---

**Remember:** DevOS is a powerful tool. Always:
- Review commands before execution
- Keep confirmation mode enabled
- Understand what each command does
- Don't blindly trust AI output

**Happy coding! 🚀**
