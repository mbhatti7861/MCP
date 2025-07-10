#!/bin/bash
# Start script for LIVE Terraform MCP Demo with REAL server connection

echo "🚀 Starting LIVE Terraform MCP Demo"
echo "=================================="
echo "This connects to the REAL AWS Terraform MCP Server"
echo ""

# Set environment variables
export PATH="/Users/muhammadali/.local/bin:$PATH"
export PATH="$PATH:/Users/muhammadali/Library/Python/3.9/bin"

# Function to install prerequisites
install_prerequisites() {
    echo "🔧 Installing missing prerequisites..."
    
    # Install uv if needed
    if ! command -v uv &> /dev/null; then
        echo "📦 Installing uv package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="/Users/muhammadali/.local/bin:$PATH"
    fi
    
    # Install Python 3.10 if needed
    if ! command -v python3.10 &> /dev/null; then
        echo "🐍 Installing Python 3.10..."
        uv python install 3.10
    fi
    
    # Install Terraform if needed
    if ! command -v terraform &> /dev/null; then
        echo "🏗️ Installing Terraform..."
        if command -v brew &> /dev/null; then
            brew install terraform
        else
            echo "❌ Please install Homebrew first or install Terraform manually"
            exit 1
        fi
    fi
    
    # Install Checkov if needed
    if ! command -v checkov &> /dev/null; then
        echo "🔒 Installing Checkov..."
        pip3 install checkov
    fi
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check uv
if ! command -v uv &> /dev/null; then
    echo "⚠️ uv not found. Installing..."
    install_prerequisites
else
    echo "✅ uv: $(uv --version)"
fi

# Check Python 3.10
if ! command -v python3.10 &> /dev/null; then
    echo "⚠️ python3.10 not found. Installing..."
    install_prerequisites
else
    echo "✅ python3.10: $(python3.10 --version)"
fi

# Check terraform
if ! command -v terraform &> /dev/null; then
    echo "⚠️ terraform not found. Installing..."
    install_prerequisites
else
    echo "✅ terraform: $(terraform --version | head -1)"
fi

# Check checkov
if ! command -v checkov &> /dev/null; then
    echo "⚠️ checkov not found. Installing..."
    install_prerequisites
else
    echo "✅ checkov: $(checkov --version)"
fi

# Clone AWS MCP repository if not exists
if [ ! -d "mcp" ]; then
    echo "📂 Cloning AWS MCP repository..."
    git clone https://github.com/awslabs/mcp.git
fi

# Install MCP server if not already installed
echo "🔍 Checking MCP server installation..."
if ! python3.10 -c "import awslabs.terraform_mcp_server" &> /dev/null; then
    echo "📦 Installing AWS Terraform MCP Server..."
    cd mcp/src/terraform-mcp-server
    uv pip install -e . --system --python 3.10
    cd ../../..
    echo "✅ AWS Terraform MCP Server installed"
else
    echo "✅ AWS Terraform MCP Server: Already installed"
fi

# Install Python dependencies for demo
echo "🐍 Installing Python dependencies..."
python3.10 -m pip install Flask==2.3.3 requests==2.31.0

echo ""
echo "🎯 All prerequisites verified!"
echo ""

# Test MCP connection
echo "🔗 Testing MCP server connection..."
if python3.10 -c "
from mcp_client import run_async_function, get_live_best_practices
try:
    result = run_async_function(get_live_best_practices())
    print(f'✅ MCP connection successful! Content: {result[\"status\"]} ({len(result.get(\"content\", \"\"))} chars)')
except Exception as e:
    print(f'❌ MCP connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    echo "🎉 MCP server connection verified!"
else
    echo "❌ MCP server connection failed. Please check installation."
    exit 1
fi

echo ""

# Start the live demo application
echo "🚀 Starting LIVE Terraform MCP Demo Interface..."
echo "🌐 Demo Interface: http://localhost:5005"
echo "🔗 Connected to REAL AWS Terraform MCP Server"
echo ""
echo "LIVE Demo Features:"
echo "• 🤖 Real MCP Server Connection (stdio protocol)"
echo "• 📖 Live AWS Terraform Best Practices (87K+ characters)"
echo "• 🔍 Live AWS Provider Documentation Search"
echo "• 🔒 Live Security Scanning with Checkov"
echo "• ⚡ Live Terraform Workflow Execution"
echo ""
echo "🎯 This is NOT mock data - real AI-powered responses!"
echo ""
echo "Press Ctrl+C to stop the demo"
echo ""

# Start Flask app with Python 3.10
python3.10 terraform_demo_live.py