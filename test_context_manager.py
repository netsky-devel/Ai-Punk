#!/usr/bin/env python3
"""
Test Script for Smart Context Manager
Simple test to verify SurrealDB integration and vector search
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.context.manager import SmartContextManager
from src.workspace.manager import WorkspaceManager
from rich.console import Console


async def test_context_manager():
    """Test Smart Context Manager functionality"""
    console = Console()
    console.print("🧪 [bold blue]Testing Smart Context Manager[/bold blue]\n")
    
    try:
        # Setup workspace
        workspace_manager = WorkspaceManager()
        current_workspace = workspace_manager.get_current_workspace()
        
        if not current_workspace:
            console.print("❌ [red]No workspace selected. Please select a workspace first.[/red]")
            return
        
        console.print(f"📁 Workspace: {current_workspace}")
        
        # Initialize Smart Context Manager
        console.print("\n🧠 Initializing Smart Context Manager...")
        context_manager = SmartContextManager(workspace_manager)
        
        result = await context_manager.initialize()
        
        if result["success"]:
            console.print("✅ [green]Smart Context Manager initialized successfully![/green]")
            console.print(f"   Session ID: {result['session_id']}")
        else:
            console.print(f"❌ [red]Initialization failed: {result['error']}[/red]")
            return
        
        # Test 1: Basic functionality
        console.print("\n📝 Test 1: Adding sample code to context...")
        sample_code = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def optimize_fibonacci(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = optimize_fibonacci(n-1, memo) + optimize_fibonacci(n-2, memo)
    return memo[n]
"""
        
        await context_manager.add_code_embedding("test_fibonacci.py", sample_code, "function")
        console.print("✅ [green]Sample code added to context[/green]")
        
        # Test 2: Semantic search
        console.print("\n🔍 Test 2: Semantic search...")
        search_queries = [
            "recursive function",
            "optimization algorithm",
            "fibonacci calculation",
            "dynamic programming"
        ]
        
        for query in search_queries:
            results = await context_manager.semantic_search(query, limit=2)
            console.print(f"   Query: '{query}' -> {len(results)} results")
            
            if results:
                for result in results:
                    similarity = result.get('similarity', 0)
                    console.print(f"     • {result['file_path']} (similarity: {similarity:.3f})")
        
        # Test 3: Action tracking
        console.print("\n⚡ Test 3: Action tracking...")
        await context_manager.track_action(
            tool_name="test_tool",
            input_data={"test": "sample_input"},
            result={"success": True, "output": "test_output"},
            execution_time=0.5
        )
        console.print("✅ [green]Action tracked successfully[/green]")
        
        # Test 4: Workflow patterns
        console.print("\n🔄 Test 4: Getting workflow patterns...")
        patterns = await context_manager.get_workflow_patterns(5)
        console.print(f"   Found {len(patterns)} workflow patterns")
        
        # Test 5: Context suggestions
        console.print("\n💡 Test 5: Getting context suggestions...")
        suggestions = await context_manager.suggest_next_actions("implement efficient algorithm")
        
        console.print(f"   Semantic matches: {len(suggestions.get('semantic_matches', []))}")
        console.print(f"   Workflow patterns: {len(suggestions.get('workflow_patterns', []))}")
        console.print(f"   Suggested steps: {len(suggestions.get('suggested_next_steps', []))}")
        
        if suggestions.get('suggested_next_steps'):
            console.print("   Suggestions:")
            for suggestion in suggestions['suggested_next_steps']:
                console.print(f"     • {suggestion}")
        
        # Test 6: Status check
        console.print("\n📊 Test 6: Context Manager status...")
        status = await context_manager.get_status()
        console.print(f"   Initialized: {status['initialized']}")
        console.print(f"   Session ID: {status['session_id']}")
        console.print(f"   Active files: {status['active_files_count']}")
        console.print(f"   Embedding model: {status['embedding_model']}")
        
        console.print("\n🎉 [bold green]All tests completed successfully![/bold green]")
        
        # Cleanup
        await context_manager.cleanup()
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Test failed: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(test_context_manager()) 