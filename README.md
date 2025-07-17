# 🤖 AI Punk - Autonomous Software Development Assistant

🤖 **AI Punk** is a full-featured autonomous software development assistant with **complete transparency of the thinking process**. The agent uses LangChain ReAct pattern and modern AI models to independently perform programming tasks.

## ✨ Key Features

- **🧠 Complete thinking transparency**: See every step of the agent's reasoning in real-time
- **🤖 Autonomous execution**: Agent independently plans and executes complex tasks
- **🏗️ Modular architecture**: Clean, organized codebase with separated concerns
- **🔒 Secure workspace**: Agent works only within the selected directory for security
- **🛠️ Rich tool set**: Comprehensive file operations, search, terminal commands, and editing
- **🎨 Beautiful interface**: Rich terminal UI with full process visualization
- **🌐 Multi-language support**: Automatically detects user language (English/Russian)
- **⚡ High performance**: Fast LangChain integration with optimized tools
- **🔍 Smart search**: Advanced file search with relevance scoring and semantic search

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AI provider**:
   ```bash
   python main.py
   # Select option 1 - Setup AI Provider
   ```

3. **Select working directory**:
   ```bash
   # Select option 2 - Select Working Directory
   ```

4. **Initialize agent**:
   ```bash
   # Select option 3 - Initialize Agent
   ```

5. **Start working**:
   ```bash
   # Select option 4 - Start Chat with Agent
   ```

## 🧠 Process Transparency

AI Punk shows the **complete agent thinking process**:

```
╭─ 🧠 Agent Thinking (Step 1) ─────────────────────────────────────────────────────╮
│ I need to analyze the project structure first to understand what we're working   │
│ with. Let me start by listing the current directory contents.                    │
╰──────────────────────────────────────────────────────────────────────────────────╯

╭─ ⚡ Agent Action ─────────────────────────────────────────────────────────────────╮
│  🔧 Tool:  list_directory                                                        │
│  📝 Input: "."                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────╯

╭─ ✅ Execution Result (in 0.15s) ────────────────────────────────────────────────╮
│ [Agent's final answer]                                                           │
╰──────────────────────────────────────────────────────────────────────────────────╯
```

## 📁 Project Structure

```
ai-punk/
├── main.py                    # Application entry point
├── src/
│   ├── agent/                 # AI Agent Core
│   │   ├── agent.py          # Main ReAct agent with transparency
│   │   ├── transparency.py   # Thinking process visualization
│   │   └── wrappers/         # LangChain tool wrappers
│   │       ├── factory.py    # Tool factory for agent integration
│   │       ├── filesystem.py # File operation wrappers
│   │       ├── search.py     # Search tool wrappers
│   │       ├── terminal.py   # Terminal command wrappers
│   │       ├── semantic.py   # Semantic search wrappers
│   │       └── file_ops.py   # Additional file operation wrappers
│   ├── config/               # Configuration Management
│   │   ├── models.py         # Configuration data models
│   │   └── manager.py        # Configuration manager
│   ├── localization/         # Multi-language Support
│   │   ├── models.py         # Language data models
│   │   ├── core.py           # Localization core logic
│   │   └── messages/         # Language-specific messages
│   │       ├── english.py    # English translations
│   │       └── russian.py    # Russian translations
│   ├── workspace/            # Workspace Management
│   │   └── manager.py        # Secure workspace handling
│   ├── tools/                # Core Tools
│   │   ├── base.py           # Base tool classes
│   │   ├── codebase_search.py # Semantic code search
│   │   └── filesystem/       # File System Operations
│   │       ├── models.py     # File operation data models
│   │       ├── security.py   # Security validation
│   │       ├── list_dir.py   # Directory listing
│   │       ├── read_file.py  # File reading
│   │       ├── edit_file.py  # File editing
│   │       ├── delete_file.py # Safe file deletion
│   │       ├── file_search.py # Smart file search
│   │       ├── grep.py       # Pattern search in files
│   │       └── terminal.py   # Terminal command execution
│   └── ui/                   # User Interface
│       ├── agent_interface.py # Rich terminal interface
│       └── workspace_selector.py # Directory selection UI
├── requirements.txt          # Python dependencies
├── env.example              # Environment configuration template
└── README.md               # This file
```

