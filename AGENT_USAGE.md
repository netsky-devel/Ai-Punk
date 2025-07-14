# 🤖 AI Punk Agent - Usage Guide

Complete guide for using AI Punk Agent - an autonomous software development assistant with full process transparency.

## 🚀 Quick Start

### 1. Initial Setup
```bash
python main.py
```

The application will launch an interactive menu where you can configure all necessary settings.

### 2. AI Provider Configuration
Select option **1 - Setup AI Provider** and configure one of the supported providers:

- **OpenAI**: Requires API key and model selection (gpt-4, gpt-3.5-turbo)
- **Google**: Requires API key for Gemini models
- **Anthropic**: Requires API key for Claude models

### 3. Working Directory
Select option **2 - Select Working Directory** to choose the project folder where the agent will work.

**Important**: The agent works only within the selected working directory for security.

### 4. Agent Initialization
Select option **3 - Initialize Agent** to prepare the agent for work.

### 5. Start Working
Select option **4 - Start Chat with Agent** to begin interacting with the agent.

## 💬 Interaction with Agent

### Basic Commands
The agent understands natural language and can perform various programming tasks:

```
# File analysis
"Analyze the project structure"
"What does this code do?"
"Find all TODO comments"

# Code modification
"Add error handling to main.py"
"Refactor the database connection function"
"Create a new configuration file"

# Project tasks
"Set up a new Flask application"
"Add unit tests for the user module"
"Optimize the performance of the algorithm"
```

### 🧠 Agent Thinking
Shows the agent's reasoning about what needs to be done:
```
🧠 Agent Thinking (Step 1)
I need to analyze the project structure first to understand 
what we're working with. Let me start by listing the directory contents.
```

### ⚡ Agent Actions
Shows which tools the agent is using:
```
⚡ Agent Action
🔧 Tool: list_directory
📝 Input: "."
```

### ✅ Results
Shows the execution results and final answer:
```
✅ Execution Result (in 0.15s)
The project structure has been analyzed. This is a Python web application...
```

## 🛠️ Available Tools

### 📁 File Operations
- **list_directory**: Shows directory contents
- **read_file**: Reads file contents
- **edit_file**: Modifies files with search and replace

### 🔍 Search and Analysis
- **grep_search**: Searches for text patterns in files

### 💻 System Operations
- **run_terminal**: Executes terminal commands

## 🔒 Security and Limitations

### Working Directory
- The agent works only within the selected working directory
- Cannot access files outside this directory
- All paths are relative to the working directory

### Safe Operations
- All file operations are logged and visible
- Terminal commands run in a controlled environment
- No access to sensitive system areas

## 🌐 Multi-Language Support

The agent automatically detects your language and responds accordingly:

### English Example:
```
User: "Create a new Python module for database operations"
Agent: I'll create a new Python module for database operations...
```

### Russian Example:
```
User: "создай новый файл конфигурации"
Agent: Я создам новый файл конфигурации...
```

## ⚠️ Troubleshooting

### Error "Working directory not selected"
**Solution**: Select a working directory through the main menu (option 2)

### Agent doesn't initialize
**Solution**: 
1. Check that the AI provider is configured
2. Ensure the working directory is selected
3. Verify internet connection for AI model access

### Tools don't work
**Solution**:
1. Restart the agent
2. Check file permissions in the working directory
3. Ensure the working directory exists

### Performance Issues
**Solution**:
1. Use more specific requests
2. Break large tasks into smaller parts
3. Check internet connection speed

## 🎯 Best Practices

### Effective Requests
- Be specific about what you want to achieve
- Provide context about the project
- Break complex tasks into steps

### Working with Files
- Use relative paths (e.g., "src/main.py")
- Specify exact file names when possible
- Describe the changes you want clearly

### Code Quality
- Ask the agent to add comments and documentation
- Request error handling and validation
- Ask for code reviews and suggestions

## 📈 Advanced Usage

### Complex Projects
The agent can handle multi-file projects and understand dependencies between components.

### Code Refactoring
The agent can analyze code structure and suggest improvements while maintaining functionality.

### Documentation Generation
The agent can create documentation, README files, and code comments.

### Testing
The agent can create unit tests, integration tests, and help with debugging.

## 🤝 Tips for Success

1. **Start small**: Begin with simple tasks to understand the agent's capabilities
2. **Be clear**: Provide clear, specific instructions
3. **Review results**: Always check the agent's work
4. **Iterate**: Use the agent's suggestions to improve your code
5. **Learn**: Observe the agent's thinking process to learn new approaches 