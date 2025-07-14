# 🤖 AI Punk - Autonomous Software Development Assistant

🤖 **AI Punk** is a full-featured autonomous software development assistant with **complete transparency of the thinking process**. The agent uses LangChain ReAct pattern and modern AI models to independently perform programming tasks.

## ✨ Key Features

- **🧠 Complete thinking transparency**: See every step of the agent's reasoning in real-time
- **🤖 Autonomous execution**: Agent independently plans and executes complex tasks
- **🔒 Secure workspace**: Agent works only within the selected directory for security
- **🛠️ Rich tool set**: File operations, terminal commands, code search, and editing
- **🎨 Beautiful interface**: Rich terminal UI with full process visualization
- **🌐 Multi-language support**: Automatically detects user language (English/Russian)
- **⚡ High performance**: Fast LangChain integration with optimized tools

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
├── main.py             # Application entry point
├── src/
│   ├── agent/          # LangChain ReAct agent with transparency
│   ├── tools/          # File operations and system tools
│   ├── ui/             # Rich terminal interface
│   ├── config.py       # Configuration management
│   ├── workspace.py    # Secure workspace management
│   └── localization.py # Multi-language support
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🛠️ Available Tools

- **📁 File Operations**: list_directory, read_file, edit_file
- **🔍 Search**: grep_search for finding code patterns
- **💻 Terminal**: run_terminal for executing commands
- **🔒 Security**: All operations limited to selected workspace

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

### Code modification:
```
User: "Add error handling to the main.py file"
Agent: [Reads file, adds proper error handling, explains changes]
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