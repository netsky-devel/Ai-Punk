import { DynamicTool } from "langchain/tools";
import { workspace } from "vscode";
import { glob } from "glob";
import * as path from "path";

export const fileSearchTool = new DynamicTool({
    name: "file_search",
    description: "Fast file search based on fuzzy matching against file path. Use if you know part of the file path but don't know where it's located exactly. Response will be capped to 10 results. Make your query more specific if need to filter results further.",
    func: async (query: string) => {
        try {
            const rootPath = workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (!rootPath) {
                return "Error: No workspace is open.";
            }

            // Create fuzzy search pattern
            const searchPattern = `**/*${query}*`;
            
            // Use glob to find matching files
            const matches = await glob(searchPattern, {
                cwd: rootPath,
                ignore: [
                    'node_modules/**',
                    '.git/**',
                    'dist/**',
                    'build/**',
                    '*.log',
                    '.env*'
                ],
                nodir: true, // Only return files, not directories
                absolute: false
            });

            if (matches.length === 0) {
                return `No files found matching "${query}"`;
            }

            // Limit to 10 results and sort by relevance (shorter paths first)
            const limitedMatches = matches
                .sort((a, b) => a.length - b.length)
                .slice(0, 10);

            const resultList = limitedMatches
                .map((match, index) => `${index + 1}. ${match}`)
                .join('\n');

            return `Found ${matches.length} file(s) matching "${query}" (showing first 10):\n${resultList}`;
        } catch (error: any) {
            return `Error searching for files: ${error.message}`;
        }
    }
}); 