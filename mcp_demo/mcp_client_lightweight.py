#!/usr/bin/env python3
"""
Lightweight MCP Client for DevGenius
Direct diagram generation without full MCP server
"""

import json
import tempfile
import base64
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LightweightMCPClient:
    """Lightweight MCP client that generates diagrams directly"""
    
    def __init__(self, config_path: str = "mcp_config.json"):
        """Initialize lightweight MCP client"""
        self.config_path = config_path
        self.server_config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration (for compatibility)"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                return config['mcpServers']['aws-diagram']
        except Exception:
            return {
                "command": "python",
                "args": ["-m", "direct_diagram_generator"],
                "env": {"PYTHONPATH": "."}
            }
    
    def start_server(self) -> bool:
        """Mock server start (direct generation)"""
        try:
            # Test if diagrams package is available
            from diagrams import Diagram
            logger.info("✅ Direct diagram generation available")
            return True
        except ImportError as e:
            logger.error(f"❌ Diagrams package not available: {e}")
            return False
    
    def stop_server(self):
        """Mock server stop"""
        logger.info("🛑 Direct generation mode stopped")
    
    def generate_aws_diagram(self, requirements: str, components: List[str] = None) -> Dict[str, Any]:
        """Generate AWS diagram directly using diagrams library"""
        try:
            return self._generate_diagram_direct(requirements, components or [])
        except Exception as e:
            logger.error(f"Direct generation failed: {e}")
            return {"error": str(e)}
    
    def _generate_diagram_direct(self, requirements: str, components: List[str]) -> Dict[str, Any]:
        """Direct diagram generation"""
        from diagrams import Diagram, Cluster
        from diagrams.aws.compute import Lambda, EC2
        from diagrams.aws.database import DynamoDB, RDS
        from diagrams.aws.network import APIGateway, CloudFront, ELB
        from diagrams.aws.storage import S3
        from diagrams.aws.integration import SQS, SNS
        from diagrams.aws.security import Cognito, IAM
        from diagrams.aws.management import CloudWatch
        import os
        import tempfile
        
        # Create temporary file for diagram
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            diagram_path = tmp_file.name
        
        # Map components to diagram objects
        component_map = {
            'Lambda': Lambda,
            'EC2': EC2,
            'DynamoDB': DynamoDB,
            'RDS': RDS,
            'APIGateway': APIGateway,
            'CloudFront': CloudFront,
            'ELB': ELB,
            'S3': S3,
            'SQS': SQS,
            'SNS': SNS,
            'Cognito': Cognito,
            'IAM': IAM,
            'CloudWatch': CloudWatch
        }
        
        # Generate diagram name from requirements
        diagram_name = "AWS Architecture"
        if "serverless" in requirements.lower():
            diagram_name = "Serverless Architecture"
        elif "web" in requirements.lower():
            diagram_name = "Web Application Architecture"
        
        # Create diagram
        diagram_code = f'''from diagrams import Diagram, Cluster
from diagrams.aws.compute import Lambda, EC2
from diagrams.aws.database import DynamoDB, RDS
from diagrams.aws.network import APIGateway, CloudFront, ELB
from diagrams.aws.storage import S3
from diagrams.aws.integration import SQS, SNS
from diagrams.aws.security import Cognito, IAM
from diagrams.aws.management import CloudWatch

with Diagram("{diagram_name}", filename="{diagram_path[:-4]}", show=False):'''
        
        # Create diagram objects based on components
        service_objects = {}
        for component in components[:8]:  # Limit to 8 services for clarity
            if component in component_map:
                service_class = component_map[component]
                service_name = component.replace('Gateway', ' Gateway').replace('DB', ' DB')
                var_name = component.lower().replace('gateway', '_gateway')
                service_objects[component] = f'{var_name} = {service_class.__name__}("{service_name}")'
                diagram_code += f'\n    {service_objects[component]}'
        
        # Add simple connections if multiple services
        if len(service_objects) > 1:
            service_vars = [comp.lower().replace('gateway', '_gateway') for comp in service_objects.keys()]
            if len(service_vars) >= 2:
                diagram_code += f'\n    {service_vars[0]} >> {service_vars[1]}'
                if len(service_vars) >= 3:
                    diagram_code += f' >> {service_vars[2]}'
        
        # Execute the diagram generation
        try:
            # Change to temp directory to avoid file permission issues
            original_dir = os.getcwd()
            temp_dir = os.path.dirname(diagram_path)
            os.chdir(temp_dir)
            
            with Diagram(diagram_name, filename=os.path.basename(diagram_path)[:-4], show=False):
                services = {}
                for component in components[:8]:
                    if component in component_map:
                        service_class = component_map[component]
                        service_name = component.replace('Gateway', ' Gateway').replace('DB', ' DB')
                        services[component] = service_class(service_name)
                
                # Create simple connections
                service_list = list(services.values())
                if len(service_list) >= 2:
                    service_list[0] >> service_list[1]
                    if len(service_list) >= 3:
                        service_list[1] >> service_list[2]
                    if len(service_list) >= 4:
                        service_list[2] >> service_list[3]
            
            os.chdir(original_dir)
            
            # Read generated PNG and encode as base64
            if os.path.exists(diagram_path):
                with open(diagram_path, 'rb') as f:
                    image_data = f.read()
                    image_b64 = base64.b64encode(image_data).decode()
                    
                # Clean up temp file
                os.unlink(diagram_path)
                
                return {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "diagram": f"data:image/png;base64,{image_b64}",
                        "code": diagram_code,
                        "components": components
                    }
                }
            else:
                return {"error": "Diagram file not generated"}
                
        except Exception as e:
            os.chdir(original_dir)
            if os.path.exists(diagram_path):
                os.unlink(diagram_path)
            raise e
    
    def list_available_tools(self) -> Dict[str, Any]:
        """Mock tools list"""
        return {
            "jsonrpc": "2.0", 
            "id": 1,
            "result": [{"name": "generate_diagram", "description": "Generate AWS diagrams"}]
        }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Mock server info"""
        return {
            "jsonrpc": "2.0",
            "id": 1, 
            "result": {
                "name": "lightweight-diagram-generator",
                "version": "1.0.0"
            }
        }


# For compatibility, create an alias
MCPDiagramClient = LightweightMCPClient