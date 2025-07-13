import * as vscode from 'vscode';
import { AgentExecutor, createOpenAIToolsAgent } from 'langchain/agents';
import { ChatPromptTemplate, MessagesPlaceholder } from '@langchain/core/prompts';
import { BaseMessage, HumanMessage, AIMessage } from '@langchain/core/messages';
import { ChatGoogleGenerativeAI } from '@langchain/google-genai';
import { ChatOpenAI } from '@langchain/openai';
import { Message } from '../../domain/entities/Message';
import { IAIAdapter } from '../../application/ports/IAIAdapter';
import { BaseChatModel } from '@langchain/core/language_models/chat_models';

import { ListDirTool } from '../tools/ListDirTool';
import { ReadFileTool } from '../tools/ReadFileTool';
import { WriteFileTool } from '../tools/WriteFileTool';
import { RunTerminalCmdTool } from '../tools/RunTerminalCmdTool';

const AGENT_SYSTEM_PROMPT = `You are an AI coding assistant, powered by GPT-4. You operate in Cursor.

You are pair programming with a USER to solve their coding task. Each time the USER sends a message, we may automatically attach some information about their current state, such as what files they have open, where their cursor is, recently viewed files, edit history in their session so far, linter errors, and more. This information may or may not be relevant to the coding task, it is up for you to decide.

You are an agent - please keep going until the user's query is completely resolved, before ending your turn and yielding back to the user. Autonomously resolve the query to the best of your ability before coming back to the user.`;

export class LangChainAdapter implements IAIAdapter {
    private _agentExecutor: AgentExecutor | undefined;

    constructor() {
        this.initializeAgent();
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('aiPunk')) {
                this.initializeAgent();
            }
        });
    }

    private async initializeAgent() {
        const model = this.createModelFromSettings();
        if (!model) {
            this._agentExecutor = undefined;
            return;
        }

        const tools = [
            new ListDirTool(),
            new ReadFileTool(),
            new WriteFileTool(),
            new RunTerminalCmdTool(),
        ];

        const prompt = ChatPromptTemplate.fromMessages([
            ["system", AGENT_SYSTEM_PROMPT],
            new MessagesPlaceholder("chat_history"),
            ["human", "{input}"],
            new MessagesPlaceholder("agent_scratchpad"),
        ]);
        
        const agent = await createOpenAIToolsAgent({ llm: model, tools, prompt });
        
        this._agentExecutor = new AgentExecutor({ agent, tools });
    }

    private createModelFromSettings(): BaseChatModel | undefined {
        const config = vscode.workspace.getConfiguration('aiPunk');
        const provider = config.get<string>('aiProvider');
        
        try {
            switch (provider) {
                case 'Google': {
                    const apiKey = config.get<string>('google.apiKey');
                    const model = config.get<string>('google.model');
                    if (!apiKey || !model) {
                        return undefined;
                    }
                    return new ChatGoogleGenerativeAI({ apiKey, model });
                }
                case 'OpenAI': {
                     const apiKey = config.get<string>('openAI.apiKey');
                     const modelName = config.get<string>('openAI.model');
                     if (!apiKey || !modelName) {
                        return undefined;
                     }
                     return new ChatOpenAI({ apiKey, modelName });
                }
                default:
                    vscode.window.showWarningMessage(`AI Punk: Unsupported AI provider selected: ${provider}`);
                    return undefined;
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(`Failed to create AI model: ${error.message}`);
            return undefined;
        }
    }

    public async getCompletion(messages: Message[]): Promise<string> {
        if (!this._agentExecutor) {
            await this.initializeAgent();
        }

        if (!this._agentExecutor) {
            const message = "AI Agent could not be initialized. Please check AI Punk settings.";
            vscode.window.showErrorMessage(message);
            return message;
        }
        
        const history: BaseMessage[] = messages.slice(0, -1).map(msg => 
            msg.sender === 'user' ? new HumanMessage(msg.text) : new AIMessage(msg.text)
        );
        const latestMessage = messages[messages.length - 1].text;

        try {
            const result = await this._agentExecutor.invoke({
                input: latestMessage,
                chat_history: history,
            });

            return result.output;
        } catch (error: any) {
            vscode.window.showErrorMessage(`AI Agent Error: ${error.message}`);
            return `Sorry, I encountered an error: ${error.message}`;
        }
    }
} 