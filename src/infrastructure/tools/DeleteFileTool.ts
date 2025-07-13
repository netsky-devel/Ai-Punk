import { DynamicTool } from "langchain/tools";
import * as fs from "fs/promises";
import * as path from "path";
import { workspace } from "vscode";

export const deleteFileTool = new DynamicTool({
    name: "delete_file",
    description: "Deletes a file at the specified path. The operation will fail gracefully if: - The file doesn't exist - The operation is rejected for security reasons - The file cannot be deleted",
    func: async (filePath: string) => {
        try {
            const rootPath = workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (!rootPath) {
                return "Error: No workspace is open.";
            }
            
            const targetPath = path.resolve(rootPath, filePath);
            
            // Security check: ensure the target path is within the workspace
            if (!targetPath.startsWith(rootPath)) {
                return "Error: Cannot delete files outside the workspace for security reasons.";
            }
            
            // Check if file exists
            try {
                await fs.access(targetPath);
            } catch {
                return `Error: File "${filePath}" does not exist.`;
            }
            
            // Prevent deletion of critical files
            const fileName = path.basename(targetPath);
            const criticalFiles = ['package.json', 'tsconfig.json', '.gitignore', 'README.md'];
            if (criticalFiles.includes(fileName)) {
                return `Error: Cannot delete critical file "${fileName}" for safety reasons.`;
            }
            
            // Delete the file
            await fs.unlink(targetPath);
            
            return `Successfully deleted file "${filePath}".`;
        } catch (error: any) {
            if (error.code === 'ENOENT') {
                return `Error: File "${filePath}" not found.`;
            }
            if (error.code === 'EACCES') {
                return `Error: Permission denied when trying to delete "${filePath}".`;
            }
            return `Error deleting file: ${error.message}`;
        }
    }
}); 