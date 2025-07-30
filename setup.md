# AWS Diagram MCP Server Integration with DevGenius Solution Builder

## Overview
This guide shows how to integrate the AWS Diagram MCP Server with your modified DevGenius AWS Solution Builder, replacing the existing `generate_arch_widget` with MCP server-powered diagram generation. The MCP server provides more reliable, code-based diagram generation compared to AI-generated draw.io XML.

## Prerequisites

### 1. Install Required Tools

#### Install UV Package Manager
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: Using pip
pip install uv
```

#### Install Python 3.10
```bash
# Using uv to install Python 3.10
uv python install 3.10

# Verify installation
python3.10 --version
```

#### Install GraphViz
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows
# Download from: https://graphviz.org/download/
# Or use chocolatey: choco install graphviz
```

## Installation Options

### Option 1: Direct Installation with UV

1. **Clone the repository:**
```bash
git clone https://github.com/awslabs/mcp.git
cd mcp/src/aws-diagram-mcp-server
```

2. **Install the package:**
```bash
uv pip install .
```

3. **For development (with dev dependencies):**
```bash
uv pip install -e ".[dev]"
```

### Option 2: Docker Installation

1. **Build the Docker image:**
```bash
docker build -t aws-diagram-mcp-server .
```

2. **Run the container:**
```bash
docker run -p 8000:8000 aws-diagram-mcp-server
```

### Option 3: VS Code/Cursor Integration

1. **Install the MCP extension in VS Code/Cursor**

2. **Add to your MCP configuration:**
```json
{
  "mcpServers": {
    "aws-diagram": {
      "command": "uv",
      "args": ["--directory", "/path/to/aws-diagram-mcp-server", "run", "aws-diagram-mcp-server"]
    }
  }
}
```

## Configuration

### MCP Client Setup

Add the following to your MCP client configuration:

```json
{
  "mcpServers": {
    "aws-diagram": {
      "command": "python",
      "args": ["-m", "aws_diagram_mcp_server"]
    }
  }
}
```

## Testing the Setup

### 1. Basic Test
Create a simple test diagram:

```python
from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.network import APIGateway

with Diagram("Serverless Application", show=False):
    api = APIGateway("API Gateway")
    function = Lambda("Function")
    database = Dynamodb("DynamoDB")

    api >> function >> database
```

### 2. Run Tests (Development)
```bash
# Run all tests
./run_tests.sh

# Or run with pytest directly
pytest
```

### 3. Verify MCP Server
```bash
# Test the MCP server directly
python -m aws_diagram_mcp_server
```

## Usage Examples

### AWS Architecture Diagram
```python
from diagrams import Diagram
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB, VPC

with Diagram("Web Service", show=False):
    vpc = VPC("VPC")
    lb = ELB("Load Balancer")
    web_servers = [EC2("Web Server 1"), EC2("Web Server 2")]
    database = RDS("Database")
    
    vpc >> lb >> web_servers >> database
```

### Sequence Diagram
```python
from diagrams import Diagram
from diagrams.generic.blank import Blank

with Diagram("User Authentication Flow", show=False):
    user = Blank("User")
    api = Blank("API Gateway")
    auth = Blank("Auth Service")
    db = Blank("Database")
    
    user >> api >> auth >> db
```

## Troubleshooting

### Common Issues

1. **GraphViz not found:**
   - Ensure GraphViz is installed and in your PATH
   - Restart your terminal after installation

2. **Python version conflicts:**
   - Use `uv python pin 3.10` to pin Python version
   - Verify with `python --version`

3. **Permission errors:**
   - Use virtual environments: `uv venv && source .venv/bin/activate`

4. **MCP connection issues:**
   - Check your MCP client configuration
   - Verify the server path and arguments

### Verification Steps

1. **Check installations:**
```bash
uv --version
python3.10 --version
dot -V  # GraphViz
```

2. **Test diagram generation:**
```bash
python -c "from diagrams import Diagram; print('Diagrams package working')"
```

3. **Test MCP server:**
```bash
python -m aws_diagram_mcp_server --help
```

## DevGenius Integration Setup

### 1. MCP Server Deployment

