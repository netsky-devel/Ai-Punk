export type MessageSender = 'user' | 'bot';

export interface Message {
    id: string;
    sender: MessageSender;
    text: string;
    timestamp: Date;
} 