# How to Distribute Your AI Assistant Extension

There are two main ways to share your extension with others:

## Method 1: Share the .vsix File (Private/Internal)

This is the best method for internal tools or sharing with a small team without publishing to the public marketplace.

### 1. Package the Extension
Run this command in your terminal (`Extension/ai-assistant-vscode` folder):
```bash
npx vsce package
```
This will generate a file named `ai-assistant-vscode-0.0.1.vsix`.

### 2. Share the File
Send this `.vsix` file to your colleagues via email, Slack, or a shared drive.

### 3. How they Install it
1.  Open VS Code.
2.  Go to the **Extensions** view (`Ctrl+Shift+X`).
3.  Click the **... (Views and More Actions)** menu at the top right of the Extensions pane.
4.  Select **Install from VSIX...**
5.  Select the `.vsix` file.

**Important:** They must configure the **Backend URL** in their VS Code settings to point to your running Kubernetes cluster (or their own backend).

---

## Method 2: Publish to VS Code Marketplace (Public)

This makes your extension searchable and installable by anyone.

### 1. Create a Publisher
1.  Go to [VS Code Marketplace Management](https://marketplace.visualstudio.com/manage).
2.  Sign in with a Microsoft account.
3.  Create a **Publisher**. Note the **Publisher ID**.

### 2. Update package.json
Edit `Extension/ai-assistant-vscode/package.json`:
```json
"publisher": "YOUR_PUBLISHER_ID",
```

### 3. Login via CLI
Install `vsce`:
```bash
npm install -g @vscode/vsce
```
Login (requires a Personal Access Token from Azure DevOps):
```bash
vsce login YOUR_PUBLISHER_ID
```

### 4. Publish
```bash
vsce publish
```

---

## Configuration for Users

Regardless of the installation method, users need to connect to the backend.

1.  **Backend:** Ensure your Kubernetes backend is running and accessible (e.g., via LoadBalancer IP).
2.  **Settings:** Users must set:
    *   **AI Assistant: Backend Url**: `http://<YOUR_LOAD_BALANCER_IP>/query`

### Tips for Sharing
*   Since your backend uses **Azure Managed Identity**, users don't need API keys!
*   However, they need network access to your Kubernetes Service (LoadBalancer).
