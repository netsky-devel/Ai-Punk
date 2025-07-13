import { DynamicTool } from "langchain/tools";
import * as fs from "fs/promises";
import * as path from "path";
import { workspace } from "vscode";

interface ReadFileParams {
    path: string;
    startLine?: number;
    endLine?: number;
}

export const readFileTool = new DynamicTool({
    name: "read_file",
    description: "Read the contents of a file. the output of this tool call will be the 1-indexed file contents from start_line_one_indexed to end_line_one_indexed_inclusive, together with a summary of the lines outside start_line_one_indexed and end_line_one_indexed_inclusive. Note that this call can view at most 250 lines at a time. When using this tool to gather information, it's your responsibility to ensure you have the COMPLETE context. Specifically, each time you call this command you should: 1) Assess if the contents you viewed are sufficient to proceed with your task. 2) Take note of where there are lines not shown. 3) If the file contents you have viewed are insufficient, and you suspect they may be in lines not shown, proactively call the tool again to view those lines. 4) When in doubt, call this tool again to gather more information. Remember that partial file views may miss critical dependencies, imports, or functionality.",
    func: async (params: string | ReadFileParams) => {
        let filePath: string;
        let startLine: number | undefined;
        let endLine: number | undefined;

        if (typeof params === 'string') {
            filePath = params;
        } else {
            filePath = params.path;
            startLine = params.startLine;
            endLine = params.endLine;
        }

        try {
            const rootPath = workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (!rootPath) {
                return "Error: No workspace is open.";
            }
            const targetPath = path.resolve(rootPath, filePath);
            const content = await fs.readFile(targetPath, 'utf-8');

            if (startLine === undefined && endLine === undefined) {
                return `Contents of ${filePath}:\n${content}`;
            }

            const lines = content.split(/\r?\n/);
            const start = startLine ? Math.max(0, startLine - 1) : 0;
            const end = endLine ? Math.min(lines.length, endLine) : lines.length;
            
            const selectedLines = lines.slice(start, end);

            return `Contents of ${filePath} (lines ${start + 1}-${end}):\n${selectedLines.join('\n')}`;
        } catch (error: any) {
            if (error.code === 'ENOENT') {
                return `Error: File not found at ${error.path}`;
            }
            return `Error reading file: ${error.message}`;
        }
    }
}); 