package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
)

// Config represents the DevOS configuration
type Config struct {
	// System
	OS         string `json:"os"`
	ConfigPath string `json:"config_path"`

	// AI Configuration
	AIProvider string `json:"ai_provider"` // openai, anthropic, gemini, ollama
	Model      string `json:"model"`
	APIKey     string `json:"api_key,omitempty"`
	BaseURL    string `json:"base_url,omitempty"` // For Ollama or custom endpoints

	// Behavior
	ConfirmationMode bool   `json:"confirmation_mode"`
	LogLevel         string `json:"log_level"` // debug, info, warn, error
	MaxTokens        int    `json:"max_tokens"`
	Temperature      float64 `json:"temperature"`

	// Security
	SandboxMode     bool     `json:"sandbox_mode"`
	AllowedCommands []string `json:"allowed_commands,omitempty"`
	BlockedCommands []string `json:"blocked_commands"`

	// Plugins
	Plugins       []string `json:"plugins"`
	PluginPath    string   `json:"plugin_path"`

	// Memory
	MemoryPath string `json:"memory_path"`
	MemorySize int    `json:"memory_size"` // Max context items
}

// Default configuration values
var DefaultConfig = Config{
	AIProvider:       "ollama",
	Model:            "llama3.2",
	ConfirmationMode: true,
	LogLevel:         "info",
	MaxTokens:        2048,
	Temperature:      0.7,
	SandboxMode:      true,
	BlockedCommands: []string{
		"rm -rf /",
		"dd if=",
		"mkfs",
		"format",
		":(){:|:&};:",
	},
	Plugins:    []string{},
	MemorySize: 100,
}

// Load reads the configuration from the config file or creates a default one
func Load() (*Config, error) {
	configDir, err := getConfigDir()
	if err != nil {
		return nil, err
	}

	configPath := filepath.Join(configDir, "config.json")

	// Create config directory if it doesn't exist
	if err := os.MkdirAll(configDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create config directory: %w", err)
	}

	// Check if config file exists
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		// Create default config
		config := DefaultConfig
		config.OS = runtime.GOOS
		config.ConfigPath = configPath
		config.PluginPath = filepath.Join(configDir, "plugins")
		config.MemoryPath = filepath.Join(configDir, "memory.db")

		if err := config.Save(); err != nil {
			return nil, fmt.Errorf("failed to save default config: %w", err)
		}

		return &config, nil
	}

	// Load existing config
	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	var config Config
	if err := json.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse config file: %w", err)
	}

	// Update OS and paths
	config.OS = runtime.GOOS
	config.ConfigPath = configPath

	return &config, nil
}

// Save writes the configuration to disk
func (c *Config) Save() error {
	data, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	if err := os.WriteFile(c.ConfigPath, data, 0644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}

	return nil
}

// getConfigDir returns the platform-specific configuration directory
func getConfigDir() (string, error) {
	var baseDir string

	switch runtime.GOOS {
	case "windows":
		baseDir = os.Getenv("APPDATA")
		if baseDir == "" {
			return "", fmt.Errorf("APPDATA environment variable not set")
		}
	case "darwin":
		home, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		baseDir = filepath.Join(home, "Library", "Application Support")
	default: // linux and others
		home, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		xdgConfig := os.Getenv("XDG_CONFIG_HOME")
		if xdgConfig != "" {
			baseDir = xdgConfig
		} else {
			baseDir = filepath.Join(home, ".config")
		}
	}

	return filepath.Join(baseDir, "devos"), nil
}

// Validate checks if the configuration is valid
func (c *Config) Validate() error {
	// Check AI provider
	validProviders := map[string]bool{
		"openai":    true,
		"anthropic": true,
		"gemini":    true,
		"ollama":    true,
	}

	if !validProviders[c.AIProvider] {
		return fmt.Errorf("invalid AI provider: %s", c.AIProvider)
	}

	// Check API key for cloud providers
	if c.AIProvider != "ollama" && c.APIKey == "" {
		return fmt.Errorf("API key required for provider: %s", c.AIProvider)
	}

	// Check log level
	validLevels := map[string]bool{
		"debug": true,
		"info":  true,
		"warn":  true,
		"error": true,
	}

	if !validLevels[c.LogLevel] {
		return fmt.Errorf("invalid log level: %s", c.LogLevel)
	}

	return nil
}
