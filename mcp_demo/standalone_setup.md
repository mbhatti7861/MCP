# Standalone MCP Setup (No MCP Repo Required)

Setup MCP integration for DevGenius without cloning the full MCP repository.

## 🚀 Quick Setup Options

### Option 1: Package Installation (Recommended)
```bash
# Install the MCP server package directly
pip install awslabs.aws-diagram-mcp-server

# Or with UV
uv add awslabs.aws-diagram-mcp-server
```

### Option 2: Lightweight Direct Generation
```bash
# Install only core dependencies
pip install diagrams>=0.24.4 boto3 pydantic graphviz

# Use the lightweight client (included in mcp_demo files)
cp mcp_client_lightweight.py mcp_client.py
```

## 📁 Files You Need

Copy these files to your DevGenius chatbot directory:

```
DevGenius/chatbot/
├── devgenius_mcp_arch_widget.py  # Main widget replacement
├── mcp_client.py                 # OR mcp_client_lightweight.py
├── mcp_config.json              # Configuration
└── requirements.txt             # Add: diagrams>=0.24.4
```

## 🔧 Integration Steps

1. **Install GraphViz:**
   ```bash
   brew install graphviz  # macOS
   sudo apt-get install graphviz  # Ubuntu
   ```

2. **Install Python dependencies:**
   ```bash
   pip install diagrams boto3 pydantic
   ```

3. **Update DevGenius imports:**
   ```python
   # In agent.py, change line 15:
   # OLD: from generate_arch_widget import generate_arch
   # NEW: from devgenius_mcp_arch_widget import generate_arch
   ```

4. **Test the integration:**
   ```bash
   python devgenius_mcp_arch_widget.py  # Standalone test
   streamlit run agent.py --server.port 8501  # Full DevGenius
   ```

## ✅ Verification

- Architecture generation shows "Generate Architecture (MCP)" 
- PNG diagrams generated instead of draw.io XML
- Download button provides PNG files
- No import errors in DevGenius

## 🎯 Benefits of Standalone Setup

- ✅ No need to clone 300MB+ MCP repository
- ✅ Faster setup and deployment
- ✅ Same functionality as full MCP integration
- ✅ Easier to include in your own repository
- ✅ No external repository dependencies