import { DynamicTool } from "langchain/tools";
import * as fs from "fs/promises";
import * as path from "path";
import { workspace } from "vscode";

interface EditFileParams {
    path: string;
    content: string;
}

export const editFileTool = new DynamicTool({
    name: "edit_file",
    description: "Use this tool to propose an edit to an existing file or create a new file. This will be read by a less intelligent model, which will quickly apply the edit. You should make it clear what the edit is, while also minimizing the unchanged code you write. When writing the edit, you should specify each edit in sequence, with the special comment `// ... existing code ...` to represent unchanged code in between edited lines. You should still bias towards repeating as few lines of the original file as possible to convey the change. But, each edit should contain sufficient context of unchanged lines around the code you're editing to resolve ambiguity. DO NOT omit spans of pre-existing code (or comments) without using the `// ... existing code ...` comment to indicate its absence. If you omit the existing code comment, the model may inadvertently delete these lines. Make sure it is clear what the edit should be, and where it should be applied. To create a new file, simply specify the content of the file in the code_edit field.",
    func: async (params: any) => {
        try {
            const { path: filePath, content } = params;
            if (typeof filePath !== 'string' || typeof content !== 'string') {
                return "Error: Input must be an object with 'path' and 'content' string properties.";
            }
            const rootPath = workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (!rootPath) {
                return "Error: No workspace is open.";
            }
            
            const targetPath = path.resolve(rootPath, filePath);
            
            // Ensure the directory exists
            const dir = path.dirname(targetPath);
            await fs.mkdir(dir, { recursive: true });

            await fs.writeFile(targetPath, content, 'utf-8');

            return `Successfully wrote to ${filePath}.`;
        } catch (error: any) {
            return `Error writing to file: ${error.message}`;
        }
    }
}); 