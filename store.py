"""
DevOS Memory Store
Provides context persistence using SQLite
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class MemoryStore:
    """SQLite-based context and command history store"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize memory store
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            config_dir = self._get_config_dir()
            db_path = os.path.join(config_dir, 'memory.db')
        
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_db()
    
    def _get_config_dir(self) -> str:
        """Get platform-specific config directory"""
        if os.name == 'nt':  # Windows
            base_dir = os.getenv('APPDATA')
        elif os.uname().sysname == 'Darwin':  # macOS
            base_dir = os.path.join(Path.home(), 'Library', 'Application Support')
        else:  # Linux
            base_dir = os.getenv('XDG_CONFIG_HOME', os.path.join(Path.home(), '.config'))
        
        return os.path.join(base_dir, 'devos')
    
    def _ensure_db_dir(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        os.makedirs(db_dir, exist_ok=True)
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Commands history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_input TEXT NOT NULL,
                intent TEXT,
                commands TEXT,
                success BOOLEAN,
                output TEXT,
                error TEXT,
                metadata TEXT
            )
        ''')
        
        # Context store table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_store (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                category TEXT,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        # Project context table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_path TEXT UNIQUE NOT NULL,
                project_type TEXT,
                dependencies TEXT,
                last_updated TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON command_history(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_intent ON command_history(intent)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON context_store(category)')
        
        conn.commit()
        conn.close()
    
    def add_command(self, user_input: str, intent: str, commands: List[str],
                   success: bool, output: str = "", error: str = "",
                   metadata: Dict[str, Any] = None) -> int:
        """
        Add command execution to history
        
        Args:
            user_input: Original user input
            intent: Classified intent
            commands: List of executed commands
            success: Whether execution succeeded
            output: Command output
            error: Error message if any
            metadata: Additional metadata
        
        Returns:
            ID of inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO command_history 
            (timestamp, user_input, intent, commands, success, output, error, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            user_input,
            intent,
            json.dumps(commands),
            success,
            output,
            error,
            json.dumps(metadata or {})
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def get_recent_commands(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent command history
        
        Args:
            limit: Maximum number of records to return
        
        Returns:
            List of command history records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM command_history
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def search_history(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search command history
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            Matching command records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM command_history
            WHERE user_input LIKE ? OR commands LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def set_context(self, key: str, value: Any, category: str = "general",
                    metadata: Dict[str, Any] = None):
        """
        Store context value
        
        Args:
            key: Context key
            value: Context value (will be JSON serialized)
            category: Context category
            metadata: Additional metadata
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO context_store
            (key, value, category, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            key,
            json.dumps(value),
            category,
            datetime.now().isoformat(),
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
    
    def get_context(self, key: str) -> Optional[Any]:
        """
        Get context value
        
        Args:
            key: Context key
        
        Returns:
            Context value or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM context_store WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None
    
    def get_context_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get all context values in a category
        
        Args:
            category: Context category
        
        Returns:
            Dictionary of key-value pairs
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT key, value FROM context_store WHERE category = ?', (category,))
        rows = cursor.fetchall()
        conn.close()
        
        return {row['key']: json.loads(row['value']) for row in rows}
    
    def save_project_context(self, project_path: str, project_type: str,
                            dependencies: List[str], metadata: Dict[str, Any] = None):
        """
        Save project context
        
        Args:
            project_path: Path to project
            project_type: Type of project (fastapi, react, etc.)
            dependencies: List of dependencies
            metadata: Additional metadata
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO project_context
            (project_path, project_type, dependencies, last_updated, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            project_path,
            project_type,
            json.dumps(dependencies),
            datetime.now().isoformat(),
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
    
    def get_project_context(self, project_path: str) -> Optional[Dict[str, Any]]:
        """
        Get project context
        
        Args:
            project_path: Path to project
        
        Returns:
            Project context or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM project_context WHERE project_path = ?', (project_path,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def cleanup_old_records(self, days: int = 30):
        """
        Clean up records older than specified days
        
        Args:
            days: Number of days to keep
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now().replace(day=datetime.now().day - days).isoformat()
        
        cursor.execute('DELETE FROM command_history WHERE timestamp < ?', (cutoff_date,))
        cursor.execute('DELETE FROM context_store WHERE timestamp < ?', (cutoff_date,))
        
        conn.commit()
        conn.close()
