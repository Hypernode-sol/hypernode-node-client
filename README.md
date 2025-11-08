# Hypernode Node Client

**GPU/CPU Worker for Hypernode Distributed Compute Network**

Docker-based worker software that runs on GPU providers' machines to execute AI/compute jobs and earn HYPER tokens.

![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![CUDA](https://img.shields.io/badge/CUDA-Supported-green)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)

---

## 🎯 Overview

The Hypernode Node Client is a lightweight worker that:
- Detects your GPU specifications automatically
- Registers your hardware with the Hypernode network
- Sends periodic heartbeats to stay online
- Receives and executes AI/compute jobs
- Reports results back to the network
- Earns you HYPER tokens for completed work

---

## ✨ Features

- ✅ **Auto GPU Detection**: NVIDIA, AMD, Apple Silicon support
- ✅ **Docker Isolated**: Jobs run in secure containers
- ✅ **Zero Configuration**: Just provide wallet address
- ✅ **Real-time Monitoring**: View logs and metrics
- ✅ **Auto Updates**: Self-updating mechanism
- ✅ **Multi-GPU Support**: Run on machines with multiple GPUs
- ✅ **Telemetry**: Report GPU usage, temp, VRAM

---

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+ (with NVIDIA Container Toolkit for GPU)
- NVIDIA GPU with CUDA support (or AMD/CPU)
- Ubuntu 20.04+ / Debian 11+ / macOS / Windows with WSL2
- Internet connection

### 1. Install Docker + NVIDIA Toolkit

**Ubuntu/Debian:**
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

**Verify GPU access:**
```bash
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

---

### 2. Run the Node Client

Get your command from https://hypernodesolana.org/app after connecting your wallet.

**Example:**
```bash
docker run -d \
  --name hypernode-worker \
  --gpus all \
  --restart unless-stopped \
  -e HN_NODE_TOKEN=hn_abc123... \
  -e WALLET_PUBKEY=YourSolanaWalletAddress \
  -e BACKEND_URL=https://api.hypernode.sol \
  hypernode/node-client:latest
```

---

### 3. Check Status

```bash
# View logs
docker logs -f hypernode-worker

# Check GPU usage
docker exec hypernode-worker nvidia-smi

# View node status
docker exec hypernode-worker python check_status.py
```

---

## 🛠️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HN_NODE_TOKEN` | ✅ Yes | - | Node authentication token from /app |
| `WALLET_PUBKEY` | ✅ Yes | - | Your Solana wallet address |
| `BACKEND_URL` | No | `https://api.hypernode.sol` | Backend API endpoint |
| `HEARTBEAT_INTERVAL` | No | `60` | Heartbeat interval (seconds) |
| `MAX_JOBS_CONCURRENT` | No | `1` | Max jobs to run simultaneously |
| `GPU_INDEX` | No | `0` | GPU index to use (for multi-GPU) |
| `LOG_LEVEL` | No | `INFO` | Logging level |

---

## 📁 Project Structure

```
hypernode-node-client/
├── src/
│   ├── main.py                 # Main worker loop
│   ├── gpu_detector.py         # Detect GPU specs
│   ├── heartbeat.py            # Send periodic heartbeats
│   ├── job_executor.py         # Execute received jobs
│   ├── telemetry.py            # Report metrics
│   └── config.py               # Configuration loader
│
├── jobs/                        # Job execution modules
│   ├── llm_inference.py        # LLM inference jobs
│   ├── llm_finetuning.py       # Fine-tuning jobs
│   ├── rag_indexing.py         # RAG indexing jobs
│   └── render.py               # Render jobs
│
├── Dockerfile                   # Multi-stage Docker build
├── docker-compose.yml           # Compose file for easy setup
├── requirements.txt             # Python dependencies
├── .dockerignore
├── .gitignore
└── README.md                    # This file
```

---

## 🐳 Docker Build

### Build locally
```bash
docker build -t hypernode/node-client:latest .
```

### Run locally built image
```bash
docker run -d \
  --name hypernode-worker \
  --gpus all \
  -e HN_NODE_TOKEN=your_token \
  -e WALLET_PUBKEY=your_wallet \
  hypernode/node-client:latest
```

---

## 🔧 Development

### Run without Docker (for development)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export HN_NODE_TOKEN=your_token
export WALLET_PUBKEY=your_wallet
export BACKEND_URL=http://localhost:3001

# Run worker
python src/main.py
```

---

## 📊 Supported Job Types

### 1. LLM Inference
Run inference on language models (Qwen, DeepSeek, Llama, Mistral)
- Models loaded via Ollama or HuggingFace
- Streaming support
- Batch processing

### 2. LLM Fine-tuning
Fine-tune models with LoRA/QLoRA
- Parameter-efficient fine-tuning
- Custom datasets
- Checkpoint management

### 3. RAG Indexing
Build vector indexes for RAG systems
- Embedding generation
- Vector storage (FAISS, Chroma)
- Document chunking

### 4. Vision Pipeline
Computer vision tasks
- Object detection
- Image classification
- OCR

### 5. Rendering
3D rendering and video processing
- Blender renders
- Video transcoding
- Image processing

### 6. Generic Compute
Custom Python/Bash scripts
- Data processing
- Scientific computing
- Batch jobs

---

## 🔐 Security

### Isolation
- All jobs run in isolated Docker containers
- No access to host filesystem (except job data)
- Network sandboxing
- Resource limits (CPU, RAM, GPU)

### Data Privacy
- No job data stored locally after completion
- Results encrypted in transit
- Optional local logging (disabled by default)

### Updates
- Auto-update mechanism for client software
- Signature verification on updates
- Rollback capability

---

## 📈 Monitoring & Telemetry

### Metrics Reported
- GPU utilization %
- VRAM usage
- GPU temperature
- Power consumption
- Job execution time
- Network bandwidth
- CPU usage
- RAM usage

### Logs
```bash
# View real-time logs
docker logs -f hypernode-worker

# Export logs
docker logs hypernode-worker > node-logs.txt
```

---

## 🎮 GPU Support

### NVIDIA (Recommended)
- CUDA 11.0+
- Driver 450.80.02+
- Compute Capability 3.5+

**Supported Models:**
- RTX 4090, 4080, 4070
- RTX 3090, 3080, 3070
- A100, A6000, A4000
- Tesla V100, T4

### AMD
- ROCm 5.0+
- Radeon RX 7900 XTX, 7800 XT
- Radeon RX 6900 XT, 6800 XT

### Apple Silicon
- M1/M2/M3 (Metal acceleration)
- 8GB+ unified memory recommended

### CPU-only
- Can participate in CPU-only jobs
- Lower earnings but still supported

---

## 💰 Earnings

### How Earnings Work
1. You register your node via /app
2. Node client runs on your machine
3. Jobs are assigned based on your GPU specs
4. You execute jobs and submit results
5. Upon verification, HYPER is sent to your wallet

### Payment Distribution
- **80%** of job price → You (node operator)
- **10%** → Protocol treasury
- **5%** → Incentive pool
- **5%** → Orchestrator/Agent

### Reputation System

**On-Chain Reputation Tracking** (Solana-based):
- All reputation metrics stored on blockchain
- Transparent and verifiable performance history
- Cannot be manipulated or reset

**Health Check System** (Permissionless Verification):
- **Anyone can verify node health** - Decentralized quality monitoring
- **Automatic penalties** - Failed checks reduce reputation by 10 points
- **Anti-spam protection** - 5-minute minimum interval between checks
- **Transparent metrics** - All checks recorded on-chain
  - Total health checks performed
  - Passed/failed check counts
  - Health check pass rate (0-100%)
  - Last check timestamp

**Reputation Score** (0-1000 points):
- Completion rate (60% weight)
- Uptime (30% weight)
- Response time (10% weight)
- **Health check pass rate affects priority** - Higher pass rate = better job matching

**Tier System**:
- Starter (0-200): New nodes
- Bronze (201-400): Basic tier
- Silver (401-600): Intermediate tier
- Gold (601-800): High tier
- Diamond (801-1000): Elite tier

**Tracked Metrics**:
- Total jobs completed
- Failed jobs count
- Timeout jobs count
- Average response time
- Total uptime (hours)
- Total revenue earned (SOL)

**Priority System**:
- Higher tiers get priority for job matching
- Diamond tier: +10 priority boost
- Gold tier: +5 priority boost
- Silver tier: +2 priority boost
- Bronze tier: +1 priority boost

**Implementation**:
See [ReputationHandler.ts](https://github.com/Hypernode-sol/hypernode-llm-deployer/blob/main/worker/src/handlers/ReputationHandler.ts) for the full implementation.

---

## 🔗 Integration with Solana Programs

The node client integrates directly with Hypernode's Solana smart contracts:

**Program Interactions**:
- **Markets Program**: List node, accept jobs, submit results
- **Staking Program**: Verify xHYPER stake requirements
- **Reputation Program**: Update on-chain performance metrics
- **Slashing Program**: Subject to fraud detection and penalties

**Worker Architecture** (TypeScript):
```
worker/src/
├── NodeManager.ts          # Main orchestrator
├── solana/
│   └── SolanaClient.ts     # Solana program interactions
├── handlers/
│   ├── SpecsHandler.ts     # GPU detection
│   ├── HealthHandler.ts    # Health monitoring
│   ├── JobHandler.ts       # Job execution
│   └── ReputationHandler.ts # Reputation tracking
└── providers/
    └── DockerProvider.ts   # Container orchestration
```

**Source Code**: [hypernode-llm-deployer/worker](https://github.com/Hypernode-sol/hypernode-llm-deployer/tree/main/worker)

---

## 🆘 Troubleshooting

### GPU not detected
```bash
# Check NVIDIA driver
nvidia-smi

# Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi

# Reinstall NVIDIA Container Toolkit
sudo apt-get install --reinstall nvidia-container-toolkit
sudo systemctl restart docker
```

### Node offline
```bash
# Check if container is running
docker ps | grep hypernode-worker

# Check logs for errors
docker logs hypernode-worker | tail -50

# Restart container
docker restart hypernode-worker
```

### No jobs received
- Check your reputation score on /app
- Ensure your node is "Online" status
- Verify GPU specs meet job requirements
- Check network connectivity
- Ensure HYPER stake is sufficient (if required)

---

## 🔄 Updates

The client auto-updates to the latest version. To manually update:

```bash
# Pull latest image
docker pull hypernode/node-client:latest

# Stop and remove old container
docker stop hypernode-worker
docker rm hypernode-worker

# Start with latest image
docker run -d \
  --name hypernode-worker \
  --gpus all \
  --restart unless-stopped \
  -e HN_NODE_TOKEN=your_token \
  -e WALLET_PUBKEY=your_wallet \
  hypernode/node-client:latest
```

---

## 🏗️ Project Status

**Current Phase**: Devnet Testing

The Hypernode network is built on Solana with 5 core smart contracts:
- ✅ **Markets Program** - Job/node matching, escrow payments
- ✅ **Staking Program** - Time-locked HYPER staking (2 weeks to 1 year)
- ✅ **Rewards Program** - O(1) reflection-based rewards distribution
- ✅ **Slashing Program** - Fraud detection with 7-day appeal period
- ✅ **Governance Program** - DAO voting with xHYPER-weighted power

**Security**: 6 critical/high vulnerabilities fixed, 35-40% gas optimized

**Worker Implementation**: TypeScript-based worker client with full Solana integration, reputation tracking, and Docker orchestration.

---

## 📚 Resources

**Official Links**:
- [GitHub Organization](https://github.com/Hypernode-sol)
- [Twitter](https://x.com/hypernode_sol)

**Technical Documentation**:
- [Solana Programs](https://github.com/Hypernode-sol/hypernode-llm-deployer) - Core smart contracts
- [Worker Source Code](https://github.com/Hypernode-sol/hypernode-llm-deployer/tree/main/worker) - TypeScript worker implementation
- [Security Audit](https://github.com/Hypernode-sol/hypernode-llm-deployer/blob/main/SECURITY_AUDIT.md)
- [Gas Optimization Report](https://github.com/Hypernode-sol/hypernode-llm-deployer/blob/main/GAS_OPTIMIZATION.md)
- [SDK Documentation](https://github.com/Hypernode-sol/hypernode-llm-deployer/tree/main/sdk)

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Test with real GPU hardware
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## 📄 License

MIT License - see LICENSE file for details

---

## ⚠️ Disclaimer

- Running compute jobs uses electricity - monitor your power costs
- Ensure proper cooling for your GPU
- Jobs from untrusted sources run in isolated containers
- You are responsible for your hardware
- Earnings depend on network demand and your hardware specs

---

**Start earning HYPER with your idle GPU!**
