# MCP Setup Guide for DevGenius Integration

Complete step-by-step guide to integrate aws-diagram-mcp-server with DevGenius AWS Solution Builder.

## 📋 Overview

This guide walks you through replacing DevGenius's AI-generated draw.io diagrams with code-generated AWS architecture diagrams using the MCP (Model Context Protocol) server.

**Before**: DevGenius → Bedrock → XML → draw.io viewer  
**After**: DevGenius → MCP Server → Python Code → GraphViz → PNG Image

---

## 📁 File Reference Guide

### 🔧 Core Integration Files

#### `devgenius_mcp_arch_widget.py`
**Purpose**: Drop-in replacement for DevGenius's `generate_arch_widget.py`  
**What it does**:
- Maintains exact same UI interface (checkbox, retry button)
- Extracts solution requirements from DevGenius conversation history
- Identifies AWS components from solution text
- Communicates with MCP server to generate diagrams
- Displays PNG diagrams instead of draw.io XML
- Provides download functionality for generated diagrams

**Key Functions**:
- `generate_arch(arch_messages)` - Main function that replaces the original
- `_extract_solution_from_messages()` - Parses DevGenius conversation format
- `_parse_aws_components()` - Identifies AWS services from text
- `_generate_and_display_architecture()` - Handles MCP communication

#### `mcp_client.py` 
**Purpose**: Python client for communicating with aws-diagram-mcp-server  
**What it does**:
- Manages MCP server subprocess lifecycle (start/stop)
- Handles JSON-RPC 2.0 protocol communication
- Sends diagram generation requests
- Processes MCP server responses
- Provides error handling and retry logic

**Key Functions**:
- `start_server()` - Launches MCP server subprocess
- `send_request()` - JSON-RPC communication with server
- `generate_aws_diagram()` - Main diagram generation method
- `stop_server()` - Clean shutdown of MCP server

#### `mcp_config.json`
**Purpose**: Configuration file for MCP server connection  
**What it contains**:
```json
{
  "mcpServers": {
    "aws-diagram": {
      "command": "python",              // How to launch server
      "args": ["-m", "aws_diagram_mcp_server"], // Server module
      "env": {
        "PYTHONPATH": "."              // Environment variables
      }
    }
  }
}
```

#### `requirements.txt`
**Purpose**: Python dependencies for MCP integration  
**Contains**:
- `asyncio-subprocess` - For async subprocess management
- `json-rpc` - JSON-RPC protocol support
- `streamlit` - UI framework (DevGenius requirement)
- `requests` - HTTP client for communication
- `Pillow` - Image processing

### 🤖 Automation Files

#### `integrate_mcp.sh` *(Generated)*
**Purpose**: Automated integration script  
**What it does**:
- Backs up original DevGenius files
- Copies MCP files to DevGenius directory
- Updates import statements in `agent.py`
- Adds dependencies to requirements.txt
- Provides manual steps checklist

#### `test_integration.py` *(Generated)*
**Purpose**: Comprehensive test suite  
**What it tests**:
- MCP server installation and accessibility
- GraphViz installation
- Python dependencies
- File integration correctness
- Widget functionality
- End-to-end communication

#### `integration_guide.py`
**Purpose**: Script generator for automation tools  
**What it creates**:
- Generates `integrate_mcp.sh` script
- Creates `test_integration.py` test suite
- Displays step-by-step integration instructions

### 🧪 Demo and Testing Files

#### `demo_without_server.py`
**Purpose**: Demonstration without full MCP server installation  
**What it shows**:
- Complete integration flow simulation
- Component parsing examples
- Mock MCP responses
- DevGenius message format handling

#### `README.md`
**Purpose**: Complete documentation  
**Contains**:
- Architecture overview
- Feature descriptions
- Troubleshooting guide
- Quick start instructions

---

## 🚀 Step-by-Step Setup Guide

### Step 1: Verify Your Environment

**Check your directory structure**:
```bash
/Users/muhammadali/MCP/
├── mcp/                                    # MCP repo (cloned)
│   └── src/aws-diagram-mcp-server/        # The actual MCP server
├── sample-devgenius-aws-solution-builder/ # DevGenius repo
│   └── chatbot/                           # DevGenius application
└── mcp_demo/                              # Integration files (created)
```

**Verify you have both repos**:
```bash
ls -la
# Should show: mcp/, sample-devgenius-aws-solution-builder/, mcp_demo/
```

