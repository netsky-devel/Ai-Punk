import { Message } from './Message';

export interface Conversation {
    id: string;
    messages: Message[];
    createdAt: Date;
} 