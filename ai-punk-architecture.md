# AI Punk Architecture

## Clean Architecture Layers

### 1. Domain Layer (`src/domain/`)
**Pure business logic, independent of frameworks**

- **Entities:** Core business objects
  - `Message` - Chat message entity
  - `Conversation` - Chat conversation entity
  - `Project` - Project metadata entity

- **Repositories:** Abstract interfaces for data access
  - `IConversationRepository` - Conversation storage interface

### 2. Application Layer (`src/application/`)
**Business logic coordinating domain and infrastructure**

- **Use Cases:** Business operations
  - `SendMessage` - Process user messages and AI responses
  - `IndexProject` - Create vector embeddings for codebase

- **Ports:** Interfaces for external dependencies
  - `IAIAdapter` - AI provider abstraction
  - `IConversationRepository` - Data storage abstraction

### 3. Infrastructure Layer (`src/infrastructure/`)
**External dependencies and framework implementations**

- **Adapters:** Concrete implementations
  - `LangChainAdapter` - AI provider using LangChain
  - `InMemoryConversationRepository` - In-memory storage
  - `CodebaseIndexer` - Vector search indexing

- **Tools:** AI agent tools
  - File system operations
  - Search and analysis
  - Terminal command execution

### 4. Presentation Layer (`src/presentation/`)
**User interface and framework-specific code**

- **VS Code Integration:**
  - `ChatViewProvider` - Webview provider for chat interface
  - `extension.ts` - VS Code extension entry point

## Key Components

### LangChain Agent System
```typescript
// ReAct Agent with autonomous tool usage
const agent = await createReactAgent({
    llm: model,
    tools: [
        listDirTool,
        readFileTool,
        editFileTool,
        runTerminalCmdTool,
        codebaseSearchTool,
        grepSearchTool,
        fileSearchTool,
        deleteFileTool,
        searchReplaceTool,
    ],
    prompt: AI_PUNK_PROMPT,
});

const agentExecutor = new AgentExecutor({
    agent,
    tools,
    verbose: true,
    maxIterations: 10,
    returnIntermediateSteps: true,
});
```

### AI Provider Support
- **Google Gemini** (default)
- **OpenAI GPT-4**
- Extensible for additional providers

### Vector Search System
- **FAISS** vector store for semantic search
- **Embeddings** for code understanding
- **Indexing** for workspace analysis

## Data Flow

### User Message Processing
```
1. User sends message → ChatViewProvider
2. ChatViewProvider → SendMessage use case
3. SendMessage → LangChainAdapter
4. LangChainAdapter → AgentExecutor
5. AgentExecutor → Tool execution loop
6. Tools → File system / Search / Commands
7. Agent → Final response
8. Response → ChatViewProvider → User
```

### Tool Execution Pattern
```
1. Agent receives user query
2. Agent thinks about required actions
3. Agent selects appropriate tool
4. Tool executes with parameters
5. Tool returns observation
6. Agent processes observation
7. Loop continues until task complete
8. Agent provides final answer
```

## Configuration

### VS Code Settings
```json
{
  "aiPunk.provider": "google",
  "aiPunk.google.apiKey": "your-api-key",
  "aiPunk.google.model": "gemini-pro",
  "aiPunk.openAI.apiKey": "your-api-key",
  "aiPunk.openAI.model": "gpt-4-turbo-preview"
}
```

### Extension Manifest
```json
{
  "contributes": {
    "viewsContainers": {
      "activitybar": [
        {
          "id": "ai-punk-view-container",
          "title": "AI Punk",
          "icon": "$(beaker)"
        }
      ]
    },
    "views": {
      "ai-punk-view-container": [
        {
          "type": "webview",
          "id": "ai-punk-chat-view",
          "name": "Chat"
        }
      ]
    }
  }
}
```

## Dependencies

### Core Dependencies
- `@langchain/core` - LangChain framework
- `@langchain/google-genai` - Google AI integration
- `@langchain/openai` - OpenAI integration
- `@langchain/community` - Vector stores and tools
- `langchain` - Agent system and tools

### VS Code Dependencies
- `vscode` - VS Code extension API
- TypeScript compilation to `dist/`

### File System Tools
- `fs/promises` - Async file operations
- `glob` - File pattern matching
- `child_process` - Command execution

## Security Features

1. **Workspace Restriction:** All file operations limited to workspace
2. **Critical File Protection:** Prevents deletion of important files
3. **Path Validation:** Security checks for path traversal
4. **Command Approval:** User approval required for terminal commands
5. **Error Handling:** Graceful failure with informative messages

## Extension Points

### Adding New Tools
```typescript
export const myTool = new DynamicTool({
    name: "my_tool",
    description: "Description of what this tool does",
    func: async (input: string) => {
        // Tool implementation
        return "Result";
    }
});
```

### Adding New AI Providers
```typescript
class MyAIAdapter implements IAIAdapter {
    async getCompletion(messages: Message[]): Promise<string> {
        // Provider implementation
        return "AI response";
    }
}
```

### Adding New Use Cases
```typescript
class MyUseCase {
    constructor(
        private repository: IRepository,
        private aiAdapter: IAIAdapter
    ) {}
    
    async execute(input: any): Promise<any> {
        // Use case implementation
    }
}
```

## Philosophy

**Clean Architecture Principles:**
- **Independence:** Core business logic independent of frameworks
- **Testability:** Each layer can be tested in isolation
- **Flexibility:** Easy to swap implementations
- **Maintainability:** Clear separation of concerns

**Autonomous Agent Design:**
- **No Permission Asking:** Agent acts autonomously
- **Multi-step Planning:** Complex task decomposition
- **Tool Chaining:** Combines multiple tools for solutions
- **Context Awareness:** Thorough codebase exploration
- **Multilingual Support:** Responds in user's language 