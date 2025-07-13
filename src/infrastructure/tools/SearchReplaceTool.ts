import { DynamicTool } from "langchain/tools";
import * as fs from "fs/promises";
import * as path from "path";
import { workspace } from "vscode";

interface SearchReplaceParams {
    file_path: string;
    old_string: string;
    new_string: string;
}

export const searchReplaceTool = new DynamicTool({
    name: "search_replace",
    description: "Use this tool to propose a search and replace operation on an existing file. The tool will replace ONE occurrence of old_string with new_string in the specified file. CRITICAL REQUIREMENTS: 1. UNIQUENESS: The old_string MUST uniquely identify the specific instance you want to change. This means: - Include AT LEAST 3-5 lines of context BEFORE the change point - Include AT LEAST 3-5 lines of context AFTER the change point - Include all whitespace, indentation, and surrounding code exactly as it appears in the file. 2. SINGLE INSTANCE: This tool can only change ONE instance at a time.",
    func: async (input: string) => {
        try {
            let params: SearchReplaceParams;
            
            // Try to parse input as JSON
            try {
                params = JSON.parse(input);
            } catch {
                return "Error: Input must be a valid JSON object with file_path, old_string, and new_string properties.";
            }
            
            const { file_path, old_string, new_string } = params;
            
            if (!file_path || !old_string || new_string === undefined) {
                return "Error: Missing required parameters. Need file_path, old_string, and new_string.";
            }
            
            const rootPath = workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (!rootPath) {
                return "Error: No workspace is open.";
            }
            
            const targetPath = path.resolve(rootPath, file_path);
            
            // Security check: ensure the target path is within the workspace
            if (!targetPath.startsWith(rootPath)) {
                return "Error: Cannot modify files outside the workspace for security reasons.";
            }
            
            // Read the file
            let content: string;
            try {
                content = await fs.readFile(targetPath, 'utf-8');
            } catch (error: any) {
                if (error.code === 'ENOENT') {
                    return `Error: File "${file_path}" not found.`;
                }
                return `Error reading file: ${error.message}`;
            }
            
            // Check if old_string exists in the file
            const occurrences = content.split(old_string).length - 1;
            if (occurrences === 0) {
                return `Error: The specified old_string was not found in "${file_path}". Please check the exact text including whitespace and indentation.`;
            }
            
            if (occurrences > 1) {
                return `Error: The old_string appears ${occurrences} times in "${file_path}". Please provide more specific context to uniquely identify the instance you want to replace.`;
            }
            
            // Perform the replacement
            const newContent = content.replace(old_string, new_string);
            
            // Write the file back
            await fs.writeFile(targetPath, newContent, 'utf-8');
            
            return `Successfully replaced text in "${file_path}". Changed 1 occurrence.`;
        } catch (error: any) {
            return `Error performing search and replace: ${error.message}`;
        }
    }
}); 