#### Option A: Local Development Server
```bash
# In your DevGenius project directory
cd /path/to/your/devgenius-project
mkdir mcp-services
cd mcp-services

# Clone and setup AWS Diagram MCP Server
git clone https://github.com/awslabs/mcp.git
cd mcp/src/aws-diagram-mcp-server

# Install with UV
uv pip install -e .

# Test the server
python -m aws_diagram_mcp_server
```

#### Option B: Docker Container
```bash
# Build MCP server container
docker build -t aws-diagram-mcp-server .

# Run as service
docker run -d -p 8080:8080 --name mcp-diagram-server aws-diagram-mcp-server
```

### 2. DevGenius Widget Integration

#### Replace generate_arch_widget.py

Create a new MCP-powered widget:

```python
# chatbot/mcp_arch_widget.py
import streamlit as st
import requests
import json
from typing import Dict, Any
import logging

class MCPArchitectureGenerator:
    def __init__(self, mcp_server_url: str = "http://localhost:8080"):
        self.mcp_server_url = mcp_server_url
        self.logger = logging.getLogger(__name__)
    
    def generate_architecture_diagram(self, requirements: str, architecture_type: str = "aws") -> Dict[str, Any]:
        """Generate architecture diagram using MCP server"""
        try:
            payload = {
                "method": "generate_diagram",
                "params": {
                    "requirements": requirements,
                    "diagram_type": architecture_type,
                    "format": "png",
                    "include_labels": True
                }
            }
            
            response = requests.post(
                f"{self.mcp_server_url}/mcp/call",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"MCP server error: {response.status_code}")
                return {"error": f"Server error: {response.status_code}"}
                
        except Exception as e:
            self.logger.error(f"Failed to generate diagram: {str(e)}")
            return {"error": str(e)}
    
    def render_widget(self):
        """Render the Streamlit widget"""
        st.subheader("🏗️ Architecture Diagram Generation")
        
        if st.checkbox("Generate Architecture Diagram", key="generate_arch"):
            with st.spinner("Generating architecture diagram..."):
                # Get requirements from session state or user input
                requirements = st.session_state.get('current_solution', '')
                
                if not requirements:
                    st.warning("No solution requirements found. Please complete the solution generation first.")
                    return
                
                # Generate diagram
                result = self.generate_architecture_diagram(requirements)
                
                if "error" in result:
                    st.error(f"Failed to generate diagram: {result['error']}")
                else:
                    # Display generated diagram
                    if "diagram_url" in result:
                        st.image(result["diagram_url"], caption="Generated Architecture Diagram")
                    
                    if "diagram_code" in result:
                        with st.expander("View Diagram Code"):
                            st.code(result["diagram_code"], language="python")
                    
                    # Provide download option
                    if "diagram_data" in result:
                        st.download_button(
                            label="Download Diagram",
                            data=result["diagram_data"],
                            file_name="architecture_diagram.png",
                            mime="image/png"
                        )

# Usage in main app
def show_mcp_architecture_widget():
    generator = MCPArchitectureGenerator()
    generator.render_widget()
```

#### Update main Streamlit app

In your main DevGenius app file:

```python
# Replace the old import
# from chatbot.generate_arch_widget import show_architecture_generation
from chatbot.mcp_arch_widget import show_mcp_architecture_widget

# Replace the function call
# show_architecture_generation()
show_mcp_architecture_widget()
```

### 3. Configuration Setup

#### Environment Variables
```bash
# Add to your .env file
MCP_SERVER_URL=http://localhost:8080
MCP_DIAGRAM_FORMAT=png
MCP_TIMEOUT=30
```

#### Configuration File
```json
// config/mcp_config.json
{
  "mcp_server": {
    "url": "http://localhost:8080",
    "timeout": 30,
    "retry_attempts": 3
  },
  "diagram_settings": {
    "format": "png",
    "include_labels": true,
    "show_icons": true,
    "direction": "TB"
  }
}
```

### 4. Backend API Integration

#### Create MCP Service Handler

