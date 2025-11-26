import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.commands.registerCommand('aiAssistant.openChat', () => {
        const panel = vscode.window.createWebviewPanel(
            'aiChat',                  // Identifies the type of the webview
            'AI Assistant',            // Title
            vscode.ViewColumn.Beside,  // Show beside the current editor
            { enableScripts: true }    // Allow JS in Webview
        );

        // Load previous chat history from globalState
        const previousChats: { user: string; ai: string }[] = context.globalState.get('chatHistory', []);

        panel.webview.html = getWebviewContent(previousChats);

        // Listen to messages from the Webview
        panel.webview.onDidReceiveMessage(async (message) => {
            if (message.command === 'sendQuery') {
                try {
                    const response = await fetch('http://localhost:8000/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ session_id: 'vscode', question: message.text })
                    });
                    const data = (await response.json()) as { response: string };

                    // Send AI response back to Webview
                    panel.webview.postMessage({ command: 'showResponse', userQuery: message.text, aiResponse: data.response });

                    // Save to globalState
                    previousChats.push({ user: message.text, ai: data.response });
                    context.globalState.update('chatHistory', previousChats);

                } catch (err) {
                    panel.webview.postMessage({ command: 'showResponse', userQuery: message.text, aiResponse: 'Error: ' + err });
                }
            }
        });
    });

    context.subscriptions.push(disposable);
}

function getWebviewContent(previousChats: { user: string; ai: string }[]) {
    // Build the initial chat history HTML
    let chatHistoryHtml = '';
    previousChats.forEach(chat => {
        chatHistoryHtml += `<p><b>You:</b> ${chat.user}</p>`;
        chatHistoryHtml += `<p><b>AI:</b> ${chat.ai}</p>`;
    });

    return `
    <!DOCTYPE html>
    <html lang="en">
    <body>
        <h3>AI Assistant</h3>
        <div id="chat" style="height:300px; overflow-y:auto; border:1px solid #ccc; padding:10px;">
            ${chatHistoryHtml}
        </div>
        <textarea id="userQuery" rows="3" cols="50" placeholder="Type your question here..."></textarea><br>
        <button onclick="sendQuery()">Send</button>

        <script>
            const vscode = acquireVsCodeApi();
            const chatDiv = document.getElementById('chat');

            function sendQuery() {
                const query = document.getElementById('userQuery').value;
                if (!query) return;
                chatDiv.innerHTML += \`<p><b>You:</b> \${query}</p>\`;
                chatDiv.scrollTop = chatDiv.scrollHeight;
                document.getElementById('userQuery').value = '';
                vscode.postMessage({ command: 'sendQuery', text: query });
            }

            // Listen for messages from extension.ts
            window.addEventListener('message', event => {
                const message = event.data;
                if (message.command === 'showResponse') {
                    chatDiv.innerHTML += \`<p><b>AI:</b> \${message.aiResponse}</p>\`;
                    chatDiv.scrollTop = chatDiv.scrollHeight;
                }
            });
        </script>
    </body>
    </html>
    `;
}

export function deactivate() {}