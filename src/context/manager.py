"""
Smart Context Manager
Main context management system for AI Punk agent
"""

import asyncio
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from sentence_transformers import SentenceTransformer

from .database.connection import SurrealConnection
from .database.schema import setup_context_schema
from ..workspace.manager import WorkspaceManager


class SmartContextManager:
    """
    Intelligent context management system using SurrealDB multi-model database
    
    Features:
    - Session state tracking
    - Semantic code search with vector embeddings
    - Action logging and pattern recognition
    - File dependency graph analysis
    - Automatic workflow learning
    """
    
    def __init__(self, workspace_manager: WorkspaceManager):
        self.workspace_manager = workspace_manager
        self.workspace_path = workspace_manager.get_current_workspace()
        
        if not self.workspace_path:
            raise ValueError("No workspace selected. Please select a workspace first.")
        
        # Database connection
        self.db = SurrealConnection(str(self.workspace_path))
        
        # Embedding model for semantic search
        self.embedding_model = None
        self._embedding_model_name = "all-MiniLM-L6-v2"
        
        # Session state
        self.session_id = None
        self.is_initialized = False
        self.current_task = None
        self.active_files = []
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the context manager and database schema"""
        try:
            # Setup database schema
            schema_results = await setup_context_schema(self.db)
            
            # Load embedding model
            await self._load_embedding_model()
            
            # Create new session
            await self._create_session()
            
            self.is_initialized = True
            
            return {
                "success": True,
                "message": "Smart Context Manager initialized successfully",
                "session_id": self.session_id,
                "schema_results": schema_results,
                "workspace": str(self.workspace_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to initialize Smart Context Manager: {e}"
            }
    
    async def _load_embedding_model(self):
        """Load the sentence transformer model for embeddings"""
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(self._embedding_model_name)
    
    async def _create_session(self):
        """Create a new context session"""
        self.session_id = f"sess_{int(time.time())}_{hash(str(self.workspace_path)) % 10000}"
        
        session_data = {
            "session_id": self.session_id,
            "workspace_path": str(self.workspace_path),
            "current_task": None,
            "active_files": [],
            "focus_area": None
        }
        
        await self.db.create_record("context_session", session_data)
    
    async def update_current_task(self, task: str) -> bool:
        """Update the current task being worked on"""
        try:
            self.current_task = task
            
            # Update session in database
            await self.db.execute_query(
                "UPDATE context_session SET current_task = $task, updated_at = time::now() WHERE session_id = $session_id",
                {"task": task, "session_id": self.session_id}
            )
            
            return True
        except Exception:
            return False
    
    async def track_action(self, tool_name: str, input_data: Dict[str, Any], 
                          result: Dict[str, Any], execution_time: float = 0) -> bool:
        """Track tool usage and execution for pattern learning"""
        try:
            action_data = {
                "tool_name": tool_name,
                "input_data": input_data,
                "result": result,
                "execution_time": f"{execution_time}s"
            }
            
            await self.db.create_record("action_log", action_data)
            return True
            
        except Exception as e:
            print(f"Failed to track action: {e}")
            return False
    
    async def add_code_embedding(self, file_path: str, content: str, 
                                chunk_type: str = "code") -> bool:
        """Add semantic embeddings for code content"""
        try:
            # Generate embedding
            if not self.embedding_model:
                await self._load_embedding_model()
            
            embedding = self.embedding_model.encode(content).tolist()
            
            # Create unique chunk ID
            chunk_id = hashlib.md5(f"{file_path}_{content[:100]}".encode()).hexdigest()
            
            # Store in database
            embedding_data = {
                "file_path": file_path,
                "chunk_id": chunk_id,
                "content": content[:1000],  # Store preview only
                "embedding": embedding,
                "chunk_type": chunk_type
            }
            
            await self.db.create_record("code_embedding", embedding_data)
            return True
            
        except Exception as e:
            print(f"Failed to add code embedding: {e}")
            return False
    
    async def semantic_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search using vector similarity"""
        try:
            if not self.embedding_model:
                await self._load_embedding_model()
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Perform vector search using SurrealDB
            result = await self.db.execute_query("""
                SELECT file_path, content, chunk_type,
                       vector::similarity::cosine(embedding, $query_vec) AS similarity
                FROM code_embedding 
                WHERE embedding <|$limit|> $query_vec
                ORDER BY similarity DESC
            """, {
                "query_vec": query_embedding,
                "limit": limit
            })
            
            if result and result[0] and "result" in result[0]:
                return result[0]["result"]
            return []
            
        except Exception as e:
            print(f"Semantic search failed: {e}")
            return []
    
    async def track_file_access(self, file_path: str, file_size: int = 0) -> bool:
        """Track file access for context awareness"""
        try:
            # Calculate content hash if file exists
            content_hash = ""
            if Path(file_path).exists():
                with open(file_path, 'rb') as f:
                    content_hash = hashlib.md5(f.read()).hexdigest()
            
            # Update or create file context
            await self.db.execute_query("""
                UPSERT file_context SET
                    file_path = $file_path,
                    workspace = $workspace,
                    last_accessed = time::now(),
                    modification_count = modification_count + 1 IF modification_count ELSE 1,
                    content_hash = $content_hash,
                    file_size = $file_size
                WHERE file_path = $file_path
            """, {
                "file_path": file_path,
                "workspace": str(self.workspace_path),
                "content_hash": content_hash,
                "file_size": file_size
            })
            
            # Add to active files if not already there
            if file_path not in self.active_files:
                self.active_files.append(file_path)
                await self.db.execute_query(
                    "UPDATE context_session SET active_files = $active_files WHERE session_id = $session_id",
                    {"active_files": self.active_files, "session_id": self.session_id}
                )
            
            return True
            
        except Exception as e:
            print(f"Failed to track file access: {e}")
            return False
    
    async def get_workflow_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow patterns for suggestions"""
        try:
            result = await self.db.execute_query("""
                SELECT pattern_name, tools_sequence, frequency, success_rate, last_used
                FROM workflow_pattern
                ORDER BY frequency DESC, last_used DESC
                LIMIT $limit
            """, {"limit": limit})
            
            if result and result[0] and "result" in result[0]:
                return result[0]["result"]
            return []
            
        except Exception as e:
            print(f"Failed to get workflow patterns: {e}")
            return []
    
    async def suggest_next_actions(self, current_task: str) -> Dict[str, Any]:
        """Get intelligent suggestions for next actions"""
        try:
            # Update current task
            await self.update_current_task(current_task)
            
            # Get semantic matches
            semantic_results = await self.semantic_search(current_task, 3)
            
            # Get workflow patterns
            patterns = await self.get_workflow_patterns(5)
            
            # Get recent actions for context
            recent_actions = await self.db.execute_query("""
                SELECT tool_name, created_at
                FROM action_log
                WHERE created_at > time::now() - 1h
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            recent_tools = []
            if recent_actions and recent_actions[0] and "result" in recent_actions[0]:
                recent_tools = [action["tool_name"] for action in recent_actions[0]["result"]]
            
            return {
                "semantic_matches": semantic_results,
                "workflow_patterns": patterns,
                "recent_tools": recent_tools,
                "active_files": self.active_files,
                "suggested_next_steps": self._generate_suggestions(semantic_results, patterns, recent_tools)
            }
            
        except Exception as e:
            print(f"Failed to generate suggestions: {e}")
            return {"error": str(e)}
    
    def _generate_suggestions(self, semantic_results: List[Dict], 
                            patterns: List[Dict], recent_tools: List[str]) -> List[str]:
        """Generate contextual suggestions based on analysis"""
        suggestions = []
        
        # Suggest based on semantic matches
        if semantic_results:
            suggestions.append(f"Consider reviewing {semantic_results[0]['file_path']} - it's semantically related")
        
        # Suggest based on workflow patterns
        if patterns and recent_tools:
            for pattern in patterns[:2]:
                tools_seq = pattern["tools_sequence"]
                if len(recent_tools) >= 2 and recent_tools[-2:] == tools_seq[:2]:
                    if len(tools_seq) > 2:
                        suggestions.append(f"Based on pattern, consider using {tools_seq[2]} next")
        
        # General suggestions
        if not self.active_files:
            suggestions.append("Start by listing directory contents to understand the project structure")
        elif len(self.active_files) > 5:
            suggestions.append("Consider focusing on fewer files to maintain context")
        
        return suggestions
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current context manager status"""
        return {
            "initialized": self.is_initialized,
            "session_id": self.session_id,
            "workspace_path": str(self.workspace_path) if self.workspace_path else None,
            "current_task": self.current_task,
            "active_files_count": len(self.active_files),
            "embedding_model": self._embedding_model_name,
            "database_info": self.db.get_connection_info()
        }
    
    async def cleanup(self):
        """Cleanup resources and close connections"""
        # Database connections are automatically closed by the async context manager
        self.is_initialized = False
        self.session_id = None 