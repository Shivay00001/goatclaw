# DevOS Installation Script for Windows
# Run with: PowerShell -ExecutionPolicy Bypass -File install.ps1

Write-Host @"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ██████╗ ███████╗██╗   ██╗ ██████╗ ███████╗           ║
║   ██╔══██╗██╔════╝██║   ██║██╔═══██╗██╔════╝           ║
║   ██║  ██║█████╗  ██║   ██║██║   ██║███████╗           ║
║   ██║  ██║██╔══╝  ╚██╗ ██╔╝██║   ██║╚════██║           ║
║   ██████╔╝███████╗ ╚████╔╝ ╚██████╔╝███████║           ║
║   ╚═════╝ ╚══════╝  ╚═══╝   ╚═════╝ ╚══════╝           ║
║                                                          ║
║   AI-Native Developer Operating Layer                   ║
║   Windows Installer v0.1.0                              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Check for Administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠ Warning: Running without administrator privileges" -ForegroundColor Yellow
    Write-Host "  Some features may not work correctly" -ForegroundColor Yellow
    Write-Host ""
}

# Check Python
Write-Host ""
Write-Host "Checking prerequisites..." -ForegroundColor White

$pythonCommand = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCommand = $cmd
            Write-Host "✓ Python found: $version" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $pythonCommand) {
    Write-Host "✗ Python 3 is not installed" -ForegroundColor Red
    Write-Host "  Please install Python 3.8 or higher from https://www.python.org" -ForegroundColor Red
    exit 1
}

# Check Go
$goInstalled = $false
try {
    $goVersion = go version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Go found: $goVersion" -ForegroundColor Green
        $goInstalled = $true
    }
} catch {
    Write-Host "⚠ Go not installed (optional for CLI)" -ForegroundColor Yellow
    Write-Host "  Install from: https://golang.org" -ForegroundColor Yellow
}

# Check Ollama
try {
    $ollamaVersion = ollama --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Ollama found (local LLM support enabled)" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ Ollama not found (install for local LLM support)" -ForegroundColor Yellow
    Write-Host "  Install from: https://ollama.ai" -ForegroundColor Yellow
}

# Install Python dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor White

& $pythonCommand -m pip install --upgrade pip
& $pythonCommand -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Python dependencies installed" -ForegroundColor Green

# Build Go CLI (if Go is available)
if ($goInstalled) {
    Write-Host ""
    Write-Host "Building Go CLI..." -ForegroundColor White
    
    Push-Location core-cli
    go mod download
    go build -o ..\bin\devos.exe .
    Pop-Location
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Go CLI built successfully" -ForegroundColor Green
        
        # Install to user directory
        $installDir = "$env:USERPROFILE\.devos"
        $binDir = "$installDir\bin"
        
        New-Item -ItemType Directory -Force -Path $binDir | Out-Null
        Copy-Item "bin\devos.exe" "$binDir\devos.exe" -Force
        
        # Add to PATH
        $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($userPath -notlike "*$binDir*") {
            [Environment]::SetEnvironmentVariable("Path", "$userPath;$binDir", "User")
            Write-Host "✓ Added DevOS to PATH" -ForegroundColor Green
            Write-Host "  Restart your terminal to use 'devos' command" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✗ Failed to build Go CLI" -ForegroundColor Red
        Write-Host "  Continuing with Python-only installation..." -ForegroundColor Yellow
    }
}

# Create config directory
Write-Host ""
Write-Host "Setting up configuration..." -ForegroundColor White

$configDir = "$env:APPDATA\devos"
New-Item -ItemType Directory -Force -Path "$configDir\plugins" | Out-Null
New-Item -ItemType Directory -Force -Path "$configDir\logs" | Out-Null

Write-Host "✓ Configuration directory created: $configDir" -ForegroundColor Green

# Installation complete
Write-Host ""
Write-Host @"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ✓ Installation Complete!                              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

Write-Host ""
Write-Host "Quick Start:" -ForegroundColor White
Write-Host "  1. Restart your terminal (PowerShell or Command Prompt)" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. (Optional) Configure AI provider:" -ForegroundColor Gray
Write-Host "     Edit: $configDir\config.json" -ForegroundColor Gray
Write-Host "     Set your API key for OpenAI, Anthropic, or Gemini" -ForegroundColor Gray
Write-Host "     OR use local Ollama (default)" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Run DevOS:" -ForegroundColor Gray
Write-Host "     devos" -ForegroundColor Gray
Write-Host ""
Write-Host "Examples:" -ForegroundColor White
Write-Host "  devos> setup fastapi project with docker" -ForegroundColor Gray
Write-Host "  devos> analyze system performance" -ForegroundColor Gray
Write-Host "  devos> fix build error" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentation: https://docs.devos.ai" -ForegroundColor Yellow
Write-Host "GitHub: https://github.com/devos-ai/devos" -ForegroundColor Yellow
Write-Host ""
