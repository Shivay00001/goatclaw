package logger

import (
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"runtime"
	"time"
)

// LogLevel represents the logging level
type LogLevel int

const (
	DEBUG LogLevel = iota
	INFO
	WARN
	ERROR
)

// Logger handles structured logging for DevOS
type Logger struct {
	level      LogLevel
	fileLogger *log.Logger
	file       *os.File
}

// New creates a new logger instance
func New(levelStr string) *Logger {
	level := parseLevel(levelStr)

	// Create log directory
	logDir, err := getLogDir()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Warning: failed to get log directory: %v\n", err)
		return &Logger{level: level}
	}

	if err := os.MkdirAll(logDir, 0755); err != nil {
		fmt.Fprintf(os.Stderr, "Warning: failed to create log directory: %v\n", err)
		return &Logger{level: level}
	}

	// Create log file
	logFile := filepath.Join(logDir, fmt.Sprintf("devos-%s.log", time.Now().Format("2006-01-02")))
	file, err := os.OpenFile(logFile, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Warning: failed to open log file: %v\n", err)
		return &Logger{level: level}
	}

	// Create multi-writer for both file and stdout (for debug mode)
	var writer io.Writer
	if level == DEBUG {
		writer = io.MultiWriter(file, os.Stdout)
	} else {
		writer = file
	}

	return &Logger{
		level:      level,
		fileLogger: log.New(writer, "", 0),
		file:       file,
	}
}

// Close closes the log file
func (l *Logger) Close() error {
	if l.file != nil {
		return l.file.Close()
	}
	return nil
}

// Debug logs a debug message
func (l *Logger) Debug(format string, args ...interface{}) {
	if l.level <= DEBUG {
		l.log(DEBUG, format, args...)
	}
}

// Info logs an info message
func (l *Logger) Info(format string, args ...interface{}) {
	if l.level <= INFO {
		l.log(INFO, format, args...)
	}
}

// Warn logs a warning message
func (l *Logger) Warn(format string, args ...interface{}) {
	if l.level <= WARN {
		l.log(WARN, format, args...)
	}
}

// Error logs an error message
func (l *Logger) Error(format string, args ...interface{}) {
	if l.level <= ERROR {
		l.log(ERROR, format, args...)
	}
}

// log is the internal logging function
func (l *Logger) log(level LogLevel, format string, args ...interface{}) {
	if l.fileLogger == nil {
		return
	}

	// Get caller information
	_, file, line, ok := runtime.Caller(2)
	caller := "unknown"
	if ok {
		caller = fmt.Sprintf("%s:%d", filepath.Base(file), line)
	}

	// Format message
	timestamp := time.Now().Format("2006-01-02 15:04:05")
	levelStr := levelString(level)
	message := fmt.Sprintf(format, args...)

	logLine := fmt.Sprintf("[%s] [%s] [%s] %s", timestamp, levelStr, caller, message)

	l.fileLogger.Println(logLine)
}

// parseLevel converts a string level to LogLevel
func parseLevel(level string) LogLevel {
	switch level {
	case "debug":
		return DEBUG
	case "info":
		return INFO
	case "warn":
		return WARN
	case "error":
		return ERROR
	default:
		return INFO
	}
}

// levelString converts a LogLevel to string
func levelString(level LogLevel) string {
	switch level {
	case DEBUG:
		return "DEBUG"
	case INFO:
		return "INFO"
	case WARN:
		return "WARN"
	case ERROR:
		return "ERROR"
	default:
		return "UNKNOWN"
	}
}

// getLogDir returns the platform-specific log directory
func getLogDir() (string, error) {
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
		baseDir = filepath.Join(home, "Library", "Logs")
	default: // linux and others
		home, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		baseDir = filepath.Join(home, ".local", "share")
	}

	return filepath.Join(baseDir, "devos", "logs"), nil
}
