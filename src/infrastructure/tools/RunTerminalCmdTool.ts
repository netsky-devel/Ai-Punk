import { StructuredTool, ToolParams } from "langchain/tools";
import { z } from "zod";
import * as vscode from 'vscode';

export class RunTerminalCmdTool extends StructuredTool {
    name = "run_terminal_cmd";
    
    schema = z.object({
        command: z.string().describe("The terminal command to execute.")
    });

    description = "Executes a command in the integrated terminal. The output of the command is not returned to the agent. The user will see the output.";
    
    constructor(params?: ToolParams) {
        super(params);
    }
    
    protected async _call({ command }: z.infer<this["schema"]>): Promise<string> {
        try {
            let terminal = vscode.window.terminals.find(t => t.name === "AI Punk Agent");
            if (!terminal || terminal.exitStatus) {
                terminal = vscode.window.createTerminal("AI Punk Agent");
            }
            terminal.show();
            terminal.sendText(command);
            
            return `Command "${command}" executed in the 'AI Punk Agent' terminal. Please check the terminal for output.`;
        } catch (error: any) {
            return `Error executing command: ${error.message}`;
        }
    }
} 