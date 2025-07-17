"""
Core Prompt Management System
Integrates with Smart Context Manager for intelligent prompt enhancement
"""

import asyncio
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from pathlib import Path

from .templates import (
    ContextInfo, 
    SystemPromptTemplate, 
    ContextualPromptTemplate
)

if TYPE_CHECKING:
    from ...context.manager import SmartContextManager


class PromptManager:
    """
    Advanced prompt management system with context integration
    Maintains session continuity and contextual awareness
    """
    
    def __init__(self, context_manager: Optional['SmartContextManager'] = None):
        self.context_manager = context_manager
        self.system_template = SystemPromptTemplate()
        self.contextual_template = ContextualPromptTemplate()
        
        # Session state for continuity
        self.session_memory = SessionMemory()
        
    async def create_enhanced_prompt(
        self, 
        base_task: str,
        tools: List[str] = None,
        scenario: str = "general",
        workspace_path: str = None,
        **kwargs
    ) -> str:
        """
        Create context-enhanced prompt with Smart Context Manager integration
        """
        # Build context information
        context_info = await self._build_context_info(
            base_task, workspace_path, **kwargs
        )
        
        # Add session memory to context
        self.session_memory.add_interaction(base_task)
        context_info.session_history = self.session_memory.get_recent_history()
        
        # Generate enhanced prompt
        if scenario == "general":
            enhanced_prompt = self.system_template.render(
                context_info, 
                tools=tools or [],
                **kwargs
            )
        else:
            # Use contextual template for specific scenarios
            enhanced_prompt = self.contextual_template.render(
                context_info,
                scenario=scenario,
                **kwargs
            )
        
        return enhanced_prompt
    
    async def _build_context_info(
        self, 
        task: str, 
        workspace_path: str = None,
        **kwargs
    ) -> ContextInfo:
        """Build comprehensive context information"""
        context = ContextInfo()
        context.workspace_path = workspace_path
        context.current_task = task
        context.error_context = kwargs.get('error_context')
        
        # Get context from Smart Context Manager if available
        if self.context_manager and await self._ensure_context_ready():
            try:
                # Get intelligent suggestions and context
                suggestions = await self.context_manager.suggest_next_actions(task)
                
                context.semantic_matches = suggestions.get("semantic_matches", [])
                context.workflow_patterns = suggestions.get("workflow_patterns", [])
                context.active_files = suggestions.get("active_files", [])
                
                # Get recent actions
                context.recent_actions = await self._get_recent_actions()
                
            except Exception as e:
                # Graceful fallback if context manager fails
                print(f"Context manager error: {e}")
        
        return context
    
    async def _ensure_context_ready(self) -> bool:
        """Ensure Smart Context Manager is ready"""
        if not self.context_manager:
            return False
        
        try:
            status = await self.context_manager.get_status()
            return status.get("initialized", False)
        except Exception:
            return False
    
    async def _get_recent_actions(self) -> List[Dict[str, Any]]:
        """Get recent actions from context manager"""
        try:
            # This would need to be implemented in SmartContextManager
            # For now, return empty list
            return []
        except Exception:
            return []
    
    def update_session_memory(self, interaction: str, result: Dict[str, Any]):
        """Update session memory with interaction results"""
        self.session_memory.add_result(interaction, result)
    
    def get_session_context(self) -> Dict[str, Any]:
        """Get current session context for continuity"""
        return {
            "history": self.session_memory.get_recent_history(),
            "patterns": self.session_memory.get_interaction_patterns(),
            "context_size": len(self.session_memory.interactions)
        }
    
    def clear_session(self):
        """Clear session memory (new session)"""
        self.session_memory.clear()