```python
# services/mcp_service.py
import requests
import json
from typing import Dict, Any, Optional
import logging

class MCPDiagramService:
    def __init__(self, server_url: str, api_key: Optional[str] = None):
        self.server_url = server_url
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
    
    def create_aws_diagram(self, solution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create AWS architecture diagram from solution data"""
        
        # Transform solution data to diagram requirements
        diagram_prompt = self._build_diagram_prompt(solution_data)
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "generate_aws_diagram",
            "params": {
                "requirements": diagram_prompt,
                "components": solution_data.get("components", []),
                "connections": solution_data.get("connections", []),
                "format": "png"
            }
        }
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.post(
                f"{self.server_url}/jsonrpc",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"MCP service error: {str(e)}")
            return {"error": str(e)}
    
    def _build_diagram_prompt(self, solution_data: Dict[str, Any]) -> str:
        """Build diagram generation prompt from solution data"""
        components = solution_data.get("components", [])
        description = solution_data.get("description", "")
        
        prompt = f"""
        Generate an AWS architecture diagram for: {description}
        
        Required components:
        {chr(10).join(f"- {comp}" for comp in components)}
        
        Architecture requirements:
        - Follow AWS Well-Architected principles
        - Include proper security boundaries
        - Show data flow connections
        - Use appropriate AWS service icons
        """
        
        return prompt
```

### 5. Testing and Verification

#### Test MCP Server Connection
```python
# test_mcp_integration.py
import requests
import json

def test_mcp_server():
    url = "http://localhost:8080"
    
    # Test health check
    try:
        response = requests.get(f"{url}/health")
        print(f"Health check: {response.status_code}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test diagram generation
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "generate_diagram",
        "params": {
            "requirements": "Create a simple web application with API Gateway, Lambda, and DynamoDB",
            "format": "png"
        }
    }
    
    try:
        response = requests.post(f"{url}/jsonrpc", json=payload)
        result = response.json()
        print(f"Diagram generation: {result}")
    except Exception as e:
        print(f"Diagram generation failed: {e}")

if __name__ == "__main__":
    test_mcp_server()
```

#### Run Integration Tests
```bash
# Test MCP server
python test_mcp_integration.py

# Test DevGenius integration
cd /path/to/devgenius
streamlit run app.py
```

### 6. Production Deployment

#### Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  devgenius-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - MCP_SERVER_URL=http://mcp-server:8080
    depends_on:
      - mcp-server
  
  mcp-server:
    build: ./mcp-services/mcp/src/aws-diagram-mcp-server
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
```

#### Kubernetes Deployment
```yaml
# k8s/mcp-server-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-diagram-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mcp-diagram-server
  template:
    metadata:
      labels:
        app: mcp-diagram-server
    spec:
      containers:
      - name: mcp-server
        image: aws-diagram-mcp-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: PORT
          value: "8080"
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-diagram-service
spec:
  selector:
    app: mcp-diagram-server
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP
```

## Migration Steps from Original Widget

### 1. Backup Current Implementation
```bash
cp chatbot/generate_arch_widget.py chatbot/generate_arch_widget.py.backup
```

### 2. Update Dependencies
```bash
# Add to requirements.txt
requests>=2.28.0
python-multipart>=0.0.5
```

### 3. Update Configuration
- Replace Bedrock model calls with MCP server calls
- Update error handling to match MCP response format
- Maintain existing UI/UX patterns

### 4. Data Flow Changes
- **Before**: Streamlit → Bedrock → XML → HTML
- **After**: Streamlit → MCP Server → Python Diagrams → PNG/SVG

## Benefits of MCP Integration

1. **Reliability**: Code-based diagrams vs AI-generated XML
2. **Consistency**: Standardized AWS iconography and layouts
3. **Performance**: Faster generation without LLM overhead
4. **Extensibility**: Easy to add new diagram types
5. **Version Control**: Diagram code can be stored and versioned

## Troubleshooting

### Common Issues
1. **MCP Server Connection**: Check server URL and port
2. **Diagram Generation Errors**: Verify GraphViz installation
3. **Performance Issues**: Consider MCP server scaling
4. **UI Integration**: Test Streamlit widget rendering

For more examples and advanced usage, refer to the [diagrams documentation](https://diagrams.mingrammer.com/).