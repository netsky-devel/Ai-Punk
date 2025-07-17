"""
Predefined queries for Smart Context Manager
Collection of common SurrealQL queries for context operations
"""

from typing import Dict, Any, List
from .connection import SurrealConnection


class ContextQueries:
    """Collection of optimized queries for context operations"""
    
    def __init__(self, connection: SurrealConnection):
        self.db = connection
    
    async def get_active_session(self, workspace_path: str) -> Dict[str, Any]:
        """Get the most recent active session for workspace"""
        result = await self.db.execute_query("""
            SELECT * FROM context_session 
            WHERE workspace_path = $workspace_path 
            ORDER BY created_at DESC 
            LIMIT 1
        """, {"workspace_path": workspace_path})
        
        return result[0]["result"][0] if result and result[0]["result"] else {}
    
    async def get_recent_actions(self, hours: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent tool actions within specified hours"""
        result = await self.db.execute_query("""
            SELECT tool_name, input_data, result, execution_time, created_at
            FROM action_log 
            WHERE created_at > time::now() - $hours
            ORDER BY created_at DESC 
            LIMIT $limit
        """, {"hours": f"{hours}h", "limit": limit})
        
        return result[0]["result"] if result and result[0]["result"] else []
    
    async def search_code_semantically(self, query_embedding: List[float], 
                                     limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Perform semantic code search with similarity threshold"""
        result = await self.db.execute_query("""
            SELECT file_path, content, chunk_type,
                   vector::similarity::cosine(embedding, $query_vec) AS similarity
            FROM code_embedding 
            WHERE embedding <|$limit|> $query_vec
            AND vector::similarity::cosine(embedding, $query_vec) > $threshold
            ORDER BY similarity DESC
        """, {
            "query_vec": query_embedding,
            "limit": limit,
            "threshold": threshold
        })
        
        return result[0]["result"] if result and result[0]["result"] else []
    
    async def get_file_dependencies(self, file_path: str) -> Dict[str, List[str]]:
        """Get file dependencies (both ways)"""
        result = await self.db.execute_query("""
            SELECT 
                ->depends_on->file_context.file_path AS dependencies,
                <-depends_on<-file_context.file_path AS dependents
            FROM file_context 
            WHERE file_path = $file_path
        """, {"file_path": file_path})
        
        if result and result[0]["result"]:
            data = result[0]["result"][0]
            return {
                "dependencies": data.get("dependencies", []),
                "dependents": data.get("dependents", [])
            }
        return {"dependencies": [], "dependents": []}
    
    async def get_top_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequent workflow patterns"""
        result = await self.db.execute_query("""
            SELECT pattern_name, tools_sequence, frequency, success_rate, last_used
            FROM workflow_pattern 
            ORDER BY frequency DESC, success_rate DESC
            LIMIT $limit
        """, {"limit": limit})
        
        return result[0]["result"] if result and result[0]["result"] else []
    
    async def update_pattern_success(self, pattern_name: str, success: bool) -> bool:
        """Update pattern success rate"""
        try:
            await self.db.execute_query("""
                UPDATE workflow_pattern SET 
                    success_rate = (success_rate * frequency + $success_value) / (frequency + 1),
                    frequency = frequency + 1,
                    last_used = time::now()
                WHERE pattern_name = $pattern_name
            """, {
                "pattern_name": pattern_name,
                "success_value": 1.0 if success else 0.0
            })
            return True
        except Exception:
            return False
    
    async def get_workspace_stats(self, workspace_path: str) -> Dict[str, Any]:
        """Get comprehensive workspace statistics"""
        # Get file stats
        files_result = await self.db.execute_query("""
            SELECT 
                count() AS total_files,
                math::sum(file_size) AS total_size,
                math::mean(modification_count) AS avg_modifications
            FROM file_context 
            WHERE workspace = $workspace_path
            GROUP ALL
        """, {"workspace_path": workspace_path})
        
        # Get action stats
        actions_result = await self.db.execute_query("""
            SELECT 
                tool_name,
                count() AS usage_count,
                math::mean(math::abs(time::unix(execution_time))) AS avg_execution_time
            FROM action_log 
            WHERE created_at > time::now() - 24h
            GROUP BY tool_name
            ORDER BY usage_count DESC
        """)
        
        # Get embeddings count
        embeddings_result = await self.db.execute_query("""
            SELECT count() AS total_embeddings
            FROM code_embedding
            GROUP ALL
        """)
        
        return {
            "files": files_result[0]["result"][0] if files_result and files_result[0]["result"] else {},
            "actions": actions_result[0]["result"] if actions_result and actions_result[0]["result"] else [],
            "embeddings": embeddings_result[0]["result"][0] if embeddings_result and embeddings_result[0]["result"] else {"total_embeddings": 0}
        }
    
    async def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """Clean up old data beyond specified days"""
        cutoff_date = f"time::now() - {days}d"
        
        # Clean old action logs
        actions_result = await self.db.execute_query(f"""
            DELETE action_log WHERE created_at < {cutoff_date}
        """)
        
        # Clean old embeddings for non-existent files
        embeddings_result = await self.db.execute_query("""
            DELETE code_embedding WHERE file_path NOT IN (
                SELECT file_path FROM file_context
            )
        """)
        
        return {
            "actions_cleaned": len(actions_result[0]["result"]) if actions_result and actions_result[0]["result"] else 0,
            "embeddings_cleaned": len(embeddings_result[0]["result"]) if embeddings_result and embeddings_result[0]["result"] else 0
        } 