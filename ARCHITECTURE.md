# DevOS Architecture

## System Overview

DevOS is a cross-platform AI-native developer orchestration layer that translates natural language commands into safe, validated system operations. It consists of two main components working in tandem:

1. **Go-based CLI Control Engine** - Fast, efficient command-line interface
2. **Python-based AI Reasoning Core** - Flexible AI integration and command processing

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (Terminal/Shell/CLI)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Go CLI Control Engine                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Config     │  │    Logger    │  │   Executor   │         │
│  │  Management  │  │  Structured  │  │   Command    │         │
│  │              │  │   Logging    │  │  Execution   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ JSON-RPC / Process
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              Python AI Reasoning Core                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Natural Language Processor                  │  │
│  │  • Intent Classification                                │  │
│  │  • Command Generation                                   │  │
│  │  • Context Management                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  LLM Adapters                            │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
│  │  │  Ollama  │ │  OpenAI  │ │ Anthropic│ │  Gemini  │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Security Validator                          │  │
│  │  • Pattern Matching                                     │  │
│  │  • Risk Assessment                                      │  │
│  │  • Command Sanitization                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                Plugin System                             │  │
│  │  • Plugin Manager                                       │  │
│  │  • Dynamic Loading                                      │  │
│  │  • Permission Control                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OS Adapters                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Windows    │  │    macOS     │  │    Linux     │         │
│  │   Adapter    │  │   Adapter    │  │   Adapter    │         │
│  │              │  │              │  │              │         │
│  │  PowerShell  │  │     zsh      │  │     bash     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Memory & Context Store                         │
│                     (SQLite Database)                           │
│  • Command History                                              │
│  • Project Context                                              │
│  • User Preferences                                             │
│  • Execution Results                                            │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Go CLI Control Engine

**Purpose:** Fast, efficient command-line interface and system interaction

**Modules:**

#### main.go
- Entry point and CLI initialization
- Interactive REPL loop
- Built-in command handling
- User interface rendering

#### config/config.go
- Configuration management
- Platform-specific paths
- Settings persistence
- Validation

#### executor/executor.go
- Command execution coordination
- Python AI engine integration
- Command validation
- Security enforcement

#### logger/logger.go
- Structured logging
- Multi-level logging (DEBUG, INFO, WARN, ERROR)
- File and console output
- Performance tracking

**Technology Stack:**
- Language: Go 1.21+
- Dependencies: Standard library only
- Build: Native compilation

**Advantages:**
- ⚡ Fast startup time (~10ms)
- 📦 Single binary distribution
- 🔒 Memory safe
- 🌐 Cross-platform compilation

### 2. Python AI Reasoning Core

**Purpose:** AI-powered command interpretation and generation

**Modules:**

#### core/processor.py
- Natural language understanding
- Intent classification
- Command generation
- Multi-step planning

**Intent Categories:**
```python
INTENTS = {
    'project_setup': ['setup', 'create', 'init', 'scaffold'],
    'debug': ['fix', 'debug', 'error', 'problem'],
    'analyze': ['analyze', 'check', 'inspect', 'performance'],
    'install': ['install', 'add', 'dependency'],
    'build': ['build', 'compile', 'make'],
    'deploy': ['deploy', 'push', 'release'],
    'test': ['test', 'run tests']
}
```

#### adapters/llm_adapter.py
- Unified LLM interface
- Provider abstraction
- Error handling
- Retry logic

**Supported Providers:**
1. **Ollama** (Local, Free)
   - Models: llama3.2, codellama, mistral
   - Endpoint: http://localhost:11434

2. **OpenAI**
   - Models: gpt-4, gpt-3.5-turbo
   - Endpoint: https://api.openai.com/v1

3. **Anthropic**
   - Models: claude-3-opus, claude-3-sonnet
   - Endpoint: https://api.anthropic.com/v1

4. **Google Gemini**
   - Models: gemini-pro, gemini-ultra
   - Endpoint: https://generativelanguage.googleapis.com/v1beta

#### security/validator.py
- Pattern-based validation
- Risk level assessment
- Command sanitization
- Sandbox environment preparation

**Risk Levels:**
```python
class RiskLevel(Enum):
    SAFE = 1      # No risk
    LOW = 2       # Minimal risk
    MEDIUM = 3    # Requires awareness
    HIGH = 4      # Requires confirmation
    CRITICAL = 5  # Blocked
```

#### plugins/plugin_manager.py
- Dynamic plugin discovery
- Plugin lifecycle management
- Permission enforcement
- Manifest validation

