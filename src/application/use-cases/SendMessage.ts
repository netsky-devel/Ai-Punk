import { Conversation } from '../../domain/entities/Conversation';
import { Message } from '../../domain/entities/Message';
import { IConversationRepository } from '../ports/IConversationRepository';
import { IAIAdapter } from '../ports/IAIAdapter';
import { randomUUID } from 'crypto';

export class SendMessage {
    constructor(
        private conversationRepository: IConversationRepository,
        private aiAdapter: IAIAdapter
    ) {}

    public async execute(conversationId: string, text: string): Promise<Conversation> {
        const conversation = await this.conversationRepository.findById(conversationId);
        if (!conversation) {
            throw new Error('Conversation not found');
        }

        const userMessage: Message = {
            id: randomUUID(),
            sender: 'user',
            text,
            timestamp: new Date(),
        };

        conversation.messages.push(userMessage);

        const botResponseText = await this.aiAdapter.getCompletion(conversation.messages);
        
        const botMessage: Message = {
            id: randomUUID(),
            sender: 'bot',
            text: botResponseText,
            timestamp: new Date(),
        };

        conversation.messages.push(botMessage);

        await this.conversationRepository.save(conversation);

        return conversation;
    }
} 