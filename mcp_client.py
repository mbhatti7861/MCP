#!/usr/bin/env python3
"""
MCP Client for Terraform MCP Server
Connects to the real AWS Terraform MCP server and provides live data
"""

import asyncio
import json
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class TerraformMCPClient:
    """Client for interacting with the AWS Terraform MCP Server"""
    
    def __init__(self):
        self.server_path = "python3.10"
        self.server_args = ["-m", "awslabs.terraform_mcp_server.server"]
        self.session = None
        
    @asynccontextmanager
    async def connect(self):
        """Context manager for MCP server connection"""
        server_params = StdioServerParameters(
            command=self.server_path,
            args=self.server_args,
            env=None
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.session = session
                yield self
                
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from the MCP server"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        response = await self.session.list_tools()
        # Convert tools to JSON-serializable format
        tools = []
        for tool in response.tools:
            tool_dict = {
                "name": tool.name,
                "description": tool.description,
            }
            if hasattr(tool, 'inputSchema'):
                tool_dict["inputSchema"] = tool.inputSchema
            tools.append(tool_dict)
        return tools
    
    async def get_available_resources(self) -> List[Dict[str, Any]]:
        """Get list of available resources from the MCP server"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        response = await self.session.list_resources()
        # Convert resources to JSON-serializable format
        resources = []
        for resource in response.resources:
            resource_dict = {
                "uri": str(resource.uri),  # Convert AnyUrl to string
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mimeType
            }
            resources.append(resource_dict)
        return resources
    
    async def get_aws_best_practices(self) -> Dict[str, Any]:
        """Get AWS Terraform best practices"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        try:
            response = await self.session.read_resource("terraform://aws_best_practices")
            return {
                "status": "success",
                "content": response.contents[0].text if response.contents else "No content available",
                "type": "aws_best_practices",
                "content_length": len(response.contents[0].text) if response.contents else 0
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "type": "aws_best_practices"
            }
    
    async def get_workflow_guide(self) -> Dict[str, Any]:
        """Get Terraform development workflow guide"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        try:
            response = await self.session.read_resource("terraform://development_workflow")
            return {
                "status": "success",
                "content": response.contents[0].text if response.contents else "No content available",
                "type": "workflow_guide",
                "content_length": len(response.contents[0].text) if response.contents else 0
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "type": "workflow_guide"
            }
    
    async def get_aws_provider_resources(self) -> Dict[str, Any]:
        """Get AWS provider resources listing"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        try:
            response = await self.session.read_resource("terraform://aws_provider_resources_listing")
            return {
                "status": "success",
                "content": response.contents[0].text if response.contents else "No content available",
                "type": "aws_provider_resources",
                "content_length": len(response.contents[0].text) if response.contents else 0
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "type": "aws_provider_resources"
            }
    
    async def execute_terraform_command(self, command: str, working_directory: str, 
                                      variables: Optional[Dict[str, str]] = None,
                                      aws_region: Optional[str] = None) -> Dict[str, Any]:
        """Execute Terraform command via MCP server"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        try:
            response = await self.session.call_tool(
                "ExecuteTerraformCommand",
                {
                    "command": command,
                    "working_directory": working_directory,
                    "variables": variables or {},
                    "aws_region": aws_region,
                    "strip_ansi": True
                }
            )
            
            if response.content:
                # Handle both JSON and text responses
                try:
                    result = json.loads(response.content[0].text)
                except json.JSONDecodeError:
                    result = {"output": response.content[0].text}
                
                return {
                    "status": "success",
                    "result": result,
                    "type": "terraform_execution"
                }
            else:
                return {
                    "status": "error",
                    "error": "No response content",
                    "type": "terraform_execution"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "type": "terraform_execution"
            }
    
    async def run_checkov_scan(self, working_directory: str, 
                             framework: str = "terraform",
                             check_ids: Optional[List[str]] = None,
                             skip_check_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run Checkov security scan via MCP server"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        try:
            response = await self.session.call_tool(
                "RunCheckovScan",
                {
                    "working_directory": working_directory,
                    "framework": framework,
                    "check_ids": check_ids or [],
                    "skip_check_ids": skip_check_ids or [],
                    "output_format": "json"
                }
            )
            
            if response.content:
                # Handle both JSON and text responses
                try:
                    result = json.loads(response.content[0].text)
                except json.JSONDecodeError:
                    result = {"output": response.content[0].text}
                
                return {
                    "status": "success",
                    "result": result,
                    "type": "checkov_scan"
                }
            else:
                return {
                    "status": "error",
                    "error": "No response content",
                    "type": "checkov_scan"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "type": "checkov_scan"
            }
    
    async def search_aws_provider_docs(self, asset_name: str, 
                                     asset_type: str = "resource") -> Dict[str, Any]:
        """Search AWS provider documentation"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        try:
            response = await self.session.call_tool(
                "SearchAwsProviderDocs",
                {
                    "asset_name": asset_name,
                    "asset_type": asset_type
                }
            )
            
            if response.content:
                # Handle both JSON and text responses
                try:
                    result = json.loads(response.content[0].text)
                except json.JSONDecodeError:
                    result = {"output": response.content[0].text}
                
                return {
                    "status": "success",
                    "result": result,
                    "type": "aws_provider_docs",
                    "search_term": asset_name
                }
            else:
                return {
                    "status": "error",
                    "error": "No response content",
                    "type": "aws_provider_docs"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "type": "aws_provider_docs"
            }


# Async wrapper functions for Flask integration
async def get_live_best_practices() -> Dict[str, Any]:
    """Get live best practices from MCP server"""
    client = TerraformMCPClient()
    async with client.connect():
        return await client.get_aws_best_practices()

async def get_live_workflow_guide() -> Dict[str, Any]:
    """Get live workflow guide from MCP server"""
    client = TerraformMCPClient()
    async with client.connect():
        return await client.get_workflow_guide()

async def execute_live_terraform_command(command: str, working_directory: str, 
                                       variables: Optional[Dict[str, str]] = None,
                                       aws_region: Optional[str] = None) -> Dict[str, Any]:
    """Execute live Terraform command via MCP server"""
    client = TerraformMCPClient()
    async with client.connect():
        return await client.execute_terraform_command(command, working_directory, variables, aws_region)

async def run_live_checkov_scan(working_directory: str, 
                              framework: str = "terraform") -> Dict[str, Any]:
    """Run live Checkov scan via MCP server"""
    client = TerraformMCPClient()
    async with client.connect():
        return await client.run_checkov_scan(working_directory, framework)

async def search_live_aws_provider_docs(asset_name: str, 
                                      asset_type: str = "resource") -> Dict[str, Any]:
    """Search live AWS provider documentation"""
    client = TerraformMCPClient()
    async with client.connect():
        return await client.search_aws_provider_docs(asset_name, asset_type)

async def get_live_aws_provider_resources() -> Dict[str, Any]:
    """Get live AWS provider resources"""
    client = TerraformMCPClient()
    async with client.connect():
        return await client.get_aws_provider_resources()

async def get_available_tools() -> Dict[str, Any]:
    """Get available MCP tools"""
    client = TerraformMCPClient()
    async with client.connect():
        tools = await client.get_available_tools()
        return {
            "status": "success",
            "tools": tools,
            "tool_count": len(tools),
            "type": "available_tools"
        }

async def get_available_resources() -> Dict[str, Any]:
    """Get available MCP resources"""
    client = TerraformMCPClient()
    async with client.connect():
        resources = await client.get_available_resources()
        return {
            "status": "success",
            "resources": resources,
            "resource_count": len(resources),
            "type": "available_resources"
        }


# Sync wrapper for Flask
def run_async_function(coro):
    """Run async function in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


if __name__ == "__main__":
    # Test the MCP client
    async def test_client():
        print("🔗 Testing MCP client connection...")
        client = TerraformMCPClient()
        try:
            async with client.connect():
                print("✅ Connected to MCP server!")
                
                # Test available tools
                tools = await client.get_available_tools()
                print(f"📧 Available tools: {len(tools)}")
                for tool in tools[:3]:  # Show first 3
                    print(f"  - {tool['name']}: {tool['description'][:100]}...")
                
                # Test best practices
                best_practices = await client.get_aws_best_practices()
                print(f"📖 Best practices status: {best_practices['status']}")
                if best_practices['status'] == 'success':
                    print(f"   Content length: {best_practices.get('content_length', 0):,} characters")
                
                print("🎉 MCP client test successful!")
        except Exception as e:
            print(f"❌ MCP client test failed: {e}")
    
    asyncio.run(test_client())