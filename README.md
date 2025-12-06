# 🚀 AI Assistant VS Code Extension

**A cloud-native AI assistant with intelligent auto-scaling, deployed on Azure Kubernetes Service**

[![Platform](https://img.shields.io/badge/Platform-Mac%20%7C%20Windows-blue)]()
[![Cloud](https://img.shields.io/badge/Cloud-Azure-0078D4)]()
[![AI Model](https://img.shields.io/badge/AI-Qwen%202.5%3A1.5B-orange)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

**Team:** Swarup Panda & Jayanth Sibbala  
**Course:** Datacenter Scale Computing (DCSC)  
**Institution:** University of Colorado Boulder

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Technologies Used](#-technologies-used)
- [Prerequisites](#-prerequisites)
- [Setup Instructions](#-setup-instructions)
- [Usage](#-usage)
- [Autoscaling Demo](#-autoscaling-demo)
- [Project Metrics](#-project-metrics)
- [Cost Analysis](#-cost-analysis)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Acknowledgments](#-acknowledgments)

---

## 🎯 Overview

This project is a production-ready AI assistant integrated into Visual Studio Code, leveraging cloud-native technologies to provide intelligent code assistance with automatic scaling capabilities. The system uses Ollama with the Qwen 2.5:1.5B model for natural language processing, deployed on Azure Kubernetes Service (AKS) with comprehensive autoscaling at both pod and node levels.

### Key Highlights

- ✅ **Full-stack cloud-native application**
- ✅ **Kubernetes-based container orchestration**
- ✅ **Intelligent horizontal and vertical autoscaling**
- ✅ **Real-time data persistence with Azure Blob Storage**
- ✅ **Secure secret management with Azure Key Vault**
- ✅ **Cross-platform support (Mac & Windows)**
- ✅ **Production-grade load balancing**

---

## ✨ Features

### 🤖 AI Capabilities
- Real-time AI assistance within VS Code
- Natural language query processing
- Context-aware code suggestions
- Powered by Qwen 2.5:1.5B model (optimized for performance)

### ☸️ Cloud-Native Architecture
- **Kubernetes orchestration** on Azure AKS
- **Horizontal Pod Autoscaler (HPA)** - Scales from 1 to 10 pods based on CPU/Memory
- **Cluster Autoscaler** - Automatically adds/removes nodes (2-5 nodes)
- **Load balancing** across multiple FastAPI pods
- **Service mesh** with internal ClusterIP services

### 💾 Data Persistence
- **Azure Blob Storage** - All chat logs saved in JSON format
- **Structured logging** - Session ID, timestamps, latency metrics, token counts
- **Azure Key Vault** - Secure credential management

### 🔐 Security
- No hardcoded secrets in codebase
- Azure Key Vault integration
- Managed identities for Azure services
- Internal-only communication for AI services

### 📊 Monitoring & Performance
- Real-time CPU and memory metrics
- Autoscaling based on 70% CPU / 80% memory thresholds
- Load testing validated (286% CPU peak)
- Response time tracking

---

## 🏗️ Architecture

### System Overview

```
Developer Workstation (VS Code)
    ↓
Azure Load Balancer (172.193.220.19:80)
    ↓
FastAPI Backend Pods (2 replicas)
    ↓
Ollama Service (ClusterIP - Internal)
    ↓
Ollama AI Pods (1-10 replicas - Auto-scaled)
    ↓
[Blob Storage] ← Chat logs
[Key Vault] ← Secrets
```

### Request Flow

1. User types query in VS Code extension
2. Extension sends POST request to Load Balancer
3. Load Balancer routes to available FastAPI pod
4. FastAPI retrieves credentials from Key Vault
5. FastAPI forwards query to Ollama Service
6. Ollama Service load-balances across AI pods
7. AI pod generates response using Qwen 2.5:1.5B
8. Response returns through FastAPI
9. FastAPI saves chat log to Blob Storage
10. Response displayed in VS Code

### Autoscaling Flow

```
Normal Load (1 pod, 20% CPU)
    ↓
Traffic Increase (100+ concurrent requests)
    ↓
CPU/Memory Threshold Exceeded (286% CPU observed)
    ↓
HPA Triggers Scale-Up (1 → 2 → 4 → 8 pods)
    ↓
Load Distributed (60% CPU per pod)
    ↓
Traffic Decreases
    ↓
HPA Triggers Scale-Down (8 → 4 → 2 → 1, 5-min cooldown)
    ↓
Back to Baseline
```

---

## 🛠️ Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | VS Code Extension (TypeScript) | User interface for developers |
| **API Gateway** | FastAPI (Python) | Request routing, logging, coordination |
| **AI Engine** | Ollama + Qwen 2.5:1.5B | Natural language processing |
| **Orchestration** | Azure Kubernetes Service (AKS) | Container management, scaling |
| **Container Registry** | Docker Hub | Image hosting and distribution |
| **Storage** | Azure Blob Storage | Chat log persistence |
| **Secrets** | Azure Key Vault | Secure credential management |
| **Load Testing** | hey | Performance validation |

### Infrastructure Specifications

- **Kubernetes Version:** 1.32.9
- **Node Type:** Standard_D2s_v3 (2 vCPU, 8GB RAM)
- **Node Count:** 2-5 (autoscaling enabled)
- **Region:** West US 2
- **Ollama Resources:** 500m CPU (request), 2Gi Memory (request)
- **FastAPI Resources:** 250m CPU, 512Mi Memory

---

## 📦 Prerequisites

### Required Tools

- **Azure CLI** - Version 2.x or higher
- **kubectl** - Kubernetes command-line tool
- **Docker** - For building container images
- **Node.js & npm** - For VS Code extension development
- **Python 3.9+** - For FastAPI backend
- **VS Code** - For extension testing
- **hey** - For load testing (optional)

### Azure Requirements

- Active Azure subscription (Student credits recommended)
- Resource group created
- Sufficient quota for:
  - 2-5 Standard_D2s_v3 VMs
  - Load Balancer
  - Storage Account
  - Key Vault

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/VS_Code_AI_Extension.git
cd VS_Code_AI_Extension
```

### 2. Azure Infrastructure Setup

#### 2.1 Login to Azure

```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

#### 2.2 Create Resource Group

```bash
az group create \
  --name ai-assistant-rg \
  --location westus2
```

#### 2.3 Create AKS Cluster

```bash
az aks create \
  --resource-group ai-assistant-rg \
  --name ai-assistant-cluster \
  --node-count 2 \
  --node-vm-size Standard_D2s_v3 \
  --enable-managed-identity \
  --enable-cluster-autoscaler \
  --min-count 2 \
  --max-count 5 \
  --generate-ssh-keys
```

#### 2.4 Get Cluster Credentials

```bash
az aks get-credentials \
  --resource-group ai-assistant-rg \
  --name ai-assistant-cluster \
  --overwrite-existing
```

#### 2.5 Create Azure Blob Storage

```bash
# Create storage account
az storage account create \
  --name aiassistantstorage \
  --resource-group ai-assistant-rg \
  --location westus2 \
  --sku Standard_LRS

# Create container
az storage container create \
  --name chat-logs \
  --account-name aiassistantstorage

# Get connection string
az storage account show-connection-string \
  --name aiassistantstorage \
  --resource-group ai-assistant-rg \
  --output tsv
```

**Save the connection string - you'll need it later!**

#### 2.6 Create Azure Key Vault

```bash
az keyvault create \
  --name ai-assistant-vault \
  --resource-group ai-assistant-rg \
  --location westus2

# Add blob storage connection string
az keyvault secret set \
  --vault-name ai-assistant-vault \
  --name blob-connection-string \
  --value "YOUR_CONNECTION_STRING"
```

### 3. Build and Push Docker Images

#### 3.1 Build Ollama Image

```bash
cd kubernetes/ollama
docker build --platform linux/amd64 --no-cache -t YOUR_DOCKERHUB_USERNAME/ollama-qwen:latest .
docker push YOUR_DOCKERHUB_USERNAME/ollama-qwen:latest
```

#### 3.2 Build FastAPI Image

```bash
cd ../../backend
docker build --platform linux/amd64 -t YOUR_DOCKERHUB_USERNAME/fastapi-backend:latest .
docker push YOUR_DOCKERHUB_USERNAME/fastapi-backend:latest
```

**Important:** Update image names in deployment YAMLs to match your Docker Hub username.

### 4. Deploy to Kubernetes

#### 4.1 Create Namespace

```bash
kubectl create namespace ai-assistant
```

#### 4.2 Create Secrets

```bash
# Create secrets.yaml from template
cp kubernetes/backend/secrets.yaml.example kubernetes/backend/secrets.yaml

# Edit secrets.yaml with your actual values
nano kubernetes/backend/secrets.yaml

# Apply secrets
kubectl apply -f kubernetes/backend/secrets.yaml
```

#### 4.3 Deploy All Components

```bash
# Option 1: Use deployment script
./scripts/deploy-all.sh

# Option 2: Manual deployment
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/backend/configmap.yaml
kubectl apply -f kubernetes/backend/deployment.yaml
kubectl apply -f kubernetes/backend/service.yaml
kubectl apply -f kubernetes/ollama/deployment.yaml
kubectl apply -f kubernetes/ollama/service.yaml
kubectl apply -f kubernetes/ollama/hpa.yaml
```

#### 4.4 Verify Deployment

```bash
# Check pods
kubectl get pods -n ai-assistant

# Expected output:
# NAME                               READY   STATUS    RESTARTS   AGE
# fastapi-backend-xxxxx-xxxxx        1/1     Running   0          2m
# fastapi-backend-xxxxx-yyyyy        1/1     Running   0          2m
# ollama-qwen-xxxxx-xxxxx            1/1     Running   0          2m

# Check services
kubectl get svc -n ai-assistant

# Note the EXTERNAL-IP for fastapi-backend (e.g., 172.193.220.19)
```

### 5. Configure VS Code Extension

#### 5.1 Install Extension Dependencies

```bash
cd Extension/ai-assistant-vscode
npm install
```

#### 5.2 Configure Backend URL

Open VS Code settings (Cmd/Ctrl + ,) and search for "aiAssistant". Set:

```json
{
  "aiAssistant.backendUrl": "http://YOUR_EXTERNAL_IP/query"
}
```

Replace `YOUR_EXTERNAL_IP` with the LoadBalancer IP from step 4.4.

#### 5.3 Run Extension

```bash
# In VS Code
# Press F5 to start debugging
# A new VS Code window will open with the extension loaded
```

#### 5.4 Test Extension

1. In the new VS Code window, open Command Palette (Cmd/Ctrl + Shift + P)
2. Type "AI Assistant: Open Chat"
3. Send a test message: "What is Kubernetes?"
4. Verify you receive an AI response

---

## 💡 Usage

### Basic Usage

1. **Open VS Code** with the extension installed
2. **Open Command Palette** (Cmd/Ctrl + Shift + P)
3. **Run command:** "AI Assistant: Open Chat"
4. **Type your question** in the chat interface
5. **Receive AI response** in real-time

### Example Queries

```
- "What is Kubernetes?"
- "Explain Docker containers"
- "How does load balancing work?"
- "Write a Python function to sort a list"
- "Explain the difference between REST and GraphQL"
```

### Chat History

All conversations are automatically saved to Azure Blob Storage with:
- Session ID
- Timestamp
- Query text
- AI response
- Model used
- Latency metrics
- Token count

---

## 📊 Autoscaling Demo

### Load Testing

Generate load to trigger autoscaling:

```bash
# Install hey
brew install hey

# Generate heavy load
hey -n 5000 -c 100 -m POST \
  -H "Content-Type: application/json" \
  -d '{"session_id":"loadtest","question":"What is Kubernetes?"}' \
  http://YOUR_EXTERNAL_IP/query
```

### Monitor Autoscaling

**Terminal 1 - Watch HPA:**
```bash
kubectl get hpa -n ai-assistant --watch
```

**Terminal 2 - Watch Pods:**
```bash
kubectl get pods -n ai-assistant --watch
```

**Terminal 3 - Watch Nodes:**
```bash
kubectl get nodes --watch
```

### Expected Behavior

1. **Baseline:** 1 Ollama pod, ~20% CPU
2. **Load Applied:** CPU spikes to 180-286%
3. **HPA Triggers:** Scales from 1 → 2 → 4 → 8 pods
4. **Load Distributed:** CPU per pod drops to ~60%
5. **Load Stops:** System scales down to 1 pod (5-10 min cooldown)

---

## 📈 Project Metrics

### Performance Achievements

| Metric | Value | Description |
|--------|-------|-------------|
| **Technologies** | 6 | Cloud services integrated |
| **Autoscaling Range** | 1→10 pods | Dynamic scaling capability |
| **Peak CPU Load** | 286% | Maximum load tested |
| **Response Time** | <60s | HPA scaling response |
| **Platform Support** | 2 | Mac + Windows |
| **Cost Savings** | 15% | vs always-on cluster |

### Resource Specifications

**Ollama Pods:**
- CPU Request: 500m
- CPU Limit: 1500m
- Memory Request: 2Gi
- Memory Limit: 4Gi
- Model Size: ~3GB (Qwen 2.5:1.5B)

**FastAPI Pods:**
- CPU Request: 250m
- Memory Request: 512Mi
- Replicas: 2 (fixed)

**AKS Nodes:**
- VM Size: Standard_D2s_v3
- vCPU: 2
- Memory: 8GB
- Count: 2-5 (autoscaling)

---

## 💰 Cost Analysis

### Total Project Cost

**Actual Spend:** ~$120 Azure credits

### Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| **AKS Compute** | ~$115 | 2 nodes × ~20 hours runtime |
| **Blob Storage** | <$1 | Minimal data storage |
| **Key Vault** | $0 | Free tier |
| **Network Egress** | ~$4 | Data transfer |
| **Total** | **~$120** | Development + testing |

### Cost Optimization Strategies

1. **Stop/Start Cluster** - Shut down when not in use
   ```bash
   # Stop cluster
   az aks stop --resource-group ai-assistant-rg --name ai-assistant-cluster
   
   # Start cluster
   az aks start --resource-group ai-assistant-rg --name ai-assistant-cluster
   ```

2. **Right-Sized VMs** - Used D2s_v3 instead of larger sizes
3. **Docker Hub** - Free registry instead of ACR (~$5/month saved)
4. **Free Tiers** - Leveraged Key Vault and monitoring free tiers
5. **Efficient Development** - Completed in 20-30 hours of cluster runtime

### Cost Comparison

| Scenario | Monthly Cost | Our Cost |
|----------|-------------|----------|
| Always-On (24/7) | ~$140 | - |
| Stop/Start Strategy | - | **$120 total** |
| **Savings** | - | **15%** |

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Pods Stuck in Pending

**Issue:** Ollama pods show "Pending" status

**Cause:** Insufficient node resources

**Solution:**
```bash
# Check node capacity
kubectl describe nodes | grep -A 5 "Allocated resources"

# Option 1: Reduce resource requests
# Edit kubernetes/ollama/deployment.yaml
# Reduce memory from 4Gi to 2Gi

# Option 2: Add more nodes manually
az aks scale \
  --resource-group ai-assistant-rg \
  --cluster-name ai-assistant-cluster \
  --node-count 3
```

#### 2. VS Code Extension Not Connecting

**Issue:** "TypeError: fetch failed" in extension

**Causes & Solutions:**

```bash
# Check if cluster is running
az aks show \
  --resource-group ai-assistant-rg \
  --name ai-assistant-cluster \
  --query "powerState.code"

# If Stopped, start it
az aks start \
  --resource-group ai-assistant-rg \
  --name ai-assistant-cluster

# Verify FastAPI external IP
kubectl get svc fastapi-backend -n ai-assistant

# Update VS Code settings with correct IP
```

#### 3. HPA Shows `<unknown>` Metrics

**Issue:** HPA can't read metrics

**Solution:**
```bash
# Install metrics server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Wait 2 minutes, then check
kubectl top nodes
kubectl top pods -n ai-assistant
```

#### 4. Image Pull Errors

**Issue:** Pods fail with "ImagePullBackOff"

**Solution:**
```bash
# Verify image exists on Docker Hub
docker pull YOUR_DOCKERHUB_USERNAME/ollama-qwen:latest

# Check deployment YAML has correct image name
kubectl get deployment ollama-qwen -n ai-assistant -o yaml | grep image:

# Update if needed
kubectl set image deployment/ollama-qwen \
  ollama=YOUR_DOCKERHUB_USERNAME/ollama-qwen:latest \
  -n ai-assistant
```

#### 5. Blob Storage Not Saving

**Issue:** Chat logs not appearing in Blob Storage

**Solution:**
```bash
# Verify secret exists
kubectl get secret azure-secrets -n ai-assistant

# Check FastAPI logs
kubectl logs -l app=fastapi-backend -n ai-assistant --tail=50

# Verify connection string in Key Vault
az keyvault secret show \
  --vault-name ai-assistant-vault \
  --name blob-connection-string
```

### Getting Help

If you encounter issues:

1. Check pod logs: `kubectl logs POD_NAME -n ai-assistant`
2. Check events: `kubectl get events -n ai-assistant --sort-by='.lastTimestamp'`
3. Describe resources: `kubectl describe pod POD_NAME -n ai-assistant`

---

## 🤝 Contributing

We welcome contributions! Here's how:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and test thoroughly
4. Commit: `git commit -m "Add your feature"`
5. Push: `git push origin feature/your-feature`
6. Create a Pull Request

### Code Standards

- **Python:** Follow PEP 8
- **TypeScript:** Use ESLint configuration
- **YAML:** 2-space indentation
- **Documentation:** Update README for new features

---

## 📚 Project Structure

```
VS_Code_AI_Extension/
├── backend/
│   ├── app/
│   │   └── main.py              # FastAPI application
│   ├── Dockerfile               # FastAPI container
│   └── requirements.txt         # Python dependencies
│
├── Extension/
│   └── ai-assistant-vscode/
│       ├── src/
│       │   ├── extension.ts     # VS Code extension main code
│       │   └── test/
│       │       └── extension.test.ts
│       ├── out/                 # Compiled TypeScript
│       │   ├── extension.js
│       │   └── test/
│       ├── node_modules/        # Extension dependencies
│       ├── package.json         # Extension manifest
│       ├── package-lock.json
│       ├── tsconfig.json        # TypeScript configuration
│       └── README.md            # Extension documentation
│
├── kubernetes/
│   ├── namespace.yaml           # Kubernetes namespace
│   ├── backend/
│   │   ├── configmap.yaml       # FastAPI environment config
│   │   ├── deployment.yaml      # FastAPI deployment (2 replicas)
│   │   ├── secrets.yaml.example # Secrets template (DO NOT COMMIT REAL SECRETS)
│   │   └── service.yaml         # LoadBalancer service
│   └── ollama/
│       ├── Dockerfile           # Ollama + Qwen 2.5:1.5B container
│       ├── deployment.yaml      # Ollama deployment (1 replica)
│       ├── hpa.yaml             # Horizontal Pod Autoscaler config
│       └── service.yaml         # ClusterIP service (internal)
│
├── scripts/
│   ├── build-backend.sh         # Build & push FastAPI Docker image
│   ├── build-ollama.sh          # Build & push Ollama Docker image
│   ├── deploy-all.sh            # Deploy all K8s resources
│   ├── cleanup.sh               # Delete all K8s resources
│   └── test-load.sh             # Load testing with hey
│
├── .gitignore                   # Git ignore rules (includes secrets!)
├── README.md                    # This file
└── Report.html                  # Project report/documentation
```

### Key Files Explained

**Backend:**
- `backend/app/main.py` - FastAPI routes, Ollama integration, Blob Storage logic
- `backend/Dockerfile` - Multi-stage build for FastAPI container

**Extension:**
- `Extension/ai-assistant-vscode/src/extension.ts` - Extension activation, UI, API calls
- `Extension/ai-assistant-vscode/package.json` - Extension metadata, commands, configuration

**Kubernetes:**
- `kubernetes/namespace.yaml` - Creates `ai-assistant` namespace
- `kubernetes/backend/deployment.yaml` - 2 FastAPI pods with resource limits
- `kubernetes/backend/service.yaml` - LoadBalancer exposing port 80
- `kubernetes/ollama/deployment.yaml` - 1 Ollama pod (auto-scaled by HPA)
- `kubernetes/ollama/hpa.yaml` - Autoscaling rules (1-10 pods, 70% CPU target)

**Scripts:**
- All scripts use Docker Hub (username: swaruppanda11 or YOUR_USERNAME)
- `deploy-all.sh` applies all YAML files in correct order
- `cleanup.sh` removes all resources (USE WITH CAUTION!)

---

## 🎓 Acknowledgments

### Technologies & Tools

- **Ollama** - For the incredible AI model serving framework
- **Qwen Team** - For the efficient Qwen 2.5 models
- **Microsoft Azure** - For cloud infrastructure and student credits
- **Kubernetes** - For container orchestration
- **FastAPI** - For the high-performance Python framework
- **VS Code** - For the extensibility platform

### Educational Support

- **University of Colorado Boulder** - For the course and resources
- **DCSC Course Staff** - For guidance and support
- **Azure for Students** - For providing cloud credits

### Special Thanks

- Professor and TAs for project guidance
- Fellow students for collaboration and feedback
- Open-source community for tools and libraries

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Swarup Panda**
- Role: Infrastructure & DevOps Lead
- Focus: Kubernetes, Ollama deployment, autoscaling
- Contact: [GitHub Profile](https://github.com/swaruppanda)

**Jayanth Sibbala**
- Role: Backend & Integration Lead  
- Focus: FastAPI, Blob Storage, Key Vault integration
- Contact: [GitHub Profile](https://github.com/jayanthsibbala)

---

## 📞 Support

For questions or issues:

1. **Check Troubleshooting section** above
2. **Open an issue** on GitHub
3. **Contact team members** via GitHub

---

## 🗺️ Roadmap

### Future Enhancements

- [ ] Add Azure Cosmos DB for structured query storage
- [ ] Implement Azure Application Insights monitoring
- [ ] Add conversation history search functionality
- [ ] Support for multiple AI models
- [ ] User authentication and multi-tenancy
- [ ] Advanced analytics dashboard
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Prometheus + Grafana monitoring
- [ ] Multi-region deployment

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ by Swarup Panda & Jayanth Sibbala**

**University of Colorado Boulder | DCSC 2025**
