import { StructuredTool, ToolParams } from "langchain/tools";
import { z } from "zod";
import * as vscode from 'vscode';
import * as fs from 'fs/promises';
import * as path from 'path';

export class ReadFileTool extends StructuredTool {
    name = "read_file";
    
    schema = z.object({
        target_file: z.string().describe("The path of the file to read, relative to the workspace root."),
        start_line: z.number().optional().describe("The one-indexed line number to start reading from (inclusive)."),
        end_line: z.number().optional().describe("The one-indexed line number to end reading at (inclusive)."),
    });

    description = "Read the contents of a file. Can read the whole file or a specific range of lines.";

    constructor(params?: ToolParams) {
        super(params);
    }

    protected async _call({ target_file, start_line, end_line }: z.infer<this["schema"]>): Promise<string> {
        try {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (!workspaceFolders || workspaceFolders.length === 0) {
                return "Error: No workspace folder is open.";
            }
            const rootPath = workspaceFolders[0].uri.fsPath;
            const targetPath = path.join(rootPath, target_file);

            const content = await fs.readFile(targetPath, 'utf-8');

            if (start_line && end_line) {
                const lines = content.split('\n');
                const start = start_line - 1;
                const slicedLines = lines.slice(start, end_line);
                return `Lines ${start_line}-${end_line} of ${target_file}:\n---\n${slicedLines.join('\n')}`;
            }

            return `Contents of ${target_file}:\n---\n${content}`;
        } catch (error: any) {
            return `Error reading file: ${error.message}`;
        }
    }
} 