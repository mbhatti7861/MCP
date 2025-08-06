#!/usr/bin/env python3
"""
MCP Client for AWS Diagram Server Integration
Basic implementation to connect to aws-diagram-mcp-server
"""

import json
import asyncio
import subprocess
import sys
import os
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPDiagramClient:
    """Client for connecting to AWS Diagram MCP Server"""
    
    def __init__(self, config_path: str = "mcp_config.json"):
        """Initialize MCP client with configuration"""
        self.config_path = config_path
        self.server_config = self._load_config()
        self.server_process = None
        
    def _load_config(self) -> Dict[str, Any]:
        """Load MCP server configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                return config['mcpServers']['aws-diagram']
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {
                "command": "python",
                "args": ["-m", "aws_diagram_mcp_server"],
                "env": {"PYTHONPATH": "."}
            }
    
    def start_server(self) -> bool:
        """Start the MCP server process"""
        try:
            cmd = [self.server_config['command']] + self.server_config['args']
            env = self.server_config.get('env', {})
            
            logger.info(f"Starting MCP server: {' '.join(cmd)}")
            
            # Merge environment variables
            merged_env = {**os.environ, **env}
            
            self.server_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=merged_env
            )
            
            # Give server time to start
            import time
            time.sleep(1)
            
            if self.server_process.poll() is None:
                logger.info("MCP server started successfully")
                return True
            else:
                logger.error("MCP server failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the MCP server process"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            logger.info("MCP server stopped")
    
    def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send JSON-RPC request to MCP server"""
        if not self.server_process or self.server_process.poll() is not None:
            return {"error": "Server not running"}
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()
            
            # Read response
            response_line = self.server_process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                return response
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}
    
    def generate_aws_diagram(self, requirements: str, components: List[str] = None) -> Dict[str, Any]:
        """Generate AWS architecture diagram"""
        params = {
            "requirements": requirements,
            "diagram_type": "aws",
            "format": "png"
        }
        
        if components:
            params["components"] = components
            
        return self.send_request("generate_diagram", params)
    
    def list_available_tools(self) -> Dict[str, Any]:
        """List available tools on the MCP server"""
        return self.send_request("tools/list", {})
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "devgenius-mcp-client",
                "version": "1.0.0"
            }
        })


def main():
    """Basic test of MCP client functionality"""
    import os
    
    client = MCPDiagramClient()
    
    try:
        # Start server
        if not client.start_server():
            logger.error("Failed to start MCP server")
            return
        
        # Get server info
        logger.info("Getting server info...")
        info = client.get_server_info()
        logger.info(f"Server info: {info}")
        
        # List available tools
        logger.info("Listing available tools...")
        tools = client.list_available_tools()
        logger.info(f"Available tools: {tools}")
        
        # Generate a test diagram
        logger.info("Generating test diagram...")
        requirements = "Create a simple web application with API Gateway, Lambda function, and DynamoDB database"
        result = client.generate_aws_diagram(requirements)
        logger.info(f"Diagram generation result: {result}")
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Stop server
        client.stop_server()


if __name__ == "__main__":
    main()