"""
Database Schema for Smart Context Manager
Defines tables, indexes, and events using SurrealQL 2.0+ syntax
"""

from typing import List
from .connection import SurrealConnection


SCHEMA_QUERIES = [
    # Session Management Table
    """
    DEFINE TABLE context_session SCHEMAFULL;
    DEFINE FIELD session_id ON context_session TYPE string;
    DEFINE FIELD workspace_path ON context_session TYPE string;
    DEFINE FIELD current_task ON context_session TYPE option<string>;
    DEFINE FIELD active_files ON context_session TYPE array<string>;
    DEFINE FIELD focus_area ON context_session TYPE option<string>;
    DEFINE FIELD created_at ON context_session TYPE datetime DEFAULT time::now();
    DEFINE FIELD updated_at ON context_session TYPE datetime DEFAULT time::now();
    """,
    
    # Action Tracking (Time-series with complex IDs)
    """
    DEFINE TABLE action_log SCHEMAFULL;
    DEFINE FIELD tool_name ON action_log TYPE string;
    DEFINE FIELD input_data ON action_log TYPE object;
    DEFINE FIELD result ON action_log TYPE object;
    DEFINE FIELD execution_time ON action_log TYPE duration;
    DEFINE FIELD created_at ON action_log TYPE datetime DEFAULT time::now();
    """,
    
    # File Context
    """
    DEFINE TABLE file_context SCHEMAFULL;
    DEFINE FIELD file_path ON file_context TYPE string;
    DEFINE FIELD workspace ON file_context TYPE string;
    DEFINE FIELD last_accessed ON file_context TYPE datetime DEFAULT time::now();
    DEFINE FIELD modification_count ON file_context TYPE int DEFAULT 0;
    DEFINE FIELD content_hash ON file_context TYPE string;
    DEFINE FIELD file_size ON file_context TYPE int;
    """,
    
    # Code Embeddings for Semantic Search
    """
    DEFINE TABLE code_embedding SCHEMAFULL;
    DEFINE FIELD file_path ON code_embedding TYPE string;
    DEFINE FIELD chunk_id ON code_embedding TYPE string;
    DEFINE FIELD content ON code_embedding TYPE string;
    DEFINE FIELD embedding ON code_embedding TYPE array<float>;
    DEFINE FIELD chunk_type ON code_embedding TYPE string;
    DEFINE FIELD created_at ON code_embedding TYPE datetime DEFAULT time::now();
    """,
    
    # Vector index for code embeddings (384 dimensions for all-MiniLM-L6-v2)
    """
    DEFINE INDEX code_vector_idx ON code_embedding 
        FIELDS embedding HNSW DIMENSION 384 DIST COSINE;
    """,
    
    # File Dependencies (Graph Relations)
    """
    DEFINE TABLE depends_on SCHEMAFULL TYPE RELATION
        FROM file_context TO file_context;
    DEFINE FIELD dependency_type ON depends_on TYPE string;
    DEFINE FIELD strength ON depends_on TYPE float DEFAULT 1.0;
    """,
    
    # Workflow Patterns
    """
    DEFINE TABLE workflow_pattern SCHEMAFULL;
    DEFINE FIELD pattern_name ON workflow_pattern TYPE string;
    DEFINE FIELD tools_sequence ON workflow_pattern TYPE array<string>;
    DEFINE FIELD frequency ON workflow_pattern TYPE int DEFAULT 1;
    DEFINE FIELD success_rate ON workflow_pattern TYPE float DEFAULT 1.0;
    DEFINE FIELD last_used ON workflow_pattern TYPE datetime DEFAULT time::now();
    DEFINE FIELD created_at ON workflow_pattern TYPE datetime DEFAULT time::now();
    """,
    
    # Project Knowledge
    """
    DEFINE TABLE project_knowledge SCHEMAFULL;
    DEFINE FIELD knowledge_type ON project_knowledge TYPE string;
    DEFINE FIELD content ON project_knowledge TYPE object;
    DEFINE FIELD relevance_score ON project_knowledge TYPE float DEFAULT 1.0;
    DEFINE FIELD created_at ON project_knowledge TYPE datetime DEFAULT time::now();
    DEFINE FIELD updated_at ON project_knowledge TYPE datetime DEFAULT time::now();
    """,
    
    # Indexes for better performance
    """
    DEFINE INDEX session_workspace_idx ON context_session COLUMNS workspace_path;
    DEFINE INDEX file_path_idx ON file_context COLUMNS file_path;
    DEFINE INDEX action_time_idx ON action_log COLUMNS created_at;
    DEFINE INDEX pattern_name_idx ON workflow_pattern COLUMNS pattern_name;
    """,
    
    # Event for automatic pattern learning
    """
    DEFINE EVENT learn_workflow_pattern ON action_log WHEN $event = 'CREATE' THEN {
        -- Get recent tools used in this session
        LET $session_tools = (
            SELECT tool_name FROM action_log 
            WHERE created_at > time::now() - 5m
            ORDER BY created_at ASC
            LIMIT 10
        ).tool_name;
        
        -- If we have enough tools, create/update pattern
        IF array::len($session_tools) >= 3 {
            LET $pattern_key = string::join(array::slice($session_tools, -3), "_");
            UPSERT workflow_pattern SET
                pattern_name = $pattern_key,
                tools_sequence = array::slice($session_tools, -3),
                frequency = frequency + 1 IF frequency ELSE 1,
                last_used = time::now(),
                updated_at = time::now()
            WHERE pattern_name = $pattern_key;
        };
    };
    """,
    
    # Event for file access tracking
    """
    DEFINE EVENT track_file_access ON file_context WHEN $event = 'UPDATE' THEN {
        -- Update modification count
        UPDATE $this SET 
            modification_count = modification_count + 1,
            last_accessed = time::now();
    };
    """
]


