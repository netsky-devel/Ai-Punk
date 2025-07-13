import { StructuredTool, ToolParams } from "langchain/tools";
import { z } from "zod";
import * as vscode from 'vscode';
import * as fs from 'fs/promises';
import * as path from 'path';

export class WriteFileTool extends StructuredTool {
    name = "edit_file";
    
    schema = z.object({
        target_file: z.string().describe("The path of the file to create or overwrite, relative to the workspace root."),
        content: z.string().describe("The new content to be written to the file.")
    });

    description = "Create a new file or completely overwrite an existing file with new content. Use with caution as this will replace the entire file content.";

    constructor(params?: ToolParams) {
        super(params);
    }
    
    protected async _call({ target_file, content }: z.infer<this["schema"]>): Promise<string> {
        try {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (!workspaceFolders || workspaceFolders.length === 0) {
                return "Error: No workspace folder is open.";
            }
            const rootPath = workspaceFolders[0].uri.fsPath;
            const targetPath = path.join(rootPath, target_file);
            
            await fs.mkdir(path.dirname(targetPath), { recursive: true });

            await fs.writeFile(targetPath, content, 'utf-8');
            
            return `Successfully wrote to ${target_file}.`;
        } catch (error: any) {
            return `Error writing to file: ${error.message}`;
        }
    }
} 