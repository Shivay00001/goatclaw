# DevOS Usage Examples

## Table of Contents

- [Project Setup](#project-setup)
- [System Analysis](#system-analysis)
- [Debugging & Error Fixing](#debugging--error-fixing)
- [Git Operations](#git-operations)
- [Dependency Management](#dependency-management)
- [Docker Operations](#docker-operations)
- [Advanced Workflows](#advanced-workflows)

## Project Setup

### FastAPI Project with Docker

```bash
devos> setup fastapi project with docker
```

**What DevOS does:**
1. Creates project structure
2. Generates `main.py` with FastAPI boilerplate
3. Creates `requirements.txt` with FastAPI dependencies
4. Generates Dockerfile
5. Creates docker-compose.yml

**Expected Output:**
```
📋 Plan: Setting up new project

Steps to execute:
  1. Create Directory
  2. Create File
  3. Create File
  4. Create File
  5. Create File

📋 Executing commands:
  → mkdir -p "my-fastapi-app"
  → touch "my-fastapi-app/main.py"
  → touch "my-fastapi-app/requirements.txt"
  → touch "my-fastapi-app/Dockerfile"
  → touch "my-fastapi-app/docker-compose.yml"

✅ Execution completed successfully
```

### React App with TypeScript

```bash
devos> create react app with typescript
```

**Generated Structure:**
```
my-react-app/
├── public/
├── src/
│   ├── App.tsx
│   └── index.tsx
├── package.json
├── tsconfig.json
└── README.md
```

### Django Project

```bash
devos> setup django project with postgres and docker
```

**Generated Files:**
- Django project structure
- settings.py with Postgres config
- Dockerfile
- docker-compose.yml (Django + Postgres)
- requirements.txt

## System Analysis

### Performance Analysis

```bash
devos> analyze system performance
```

**Output:**
```
📋 Plan: Analyzing system/project

Steps to execute:
  1. Check Cpu
  2. Check Memory
  3. Check Disk

📋 Executing commands:
  → top -bn1 | grep "Cpu(s)"
  → free -h
  → df -h

CPU Usage: 23.4%
Memory: 8.2GB / 16GB (51.25%)
Disk: 145GB / 500GB (29%)
```

### Disk Usage Analysis

```bash
devos> check disk usage
```

### Process Monitoring

```bash
devos> show running processes using most CPU
```

## Debugging & Error Fixing

### General Error Fix

```bash
devos> fix build error
```

**DevOS Actions:**
1. Scans current directory for logs
2. Identifies error patterns
3. Suggests solutions
4. Offers to execute fixes

### Python Import Errors

```bash
devos> fix python import error
```

**Example Fix:**
```
Found error: ModuleNotFoundError: No module named 'fastapi'

Suggested fix:
  → pip install fastapi

Would you like me to execute this? (yes/no)
```

### Docker Build Failures

```bash
devos> fix docker build error
```

**DevOS checks:**
- Dockerfile syntax
- Base image availability
- Missing dependencies
- Port conflicts

## Git Operations

### Smart Commit

```bash
devos> commit changes with meaningful message
```

**DevOS:**
1. Analyzes staged changes
2. Generates descriptive commit message
3. Shows diff summary
4. Confirms before committing

### Safe Push

```bash
devos> push to remote
```

**Safety Checks:**
- Checks if commits exist
- Verifies remote connection
- Asks for confirmation
- Executes push

### Branch Operations

```bash
devos> create new feature branch for authentication
```

```bash
devos> merge feature branch to main
```

### Status with Analysis

```bash
devos> git status
```

**Enhanced Output:**
```
📊 Git Status Analysis:
  Modified: 3
  Added: 1
  Deleted: 0
  Untracked: 2

M  src/main.py
M  requirements.txt
M  README.md
A  src/auth.py
?? tests/
?? .env.example
```

## Dependency Management

### Python Dependencies

```bash
devos> install dependencies from requirements.txt
```

```bash
devos> update all python packages
```

### Node.js Dependencies

```bash
devos> install npm dependencies
```

```bash
devos> update package.json dependencies
```

### System Packages

```bash
# On Linux
devos> install docker using apt

# On macOS
devos> install postgres using homebrew
```

## Docker Operations

### Container Management

```bash
devos> start docker containers
```

```bash
devos> stop all running containers
```

```bash
devos> show docker container logs
```

### Image Operations

```bash
devos> build docker image
```

```bash
devos> clean up unused docker images
```

### Docker Compose

```bash
devos> start services with docker compose
```

```bash
devos> restart database service
```

## Advanced Workflows

### Complete Project Setup

```bash
devos> create a complete microservice with fastapi, docker, postgres, redis, and nginx reverse proxy
```

**DevOS creates:**
1. FastAPI application structure
2. Database models and migrations
3. Redis caching layer
4. Docker Compose with all services
5. Nginx configuration
6. Environment file templates
7. Testing setup

### CI/CD Pipeline Setup

```bash
devos> setup github actions ci/cd pipeline
```

**Generated:**
- .github/workflows/ci.yml
- .github/workflows/deploy.yml
- Testing workflow
- Docker build workflow
- Deployment scripts

### Database Operations

```bash
devos> create database migrations for user model
```

```bash
devos> backup postgres database
```

### Testing Workflows

```bash
devos> run all tests with coverage
```

```bash
devos> setup pytest with fixtures
```

### Monitoring Setup

```bash
devos> setup prometheus and grafana monitoring
```

**Creates:**
- Prometheus configuration
- Grafana dashboards
- Alert rules
- Docker Compose setup

## Context-Aware Operations

DevOS remembers context across commands:

```bash
devos> setup fastapi project
# DevOS creates project in current directory

devos> add authentication
# DevOS knows we're working on FastAPI and adds auth

devos> dockerize the application
# DevOS creates Docker files for the FastAPI project

devos> setup ci/cd
# DevOS configures CI/CD for the FastAPI project
```

## Plugin Examples

### Using Git Plugin

```bash
devos> analyze git history
devos> suggest commit message
devos> check for merge conflicts
```

### Using Docker Plugin

```bash
devos> optimize docker image size
devos> scan for security vulnerabilities
devos> generate docker-compose from existing containers
```

## Confirmation Mode

For potentially destructive operations:

```bash
devos> delete all .log files

⚠️  This operation will delete files. Proceed? (yes/no): yes

📋 Executing commands:
  → find . -name "*.log" -type f -delete

✅ Execution completed successfully
```

## Offline Mode

Using local Ollama:

```bash
# DevOS automatically uses Ollama if configured
devos> setup python project

# No internet required - all AI processing is local
```

## Error Handling

When commands fail:

```bash
devos> install package-that-doesnt-exist

❌ Error: Package 'package-that-doesnt-exist' not found

Suggestions:
  - Check package name spelling
  - Search for similar packages
  - Use different package manager

Would you like me to:
  1. Search for similar packages
  2. Check alternative package names
  3. Skip this operation
```

## Tips & Best Practices

### 1. Be Specific

❌ Bad: `devos> setup project`
✅ Good: `devos> setup fastapi project with postgres and docker`

### 2. Use Context

```bash
devos> cd my-project
devos> add tests
# DevOS knows the project type and adds appropriate tests
```

### 3. Review Before Executing

Always review commands in confirmation mode:
- Check for typos
- Verify paths
- Understand what will change

### 4. Use Memory

DevOS remembers:
- Previous commands
- Project context
- User preferences

### 5. Leverage Plugins

Install community plugins for specialized tasks:
```bash
devos> install git-helper plugin
devos> install docker-optimizer plugin
```

## Troubleshooting

### DevOS Not Finding Commands

```bash
devos> status
# Shows current configuration and loaded plugins
```

### AI Provider Issues

```bash
# Check Ollama
ollama serve

# Test API connection
devos> test ai connection
```

### Permission Errors

```bash
# Run with appropriate permissions
sudo devos
# or configure permissions in config
```

## Next Steps

- Explore [Plugin Development](docs/plugin-development.md)
- Read [Security Guide](docs/security.md)
- Join [Community Discord](https://discord.gg/devos)
