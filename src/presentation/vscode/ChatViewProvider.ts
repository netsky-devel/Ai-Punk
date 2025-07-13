import * as vscode from 'vscode';
import { SendMessage } from '../../application/use-cases/SendMessage';
import { InMemoryConversationRepository } from '../../infrastructure/adapters/InMemoryConversationRepository';
import { LangChainAdapter } from '../../infrastructure/adapters/LangChainAdapter';

export class ChatViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'ai-punk-chat-view';
    private _view?: vscode.WebviewView;

    // Use cases and adapters
    public readonly aiAdapter: LangChainAdapter;
    private readonly _sendMessage: SendMessage;
    private readonly _conversationRepository: InMemoryConversationRepository;
    private _conversationId: string;

    constructor(private readonly _extensionUri: vscode.Uri) {
        this._conversationRepository = new InMemoryConversationRepository();
        this.aiAdapter = new LangChainAdapter();
        this._sendMessage = new SendMessage(this._conversationRepository, this.aiAdapter);
        this._conversationId = this._conversationRepository.findActiveConversationId()!;
    }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        webviewView.webview.onDidReceiveMessage(async message => {
            switch (message.type) {
                case 'sendMessage':
                    this._view?.webview.postMessage({ type: 'addMessage', data: { sender: 'user', text: message.data } });
                    
                    const conversation = await this._sendMessage.execute(this._conversationId, message.data);
                    const botMessage = conversation.messages[conversation.messages.length - 1];

                    this._view?.webview.postMessage({ type: 'addMessage', data: { sender: 'bot', text: botMessage.text } });
                    break;
            }
        });
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'main.js'));
        const stylesUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'styles.css'));
        const nonce = getNonce();

        return `<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource}; script-src 'nonce-${nonce}';">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="${stylesUri}" rel="stylesheet">
                <title>AI Punk</title>
            </head>
            <body>
                <div id="chat-container"></div>
                <div id="input-container">
                    <textarea id="message-input" placeholder="Ask AI Punk..."></textarea>
                    <button id="send-button">Send</button>
                </div>
                <script nonce="${nonce}" src="${scriptUri}"></script>
            </body>
            </html>`;
    }
}

function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
} 