async def setup_context_schema(connection: SurrealConnection) -> List[str]:
    """Setup the complete database schema for Smart Context Manager"""
    results = []
    
    for query in SCHEMA_QUERIES:
        try:
            result = await connection.execute_query(query.strip())
            results.append(f"✅ Schema setup successful: {query[:50]}...")
        except Exception as e:
            results.append(f"❌ Schema setup failed: {e}")
    
    return results


async def reset_schema(connection: SurrealConnection) -> List[str]:
    """Reset the database schema (careful: this will delete all data!)"""
    drop_queries = [
        "REMOVE TABLE context_session;",
        "REMOVE TABLE action_log;", 
        "REMOVE TABLE file_context;",
        "REMOVE TABLE code_embedding;",
        "REMOVE TABLE depends_on;",
        "REMOVE TABLE workflow_pattern;",
        "REMOVE TABLE project_knowledge;",
        "REMOVE EVENT learn_workflow_pattern;",
        "REMOVE EVENT track_file_access;"
    ]
    
    results = []
    for query in drop_queries:
        try:
            await connection.execute_query(query)
            results.append(f"✅ Dropped: {query}")
        except Exception as e:
            results.append(f"⚠️ Drop failed (may not exist): {e}")
    
    # Recreate schema
    setup_results = await setup_context_schema(connection)
    results.extend(setup_results)
    
    return results


def get_schema_info() -> dict:
    """Get information about the schema structure"""
    return {
        "tables": [
            "context_session",
            "action_log", 
            "file_context",
            "code_embedding",
            "depends_on",
            "workflow_pattern",
            "project_knowledge"
        ],
        "indexes": [
            "code_vector_idx",
            "session_workspace_idx",
            "file_path_idx", 
            "action_time_idx",
            "pattern_name_idx"
        ],
        "events": [
            "learn_workflow_pattern",
            "track_file_access"
        ],
        "features": [
            "Vector search with HNSW",
            "Time-series action logging",
            "Graph relationships",
            "Automatic pattern learning",
            "Real-time events"
        ]
    } 