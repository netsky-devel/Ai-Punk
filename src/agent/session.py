"""
Session Management System
Maintains conversation context and continuity between CLI interactions
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class SessionManager:
    """
    Manages persistent session state for CLI interactions
    Solves the problem of losing context between messages
    """
    
    def __init__(self, workspace_path: Optional[str] = None, max_history: int = 20):
        self.workspace_path = workspace_path
        self.max_history = max_history  # Configurable history size
        self.session_file = self._get_session_file_path()
        self.session_data = self._load_session()
        
    def _get_session_file_path(self) -> Path:
        """Get path to session file"""
        if self.workspace_path:
            # Store session file in workspace .ai-punk directory
            session_dir = Path(self.workspace_path) / ".ai-punk"
            session_dir.mkdir(exist_ok=True)
            return session_dir / "session.json"
        else:
            # Store in user home directory
            home_dir = Path.home() / ".ai-punk"
            home_dir.mkdir(exist_ok=True)
            return home_dir / "global_session.json"
    
    def _load_session(self) -> Dict[str, Any]:
        """Load session data from file"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if session is recent (within 24 hours)
                if self._is_session_recent(data):
                    return data
                else:
                    # Session too old, start fresh
                    return self._create_new_session()
            except Exception:
                # Corrupted session file, start fresh
                return self._create_new_session()
        else:
            return self._create_new_session()
    
    def _is_session_recent(self, session_data: Dict[str, Any]) -> bool:
        """Check if session is recent enough to continue"""
        try:
            last_activity = datetime.fromisoformat(session_data.get('last_activity', ''))
            return datetime.now() - last_activity < timedelta(hours=24)
        except Exception:
            return False
    
    def _create_new_session(self) -> Dict[str, Any]:
        """Create new session data"""
        return {
            "session_id": f"session_{int(datetime.now().timestamp())}",
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "workspace_path": self.workspace_path,
            "conversation_history": [],
            "context_data": {},
            "user_preferences": {},
            "workflow_patterns": {}
        }
    
    def _save_session(self):
        """Save session data to file"""
        try:
            self.session_data["last_activity"] = datetime.now().isoformat()
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save session: {e}")
    
    def add_conversation_turn(self, user_input: str, agent_response: Dict[str, Any]):
        """Add a conversation turn to history"""
        turn = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "agent_response": {
                "success": agent_response.get("success", False),
                "output": agent_response.get("output", "")[:500],  # Truncate long outputs
                "tools_used": self._extract_tools_used(agent_response)
            }
        }
        
        self.session_data["conversation_history"].append(turn)
        
        # Keep only last max_history turns to avoid huge files
        if len(self.session_data["conversation_history"]) > self.max_history:
            self.session_data["conversation_history"] = self.session_data["conversation_history"][-self.max_history:]
        
        self._save_session()
    
    def _extract_tools_used(self, agent_response: Dict[str, Any]) -> List[str]:
        """Extract tools used from agent response"""
        try:
            tools = []
            steps = agent_response.get("intermediate_steps", [])
            for step in steps:
                if isinstance(step, tuple) and len(step) >= 2:
                    action = step[0]
                    if hasattr(action, 'tool'):
                        tools.append(action.tool)
            return tools
        except Exception:
            return []
    
    def get_conversation_context(self, max_turns: int = 5) -> str:
        """Get recent conversation context for prompt enhancement"""
        history = self.session_data.get("conversation_history", [])
        recent_turns = history[-max_turns:] if history else []
        
        if not recent_turns:
            return "No previous conversation history."
        
        context_lines = ["**RECENT CONVERSATION CONTEXT**:"]
        for i, turn in enumerate(recent_turns, 1):
            user_input = turn["user_input"][:100]  # Truncate for brevity
            success = "✅" if turn["agent_response"]["success"] else "❌"
            context_lines.append(f"{i}. User: {user_input}... {success}")
        
        return "\n".join(context_lines)
    
    def update_context_data(self, key: str, value: Any):
        """Update context data for persistence"""
        self.session_data["context_data"][key] = value
        self._save_session()
    
    def get_context_data(self, key: str, default: Any = None) -> Any:
        """Get context data"""
        return self.session_data["context_data"].get(key, default)
    
    def update_user_preference(self, key: str, value: Any):
        """Update user preference"""
        self.session_data["user_preferences"][key] = value
        self._save_session()
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        return self.session_data["user_preferences"].get(key, default)
    
    def track_workflow_pattern(self, pattern_name: str):
        """Track workflow patterns for learning"""
        patterns = self.session_data["workflow_patterns"]
        patterns[pattern_name] = patterns.get(pattern_name, 0) + 1
        self._save_session()
    
    def get_frequent_patterns(self, limit: int = 5) -> List[tuple]:
        """Get most frequent workflow patterns"""
        patterns = self.session_data["workflow_patterns"]
        sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
        return sorted_patterns[:limit]
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        history = self.session_data.get("conversation_history", [])
        successful_turns = sum(1 for turn in history if turn["agent_response"]["success"])
        
        return {
            "session_id": self.session_data["session_id"],
            "created_at": self.session_data["created_at"],
            "total_turns": len(history),
            "successful_turns": successful_turns,
            "success_rate": successful_turns / len(history) if history else 0,
            "workspace": self.workspace_path,
            "patterns_learned": len(self.session_data["workflow_patterns"])
        }
    
    def clear_session(self):
        """Clear current session and start fresh"""
        if self.session_file.exists():
            try:
                os.remove(self.session_file)
            except Exception:
                pass
        
        self.session_data = self._create_new_session()
        self._save_session()
    
    def export_session(self, export_path: str):
        """Export session data for analysis or backup"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False 