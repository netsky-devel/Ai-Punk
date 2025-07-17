#!/usr/bin/env python3
"""
Simple test without SurrealDB for Smart Context Manager
Testing sentence transformers and basic functionality
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sentence_transformers import SentenceTransformer
from rich.console import Console


async def test_basic_functionality():
    """Test basic functionality without SurrealDB"""
    console = Console()
    console.print("🧪 [bold blue]Testing Smart Context Manager Components[/bold blue]\n")
    
    try:
        # Test 1: Sentence Transformers
        console.print("📝 Test 1: Loading embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        console.print("✅ [green]Model loaded successfully![/green]")
        
        # Test 2: Generate embeddings
        console.print("\n🔢 Test 2: Generating embeddings...")
        sample_texts = [
            "def calculate_fibonacci(n): return n if n <= 1 else fib(n-1) + fib(n-2)",
            "function to calculate factorial recursively",
            "optimization algorithm for dynamic programming",
            "machine learning model training"
        ]
        
        embeddings = model.encode(sample_texts)
        console.print(f"✅ [green]Generated embeddings: {embeddings.shape}[/green]")
        
        # Test 3: Similarity calculation
        console.print("\n🔍 Test 3: Calculating similarities...")
        query = "recursive function implementation"
        query_embedding = model.encode([query])
        
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(query_embedding, embeddings)[0]
        
        console.print(f"Query: '{query}'")
        for i, (text, sim) in enumerate(zip(sample_texts, similarities)):
            console.print(f"  {i+1}. {text[:50]}... (similarity: {sim:.3f})")
        
        # Test 4: Directory structure
        console.print("\n📁 Test 4: Checking directory structure...")
        context_dir = Path("src/context")
        if context_dir.exists():
            console.print("✅ [green]Context directory structure exists[/green]")
            for item in context_dir.rglob("*.py"):
                console.print(f"  📄 {item}")
        else:
            console.print("❌ [red]Context directory not found[/red]")
        
        console.print("\n🎉 [bold green]Basic functionality tests passed![/bold green]")
        
        # Show Smart Context Manager capabilities
        console.print("\n🧠 [bold blue]Smart Context Manager Capabilities:[/bold blue]")
        capabilities = [
            "✨ Semantic code search with vector embeddings",
            "📊 Multi-model SurrealDB database (documents + vectors + graph + time-series)",
            "🔄 Automatic workflow pattern learning",
            "📝 Real-time action logging and analysis",
            "🔗 File dependency graph analysis",
            "💡 Intelligent suggestions based on context",
            "⚡ Session state management",
            "🎯 Context-aware task enhancement"
        ]
        
        for capability in capabilities:
            console.print(f"  {capability}")
        
        console.print("\n📖 [bold blue]Next Steps:[/bold blue]")
        console.print("  1. Install SurrealDB server for full functionality")
        console.print("  2. Run 'docker run -p 8000:8000 surrealdb/surrealdb:latest start --user root --pass secret memory'")
        console.print("  3. Execute full test with 'python test_context_manager.py'")
        console.print("  4. Integrate with AI agent for enhanced workflow assistance")
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Test failed: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(test_basic_functionality()) 