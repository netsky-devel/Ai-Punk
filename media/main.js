(function () {
    const vscode = acquireVsCodeApi();

    const chatContainer = document.getElementById('chat-container');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');

    // Handle messages sent from the extension to the webview
    window.addEventListener('message', event => {
        const message = event.data; // The json data that the extension sent
        switch (message.type) {
            case 'addMessage':
                addMessage(message.data);
                break;
        }
    });

    function sendMessage() {
        const text = messageInput.value;
        if (text) {
            vscode.postMessage({
                type: 'sendMessage',
                data: text
            });
            messageInput.value = '';
        }
    }

    sendButton.addEventListener('click', sendMessage);

    messageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    function addMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.sender}-message`;
        messageElement.textContent = message.text;
        chatContainer.appendChild(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}()); 