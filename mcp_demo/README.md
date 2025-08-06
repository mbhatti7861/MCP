# DevGenius MCP Integration Demo

Complete implementation for integrating aws-diagram-mcp-server with DevGenius AWS Solution Builder as a replacement for the built-in generate_arch_widget.

## 📁 Files Overview

### Core Integration Files
- **`devgenius_mcp_arch_widget.py`** - Drop-in replacement for `generate_arch_widget.py`
- **`mcp_client.py`** - MCP client for communication with aws-diagram-mcp-server  
- **`mcp_config.json`** - MCP server configuration
- **`requirements.txt`** - Python dependencies

### Automation & Testing
- **`integrate_mcp.sh`** - Automated integration script *(generated)*
- **`test_integration.py`** - Comprehensive test suite *(generated)*
- **`integration_guide.py`** - Generates automation scripts and guides
- **`demo_without_server.py`** - Demo showing integration flow (works without full MCP server)

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install UV package manager (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install GraphViz (required for diagram generation)
brew install graphviz  # macOS
# or
sudo apt-get install graphviz  # Ubuntu
```

### 2. Install MCP Server
```bash
cd ../mcp/src/aws-diagram-mcp-server
uv pip install -e .
# or if UV not available:
# pip install diagrams boto3 pydantic
```

### 3. Run Automated Integration
```bash
# Make sure you're in the MCP root directory
cd ..
./mcp_demo/integrate_mcp.sh
```

### 4. Test Integration
```bash
# Run comprehensive tests
python3 mcp_demo/test_integration.py

# Or run demo without full server
python3 mcp_demo/demo_without_server.py
```

### 5. Start DevGenius with MCP
```bash
cd sample-devgenius-aws-solution-builder/chatbot
streamlit run agent.py --server.port 8501
```

## 🏗️ Architecture

```
DevGenius Streamlit App
├── agent.py (main app)
│   ├── Tab: "Build a solution"
│   └── Tab: "Modify existing architecture"
│       └── generate_arch(messages) ← MCP Integration Point
│
└── MCP Integration Layer
    ├── devgenius_mcp_arch_widget.py
    │   ├── DevGeniusMCPArchWidget class
    │   └── generate_arch() ← Drop-in replacement
    │
    ├── mcp_client.py  
    │   └── MCPDiagramClient ← JSON-RPC communication
    │
    └── aws-diagram-mcp-server
        ├── Python Diagrams Library
        └── GraphViz Engine
```

## 🔄 Integration Process

### Before (Original DevGenius):
1. User describes solution → DevGenius/Bedrock generates solution
2. User clicks "Generate Architecture" → Bedrock generates draw.io XML  
3. XML converted to HTML → Displayed in embedded draw.io viewer

### After (MCP Integration):
1. User describes solution → DevGenius/Bedrock generates solution *(same)*
2. User clicks "Generate Architecture (MCP)" → MCP server generates Python code
3. Python code executed → PNG diagram generated → Displayed as image

## 🎯 Key Features

### ✅ What Works
- **Drop-in Replacement**: Same interface as original `generate_arch()`
- **Session State Compatible**: Maintains DevGenius conversation flow
- **Component Detection**: Automatically identifies AWS services from solution text
- **Error Handling**: Comprehensive error handling and troubleshooting
- **Download Support**: PNG diagram download functionality
- **Code Generation**: Shows underlying Python diagrams code

### 🚧 What's Different
- **Output Format**: PNG images instead of interactive draw.io diagrams
- **Generation Method**: Code-based instead of AI-generated XML
- **Dependencies**: Requires GraphViz and MCP server installation
- **Performance**: May be faster (no LLM overhead) but requires local processing

## 🧪 Testing Results

### ✅ Tests That Pass
- MCP client initialization and configuration loading
- DevGenius message format parsing and component extraction
- Request formatting for MCP server communication
- Widget UI integration (maintains same interface)

### ⏳ Tests Requiring Full Setup
- Actual MCP server communication
- Real diagram generation with GraphViz
- End-to-end integration in DevGenius application

## 📋 Manual Integration Steps

If the automated script doesn't work, follow these manual steps:

1. **Backup original files:**
   ```bash
   cp sample-devgenius-aws-solution-builder/chatbot/generate_arch_widget.py \
      sample-devgenius-aws-solution-builder/chatbot/generate_arch_widget.py.backup
   ```

2. **Copy MCP files:**
   ```bash
   cp mcp_demo/{mcp_client.py,mcp_config.json,devgenius_mcp_arch_widget.py} \
      sample-devgenius-aws-solution-builder/chatbot/
   ```

3. **Update imports in agent.py:**
   ```python
   # Replace line 15:
   # OLD: from generate_arch_widget import generate_arch  
   # NEW: from devgenius_mcp_arch_widget import generate_arch
   ```

4. **Add dependencies to requirements.txt:**
   ```
   # MCP Integration
   asyncio-subprocess>=0.1.0
   ```

## 🔧 Troubleshooting

### Common Issues

1. **"MCP server not starting"**
   - Check GraphViz installation: `dot -V`
   - Verify MCP server: `python -m aws_diagram_mcp_server --help`
   - Check Python environment: `python -c "from diagrams import Diagram"`

2. **"Import errors"**
   - Ensure all files are in the correct directory
   - Check Python path and virtual environment
   - Verify Streamlit installation

3. **"Diagram generation fails"**
   - Check MCP server logs for errors
   - Verify GraphViz PATH configuration  
   - Test with simpler solution descriptions

### Quick Fixes
- Restart Streamlit application
- Clear browser cache
- Check browser console for JavaScript errors
- Try with minimal solution requirements

## 🎉 Success Indicators

You'll know the integration is working when:
- ✅ DevGenius loads without import errors
- ✅ Architecture tab shows "Generate Architecture (MCP)" option  
- ✅ Checkbox generates PNG diagrams instead of draw.io XML
- ✅ Download button provides PNG files
- ✅ Expandable sections show Python diagrams code

## 🚀 Next Steps

1. **Enhanced Components**: Add more AWS service mappings
2. **Styling Options**: Custom diagram themes and layouts  
3. **Multiple Formats**: Support SVG, PDF output formats
4. **Caching**: Cache generated diagrams for performance
5. **Template Library**: Pre-built architecture patterns

---

**Note**: This is a basic implementation for testing purposes. For production use, consider additional error handling, logging, and security measures.