import { workspace } from 'vscode';
import * as fs from 'fs/promises';
import * as path from 'path';
import { Document } from '@langchain/core/documents';
import { FaissStore } from '@langchain/community/vectorstores/faiss';
import { Embeddings } from '@langchain/core/embeddings';
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter';
import { glob } from 'glob';

export class CodebaseIndexer {
  private readonly embeddings: Embeddings;
  private readonly workspaceRoot: string;
  private readonly indexPath: string;
  private readonly aiPunkDir: string;

  constructor(embeddings: Embeddings) {
    this.embeddings = embeddings;
    if (!workspace.workspaceFolders?.[0]) {
      throw new Error("No workspace folder found.");
    }
    this.workspaceRoot = workspace.workspaceFolders[0].uri.fsPath;
    this.aiPunkDir = path.join(this.workspaceRoot, ".ai-punk");
    this.indexPath = path.join(this.aiPunkDir, "codebase.index");
  }

  public async indexWorkspace(): Promise<void> {
    console.log("Starting codebase indexing...");

    await fs.mkdir(this.aiPunkDir, { recursive: true });

    const files = await this.findFiles();
    if (files.length === 0) {
      console.log("No files found to index.");
      return;
    }
    console.log(`Found ${files.length} files to index.`);

    const documents = await this.loadDocuments(files);
    console.log(`Loaded ${documents.length} documents.`);

    if (documents.length === 0) {
        console.log("No documents could be loaded for indexing.");
        return;
    }

    const textSplitter = new RecursiveCharacterTextSplitter({
      chunkSize: 1000,
      chunkOverlap: 200,
    });
    const splits = await textSplitter.splitDocuments(documents);
    console.log(`Split into ${splits.length} chunks.`);

    const vectorStore = await FaissStore.fromDocuments(splits, this.embeddings);
    await vectorStore.save(this.indexPath);

    console.log(`Indexing complete. Index saved to ${this.indexPath}`);
  }

  private async findFiles(): Promise<string[]> {
    const gitignore = await this.getGitignore();
    const defaultIgnore = ['node_modules/**', '.git/**', '**/dist/**', `${path.basename(this.aiPunkDir)}/**`];
    const files = await glob("**/*", {
      cwd: this.workspaceRoot,
      ignore: [...defaultIgnore, ...gitignore],
      nodir: true,
      absolute: true,
    });
    return files;
  }

  private async getGitignore(): Promise<string[]> {
    try {
      const gitignorePath = path.join(this.workspaceRoot, '.gitignore');
      const gitignoreContent = await fs.readFile(gitignorePath, 'utf-8');
      return gitignoreContent.split(/\r?\n/).filter(line => line.trim() !== '' && !line.startsWith('#'));
    } catch (error) {
      return [];
    }
  }

  private async loadDocuments(filePaths: string[]): Promise<Document[]> {
    const documents: Document[] = [];
    for (const filePath of filePaths) {
      try {
        const content = await fs.readFile(filePath, 'utf-8');
        documents.push(new Document({
          pageContent: content,
          metadata: { source: path.relative(this.workspaceRoot, filePath) },
        }));
      } catch (error) {
        console.warn(`Could not read file ${filePath}, skipping.`);
      }
    }
    return documents;
  }
} 