**Technology Stack:**
- Language: Python 3.8+
- Dependencies: requests, click
- Optional: openai, anthropic, google-generativeai

### 3. OS Adapters

**Purpose:** Platform-specific command execution and system operations

#### Windows Adapter (adapters/windows/windows_adapter.py)
- PowerShell integration
- Windows API access
- Registry operations
- Service management

**Key Features:**
- WMI (Windows Management Instrumentation)
- PowerShell cmdlet execution
- Environment variable management
- Process control

#### macOS Adapter (adapters/macos/mac_adapter.py)
- zsh/bash integration
- Homebrew package management
- System profiler access
- Service control (launchctl)

**Key Features:**
- Homebrew integration
- System profiler data
- Apple Silicon support
- Native commands

#### Linux Adapter (adapters/linux/linux_adapter.py)
- bash integration
- Package manager detection (apt, yum, dnf, pacman)
- systemd service management
- Distribution detection

**Key Features:**
- Multi-distro support
- Package manager abstraction
- systemd integration
- Network management

### 4. Memory & Context Store

**Purpose:** Persistent storage for command history and context

**Database Schema:**

```sql
-- Command History
CREATE TABLE command_history (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    user_input TEXT NOT NULL,
    intent TEXT,
    commands TEXT,
    success BOOLEAN,
    output TEXT,
    error TEXT,
    metadata TEXT
);

-- Context Store
CREATE TABLE context_store (
    id INTEGER PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    category TEXT,
    timestamp TEXT NOT NULL,
    metadata TEXT
);

-- Project Context
CREATE TABLE project_context (
    id INTEGER PRIMARY KEY,
    project_path TEXT UNIQUE NOT NULL,
    project_type TEXT,
    dependencies TEXT,
    last_updated TEXT NOT NULL,
    metadata TEXT
);
```

**Technology Stack:**
- Database: SQLite 3
- Location: Platform-specific config directory
- Size: ~10MB typical, max 100MB

### 5. Plugin System

**Architecture:**

```python
class PluginInterface(ABC):
    @property
    def name(self) -> str: pass
    
    @property
    def version(self) -> str: pass
    
    def initialize(self, config: Dict): pass
    
    def execute(self, context: Dict) -> Dict: pass
    
    def get_commands(self) -> List[str]: pass
```

**Plugin Lifecycle:**

```
┌────────────┐
│  Discover  │  Scan plugins directory
└─────┬──────┘
      │
      ▼
┌────────────┐
│   Load     │  Parse manifest, import module
└─────┬──────┘
      │
      ▼
┌────────────┐
│ Initialize │  Call plugin.initialize()
└─────┬──────┘
      │
      ▼
┌────────────┐
│  Execute   │  Call plugin.execute()
└─────┬──────┘
      │
      ▼
┌────────────┐
│  Unload    │  Cleanup and remove
└────────────┘
```

**Plugin Manifest Format:**

```json
{
  "name": "plugin-name",
  "version": "0.1.0",
  "description": "Plugin description",
  "author": "Author name",
  "entry_point": "plugin.py",
  "permissions": [
    "execute_commands",
    "read_filesystem",
    "write_filesystem",
    "network_access"
  ],
  "dependencies": ["requests", "pandas"],
  "config": {
    "setting1": "value1"
  }
}
```

## Data Flow

### Command Execution Flow

```
1. User Input
   ↓
2. CLI Parse & Validate
   ↓
3. Call Python Processor
   ↓
4. Intent Classification
   ↓
5. LLM Query (if needed)
   ↓
6. Command Generation
   ↓
7. Security Validation
   ↓
8. User Confirmation (if needed)
   ↓
9. OS Adapter Execution
   ↓
10. Result Logging
    ↓
11. Display to User
```

### Security Validation Flow

```
Command String
    ↓
[Pattern Matching]
    ↓
Critical? → BLOCK
    ↓
High Risk? → CONFIRM
    ↓
Medium Risk? → WARN
    ↓
[Sanitization]
    ↓
[Sandbox Preparation]
    ↓
Execute
```

## Configuration Files

### Primary Config (config.json)

```json
{
  "os": "linux",
  "ai_provider": "ollama",
  "model": "llama3.2",
  "api_key": "",
  "base_url": "http://localhost:11434",
  "confirmation_mode": true,
  "log_level": "info",
  "max_tokens": 2048,
  "temperature": 0.7,
  "sandbox_mode": true,
  "blocked_commands": [
    "rm -rf /",
    "mkfs",
    "format"
  ],
  "plugins": ["git-helper"],
  "memory_size": 100
}
```