### Step 2: Install Prerequisites

#### Install UV Package Manager (Recommended)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart terminal or:
source ~/.bashrc  # or ~/.zshrc
```

#### Install GraphViz (Required for diagram generation)
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Verify installation
dot -V
# Should show GraphViz version info
```

#### Verify Python Version
```bash
python3 --version
# Should be Python 3.10+ (3.9 minimum)
```

### Step 3: Install AWS Diagram MCP Server

```bash
# Navigate to MCP server directory
cd mcp/src/aws-diagram-mcp-server

# Install with UV (recommended)
uv pip install -e .

# OR install with regular pip if UV not available
python3 -m pip install -e .

# OR install dependencies manually if above fails
python3 -m pip install diagrams boto3 pydantic mcp
```

**Test MCP server installation**:
```bash
# Try to run the server (should show help or start)
python3 -m aws_diagram_mcp_server --help

# Test diagrams library
python3 -c "from diagrams import Diagram; print('Diagrams package working!')"
```

### Step 4: Run Integration Tests

```bash
# Go back to main directory
cd ../../..  # Should be in /Users/muhammadali/MCP

# Run basic demo (works without full server)
python3 mcp_demo/demo_without_server.py

# If you see successful tests, continue to next step
```

### Step 5: Automated Integration

```bash
# Run the automated integration script
./mcp_demo/integrate_mcp.sh

# This script will:
# 1. Backup original generate_arch_widget.py
# 2. Copy MCP files to DevGenius chatbot directory
# 3. Update imports in agent.py
# 4. Add dependencies to requirements.txt
```

**Manual Integration (if script fails)**:
```bash
# 1. Backup original
cp sample-devgenius-aws-solution-builder/chatbot/generate_arch_widget.py \
   sample-devgenius-aws-solution-builder/chatbot/generate_arch_widget.py.backup

# 2. Copy MCP files
cp mcp_demo/mcp_client.py sample-devgenius-aws-solution-builder/chatbot/
cp mcp_demo/mcp_config.json sample-devgenius-aws-solution-builder/chatbot/
cp mcp_demo/devgenius_mcp_arch_widget.py sample-devgenius-aws-solution-builder/chatbot/

# 3. Edit agent.py - Change line 15:
# OLD: from generate_arch_widget import generate_arch
# NEW: from devgenius_mcp_arch_widget import generate_arch
```

### Step 6: Install DevGenius Dependencies

```bash
cd sample-devgenius-aws-solution-builder/chatbot

# Install existing DevGenius requirements
pip3 install -r requirements.txt

# Install additional MCP dependencies
pip3 install asyncio-subprocess
```

### Step 7: Run Comprehensive Tests

```bash
# Go back to main directory
cd ../..

# Run full integration test suite
python3 mcp_demo/test_integration.py
```

**Expected test results**:
- ✅ MCP Server Installation: PASS
- ✅ GraphViz Installation: PASS  
- ✅ Python Dependencies: PASS
- ✅ File Integration: PASS
- ✅ MCP Widget: PASS

### Step 8: Test MCP Widget Standalone

```bash
cd sample-devgenius-aws-solution-builder/chatbot

# Test the MCP widget independently
python3 devgenius_mcp_arch_widget.py
```

**What you should see**:
- Streamlit app launches in browser
- "Load Test DevGenius Session" button
- After loading, architecture generation checkbox
- MCP-powered diagram generation

### Step 9: Launch DevGenius with MCP Integration

```bash
# Make sure you're in the chatbot directory
cd sample-devgenius-aws-solution-builder/chatbot

# Start DevGenius application
streamlit run agent.py --server.port 8501
```

**Access the application**:
- Open browser to `http://localhost:8501`
- Login with your credentials
- Navigate to solution building
- Look for "Generate Architecture (MCP)" option

---

## ✅ Verification Checklist

### Before Integration:
- [ ] MCP repo cloned under `mcp/`
- [ ] DevGenius repo under `sample-devgenius-aws-solution-builder/`
- [ ] Integration files in `mcp_demo/`
- [ ] UV package manager installed
- [ ] GraphViz installed and accessible
- [ ] Python 3.10+ available

### After MCP Server Installation:
- [ ] `python3 -m aws_diagram_mcp_server --help` works
- [ ] `python3 -c "from diagrams import Diagram"` works
- [ ] `dot -V` shows GraphViz version

