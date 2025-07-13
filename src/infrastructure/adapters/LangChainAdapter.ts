import * as vscode from 'vscode';
import { BaseMessage, HumanMessage, AIMessage, SystemMessage } from '@langchain/core/messages';
import { ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings } from '@langchain/google-genai';
import { ChatOpenAI, OpenAIEmbeddings } from '@langchain/openai';
import { Message } from '../../domain/entities/Message';
import { IAIAdapter } from '../../application/ports/IAIAdapter';
import { BaseChatModel } from '@langchain/core/language_models/chat_models';
import { Embeddings } from '@langchain/core/embeddings';
import { Tool } from "langchain/tools";
import { AgentExecutor, createReactAgent } from "langchain/agents";
import { ChatPromptTemplate } from "@langchain/core/prompts";

import { listDirTool } from '../tools/ListDirTool';
import { readFileTool } from '../tools/ReadFileTool';
import { editFileTool } from '../tools/EditFileTool';
import { runTerminalCmdTool } from '../tools/RunTerminalCmdTool';
import { createCodebaseSearchTool } from '../tools/CodebaseSearchTool';
import { grepSearchTool } from '../tools/GrepSearchTool';
import { fileSearchTool } from '../tools/FileSearchTool';
import { deleteFileTool } from '../tools/DeleteFileTool';
import { searchReplaceTool } from '../tools/SearchReplaceTool';

// Создаем агентский промпт для AI Punk для автономной работы
const AI_PUNK_PROMPT = ChatPromptTemplate.fromTemplate(`You are AI Punk - an autonomous AI coding assistant that automates engineering tasks from start to finish. You are more than just code suggestions; you can build entire projects from scratch, write and execute code, debug failures, orchestrate workflows, and interact with external APIs autonomously.

CRITICAL: Always respond in the same language that the user writes to you. If they write in Russian, respond in Russian. If they write in English, respond in English. Match their language choice exactly.

You are an AUTONOMOUS AGENT. This means:
1. You MUST keep working until the user's query is completely resolved
2. You MUST NOT ask for permission to use tools - use them autonomously  
3. You MUST plan multi-step solutions and execute them fully
4. You MUST explore the codebase thoroughly to understand context
5. Only stop when the task is 100% complete or you need clarification

AUTONOMOUS BEHAVIOR PATTERNS:
- If you need to understand a project: automatically explore its structure with list_dir and read_file
- If you need to fix code: automatically read relevant files and make changes with edit_file
- If you need to debug: automatically run tests and check outputs with run_terminal_cmd
- If you need to search: automatically use codebase_search and grep_search with multiple strategies
- If you need to find files: automatically use file_search with different patterns
- Chain tool calls together to accomplish complex tasks without asking permission

TOOLS USAGE STRATEGY:
- Use tools extensively and autonomously - don't ask permission
- Combine multiple tools to solve complex problems  
- Always verify your changes by reading the modified files
- Use semantic search (codebase_search) for understanding concepts
- Use grep_search for finding specific patterns or code
- Use file_search when you need to locate files by name
- Use edit_file for making code changes
- Use run_terminal_cmd for testing, building, or running commands

You have access to these tools:
{tools}

Tool names: {tool_names}

Use the following format:

Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: Do I need to use a tool? No
Final Answer: [your response here]

IMPORTANT: Never mix tool usage with final answer. Either use tools OR provide final answer, never both in the same response.

Begin!

Question: {input}
{agent_scratchpad}`);

export class LangChainAdapter implements IAIAdapter {
    private _model: BaseChatModel | undefined;
    private _embeddings: Embeddings | undefined;
    private _agentExecutor: AgentExecutor | undefined;
    public tools: Tool[] = [];

    public get embeddings(): Embeddings | undefined {
        return this._embeddings;
    }

    constructor() {
        this.initializeTools();
        // Инициализация модели будет выполнена при первом запросе
    }

    private async initializeModel(): Promise<void> {
        console.log('🔧 Initializing AI model...');
        
        this._model = this.createModelFromSettings();
        this._embeddings = this.createEmbeddingsFromSettings();
        
        console.log('🤖 Model:', this._model ? 'OK' : 'FAILED');
        console.log('🧠 Embeddings:', this._embeddings ? 'OK' : 'FAILED');
        console.log('🛠️ Tools count:', this.tools.length);
        
        if (this._model && this.tools.length > 0) {
            console.log('🚀 Initializing agent...');
            await this.initializeAgent();
        } else {
            console.log('❌ Cannot initialize agent: missing model or tools');
        }
    }

