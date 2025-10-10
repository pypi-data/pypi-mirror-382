# RightNow CLI - GPU-Native AI Code Editor

```
    ██████╗ ██╗ ██████╗ ██╗  ██╗████████╗███╗   ██╗ ██████╗ ██╗    ██╗
    ██╔══██╗██║██╔════╝ ██║  ██║╚══██╔══╝████╗  ██║██╔═══██╗██║    ██║
    ██████╔╝██║██║  ███╗███████║   ██║   ██╔██╗ ██║██║   ██║██║ █╗ ██║
    ██╔══██╗██║██║   ██║██╔══██║   ██║   ██║╚██╗██║██║   ██║██║███╗██║
    ██║  ██║██║╚██████╔╝██║  ██║   ██║   ██║ ╚████║╚██████╔╝╚███╔███╔╝
    ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝

                    CUDA AI Assistant • Open Source
```

<p align="center">
  <b><a href="https://rightnowai.co">rightnowai.co</a> • <a href="https://twitter.com/rightnowai_co">@rightnowai_co</a> • <a href="https://discord.com/invite/sSJqgNnq6X">Discord</a></b>
</p>

[![Version](https://img.shields.io/badge/version-1.0.0-76B900?style=for-the-badge)](https://github.com/RightNow-AI/rightnow-cli/releases)
[![Python](https://img.shields.io/badge/python-3.9+-76B900?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-Proprietary-orange?style=for-the-badge)](LICENSE)

> **Open Source CLI Tool** - Want a full-featured CUDA development environment with code completion, integrated debugging, and advanced AI features?
> Try **[RightNow Code Editor](https://www.rightnowai.co/)** - Our complete IDE for GPU development.

**RightNow CLI** is an AI-powered CUDA development assistant that helps you write, optimize, and debug GPU code. Start FREE with no credit card required!

<p align="center">
  <img src="demo.png" alt="RightNow CLI Demo" width="800"/>
</p>

---

## Quick Install (30 seconds)

### Option 1: pip (Recommended)
```bash
pip install rightnow-cli
```

### Option 2: Quick Install Scripts

**Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/RightNow-AI/rightnow-cli/main/install.sh | bash
```

**Windows (PowerShell as Admin):**
```powershell
irm https://raw.githubusercontent.com/RightNow-AI/rightnow-cli/main/install.ps1 | iex
```

## Getting Started (2 minutes)

### 1. Get your FREE API key (30 seconds)
```bash
# Visit OpenRouter (no credit card needed!)
https://openrouter.ai

# Sign up with Google/GitHub for instant access
# Copy your API key from the dashboard
```

### 2. Start RightNow
```bash
rightnow
# Paste your API key when prompted (one-time setup)
```

### 3. Start coding!
```
You: Create a vector addition CUDA kernel

RightNow: [Creates optimized kernel with detailed explanations]
```

## What Can It Do?

### For Beginners
- **Learn CUDA**: "Explain how CUDA threads work"
- **Write Code**: "Create a simple matrix multiplication kernel"
- **Fix Errors**: "Help! My kernel crashes with error X"

### For Experts
- **Optimize**: "Optimize this kernel for memory coalescing"
- **Debug**: "Find the race condition in my code"
- **Analyze**: "Profile this kernel and suggest improvements"

## Key Features

### Start FREE
- No credit card required
- Free models included (Google Gemini, Meta Llama)
- Upgrade to premium models when needed

### Smart AI Agents
- **General Assistant**: Helps with any CUDA task
- **Optimizer**: Maximizes performance
- **Debugger**: Finds and fixes bugs
- **Analyzer**: Explains and improves code

### Powerful Tools
- Read and write CUDA files
- Analyze performance bottlenecks
- Generate optimized variants
- Monitor GPU status
- Execute bash commands

## Example Usage

### Basic Commands
```bash
# Start interactive mode
rightnow

# Inside RightNow:
/models     # List available AI models
/gpu        # Show GPU status
/clear      # Clear conversation
/help       # Show help
/quit       # Exit
```

### Example Conversations

**Creating a Kernel:**
```
You: Create a parallel reduction kernel

RightNow: [Writes complete kernel with shared memory optimization]
```

**Optimizing Code:**
```
You: Optimize my matrix multiplication for RTX 4090

RightNow: [Analyzes and provides optimized version with 10x speedup]
```

**Debugging:**
```
You: My kernel gives wrong results for large arrays

RightNow: [Identifies overflow issue and provides fix]
```

## Available Models

### Free Models (No cost!)
- **Google Gemini 2.0 Flash** - Fast and capable (default)
- **Meta Llama 3.2 3B** - Efficient for simple tasks

### Premium Models (Pay-per-use via OpenRouter)
- **GPT-4o** - Most capable overall
- **Claude 3.5 Sonnet** - Best for complex code
- **Gemini 1.5 Flash** - Fast with huge context

Switch models anytime with `/models` command!

## System Requirements

### Minimum
- Python 3.9+
- Any OS (Windows, Linux, macOS)
- Internet connection

### Recommended (for CUDA features)
- NVIDIA GPU (GTX 1650 or newer)
- CUDA Toolkit 11.0+
- 8GB+ RAM

## Troubleshooting

### "Command not found"
```bash
# Add to PATH (Linux/macOS)
export PATH="$HOME/.local/bin:$PATH"

# Or reinstall
pip uninstall rightnow-cli
pip install rightnow-cli --user
```

### "API key error"
```bash
# Get your free key at:
https://openrouter.ai

# Clear old key and re-enter:
rm -rf ~/.rightnow-cli
rightnow  # Will prompt for new key
```

### GPU not detected
```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA
nvcc --version

# RightNow works without GPU (CPU simulation mode)
```

## Documentation

- **Installation Guide**: [INSTALLATION.md](INSTALLATION.md)
- **GitHub**: [github.com/RightNow-AI/rightnow-cli](https://github.com/RightNow-AI/rightnow-cli)
- **Discord Community**: [discord.com/invite/sSJqgNnq6X](https://discord.com/invite/sSJqgNnq6X)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Proprietary Non-Commercial License - FREE for personal and educational use.
See [LICENSE](LICENSE) for details.

For commercial use, contact: licensing@rightnowai.co

## Support

- **Discord**: [Join our community](https://discord.com/invite/sSJqgNnq6X)
- **Twitter**: [@rightnowai_co](https://twitter.com/rightnowai_co)
- **Email**: jaber@rightnowai.co
- **Issues**: [GitHub Issues](https://github.com/RightNow-AI/rightnow-cli/issues)

---

<p align="center">
  <b>Built with <3 by the RightNow AI Team</b><br>
  <em>First <a href="https://www.rightnowai.co/">GPU Native AI Code Editor</a></em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-Python-76B900?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Powered%20by-NVIDIA-76B900?style=flat-square&logo=nvidia&logoColor=white"/>
  <img src="https://img.shields.io/badge/Status-Active-76B900?style=flat-square"/>
</p>
