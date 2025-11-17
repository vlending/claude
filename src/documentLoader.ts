import fs from 'fs';
import path from 'path';

export interface Document {
  content: string;
  source: string;
  title: string;
}

export class DocumentLoader {
  private documents: Document[] = [];

  constructor(private docsPath: string) {
    this.loadDocuments();
  }

  private loadDocuments(): void {
    const files = fs.readdirSync(this.docsPath);

    for (const file of files) {
      if (file.endsWith('.md')) {
        const filePath = path.join(this.docsPath, file);
        const content = fs.readFileSync(filePath, 'utf-8');

        this.documents.push({
          content,
          source: file,
          title: this.extractTitle(content, file)
        });
      }
    }

    console.log(`✅ Loaded ${this.documents.length} documents`);
  }

  private extractTitle(content: string, filename: string): string {
    const titleMatch = content.match(/^#\s+(.+)$/m);
    return titleMatch ? titleMatch[1] : filename.replace('.md', '');
  }

  public getAllDocuments(): Document[] {
    return this.documents;
  }

  public getDocumentsAsContext(): string {
    return this.documents.map(doc => {
      return `=== ${doc.title} (${doc.source}) ===\n\n${doc.content}\n\n`;
    }).join('\n---\n\n');
  }

  public searchDocuments(query: string): Document[] {
    const lowerQuery = query.toLowerCase();

    return this.documents.filter(doc => {
      return doc.content.toLowerCase().includes(lowerQuery) ||
             doc.title.toLowerCase().includes(lowerQuery);
    });
  }
}
