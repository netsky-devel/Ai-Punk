import * as vscode from 'vscode';
import { ChatViewProvider } from './presentation/vscode/ChatViewProvider';
import { CodebaseIndexer } from './infrastructure/indexing/CodebaseIndexer';
import { reloadCodebaseSearchToolIndex } from './infrastructure/tools/CodebaseSearchTool';

export function activate(context: vscode.ExtensionContext) {
	const provider = new ChatViewProvider(context.extensionUri);

	context.subscriptions.push(
		vscode.window.registerWebviewViewProvider(ChatViewProvider.viewType, provider)
	);

	context.subscriptions.push(
		vscode.commands.registerCommand('ai-punk.indexWorkspace', async () => {
			const embeddings = provider.aiAdapter.embeddings;
			if (!embeddings) {
				vscode.window.showErrorMessage('AI provider is not configured correctly. Cannot create embeddings.');
				return;
			}

			await vscode.window.withProgress({
				location: vscode.ProgressLocation.Notification,
				title: "AI Punk: Indexing workspace...",
				cancellable: false
			}, async (progress) => {
				try {
					const indexer = new CodebaseIndexer(embeddings);
					await indexer.indexWorkspace();
					vscode.window.showInformationMessage('AI Punk: Workspace indexing complete.');
					// We need to reload the index in our tool
					await reloadCodebaseSearchToolIndex();
				} catch (error: any) {
					vscode.window.showErrorMessage(`Failed to index workspace: ${error.message}`);
				}
			});
		})
	);
}

export function deactivate() {} 