class SessionMemory:
    """
    Manages session continuity and memory between CLI interactions
    Solves the problem of losing context between messages
    """
    
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.interactions: List[Dict[str, Any]] = []
        self.patterns: Dict[str, int] = {}
    
    def add_interaction(self, task: str, result: Dict[str, Any] = None):
        """Add a new interaction to memory"""
        interaction = {
            "task": task,
            "timestamp": self._get_timestamp(),
            "result": result
        }
        
        self.interactions.append(interaction)
        
        # Maintain max history size
        if len(self.interactions) > self.max_history:
            self.interactions = self.interactions[-self.max_history:]
        
        # Track patterns
        self._update_patterns(task)
    
    def add_result(self, task: str, result: Dict[str, Any]):
        """Add result to the most recent matching interaction"""
        for interaction in reversed(self.interactions):
            if interaction["task"] == task and not interaction.get("result"):
                interaction["result"] = result
                break
    
    def get_recent_history(self, limit: int = 5) -> List[str]:
        """Get recent interaction history for context"""
        recent = self.interactions[-limit:] if self.interactions else []
        return [f"- {item['task']}" for item in recent]
    
    def get_interaction_patterns(self) -> Dict[str, int]:
        """Get common interaction patterns"""
        return dict(sorted(self.patterns.items(), key=lambda x: x[1], reverse=True)[:5])
    
    def _update_patterns(self, task: str):
        """Update pattern tracking"""
        # Simple keyword-based pattern recognition
        keywords = self._extract_keywords(task.lower())
        for keyword in keywords:
            self.patterns[keyword] = self.patterns.get(keyword, 0) + 1
    
    def _extract_keywords(self, task: str) -> List[str]:
        """Extract key patterns from task"""
        patterns = [
            "debug", "fix", "error", "bug",
            "create", "add", "new", "implement",
            "test", "check", "verify",
            "refactor", "optimize", "improve",
            "deploy", "build", "run",
            "search", "find", "look"
        ]
        return [p for p in patterns if p in task]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def clear(self):
        """Clear all session memory"""
        self.interactions.clear()
        self.patterns.clear()


class PromptBuilder:
    """
    Utility class for building dynamic prompts based on context
    """
    
    @staticmethod
    def enhance_with_context(
        base_prompt: str, 
        context_info: ContextInfo
    ) -> str:
        """Enhance any prompt with contextual information"""
        
        enhancements = []
        
        if context_info.semantic_matches:
            files = [m.get('file_path') for m in context_info.semantic_matches[:3]]
            enhancements.append(f"Consider these relevant files: {', '.join(files)}")
        
        if context_info.workflow_patterns:
            patterns = [p.get('pattern_name') for p in context_info.workflow_patterns[:2]]
            enhancements.append(f"Apply these workflow patterns: {', '.join(patterns)}")
        
        if context_info.recent_actions:
            actions = [a.get('tool_name') for a in context_info.recent_actions[-3:]]
            enhancements.append(f"Building on recent actions: {', '.join(actions)}")
        
        if enhancements:
            context_section = "\n\n**CONTEXTUAL ENHANCEMENT**:\n" + "\n".join([f"- {e}" for e in enhancements])
            return base_prompt + context_section
        
        return base_prompt
    
    @staticmethod
    def create_tool_specific_prompt(tool_name: str, context: ContextInfo) -> str:
        """Create tool-specific prompt enhancement"""
        
        tool_prompts = {
            "semantic_search": """
**SEMANTIC SEARCH OPTIMIZATION**:
- Focus on conceptual understanding and meaning
- Use natural language queries that capture intent
- Consider project context and architectural patterns
- Look for functional relationships, not just text matches
""",
            "grep_search": """
**EXACT SEARCH OPTIMIZATION**:
- Use precise regex patterns for exact matches
- Search for specific function names, imports, or keywords
- Escape special characters properly
- Consider file type restrictions for efficiency
""",
            "edit_file": """
**CODE EDITING EXCELLENCE**:
- Maintain consistent code style and project conventions
- Include necessary imports and dependencies
- Follow established architectural patterns
- Ensure immediate executability
- Add appropriate error handling and logging
""",
            "debug": """
**DEBUGGING STRATEGY**:
- Analyze error patterns and stack traces systematically
- Use contextual knowledge from similar past issues
- Create minimal reproducible test cases
- Apply semantic understanding to trace code flow
- Focus on root cause analysis
"""
        }
        
        return tool_prompts.get(tool_name, "") 