# AI Punk Tools

## Core File System Tools

### 1. list_dir
**Name:** `list_dir`  
**Description:** List the contents of a directory. The quick tool to use for discovery, before using more targeted tools like semantic search or file reading. Useful to try to understand the file structure before diving deeper into specific files. Can be used to explore the codebase.

**Usage:** `list_dir(dirPath?: string)`

### 2. read_file
**Name:** `read_file`  
**Description:** Read the contents of a file. the output of this tool call will be the 1-indexed file contents from start_line_one_indexed to end_line_one_indexed_inclusive, together with a summary of the lines outside start_line_one_indexed and end_line_one_indexed_inclusive.

**Usage:** `read_file(path: string, startLine?: number, endLine?: number)`

### 3. edit_file
**Name:** `edit_file`  
**Description:** Use this tool to propose an edit to an existing file or create a new file. This will be read by a less intelligent model, which will quickly apply the edit. You should make it clear what the edit is, while also minimizing the unchanged code you write.

**Usage:** `edit_file({path: string, content: string})`

### 4. delete_file
**Name:** `delete_file`  
**Description:** Deletes a file at the specified path. The operation will fail gracefully if: - The file doesn't exist - The operation is rejected for security reasons - The file cannot be deleted

**Usage:** `delete_file(filePath: string)`

## Search Tools

### 5. codebase_search
**Name:** `codebase_search`  
**Description:** Searches the codebase for relevant snippets based on a query. Input should be a single string query.

**Usage:** `codebase_search(query: string)`
**Note:** Requires vector embeddings and indexed codebase

### 6. grep_search
**Name:** `grep_search`  
**Description:** Fast text-based regex search that finds exact pattern matches within files or directories, utilizing the ripgrep command for efficient searching. Results will be formatted in the style of ripgrep and can be configured to include line numbers and content.

**Usage:** `grep_search(query: string, case_sensitive?: boolean, include_pattern?: string, exclude_pattern?: string)`

### 7. file_search
**Name:** `file_search`  
**Description:** Fast file search based on fuzzy matching against file path. Use if you know part of the file path but don't know where it's located exactly. Response will be capped to 10 results. Make your query more specific if need to filter results further.

**Usage:** `file_search(query: string)`

## Advanced Tools

### 8. search_replace
**Name:** `search_replace`  
**Description:** Use this tool to propose a search and replace operation on an existing file. The tool will replace ONE occurrence of old_string with new_string in the specified file. CRITICAL REQUIREMENTS: 1. UNIQUENESS: The old_string MUST uniquely identify the specific instance you want to change. 2. SINGLE INSTANCE: This tool can only change ONE instance at a time.

**Usage:** `search_replace({file_path: string, old_string: string, new_string: string})`

### 9. run_terminal_cmd
**Name:** `run_terminal_cmd`  
**Description:** PROPOSE a command to run on behalf of the user. If you have this tool, note that you DO have the ability to run commands directly on the USER's system. Note that the user will have to approve the command before it is executed. The user may reject it if it is not to their liking, or may modify the command before approving it.

**Usage:** `run_terminal_cmd(command: string)`

## Tool Categories

### **Discovery & Exploration**
- `list_dir` - Directory structure exploration
- `file_search` - Find files by name/path
- `codebase_search` - Semantic code search

### **File Operations**
- `read_file` - Read file contents
- `edit_file` - Create/modify files
- `delete_file` - Remove files
- `search_replace` - Targeted text replacement

### **Search & Analysis**
- `grep_search` - Pattern matching search
- `codebase_search` - Vector-based semantic search

### **Execution**
- `run_terminal_cmd` - Execute shell commands

## Implementation Notes

1. **Security:** All file operations are restricted to workspace directory
2. **Error Handling:** Graceful failure with descriptive error messages
3. **Workspace Integration:** Uses VS Code workspace API for path resolution
4. **Async Operations:** All tools return promises for non-blocking execution
5. **Type Safety:** TypeScript interfaces for tool parameters

## Usage Patterns

### Code Exploration
```
1. list_dir() -> understand project structure
2. file_search("component") -> find specific files
3. read_file("src/App.tsx") -> examine code
4. codebase_search("authentication logic") -> find related code
```

### Code Modification
```
1. read_file("config.ts") -> understand current state
2. edit_file({path: "config.ts", content: "..."}) -> make changes
3. run_terminal_cmd("npm test") -> verify changes
```

### Debugging
```
1. grep_search("error|exception") -> find error patterns
2. codebase_search("error handling") -> understand error flow
3. run_terminal_cmd("npm run lint") -> check for issues
``` 