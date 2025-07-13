import { DynamicTool } from "langchain/tools";
import { FaissStore } from "@langchain/community/vectorstores/faiss";
import { Embeddings } from "@langchain/core/embeddings";
import { workspace } from "vscode";
import * as path from "path";
import * as fs from "fs";

// This class will be instantiated once and hold the vector store.
class CodebaseSearcher {
    private vectorStore: FaissStore | null = null;
    private readonly indexPath: string;

    constructor(private embeddings: Embeddings) {
        if (!workspace.workspaceFolders?.[0]) {
            throw new Error("No workspace folder found.");
        }
        this.indexPath = path.join(workspace.workspaceFolders[0].uri.fsPath, ".ai-punk", "codebase.index");
        this.loadIndex();
    }

    async loadIndex(): Promise<void> {
        try {
            if (fs.existsSync(this.indexPath)) {
                this.vectorStore = await FaissStore.load(this.indexPath, this.embeddings);
                console.log("Codebase index loaded successfully.");
            } else {
                console.log("Codebase index not found. Please run indexing.");
                this.vectorStore = null;
            }
        } catch (error) {
            console.error("Failed to load codebase index:", error);
            this.vectorStore = null;
        }
    }

    async search(query: string): Promise<string> {
        if (!this.vectorStore) {
            return "The codebase has not been indexed yet. You may need to run the indexing command first.";
        }

        try {
            const results = await this.vectorStore.similaritySearch(query, 5);
            if (results.length === 0) {
                return `No results found for query: "${query}"`;
            }

            return results
                .map(
                    (result) =>
                        `File: ${result.metadata.source}\n\n---\n${result.pageContent}\n---`
                )
                .join("\n\n");
        } catch (error: any) {
            return `Error searching codebase: ${error.message}`;
        }
    }
}

// We need a single instance to maintain the loaded index.
let searcherInstance: CodebaseSearcher | null = null;

export const createCodebaseSearchTool = (embeddings: Embeddings) => {
    if (!searcherInstance) {
        searcherInstance = new CodebaseSearcher(embeddings);
    }

    return new DynamicTool({
        name: "codebase_search",
        description: "Searches the codebase for relevant snippets based on a query. Input should be a single string query.",
        func: (query: string) => searcherInstance!.search(query),
    });
};

// Function to reload the index for the singleton searcher.
export const reloadCodebaseSearchToolIndex = async () => {
    if (searcherInstance) {
        await searcherInstance.loadIndex();
    }
}; 