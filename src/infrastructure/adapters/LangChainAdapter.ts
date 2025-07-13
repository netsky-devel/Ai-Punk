import * as vscode from 'vscode';
import { BaseMessage, HumanMessage, AIMessage } from '@langchain/core/messages';
import { ChatGoogleGenerativeAI } from '@langchain/google-genai';
import { ChatOpenAI } from '@langchain/openai';
import { Message } from '../../domain/entities/Message';
import { IAIAdapter } from '../../application/ports/IAIAdapter';
import { BaseChatModel } from '@langchain/core/language_models/chat_models';

export class LangChainAdapter implements IAIAdapter {
    private _model: BaseChatModel | undefined;

    constructor() {
        this._model = this.createModelFromSettings();
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('aiPunk')) {
                this._model = this.createModelFromSettings();
            }
        });
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
        if (!this._model) {
            this._model = this.createModelFromSettings();
        }

        if (!this._model) {
            const message = "AI provider, model, or API key is not configured. Please check AI Punk settings.";
            vscode.window.showErrorMessage(message);
            return message;
        }

        const history: BaseMessage[] = messages.map(msg => 
            msg.sender === 'user' ? new HumanMessage(msg.text) : new AIMessage(msg.text)
        );

        try {
            const response = await this._model.invoke(history);
            return response.content.toString();
        } catch (error: any) {
            vscode.window.showErrorMessage(`AI Error: ${error.message}`);
            return `Sorry, I encountered an error: ${error.message}`;
        }
    }
} 