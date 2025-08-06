#!/bin/bash
# DevGenius MCP Integration Script
# Automates the integration of MCP architecture widget

echo "🚀 DevGenius MCP Integration Script"
echo "=================================="

# Check if we're in the right directory
if [ ! -d "sample-devgenius-aws-solution-builder" ] || [ ! -d "mcp_demo" ]; then
    echo "❌ Error: Please run this script from the MCP directory containing both folders"
    exit 1
fi

# 1. Backup original file
echo "📁 Backing up original generate_arch_widget.py..."
cp sample-devgenius-aws-solution-builder/chatbot/generate_arch_widget.py \
   sample-devgenius-aws-solution-builder/chatbot/generate_arch_widget.py.backup

# 2. Copy MCP files
echo "📋 Copying MCP integration files..."
cp mcp_demo/mcp_client.py sample-devgenius-aws-solution-builder/chatbot/
cp mcp_demo/mcp_config.json sample-devgenius-aws-solution-builder/chatbot/
cp mcp_demo/devgenius_mcp_arch_widget.py sample-devgenius-aws-solution-builder/chatbot/

# 3. Update imports in agent.py
echo "🔄 Updating imports in agent.py..."
sed -i.bak 's/from generate_arch_widget import generate_arch/from devgenius_mcp_arch_widget import generate_arch/' \
    sample-devgenius-aws-solution-builder/chatbot/agent.py

# 4. Add MCP dependencies to requirements.txt
echo "📦 Adding MCP dependencies to requirements.txt..."
echo "" >> sample-devgenius-aws-solution-builder/chatbot/requirements.txt
echo "# MCP Integration Dependencies" >> sample-devgenius-aws-solution-builder/chatbot/requirements.txt
echo "asyncio-subprocess>=0.1.0" >> sample-devgenius-aws-solution-builder/chatbot/requirements.txt

echo "✅ Integration files copied successfully!"
echo ""
echo "⚠️  MANUAL STEPS REQUIRED:"
echo "1. Install AWS Diagram MCP Server:"
echo "   cd mcp/src/aws-diagram-mcp-server && uv pip install -e ."
echo ""
echo "2. Install GraphViz:"
echo "   brew install graphviz  # macOS"
echo "   sudo apt-get install graphviz  # Ubuntu"
echo ""
echo "3. Test the integration:"
echo "   cd sample-devgenius-aws-solution-builder/chatbot"
echo "   python devgenius_mcp_arch_widget.py"
echo ""
echo "4. Run DevGenius:"
echo "   streamlit run agent.py --server.port 8501"
echo ""
echo "🎉 Integration preparation complete!"
