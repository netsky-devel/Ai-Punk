import { Conversation } from '../../domain/entities/Conversation';

export interface IConversationRepository {
    findById(id: string): Promise<Conversation | undefined>;
    save(conversation: Conversation): Promise<void>;
} 