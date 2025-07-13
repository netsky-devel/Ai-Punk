import { Conversation } from '../../domain/entities/Conversation';
import { IConversationRepository } from '../../application/ports/IConversationRepository';
import { randomUUID } from 'crypto';

export class InMemoryConversationRepository implements IConversationRepository {
    private readonly conversations: Map<string, Conversation> = new Map();

    constructor() {
        // Start with one default conversation for simplicity
        const defaultConversationId = randomUUID();
        this.conversations.set(defaultConversationId, {
            id: defaultConversationId,
            messages: [],
            createdAt: new Date(),
        });
    }

    public findById(id: string): Promise<Conversation | undefined> {
        const conversation = this.conversations.get(id);
        return Promise.resolve(conversation);
    }

    public save(conversation: Conversation): Promise<void> {
        this.conversations.set(conversation.id, conversation);
        return Promise.resolve();
    }

    public findActiveConversationId(): string | undefined {
        // For this in-memory repo, we'll just return the first one.
        // A real implementation might track the "active" one.
        return this.conversations.keys().next().value;
    }
} 