import { DynamicTool } from "langchain/tools";
import { exec } from 'child_process';
import { workspace } from "vscode";

export const runTerminalCmdTool = new DynamicTool({
    name: "run_terminal_cmd",
    description: "PROPOSE a command to run on behalf of the user. If you have this tool, note that you DO have the ability to run commands directly on the USER's system. Note that the user will have to approve the command before it is executed. The user may reject it if it is not to their liking, or may modify the command before approving it. If they do change it, take those changes into account. The actual command will NOT execute until the user approves it. The user may not approve it immediately. Do NOT assume the command has started running. If the step is WAITING for user approval, it has NOT started running. In using these tools, adhere to the following guidelines: 1. Based on the contents of the conversation, you will be told if you are in the same shell as a previous step or a different shell. 2. If in a new shell, you should `cd` to the appropriate directory and do necessary setup in addition to running the command. 3. If in the same shell, the state will persist. 4. For ANY commands that would use a pager or require user interaction, you should append ` | cat` to the command. 5. For commands that are long running/expected to run indefinitely until interruption, please run them in the background. 6. Dont include any newlines in the command.",
    func: async (command: string) => {
        return new Promise<string>((resolve) => {
            const cwd = workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (!cwd) {
                resolve("Error: No workspace is open.");
                return;
            }

            exec(command, { cwd }, (error, stdout, stderr) => {
                if (error) {
                    resolve(`Error executing command: ${error.message}\nStderr: ${stderr}`);
                    return;
                }
                if (stderr) {
                    resolve(`Command executed with stderr:\n${stderr}\nStdout:\n${stdout}`);
                    return;
                }
                resolve(`Command executed successfully:\n${stdout}`);
            });
        });
    }
}); 