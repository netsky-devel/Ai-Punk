# AI Punk

**Autonomous AI Coding Assistant with Full Process Transparency**

## 🎯 Philosophy

AI Punk is not just another AI assistant - it's an **autonomous agent** that shows you its complete thought process as it works. You'll see every decision, every tool usage, and every step of reasoning in real-time.

### Key Principles

1. **🔍 Full Transparency** - See every thought, action, and observation
2. **🤖 Autonomous Operation** - No permission asking, full automation  
3. **🧠 Educational Experience** - Learn by watching the AI work
4. **🌍 Multilingual Support** - Responds in your language
5. **🏗️ Clean Architecture** - Domain-driven design principles

## 🚀 Features

- **Real-time Process Visibility** - Watch the AI think and act
- **Multi-step Task Execution** - Complex problem decomposition
- **Tool Chaining** - Combines multiple tools for solutions
- **Codebase Understanding** - Semantic search and analysis
- **File System Operations** - Read, write, search, and manage files
- **Terminal Integration** - Execute commands and see results
- **Vector Search** - Semantic code search with embeddings
- **Multiple AI Providers** - OpenAI, Google, Anthropic support

## 📁 Project Structure

```
ai-punk/
├── ai-punk-prompts.md       # System prompts and ReAct patterns
├── ai-punk-tools.md         # Tool descriptions and usage
├── ai-punk-architecture.md  # Clean architecture documentation
└── README.md               # This file
```

## 🔧 Saved Components

All key components from the previous implementation are preserved in markdown files:

- **Prompts** (`ai-punk-prompts.md`) - Complete system prompts with transparency requirements
- **Tools** (`ai-punk-tools.md`) - All 9 tools with descriptions and usage patterns  
- **Architecture** (`ai-punk-architecture.md`) - Clean architecture layers and design patterns

## 🎸 What Makes AI Punk Different

### Traditional AI Assistants:
```
User: "Fix this bug"
AI: "I fixed the bug. Here's the solution."
```

### AI Punk:
```
User: "Fix this bug"
AI: 
Thought: I need to understand the codebase structure first
Action: list_dir
Action Input: "."
Observation: Found these files: src/, tests/, package.json...

Thought: Now I should look at the main source files
Action: read_file  
Action Input: "src/main.js"
Observation: The file contains...

Thought: I can see the bug is in line 45, let me fix it
Action: edit_file
Action Input: {"path": "src/main.js", "content": "..."}
Observation: Successfully wrote to src/main.js

Thought: Let me verify the fix works
Action: run_terminal_cmd
Action Input: "npm test"
Observation: All tests passed!

Final Answer: Bug fixed! The issue was...
```

## 🎯 Next Steps

This repository now contains clean documentation of the AI Punk system. The next implementation can use these markdown files as reference for:

1. **System Prompts** - Copy the ReAct prompt with transparency requirements
2. **Tool Implementation** - Implement all 9 tools as documented
3. **Architecture** - Follow the Clean Architecture patterns
4. **Process Visibility** - Ensure full thought process transparency

## 🔮 Vision

AI Punk will become the most transparent and educational AI coding assistant, where users don't just get solutions - they learn by watching a master craftsman work through problems step by step.

---

**AI Punk** - Your transparent AI coding companion! 🤖✨ 