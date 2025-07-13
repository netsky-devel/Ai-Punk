import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {

	console.log('Congratulations, your extension "ai-punk" is now active!');

	let disposable = vscode.commands.registerCommand('ai-punk.chat', () => {
		vscode.window.showInformationMessage('AI Punk Chat opened!');
	});

	context.subscriptions.push(disposable);
}

export function deactivate() {} 