import { Message } from '../../domain/entities/Message';

export interface IAIAdapter {
    getCompletion(messages: Message[]): Promise<string>;
} 