### After Integration:
- [ ] Files copied to DevGenius chatbot directory
- [ ] `agent.py` import updated
- [ ] `devgenius_mcp_arch_widget.py` runs standalone
- [ ] All integration tests pass
- [ ] DevGenius launches without import errors

### During DevGenius Usage:
- [ ] Architecture tab shows "Generate Architecture (MCP)" 
- [ ] Checkbox generates PNG images (not draw.io XML)
- [ ] Download button provides PNG files
- [ ] Expandable sections show Python diagrams code
- [ ] No JavaScript errors in browser console

---

## 🔧 Troubleshooting

### Issue: "command not found: uv"
**Solution**: Install UV package manager or use pip instead
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# OR use pip for all installations
```

### Issue: "dot command not found"
**Solution**: Install GraphViz properly
```bash
# macOS
brew install graphviz
# Ubuntu  
sudo apt-get install graphviz
# Restart terminal after installation
```

### Issue: "No module named 'aws_diagram_mcp_server'"
**Solution**: Install MCP server properly
```bash
cd mcp/src/aws-diagram-mcp-server
# Try different installation methods:
uv pip install -e .
# OR
python3 -m pip install -e .
# OR
python3 -m pip install diagrams boto3 pydantic
```

### Issue: "MCP server not starting"
**Solution**: Check server path and permissions
```bash
# Verify server location
ls -la mcp/src/aws-diagram-mcp-server/
# Check Python path
which python3
# Test server directly
cd mcp/src/aws-diagram-mcp-server
python3 -m aws_diagram_mcp_server
```

### Issue: DevGenius import errors
**Solution**: Check file paths and imports
```bash
# Verify files copied correctly
ls -la sample-devgenius-aws-solution-builder/chatbot/
# Should show: devgenius_mcp_arch_widget.py, mcp_client.py, mcp_config.json

# Check agent.py import was updated
grep "devgenius_mcp_arch_widget" sample-devgenius-aws-solution-builder/chatbot/agent.py
```

### Issue: Streamlit widget errors
**Solution**: Check Streamlit and dependencies
```bash
# Install/upgrade Streamlit
pip3 install --upgrade streamlit
# Check for missing dependencies
pip3 install requests pillow
```

---

## 🎯 What Success Looks Like

### 1. **In DevGenius Interface**:
- Architecture generation checkbox shows "Generate Architecture (MCP)"
- Clicking generates PNG diagrams instead of draw.io XML
- Diagrams show actual AWS service icons
- Download button provides PNG files
- Expandable section shows Python diagrams code

### 2. **In Generated Diagrams**:
- Clean, professional AWS architecture layouts
- Proper AWS service icons (Lambda, API Gateway, DynamoDB, etc.)
- Clear connections and data flow arrows
- Consistent styling and spacing

### 3. **In System Behavior**:
- Fast diagram generation (no AI overhead)
- Reliable, deterministic output
- No dependency on Bedrock/AI services for diagrams
- Offline capability (once components are identified)

---

## 🚀 Advanced Configuration

### Custom MCP Server Settings

Edit `mcp_config.json` to customize:
```json
{
  "mcpServers": {
    "aws-diagram": {
      "command": "python3",           // Specific Python version
      "args": ["-m", "aws_diagram_mcp_server", "--verbose"], // Add flags
      "env": {
        "PYTHONPATH": ".",
        "GRAPHVIZ_DOT": "/usr/local/bin/dot"  // Specific GraphViz path
      }
    }
  }
}
```

### Enhanced Component Detection

Modify `devgenius_mcp_arch_widget.py` to add more AWS services:
```python
aws_services_map = {
    # Add new services
    'step functions': 'StepFunctions',
    'eventbridge': 'EventBridge',
    'app runner': 'AppRunner',
    # ... add more as needed
}
```

---

## 📚 Additional Resources

- **MCP Documentation**: https://awslabs.github.io/mcp/
- **Python Diagrams**: https://diagrams.mingrammer.com/
- **GraphViz Documentation**: https://graphviz.org/documentation/
- **DevGenius Original**: https://github.com/aws-samples/sample-devgenius-aws-solution-builder

---

**🎉 You're all set! Your DevGenius application now uses the MCP server for generating architecture diagrams instead of AI-generated XML.**