    private async initializeAgent(): Promise<void> {
        if (!this._model) {
            console.log('❌ No model available for agent initialization');
            return;
        }

        try {
            console.log('🔨 Creating React agent...');
            
            // Создаем React агента с нашими инструментами
            const agent = await createReactAgent({
                llm: this._model,
                tools: this.tools,
                prompt: AI_PUNK_PROMPT,
            });

            console.log('⚡ Creating AgentExecutor...');
            
            // Создаем AgentExecutor для автономного выполнения
            this._agentExecutor = new AgentExecutor({
                agent,
                tools: this.tools,
                verbose: true,
                maxIterations: 10, // Максимум 10 итераций для безопасности
                returnIntermediateSteps: true,
            });
            
            console.log('✅ Agent initialized successfully!');
        } catch (error) {
            console.error('❌ Failed to initialize agent:', error);
            vscode.window.showErrorMessage(`Agent initialization failed: ${error}`);
        }
    }

    private createModelFromSettings(): BaseChatModel | undefined {
        const config = vscode.workspace.getConfiguration('aiPunk');
        const provider = config.get<string>('provider', 'google');

        console.log('🔧 Creating model with provider:', provider);

        try {
            if (provider === 'google') {
                const apiKey = config.get<string>('google.apiKey');
                const model = config.get<string>('google.model', 'gemini-pro');
                
                console.log('🔑 Google API Key:', apiKey ? 'Present' : 'Missing');
                console.log('🤖 Google Model:', model);
                
                if (!apiKey) {
                    const message = 'Google AI API key not configured. Please set aiPunk.google.apiKey in settings.';
                    console.log('❌', message);
                    vscode.window.showErrorMessage(message);
                    return undefined;
                }

                console.log('✅ Creating Google AI model...');
                return new ChatGoogleGenerativeAI({
                    apiKey: apiKey,
                    model: model,
                    temperature: 0.1, // Более низкая температура для точности
                });
            } else if (provider === 'openai') {
                const apiKey = config.get<string>('openAI.apiKey');
                const model = config.get<string>('openAI.model', 'gpt-4');
                
                console.log('🔑 OpenAI API Key:', apiKey ? 'Present' : 'Missing');
                console.log('🤖 OpenAI Model:', model);
                
                if (!apiKey) {
                    vscode.window.showErrorMessage('OpenAI API key not configured. Please set aiPunk.openAI.apiKey in settings.');
                    return undefined;
                }

                return new ChatOpenAI({
                    openAIApiKey: apiKey,
                    modelName: model,
                    temperature: 0.1,
                });
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(`Failed to initialize ${provider} model: ${error.message}`);
        }

        return undefined;
    }

    private createEmbeddingsFromSettings(): Embeddings | undefined {
        const config = vscode.workspace.getConfiguration('aiPunk');
        const provider = config.get<string>('provider', 'google');

        try {
            if (provider === 'google') {
                const apiKey = config.get<string>('google.apiKey');
                if (!apiKey) return undefined;

                return new GoogleGenerativeAIEmbeddings({
                    apiKey: apiKey,
                    modelName: "embedding-001",
                });
            } else if (provider === 'openai') {
                const apiKey = config.get<string>('openAI.apiKey');
                if (!apiKey) return undefined;

                return new OpenAIEmbeddings({
                    openAIApiKey: apiKey,
                });
            }
        } catch (error: any) {
            console.error(`Failed to initialize ${provider} embeddings:`, error);
        }

        return undefined;
    }

    private initializeTools(): void {
        // Инициализируем все инструменты
        this.tools = [
            listDirTool,
            readFileTool,
            editFileTool,
            runTerminalCmdTool,
            grepSearchTool,
            fileSearchTool,
            deleteFileTool,
            searchReplaceTool,
        ];

        // Добавляем codebase search только если embeddings доступны
        if (this._embeddings) {
            this.tools.push(createCodebaseSearchTool(this._embeddings));
        }
    }

    public async getCompletion(messages: Message[]): Promise<string> {
        if (!this._agentExecutor) {
            // Пытаемся переинициализировать агента
            await this.initializeModel();
            
            if (!this._agentExecutor) {
                const message = "AI Agent could not be initialized. Please check AI Punk settings.";
                vscode.window.showErrorMessage(message);
                return message;
            }
        }

        try {
            // Преобразуем историю сообщений в строку для агента
            const chatHistory = messages.slice(0, -1).map(msg => 
                `${msg.sender === 'user' ? 'Human' : 'Assistant'}: ${msg.text}`
            ).join('\n');
            
            const latestMessage = messages[messages.length - 1].text;

            // Используем AgentExecutor для автономного выполнения
            const result = await this._agentExecutor.invoke({
                input: latestMessage,
                chat_history: chatHistory,
            });

            // Возвращаем результат работы агента
            return result.output || "Задача выполнена, но агент не предоставил подробного ответа.";

        } catch (error: any) {
            console.error('Agent execution error:', error);
            vscode.window.showErrorMessage(`AI Agent Error: ${error.message}`);
            return `Извините, произошла ошибка при выполнении задачи: ${error.message}`;
        }
    }
} 