### Platform-Specific Paths

**Windows:**
- Config: `%APPDATA%\devos\config.json`
- Logs: `%APPDATA%\devos\logs\`
- Memory: `%APPDATA%\devos\memory.db`
- Plugins: `%APPDATA%\devos\plugins\`

**macOS:**
- Config: `~/Library/Application Support/devos/config.json`
- Logs: `~/Library/Logs/devos/`
- Memory: `~/Library/Application Support/devos/memory.db`
- Plugins: `~/Library/Application Support/devos/plugins/`

**Linux:**
- Config: `~/.config/devos/config.json`
- Logs: `~/.local/share/devos/logs/`
- Memory: `~/.config/devos/memory.db`
- Plugins: `~/.config/devos/plugins/`

## Performance Characteristics

### Latency Targets

| Operation | Target | Typical |
|-----------|--------|---------|
| CLI Startup | <50ms | ~10ms |
| Config Load | <10ms | ~2ms |
| Command Parse | <5ms | ~1ms |
| AI Query (Local) | <2s | ~500ms |
| AI Query (Cloud) | <5s | ~1-2s |
| Command Execute | Varies | 10ms-10s |
| Log Write | <1ms | ~0.1ms |

### Resource Usage

| Component | Memory | CPU |
|-----------|--------|-----|
| Go CLI | 5-10MB | <1% |
| Python Engine | 50-100MB | <5% |
| Ollama (if running) | 2-8GB | 10-50% |
| Memory DB | 1-10MB | <1% |

## Scalability

### Current Limitations

- Single-user design
- Synchronous execution
- Local context only
- Single command at a time

### Future Enhancements

- Multi-user support
- Parallel execution
- Distributed context
- Command queuing
- Remote execution

## Security Model

### Trust Boundaries

```
User → CLI → Validator → OS Adapter → System
 [Trusted]  [Trust But Verify]  [Untrusted]
```

### Threat Mitigation

| Threat | Mitigation |
|--------|------------|
| Malicious AI Output | Pattern matching, blocklist |
| User Error | Confirmation, validation |
| Privilege Escalation | Sandbox, permission checks |
| Code Injection | Input sanitization |
| Data Exfiltration | Network monitoring (planned) |

## Testing Strategy

### Unit Tests
- Go: `go test ./...`
- Python: `pytest tests/`

### Integration Tests
- End-to-end command execution
- Multi-platform testing
- Plugin loading tests

### Security Tests
- Blocked command verification
- Risk assessment validation
- Sandbox escape attempts

## Deployment

### Build Process

```bash
# Go CLI
cd core-cli
go build -o devos .

# Python Package
python setup.py sdist bdist_wheel

# Distribution
# - Binary: devos (Go executable)
# - Package: devos-ai (Python package)
```

### Installation Methods

1. **Script Installer** (Recommended)
   - Auto-detects OS
   - Installs dependencies
   - Configures PATH

2. **Package Manager**
   - `pip install devos-ai`
   - `go install devos-cli`

3. **Manual**
   - Clone repository
   - Build from source

## Monitoring & Observability

### Logging Levels

```go
DEBUG → Detailed execution info
INFO  → Normal operations
WARN  → Potential issues
ERROR → Failures
```

### Metrics (Planned)

- Commands per minute
- Success rate
- Latency distribution
- Error frequency
- AI token usage

### Audit Trail

All operations logged to:
- File: `devos-YYYY-MM-DD.log`
- Database: `command_history` table

## Contributing

### Architecture Guidelines

1. **Separation of Concerns**
   - Go handles system interaction
   - Python handles AI logic
   - Adapters handle OS specifics

2. **Security First**
   - Validate all inputs
   - Sandbox by default
   - Log everything

3. **Platform Independence**
   - Test on all OSes
   - Use adapters for OS-specific code
   - Abstract file paths

4. **Performance**
   - Keep CLI fast (<50ms startup)
   - Lazy load heavy components
   - Cache when appropriate

## Future Roadmap

### Phase 2 Features
- Multi-agent coordination
- Advanced error recovery
- IDE integration
- VS Code extension
- Team collaboration features

### Phase 3 Features
- Cloud sync
- Remote execution
- Web interface
- Mobile app

---

**Last Updated:** 2024
**Version:** 0.1.0
