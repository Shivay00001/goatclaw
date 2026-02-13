package executor

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os/exec"
	"strings"

	"devos/internal/config"
	"devos/internal/logger"
)

// ExecutionResult represents the result of command execution
type ExecutionResult struct {
	Output            string   `json:"output"`
	Commands          []string `json:"commands"`
	NeedsConfirmation bool     `json:"needs_confirmation"`
	Error             string   `json:"error,omitempty"`
}

// Executor handles command execution and AI integration
type Executor struct {
	config *config.Config
	logger *logger.Logger
}

// New creates a new executor instance
func New(cfg *config.Config, log *logger.Logger) (*Executor, error) {
	return &Executor{
		config: cfg,
		logger: log,
	}, nil
}

// Execute processes a natural language command through the AI engine
func (e *Executor) Execute(input string) (*ExecutionResult, error) {
	e.logger.Info("Executing command: %s", input)

	// Call Python AI engine
	result, err := e.callAIEngine(input)
	if err != nil {
		return nil, fmt.Errorf("AI engine error: %w", err)
	}

	// Validate commands for security
	if err := e.validateCommands(result.Commands); err != nil {
		return nil, fmt.Errorf("security validation failed: %w", err)
	}

	return result, nil
}

// ExecuteCommands executes a list of shell commands
func (e *Executor) ExecuteCommands(commands []string) error {
	for i, cmdStr := range commands {
		e.logger.Info("Executing command %d/%d: %s", i+1, len(commands), cmdStr)

		// Execute command based on OS
		output, err := e.executeShellCommand(cmdStr)
		if err != nil {
			e.logger.Error("Command failed: %s - Error: %v", cmdStr, err)
			return fmt.Errorf("command failed: %s - %w", cmdStr, err)
		}

		if output != "" {
			fmt.Printf("  Output: %s\n", output)
		}
	}

	return nil
}

// callAIEngine calls the Python AI engine for command interpretation
func (e *Executor) callAIEngine(input string) (*ExecutionResult, error) {
	// Prepare request payload
	request := map[string]interface{}{
		"input":       input,
		"os":          e.config.OS,
		"provider":    e.config.AIProvider,
		"model":       e.config.Model,
		"api_key":     e.config.APIKey,
		"base_url":    e.config.BaseURL,
		"max_tokens":  e.config.MaxTokens,
		"temperature": e.config.Temperature,
	}

	requestData, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	// Call Python AI engine
	cmd := exec.Command("python3", "-m", "ai_engine.core.processor", string(requestData))
	
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	if err := cmd.Run(); err != nil {
		return nil, fmt.Errorf("AI engine execution failed: %w - stderr: %s", err, stderr.String())
	}

	// Parse response
	var result ExecutionResult
	if err := json.Unmarshal(stdout.Bytes(), &result); err != nil {
		return nil, fmt.Errorf("failed to parse AI response: %w - output: %s", err, stdout.String())
	}

	return &result, nil
}

// validateCommands checks if commands are safe to execute
func (e *Executor) validateCommands(commands []string) error {
	if !e.config.SandboxMode {
		return nil
	}

	for _, cmd := range commands {
		// Check against blocked commands
		for _, blocked := range e.config.BlockedCommands {
			if strings.Contains(strings.ToLower(cmd), strings.ToLower(blocked)) {
				return fmt.Errorf("blocked command detected: %s", blocked)
			}
		}

		// Check for dangerous patterns
		if e.isDangerous(cmd) {
			return fmt.Errorf("potentially dangerous command detected: %s", cmd)
		}
	}

	return nil
}

// isDangerous checks if a command contains dangerous patterns
func (e *Executor) isDangerous(cmd string) bool {
	dangerousPatterns := []string{
		"rm -rf",
		"rm -fr",
		"mkfs",
		"dd if=",
		"format",
		"> /dev/",
		":/dev/",
		"curl | sh",
		"wget | sh",
		"curl | bash",
		"wget | bash",
	}

	cmdLower := strings.ToLower(cmd)
	for _, pattern := range dangerousPatterns {
		if strings.Contains(cmdLower, pattern) {
			return true
		}
	}

	return false
}

// executeShellCommand executes a shell command based on the OS
func (e *Executor) executeShellCommand(cmdStr string) (string, error) {
	var cmd *exec.Cmd

	switch e.config.OS {
	case "windows":
		cmd = exec.Command("powershell", "-Command", cmdStr)
	case "darwin", "linux":
		cmd = exec.Command("sh", "-c", cmdStr)
	default:
		return "", fmt.Errorf("unsupported OS: %s", e.config.OS)
	}

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err := cmd.Run()
	output := strings.TrimSpace(stdout.String())

	if err != nil {
		errOutput := strings.TrimSpace(stderr.String())
		if errOutput != "" {
			return "", fmt.Errorf("%s: %s", err, errOutput)
		}
		return "", err
	}

	return output, nil
}
