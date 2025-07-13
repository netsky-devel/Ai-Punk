# AI Punk - Advanced VS Code AI Assistant

AI Punk is an advanced autonomous AI assistant for VS Code with clean architecture and extended development capabilities.

## 🚀 Key Features

### Architecture
- **Clean Architecture** with separated layers: Domain, Application, Infrastructure
- **LangChain integration** for multiple AI providers
- **Google Gemini and OpenAI** model support
- **Semantic search** with FAISS vector indexes

### Autonomous AI Agent
AI Punk provides advanced autonomous capabilities:
- **Autonomous task completion** until full resolution
- **Maximum context understanding** through multiple searches
- **Multilingual support** - responds in user's language
- **Smart tool usage** without mentioning tool names
- **Thorough analysis** with symbol tracing to definitions
- **Advanced code editing** capabilities

### Complete Tool Set

#### Basic Tools
- **list_dir** - explore project structure
- **read_file** - read files with line range support
- **edit_file** - create and edit files
- **run_terminal_cmd** - execute terminal commands

#### Advanced Tools
- **codebase_search** - semantic code search
- **grep_search** - precise regex pattern search
- **file_search** - fast file search by name
- **delete_file** - safe file deletion
- **search_replace** - precise text replacement

## 📦 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-punk
```

2. Install dependencies:
```bash
npm install
```

3. Compile the project:
```bash
npm run compile
```

4. Open in VS Code and press F5 to run the extension

## ⚙️ Configuration

Configure AI Punk through VS Code settings:

### Google Gemini (Default)
```json
{
  "aiPunk.provider": "google",
  "aiPunk.google.apiKey": "your-google-api-key",
  "aiPunk.google.model": "gemini-1.5-pro"
}
```

### OpenAI
```json
{
  "aiPunk.provider": "openai",
  "aiPunk.openAI.apiKey": "your-openai-api-key",
  "aiPunk.openAI.model": "gpt-4-turbo-preview"
}
```

## 🔧 Usage

1. Open AI Punk sidebar panel
2. Index your workspace: `Ctrl+Shift+P` → "AI Punk: Index Workspace"
3. Start chatting with the AI agent
4. The agent will autonomously use tools to complete tasks

## 🚀 Key Features of AI Punk

### Advantages:
- **Open source** - full transparency and customization
- **Clean Architecture** - easy to extend and maintain
- **Multiple AI providers** - not tied to one service
- **Extensible** - easy to add new tools
- **Secure** - data and privacy control

### Functionality:
- ✅ Autonomous complex task solving
- ✅ Advanced prompts and agent behavior
- ✅ Complete development tool set
- ✅ Semantic code search
- ✅ Multilingual support

## 🤝 Contributing

We welcome contributions to AI Punk!

### Adding a new tool:
1. Create file in `src/infrastructure/tools/`
2. Implement `DynamicTool` interface
3. Add import to `LangChainAdapter.ts`
4. Update `tools` array

### Improving prompts:
1. Study prompts in `src/infrastructure/adapters/LangChainAdapter.ts`
2. Test changes
3. Create Pull Request with description

## 📝 License

MIT License - see LICENSE file for details.

## 🔗 Links

- [LangChain Documentation](https://js.langchain.com/)
- [VS Code Extension API](https://code.visualstudio.com/api)
- [Google Gemini API](https://ai.google.dev/)
- [OpenAI API](https://platform.openai.com/docs)

---

**AI Punk** - Your personal AI assistant for development, built with love for clean code and open technologies! 🎸 