import { StructuredTool, ToolParams } from "langchain/tools";
import { z } from "zod";
import * as vscode from 'vscode';
import * as fs from 'fs/promises';
import * as path from 'path';

export class ListDirTool extends StructuredTool {
    name = "list_dir";
    
    schema = z.object({
        relative_workspace_path: z.string().describe("Path to list contents of, relative to the workspace root. Use an empty string to list the root directory.")
    });

    description = "List the contents of a directory. Useful to try to understand the file structure before diving deeper into specific files.";

    constructor(params?: ToolParams) {
        super(params);
    }
    
    protected async _call({ relative_workspace_path }: z.infer<this["schema"]>): Promise<string> {
        try {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (!workspaceFolders || workspaceFolders.length === 0) {
                return "Error: No workspace folder is open.";
            }
            const rootPath = workspaceFolders[0].uri.fsPath;
            const targetPath = path.join(rootPath, relative_workspace_path);

            const items = await fs.readdir(targetPath, { withFileTypes: true });
            const itemList = items.map(item => `${item.isDirectory() ? '[dir]' : '[file]'} ${item.name}`);
            
            if(itemList.length === 0) {
                return `Directory '${relative_workspace_path}' is empty.`;
            }

            return `Contents of '${relative_workspace_path}':\n${itemList.join('\n')}`;
        } catch (error: any) {
            return `Error listing directory: ${error.message}`;
        }
    }
} 