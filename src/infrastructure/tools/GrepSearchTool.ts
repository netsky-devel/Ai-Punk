import { DynamicTool } from "langchain/tools";
import { exec } from 'child_process';
import { workspace } from "vscode";

interface GrepSearchParams {
    query: string;
    case_sensitive?: boolean;
    include_pattern?: string;
    exclude_pattern?: string;
}

export const grepSearchTool = new DynamicTool({
    name: "grep_search",
    description: "Fast text-based regex search that finds exact pattern matches within files or directories, utilizing the ripgrep command for efficient searching. Results will be formatted in the style of ripgrep and can be configured to include line numbers and content. To avoid overwhelming output, the results are capped at 50 matches. Use the include or exclude patterns to filter the search scope by file type or specific paths. This is best for finding exact text matches or regex patterns. More precise than semantic search for finding specific strings or patterns. This is preferred over semantic search when we know the exact symbol/function name/etc. to search in some set of directories/file types.",
    func: async (params: string | GrepSearchParams) => {
        return new Promise<string>((resolve) => {
            const cwd = workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (!cwd) {
                resolve("Error: No workspace is open.");
                return;
            }

            let query: string;
            let caseSensitive = false;
            let includePattern = "";
            let excludePattern = "";

            if (typeof params === 'string') {
                query = params;
            } else {
                query = params.query;
                caseSensitive = params.case_sensitive || false;
                includePattern = params.include_pattern || "";
                excludePattern = params.exclude_pattern || "";
            }

            // Build ripgrep command
            let command = "rg";
            
            // Add case sensitivity flag
            if (!caseSensitive) {
                command += " -i";
            }
            
            // Add line numbers and context
            command += " -n --heading --color=never";
            
            // Limit results to avoid overwhelming output
            command += " --max-count=50";
            
            // Add include pattern if specified
            if (includePattern) {
                command += ` --glob="${includePattern}"`;
            }
            
            // Add exclude pattern if specified
            if (excludePattern) {
                command += ` --glob="!${excludePattern}"`;
            }
            
            // Add the search query (escape it for shell)
            command += ` "${query.replace(/"/g, '\\"')}"`;

            exec(command, { cwd }, (error, stdout, stderr) => {
                if (error) {
                    // ripgrep returns exit code 1 when no matches found, which is not an error
                    if (error.code === 1) {
                        resolve(`No matches found for pattern: "${query}"`);
                        return;
                    }
                    resolve(`Error executing grep search: ${error.message}\nStderr: ${stderr}`);
                    return;
                }
                
                if (stderr) {
                    resolve(`Grep search completed with warnings:\n${stderr}\nResults:\n${stdout}`);
                    return;
                }
                
                if (!stdout.trim()) {
                    resolve(`No matches found for pattern: "${query}"`);
                    return;
                }
                
                resolve(`Grep search results for "${query}":\n${stdout}`);
            });
        });
    }
}); 