import * as vscode from 'vscode';
import { ChatWebviewPanel } from './presentation/vscode/ChatWebviewPanel';

export function activate(context: vscode.ExtensionContext) {

	console.log('Congratulations, your extension "ai-punk" is now active!');

	context.subscriptions.push(
		vscode.commands.registerCommand('ai-punk.chat', () => {
			ChatWebviewPanel.createOrShow(context.extensionUri);
		})
	);
}

export function deactivate() {} 