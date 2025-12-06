# AI Assistant for VS Code

A powerful AI assistant integration for Visual Studio Code that connects to your private LLM backend.

## Features

- **Chat Interface**: seamless chat with AI models directly within VS Code.
- **Context Aware**: (Future) Can understand your code context.
- **Secure**: Connects to your own private backend (Ollama, Azure Blob Storage).
- **Persistent History**: Chat history is saved to Azure Blob Storage.

## Requirements

This extension requires a running instance of the **AI Assistant Backend**.

- **Backend URL**: You must configure the backend URL in settings.

## Extension Settings

This extension contributes the following settings:

* `aiAssistant.backendUrl`: The URL of your AI Assistant backend API (default: `http://localhost:8000/query`).

## Setup

1. Install the extension (`.vsix`).
2. Go to **Settings** (`Ctrl+,`) -> Search for **AI Assistant**.
3. Set **Backend Url** to your backend endpoint (e.g., `http://<LOAD_BALANCER_IP>/query`).

## Release Notes

### 0.0.1

Initial release with:
- Chat interface
- Blob Storage integration
- Key Vault security

