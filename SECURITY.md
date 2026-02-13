# DevOS Security Guide

## Table of Contents

- [Overview](#overview)
- [Security Architecture](#security-architecture)
- [Command Validation](#command-validation)
- [Sandbox Execution](#sandbox-execution)
- [Risk Levels](#risk-levels)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Threat Model](#threat-model)

## Overview

DevOS implements a multi-layered security approach to protect your system while providing AI-powered automation. This document explains the security features and how to use them effectively.

### Core Security Principles

1. **Defense in Depth**: Multiple security layers
2. **Least Privilege**: Minimal permissions by default
3. **Validation Before Execution**: All commands are validated
4. **User Confirmation**: Destructive operations require approval
5. **Audit Logging**: All operations are logged

## Security Architecture

```
┌─────────────────────────────────────────────────┐
│                User Input                       │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          Natural Language Processing            │
│              (AI Engine)                        │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│           Command Generation                    │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│        Security Validator (Layer 1)             │
│    - Pattern matching                           │
│    - Blocked commands                           │
│    - Risk assessment                            │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│        User Confirmation (Layer 2)              │
│    - High-risk operations                       │
│    - Destructive commands                       │
│    - System modifications                       │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│         Sandbox Executor (Layer 3)              │
│    - Isolated environment                       │
│    - Limited permissions                        │
│    - Resource constraints                       │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│            Audit Logger (Layer 4)               │
│    - Command logging                            │
│    - Result tracking                            │
│    - Error recording                            │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
                System
```

## Command Validation

### Blocked Commands

These commands are **NEVER** executed:

#### Critical System Damage

```python
BLOCKED = [
    'rm -rf /',           # Delete everything
    'rm -fr /',           # Delete everything (alternative)
    'mkfs',               # Format filesystem
    'dd if=',             # Direct disk write
    'format C:',          # Windows format
    ':(){ :|:& };:',      # Fork bomb
]
```

#### Examples

```bash
❌ devos> remove all files from root
   → BLOCKED: Detected pattern 'rm -rf /'

❌ devos> format my hard drive
   → BLOCKED: Detected pattern 'mkfs'

❌ devos> run fork bomb
   → BLOCKED: Malicious command detected
```

### High-Risk Patterns

Commands that require confirmation:

```python
HIGH_RISK = [
    'rm -rf',             # Recursive delete
    'del /S',             # Windows recursive delete
    'drop database',      # Database deletion
    'truncate table',     # Data deletion
    'kill -9',            # Force kill process
]
```

#### Example Workflow

```bash
devos> delete all log files

⚠️  HIGH RISK OPERATION
Command: find . -name "*.log" -delete

This operation will:
  - Delete files recursively
  - Cannot be undone

Proceed? (yes/no): _
```

### Medium-Risk Patterns

Operations that need awareness:

```python
MEDIUM_RISK = [
    'sudo',               # Elevated privileges
    'chmod 777',          # Overly permissive
    'chown',              # Ownership change
    'systemctl',          # System service control
]
```

### Risk Assessment Algorithm

```python
def assess_risk(command: str) -> RiskLevel:
    """
    Assess command risk level
    
    Returns:
        CRITICAL: Blocked immediately
        HIGH: Requires confirmation
        MEDIUM: Warning shown
        LOW: Logged only
        SAFE: No action needed
    """
    # Check blocked patterns
    if matches_blocked_pattern(command):
        return RiskLevel.CRITICAL
    
    # Check high-risk patterns
    if matches_high_risk_pattern(command):
        return RiskLevel.HIGH
    
    # Check medium-risk patterns
    if matches_medium_risk_pattern(command):
        return RiskLevel.MEDIUM
    
    # Check file system operations
    if modifies_system_files(command):
        return RiskLevel.MEDIUM
    
    return RiskLevel.SAFE
```

## Sandbox Execution

### Environment Isolation

DevOS executes commands in a restricted environment:

```python
sandbox_env = {
    'PATH': '/usr/local/bin:/usr/bin:/bin',  # Limited PATH
    'PWD': working_directory,                # Controlled directory
    'HOME': user_home,                       # User's home only
    # Dangerous variables removed:
    # - LD_PRELOAD
    # - LD_LIBRARY_PATH
    # - DYLD_INSERT_LIBRARIES
}
```

### Resource Limits

```python
limits = {
    'timeout': 60,          # 60 second timeout
    'max_output': 10_000,   # 10KB output limit
    'max_memory': 512_000,  # 512MB memory limit
}
```

### Permission Restrictions

By default, sandbox mode:

- ✅ Can read user files
- ✅ Can write to project directories
- ✅ Can execute user-installed tools
- ❌ Cannot modify system files
- ❌ Cannot access other users' files
- ❌ Cannot change system settings

## Risk Levels

### Level 1: SAFE ✅

**Characteristics:**
- Read-only operations
- Status checks
- Information retrieval

**Examples:**
```bash
devos> show git status
devos> list directory contents
devos> check system uptime
```

**Security Actions:**
- None required
- Logged for audit

### Level 2: LOW ⚠️

**Characteristics:**
- File creation
- Non-destructive writes
- User-space operations

**Examples:**
```bash
devos> create new file
devos> write to log file
devos> install npm package
```

**Security Actions:**
- Logged
- No confirmation needed

### Level 3: MEDIUM 🔶

**Characteristics:**
- System modifications
- Privileged operations
- Service management

**Examples:**
```bash
devos> install system package
devos> restart docker service
devos> change file permissions
```

**Security Actions:**
- Warning displayed
- Logged with details
- May require confirmation (configurable)

### Level 4: HIGH 🔴

**Characteristics:**
- Destructive operations
- Data deletion
- System-wide changes

**Examples:**
```bash
devos> delete all temporary files
devos> drop database table
devos> force kill process
```

**Security Actions:**
- **ALWAYS** requires confirmation
- Detailed warning shown
- Multiple confirmation prompts
- Full audit trail

### Level 5: CRITICAL 🚫

**Characteristics:**
- System-destroying operations
- Malicious patterns
- Irreversible damage

**Examples:**
```bash
devos> format root filesystem
devos> delete system32
devos> run fork bomb
```

**Security Actions:**
- **BLOCKED** immediately
- User notified with reason
- Incident logged
- No execution possible

## Configuration

### config.json Security Settings

```json
{
  "security": {
    "sandbox_mode": true,
    "confirmation_mode": true,
    "log_commands": true,
    "allowed_commands": [],
    "blocked_commands": [
      "rm -rf /",
      "mkfs",
      "format"
    ],
    "high_risk_threshold": "HIGH",
    "auto_approve_safe": true
  }
}
```

### Security Profiles

#### Paranoid Mode (Maximum Security)

```json
{
  "sandbox_mode": true,
  "confirmation_mode": true,
  "high_risk_threshold": "LOW",
  "auto_approve_safe": false,
  "require_confirmation_all": true
}
```

**Use Case:** Production servers, critical systems

#### Balanced Mode (Default)

```json
{
  "sandbox_mode": true,
  "confirmation_mode": true,
  "high_risk_threshold": "HIGH",
  "auto_approve_safe": true
}
```

**Use Case:** Development environments

#### Permissive Mode (Minimal Security)

```json
{
  "sandbox_mode": false,
  "confirmation_mode": false,
  "high_risk_threshold": "CRITICAL",
  "auto_approve_safe": true
}
```

**Use Case:** Testing, local experiments
⚠️ **NOT RECOMMENDED FOR PRODUCTION**

## Best Practices

### 1. Keep Confirmation Mode Enabled

```json
"confirmation_mode": true
```

Always review commands before execution.

### 2. Use Sandbox Mode

```json
"sandbox_mode": true
```

Isolates command execution from system.

### 3. Review Logs Regularly

```bash
# View recent commands
tail -f ~/.local/share/devos/logs/devos-*.log

# Check for suspicious activity
grep "BLOCKED" ~/.local/share/devos/logs/devos-*.log
```

### 4. Whitelist Known Safe Commands

```json
"allowed_commands": [
  "npm install",
  "pip install",
  "git pull",
  "docker-compose up"
]
```

### 5. Keep DevOS Updated

```bash
pip install --upgrade devos-ai
```

Security patches are released regularly.

### 6. Use API Keys Securely

```bash
# Store in environment variables
export OPENAI_API_KEY="sk-..."

# Or use config file with restricted permissions
chmod 600 ~/.config/devos/config.json
```

### 7. Review AI Generated Commands

Don't blindly trust AI. Always review:
- Command syntax
- Target paths
- Flags and options
- Potential side effects

### 8. Limit Plugin Permissions

```json
{
  "plugins": {
    "git-helper": {
      "permissions": ["read_filesystem", "execute_git"]
    }
  }
}
```

### 9. Use Different Configs for Different Environments

```bash
# Development
cp config.dev.json ~/.config/devos/config.json

# Production
cp config.prod.json ~/.config/devos/config.json
```

### 10. Regular Security Audits

```bash
# Check blocked commands
devos> show security stats

# Review recent high-risk operations
devos> show high risk commands from last week
```

## Threat Model

### Threats DevOS Protects Against

#### ✅ Accidental System Damage

**Scenario:** User asks to "clean up disk space"
**Without DevOS:** `rm -rf /tmp/*` might become `rm -rf / tmp/*`
**With DevOS:** Validates command, catches dangerous patterns

#### ✅ Malicious AI Suggestions

**Scenario:** Compromised LLM suggests malicious command
**Without DevOS:** Command executed blindly
**With DevOS:** Pattern matching blocks malicious commands

#### ✅ Typo-Induced Disasters

**Scenario:** User typos `rm -rf / home/user` instead of `rm -rf /home/user`
**Without DevOS:** Deletes root filesystem
**With DevOS:** Detects pattern, blocks execution

#### ✅ Social Engineering via AI

**Scenario:** Attacker tricks AI into generating harmful commands
**Without DevOS:** AI complies and executes
**With DevOS:** Multi-layer validation prevents execution

### Threats DevOS Does NOT Protect Against

#### ❌ Deliberately Bypassing Security

If a user deliberately disables security features or modifies code, protection is lost.

#### ❌ Supply Chain Attacks

Compromised dependencies or plugins could bypass security.

#### ❌ System-Level Exploits

Kernel vulnerabilities or OS bugs are outside DevOS scope.

#### ❌ Physical Access

Direct physical access to the machine bypasses all software security.

## Incident Response

### If DevOS Blocks a Legitimate Command

1. **Review the command**
   ```bash
   devos> explain why command was blocked
   ```

2. **Check security logs**
   ```bash
   cat ~/.local/share/devos/logs/devos-*.log | grep BLOCKED
   ```

3. **Adjust security settings if needed**
   ```json
   "blocked_commands": []  // Remove specific pattern
   ```

4. **Use manual execution as fallback**
   ```bash
   # Exit DevOS and run command directly
   exit
   bash -c "your command here"
   ```

### If DevOS Executes Unwanted Command

1. **Immediately check what was executed**
   ```bash
   cat ~/.local/share/devos/logs/devos-*.log | tail -20
   ```

2. **Undo the operation if possible**
   ```bash
   devos> undo last operation
   ```

3. **Report the issue**
   - File a GitHub issue with details
   - Include logs (sanitized)
   - Describe expected vs actual behavior

4. **Update security rules**
   ```json
   "blocked_commands": [
     "newly-discovered-dangerous-pattern"
   ]
   ```

## Security Checklist

Before using DevOS in production:

- [ ] Enable sandbox mode
- [ ] Enable confirmation mode
- [ ] Review blocked commands list
- [ ] Set appropriate risk thresholds
- [ ] Configure audit logging
- [ ] Restrict API key access
- [ ] Test security with known dangerous commands
- [ ] Set up log monitoring
- [ ] Create environment-specific configs
- [ ] Train users on security features
- [ ] Establish incident response procedures
- [ ] Regular security updates

## Reporting Security Issues

Found a security vulnerability? Please:

1. **DO NOT** open a public GitHub issue
2. Email: security@devos.ai
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We'll respond within 48 hours and credit responsible disclosure.

---

**Remember:** DevOS is a tool to assist you, not replace human judgment. Always understand what commands will do before executing them.