## 🏗️ Architecture Overview

AI Punk follows a clean, modular architecture with clear separation of concerns:

### 🎯 Core Components

- **🤖 Agent Core** (`src/agent/`): LangChain ReAct agent with transparent thinking process
- **🔧 Tools Layer** (`src/tools/`): Modular tool system with filesystem operations and search
- **🎨 UI Layer** (`src/ui/`): Rich terminal interface for user interaction
- **⚙️ Configuration** (`src/config/`): Centralized configuration management
- **🌐 Localization** (`src/localization/`): Multi-language support system
- **📁 Workspace** (`src/workspace/`): Secure workspace management

### 🔗 Integration Patterns

- **LangChain Wrappers** (`src/agent/wrappers/`): Clean integration between tools and AI agent
- **Factory Pattern**: Centralized tool creation and management
- **Security Layer**: Consistent validation across all file operations
- **Error Handling**: Robust error management with user-friendly messages

### 📊 Data Flow

```
User Input → UI Layer → Agent Core → Tool Wrappers → Core Tools → File System
           ← UI Layer ← Transparency ← LangChain ReAct ← Tool Results ← 
```

## 🛠️ Available Tools

### 📁 File Operations
- **📋 list_directory**: Lists directory contents with file details
- **📖 read_file**: Reads and displays file contents with syntax highlighting
- **✏️ edit_file**: Advanced file editing with search and replace functionality
- **🗑️ delete_file**: Safe file deletion with backup and validation
- **🔍 file_search**: Smart file search with relevance scoring and fuzzy matching

### 🔍 Search and Analysis
- **🔎 grep_search**: Pattern search in files with regex support
- **🧠 codebase_search**: Semantic code search for understanding code structure

### 💻 System Operations
- **⚡ run_terminal**: Execute terminal commands in controlled environment

### 🔒 Security Features
- **🛡️ Path validation**: All operations use secure relative paths
- **📂 Workspace isolation**: Strict containment within selected directory
- **✅ Operation logging**: Full transparency of all file operations

## 🔧 Dependencies

- **Python 3.8+** - Core runtime
- **LangChain** - ReAct agent and AI model integration
- **Rich** - Beautiful terminal interface
- **OpenAI/Google/Anthropic** - AI model providers

## 🌐 Language Support

The agent automatically detects the user's language and responds accordingly:
- **English**: Default language for documentation and system messages
- **Russian**: Full support with automatic detection
- **Mixed languages**: Prioritizes the dominant language in user input

## 🔒 Security Features

- **Workspace isolation**: Agent cannot access files outside the selected directory
- **Path validation**: All file operations use relative paths only
- **Safe execution**: Terminal commands run in controlled environment

## 📝 Usage Examples

### Basic file analysis:
```
User: "Analyze the project structure and tell me what this codebase does"
Agent: [Analyzes files, provides detailed explanation]
```

### Advanced file search:
```
User: "Find all configuration files in the project"
Agent: [Uses smart file search to locate config files with relevance scoring]
```

### Code modification:
```
User: "Add error handling to the main.py file"
Agent: [Reads file, adds proper error handling, explains changes]
```

### Safe file operations:
```
User: "Delete the old backup files but keep the important ones"
Agent: [Uses safe deletion with validation and backup functionality]
```

### Semantic code search:
```
User: "Show me how authentication is implemented"
Agent: [Uses semantic search to find auth-related code across the project]
```

### Multi-language interaction:
```
User: "создай новый файл config.json с базовыми настройками"
Agent: [Responds in Russian, creates the file as requested]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:
1. Check that your AI provider is properly configured
2. Ensure the working directory is selected
3. Verify all dependencies are installed
4. Check the console output for detailed error messages

For additional help, please open an issue on GitHub. 