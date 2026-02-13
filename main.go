package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"devos/internal/config"
	"devos/internal/executor"
	"devos/internal/logger"
)

const (
	Version = "0.1.0"
	Banner  = `
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
║   Version: %s                                       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
`
)

type CLI struct {
	config   *config.Config
	executor *executor.Executor
	logger   *logger.Logger
}

func NewCLI() (*CLI, error) {
	// Initialize configuration
	cfg, err := config.Load()
	if err != nil {
		return nil, fmt.Errorf("failed to load config: %w", err)
	}

	// Initialize logger
	log := logger.New(cfg.LogLevel)

	// Initialize executor
	exec, err := executor.New(cfg, log)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize executor: %w", err)
	}

	return &CLI{
		config:   cfg,
		executor: exec,
		logger:   log,
	}, nil
}

func (c *CLI) Start() error {
	fmt.Printf(Banner, Version)
	fmt.Println("\n🚀 DevOS is ready. Type 'help' for commands or use natural language.")
	fmt.Println("💡 Examples:")
	fmt.Println("   - setup fastapi project with docker")
	fmt.Println("   - analyze system performance")
	fmt.Println("   - fix build error\n")

	scanner := bufio.NewScanner(os.Stdin)

	for {
		fmt.Print("devos> ")
		if !scanner.Scan() {
			break
		}

		input := strings.TrimSpace(scanner.Text())
		if input == "" {
			continue
		}

		// Handle built-in commands
		if c.handleBuiltinCommand(input) {
			continue
		}

		// Process natural language command through AI engine
		if err := c.processCommand(input); err != nil {
			c.logger.Error("Command execution failed: %v", err)
			fmt.Printf("❌ Error: %v\n", err)
		}
	}

	return scanner.Err()
}

func (c *CLI) handleBuiltinCommand(input string) bool {
	switch strings.ToLower(input) {
	case "exit", "quit", "q":
		fmt.Println("👋 Goodbye!")
		os.Exit(0)
		return true
	case "help", "h":
		c.showHelp()
		return true
	case "version", "v":
		fmt.Printf("DevOS version %s\n", Version)
		return true
	case "status":
		c.showStatus()
		return true
	case "config":
		c.showConfig()
		return true
	default:
		return false
	}
}

func (c *CLI) processCommand(input string) error {
	c.logger.Info("Processing command: %s", input)

	// Execute through AI engine
	result, err := c.executor.Execute(input)
	if err != nil {
		return err
	}

	// Display result
	fmt.Printf("\n%s\n", result.Output)

	if result.NeedsConfirmation {
		fmt.Print("\n⚠️  Proceed with execution? (yes/no): ")
		scanner := bufio.NewScanner(os.Stdin)
		if scanner.Scan() {
			response := strings.ToLower(strings.TrimSpace(scanner.Text()))
			if response != "yes" && response != "y" {
				fmt.Println("❌ Operation cancelled")
				return nil
			}
		}
	}

	if len(result.Commands) > 0 {
		fmt.Println("\n📋 Executing commands:")
		for _, cmd := range result.Commands {
			fmt.Printf("  → %s\n", cmd)
		}

		if err := c.executor.ExecuteCommands(result.Commands); err != nil {
			return err
		}

		fmt.Println("\n✅ Execution completed successfully")
	}

	return nil
}

func (c *CLI) showHelp() {
	help := `
DevOS - AI-Native Developer Operating Layer

USAGE:
  devos                    Start interactive mode
  devos [command]          Execute a single command

BUILT-IN COMMANDS:
  help, h                  Show this help message
  version, v               Show version information
  status                   Show system status
  config                   Show current configuration
  exit, quit, q            Exit DevOS

NATURAL LANGUAGE COMMANDS:
  You can use natural language to describe what you want to do.
  
  Examples:
    • setup fastapi project with docker
    • analyze system performance
    • fix build error in current directory
    • install python dependencies from requirements.txt
    • create kubernetes deployment config
    • optimize docker image size

MODES:
  Interactive Mode:        Default mode with continuous command input
  Confirmation Mode:       Prompts before executing destructive operations
  Offline Mode:           Uses local LLM (requires Ollama)

For more information, visit: https://github.com/devos-ai/devos
`
	fmt.Println(help)
}

func (c *CLI) showStatus() {
	fmt.Println("\n📊 System Status")
	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	fmt.Printf("  OS:              %s\n", c.config.OS)
	fmt.Printf("  AI Provider:     %s\n", c.config.AIProvider)
	fmt.Printf("  Confirmation:    %v\n", c.config.ConfirmationMode)
	fmt.Printf("  Log Level:       %s\n", c.config.LogLevel)
	fmt.Printf("  Plugins Loaded:  %d\n", len(c.config.Plugins))
	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
}

func (c *CLI) showConfig() {
	fmt.Println("\n⚙️  Configuration")
	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	fmt.Printf("  Config File:     %s\n", c.config.ConfigPath)
	fmt.Printf("  AI Provider:     %s\n", c.config.AIProvider)
	fmt.Printf("  Model:           %s\n", c.config.Model)
	fmt.Printf("  Confirmation:    %v\n", c.config.ConfirmationMode)
	fmt.Printf("  Max Tokens:      %d\n", c.config.MaxTokens)
	fmt.Printf("  Temperature:     %.2f\n", c.config.Temperature)
	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
}

func main() {
	cli, err := NewCLI()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to initialize DevOS: %v\n", err)
		os.Exit(1)
	}

	if err := cli.Start(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
