import { DynamicTool } from "langchain/tools";
import * as fs from "fs/promises";
import * as path from "path";
import { workspace } from "vscode";

export const listDirTool = new DynamicTool({
    name: "list_dir",
    description: "List the contents of a directory. The quick tool to use for discovery, before using more targeted tools like semantic search or file reading. Useful to try to understand the file structure before diving deeper into specific files. Can be used to explore the codebase.",
    func: async (dirPath: string = "") => {
        try {
            const rootPath = workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (!rootPath) {
                return "Error: No workspace is open.";
            }
            
            const targetPath = dirPath ? path.resolve(rootPath, dirPath) : rootPath;
            const entries = await fs.readdir(targetPath, { withFileTypes: true });
            
            const content = entries.map(entry => {
                return entry.isDirectory() ? `${entry.name}/` : entry.name;
            }).join('\n');

            if (!content) {
                return `Directory '${targetPath}' is empty.`;
            }

            return `Contents of ${targetPath}:\n${content}`;
        } catch (error: any) {
            if (error.code === 'ENOENT') {
                return `Error: Directory not found at ${error.path}`;
            }
            return `Error listing directory: ${error.message}`;
        }
    }
}); 