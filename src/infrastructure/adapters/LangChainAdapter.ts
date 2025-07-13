import * as vscode from 'vscode';
import { BaseMessage, HumanMessage, AIMessage } from '@langchain/core/messages';
import { ChatGoogleGenerativeAI } from '@langchain/google-genai';
import { ChatOpenAI } from '@langchain/openai';
import { Message } from '../../domain/entities/Message';
import { IAIAdapter } from '../../application/ports/IAIAdapter';
import { BaseChatModel } from '@langchain/core/language_models/chat_models';

export class LangChainAdapter implements IAIAdapter {
    private _model: BaseChatModel;

    constructor() {
        this._model = this.createModelFromSettings();
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('aiPunk')) {
                this._model = this.createModelFromSettings();
            }
        });
    }

    private createModelFromSettings(): BaseChatModel {
        const config = vscode.workspace.getConfiguration('aiPunk');
        const provider = config.get<string>('aiProvider');
        
        switch (provider) {
            case 'Google':
                return new ChatGoogleGenerativeAI({
                    apiKey: config.get<string>('google.apiKey'),
                    modelName: config.get<string>('google.model'),
                });
            case 'OpenAI':
                 return new ChatOpenAI({
                    apiKey: config.get<string>('openAI.apiKey'),
                    modelName: config.get<string>('openAI.model'),
                });
            default:
                throw new Error(`Unsupported AI provider: ${provider}`);
        }
    }

    public async getCompletion(messages: Message[]): Promise<string> {
        if (!this._model) {
            throw new Error("AI Model not initialized. Please check your settings.");
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