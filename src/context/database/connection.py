"""
SurrealDB Connection Manager
Handles database connections and basic operations for Smart Context Manager
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from surrealdb import Surreal


class SurrealConnection:
    """SurrealDB connection manager for context data"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / ".ai-punk" / "context.db"
        self.namespace = "ai_punk"
        self.database = "context"
        
        # Try WebSocket connection to local SurrealDB server
        # If that fails, fallback to memory
        self.db_url = "ws://localhost:8000/rpc"
        self.fallback_url = "memory"
        
        # Ensure directory exists for future file-based storage
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def connect(self) -> Surreal:
        """Create and return a new database connection"""
        try:
            # Try primary URL first
            db = Surreal(self.db_url)
            await db.use(self.namespace, self.database)
            return db
        except Exception:
            # Fallback to memory if local server not available
            db = Surreal(self.fallback_url)
            await db.use(self.namespace, self.database)
            return db
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a SurrealQL query with parameters"""
        try:
            # Try primary URL first
            async with Surreal(self.db_url) as db:
                await db.use(self.namespace, self.database)
                result = await db.query(query, params or {})
                return result
        except Exception:
            # Fallback to memory
            async with Surreal(self.fallback_url) as db:
                await db.use(self.namespace, self.database)
                result = await db.query(query, params or {})
                return result
    
    async def create_record(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in the specified table"""
        try:
            async with Surreal(self.db_url) as db:
                await db.use(self.namespace, self.database)
                result = await db.create(table, data)
                return result[0] if result else {}
        except Exception:
            async with Surreal(self.fallback_url) as db:
                await db.use(self.namespace, self.database)
                result = await db.create(table, data)
                return result[0] if result else {}
    
    async def select_records(self, table: str, condition: Optional[str] = None) -> List[Dict[str, Any]]:
        """Select records from table with optional condition"""
        query = f"SELECT * FROM {table}"
        if condition:
            query += f" WHERE {condition}"
        
        result = await self.execute_query(query)
        return result[0]["result"] if result and result[0] else []
    
    async def update_record(self, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a specific record"""
        try:
            async with Surreal(self.db_url) as db:
                await db.use(self.namespace, self.database)
                result = await db.update(record_id, data)
                return result[0] if result else {}
        except Exception:
            async with Surreal(self.fallback_url) as db:
                await db.use(self.namespace, self.database)
                result = await db.update(record_id, data)
                return result[0] if result else {}
    
    async def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            await self.execute_query("SELECT 1 as health")
            return True
        except Exception:
            return False
    
    def get_connection_info(self) -> Dict[str, str]:
        """Get connection information for debugging"""
        return {
            "primary_url": self.db_url,
            "fallback_url": self.fallback_url,
            "namespace": self.namespace,
            "database": self.database,
            "workspace_path": str(self.workspace_path),
            "db_file_exists": self.db_path.exists()
        } 