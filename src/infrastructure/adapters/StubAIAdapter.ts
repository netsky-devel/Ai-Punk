import { Message } from '../../domain/entities/Message';
import { IAIAdapter } from '../../application/ports/IAIAdapter';

export class StubAIAdapter implements IAIAdapter {
    public async getCompletion(messages: Message[]): Promise<string> {
        console.log("AI Adapter received messages:", messages);
        const lastMessage = messages[messages.length - 1]?.text || "nothing";
        const response = `This is a stub response. You said: "${lastMessage}"`;
        return Promise.resolve(response);
    }
} 