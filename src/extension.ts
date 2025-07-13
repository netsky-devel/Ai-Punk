import * as vscode from 'vscode';
import { ChatViewProvider } from './presentation/vscode/ChatViewProvider';

export function activate(context: vscode.ExtensionContext) {
	const provider = new ChatViewProvider(context.extensionUri);

	context.subscriptions.push(
		vscode.window.registerWebviewViewProvider(ChatViewProvider.viewType, provider)
	);
}

export function deactivate() {} 