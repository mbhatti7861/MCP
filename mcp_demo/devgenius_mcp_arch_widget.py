#!/usr/bin/env python3
"""
DevGenius MCP-powered Architecture Widget
Drop-in replacement for generate_arch_widget using aws-diagram-mcp-server
Designed to integrate seamlessly with the existing DevGenius application
"""

import streamlit as st
import json
import base64
import uuid
from typing import Dict, Any, Optional
import logging
from mcp_client import MCPDiagramClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DevGeniusMCPArchWidget:
    """DevGenius-specific MCP architecture widget"""
    
    def __init__(self):
        """Initialize the DevGenius MCP architecture widget"""
        self.mcp_client = MCPDiagramClient()
        self.is_server_running = False
    
    def _ensure_server_running(self) -> bool:
        """Ensure MCP server is running"""
        if not self.is_server_running:
            self.is_server_running = self.mcp_client.start_server()
        return self.is_server_running
    
    def _extract_solution_from_messages(self, arch_messages: list) -> str:
        """Extract solution requirements from DevGenius message format"""
        if not arch_messages:
            return "No conversation history found"
        
        # Find the most recent user message that contains solution details
        solution_messages = []
        for message in reversed(arch_messages):
            if message.get('role') == 'user':
                content = message.get('content', '')
                # Skip the architecture prompt itself
                if 'Generate an AWS architecture' not in content and 'draw.io' not in content:
                    solution_messages.append(content)
                    if len(solution_messages) >= 3:  # Get last 3 user messages
                        break
        
        # Also check session state for solution data
        session_sources = [
            'messages',
            'mod_messages', 
            'current_solution',
            'interaction'
        ]
        
        for key in session_sources:
            if key in st.session_state and st.session_state[key]:
                if isinstance(st.session_state[key], list):
                    # Extract from message format
                    for item in st.session_state[key]:
                        if isinstance(item, dict):
                            if 'content' in item and item.get('role') == 'assistant':
                                solution_messages.append(item['content'][:500])  # Limit length
                            elif 'details' in item:
                                solution_messages.append(str(item['details'])[:500])
                elif isinstance(st.session_state[key], str):
                    solution_messages.append(st.session_state[key])
        
        if solution_messages:
            # Combine and clean up the solution text
            combined_solution = " ".join(solution_messages)
            # Remove common DevGenius prompt text
            cleanup_phrases = [
                "Generate an AWS architecture",
                "draw.io",
                "XML file",
                "markdown format",
                "opening and closing tags"
            ]
            for phrase in cleanup_phrases:
                combined_solution = combined_solution.replace(phrase, "")
            
            return combined_solution[:2000]  # Limit to reasonable length
        
        return "Generic AWS solution architecture"
    
    def _parse_aws_components(self, solution_text: str) -> list:
        """Parse AWS components from solution text"""
        # Enhanced AWS service detection
        aws_services_map = {
            # Compute
            'lambda': 'Lambda',
            'ec2': 'EC2', 
            'ecs': 'ECS',
            'eks': 'EKS',
            'fargate': 'Fargate',
            'elastic beanstalk': 'ElasticBeanstalk',
            
            # Storage
            's3': 'S3',
            'ebs': 'EBS',
            'efs': 'EFS',
            'fsx': 'FSx',
            
            # Database
            'dynamodb': 'DynamoDB',
            'rds': 'RDS',
            'aurora': 'Aurora',
            'redshift': 'Redshift',
            'neptune': 'Neptune',
            'documentdb': 'DocumentDB',
            'elasticache': 'ElastiCache',
            
            # Networking
            'api gateway': 'APIGateway',
            'cloudfront': 'CloudFront',
            'route 53': 'Route53',
            'vpc': 'VPC',
            'load balancer': 'ELB',
            'application load balancer': 'ApplicationLoadBalancer',
            'network load balancer': 'NetworkLoadBalancer',
            
            # Messaging
            'sqs': 'SQS',
            'sns': 'SNS',
            'kinesis': 'Kinesis',
            'eventbridge': 'EventBridge',
            
            # Security
            'cognito': 'Cognito',
            'iam': 'IAM',
            'secrets manager': 'SecretsManager',
            'kms': 'KMS',
            'waf': 'WAF',
            
            # Monitoring
            'cloudwatch': 'CloudWatch',
            'cloudtrail': 'CloudTrail',
            'x-ray': 'XRay',
            
            # Analytics
            'athena': 'Athena',
            'glue': 'Glue',
            'emr': 'EMR',
            
            # Machine Learning
            'sagemaker': 'Sagemaker',
            'bedrock': 'Bedrock',
            'rekognition': 'Rekognition',
            'comprehend': 'Comprehend'
        }
        
        components = []
        solution_lower = solution_text.lower()
        
        for keyword, service in aws_services_map.items():
            if keyword in solution_lower:
                components.append(service)
        
        # If no specific services found, provide some defaults
        if not components:
            components = ['APIGateway', 'Lambda', 'DynamoDB']
        
        return list(set(components))  # Remove duplicates
    
    @st.fragment
    def generate_arch(self, arch_messages: list):
        """
        Main function to replace the original generate_arch function
        Maintains the same interface for seamless integration
        """
        # Retain messages and previous insights in the chat section
        if 'arch_messages' not in st.session_state:
            st.session_state.arch_messages = []

        # Create the radio button for architecture generation selection
        if 'arch_user_select' not in st.session_state:
            st.session_state.arch_user_select = False

        left, middle, right = st.columns([3, 1, 0.5])

        with left:
            st.markdown(
                "<div style='font-size: 18px'><b>Use the checkbox below to generate a visual representation of the proposed solution (MCP Powered)</b></div>",
                unsafe_allow_html=True)
            st.divider()
            st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
            select_arch = st.checkbox(
                "Check this box to generate architecture (MCP)",
                key="arch_mcp"
            )
            # Only update the session state when the checkbox value changes
            if select_arch != st.session_state.arch_user_select:
                st.session_state.arch_user_select = select_arch
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            if st.session_state.arch_user_select:
                st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
                if st.button(label="⟳ Retry", key="retry_mcp", type="secondary"):
                    st.session_state.arch_user_select = True
                st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.arch_user_select:
            self._generate_and_display_architecture(arch_messages)
    
    def _generate_and_display_architecture(self, arch_messages: list):
        """Generate and display architecture using MCP server"""
        with st.spinner("Generating architecture diagram via MCP server..."):
            try:
                # Ensure MCP server is running
                if not self._ensure_server_running():
                    st.error("❌ Failed to start MCP server. Please check your setup.")
                    self._show_mcp_troubleshooting()
                    return
                
                # Extract solution requirements
                solution_text = self._extract_solution_from_messages(arch_messages)
                logger.info(f"Extracted solution: {solution_text[:200]}...")
                
                # Parse AWS components
                components = self._parse_aws_components(solution_text)
                logger.info(f"Identified components: {components}")
                
                # Generate diagram using MCP
                result = self.mcp_client.generate_aws_diagram(solution_text, components)
                
                if "error" in result:
                    st.error(f"❌ MCP diagram generation failed: {result['error']}")
                    self._show_mcp_troubleshooting()
                    return
                
                # Display the result
                self._display_mcp_result(result, solution_text)
                
                # Store in session state (maintaining DevGenius format)
                st.session_state.arch_messages.append({"role": "assistant", "content": "MCP Generated Architecture"})
                
                # Store interaction (DevGenius format)
                if 'interaction' not in st.session_state:
                    st.session_state.interaction = []
                st.session_state.interaction.append({
                    "type": "Solution Architecture (MCP)",
                    "details": f"Generated using MCP server with components: {', '.join(components)}"
                })
                
                # Store diagram data for potential future use
                st.session_state.mcp_diagram_result = result
                
            except Exception as e:
                logger.error(f"MCP widget error: {e}")
                st.error(f"❌ MCP integration error: {str(e)}")
                self._show_mcp_troubleshooting()
    
    def _display_mcp_result(self, result: Dict[str, Any], solution_text: str):
        """Display MCP generation result in DevGenius format"""
        st.success("✅ MCP Architecture diagram generated successfully!")
        
        # Display diagram
        diagram_displayed = False
        
        if "result" in result:
            mcp_result = result["result"]
            
            # Try to display diagram image
            if "diagram" in mcp_result:
                diagram_data = mcp_result["diagram"]
                try:
                    if isinstance(diagram_data, str):
                        if diagram_data.startswith("data:image"):
                            st.image(diagram_data, caption="MCP Generated AWS Architecture", width=700)
                        else:
                            # Assume base64 encoded
                            image_data = base64.b64decode(diagram_data)
                            st.image(image_data, caption="MCP Generated AWS Architecture", width=700)
                        diagram_displayed = True
                except Exception as e:
                    logger.error(f"Failed to display diagram: {e}")
            
            # Show diagram code if available
            if "code" in mcp_result:
                with st.expander("🔍 View Generated Diagram Code"):
                    st.code(mcp_result["code"], language="python")
            
            # Show components used
            if "components" in mcp_result:
                with st.expander("🏗️ AWS Components Identified"):
                    st.write(", ".join(mcp_result["components"]))
        
        # Fallback display
        if not diagram_displayed:
            st.info("📊 Diagram generated by MCP server (display format not supported in this view)")
            with st.expander("🔍 View Raw MCP Response"):
                st.json(result)
        
        # Download option
        if "result" in result and "diagram" in result["result"]:
            try:
                diagram_data = result["result"]["diagram"]
                if isinstance(diagram_data, str):
                    if diagram_data.startswith("data:image"):
                        b64_data = diagram_data.split(',')[1]
                        image_bytes = base64.b64decode(b64_data)
                    else:
                        image_bytes = base64.b64decode(diagram_data)
                    
                    st.download_button(
                        label="📥 Download Architecture Diagram",
                        data=image_bytes,
                        file_name=f"devgenius_architecture_{uuid.uuid4().hex[:8]}.png",
                        mime="image/png"
                    )
            except Exception as e:
                logger.error(f"Download preparation error: {e}")
    
    def _show_mcp_troubleshooting(self):
        """Show MCP-specific troubleshooting information"""
        with st.expander("🔧 MCP Troubleshooting"):
            st.markdown("""
            **MCP Server Issues:**
            
            1. **Server Not Starting:**
               ```bash
               # Install the MCP server
               cd mcp/src/aws-diagram-mcp-server
               uv pip install -e .
               ```
               
            2. **Missing Dependencies:**
               ```bash
               # Install GraphViz
               brew install graphviz  # macOS
               sudo apt-get install graphviz  # Ubuntu
               ```
               
            3. **Python Environment:**
               ```bash
               # Verify diagrams package
               python -c "from diagrams import Diagram; print('OK')"
               ```
            
            **DevGenius Integration Issues:**
            - Check that `mcp_config.json` is in the correct path
            - Verify MCP server path in configuration
            - Ensure sufficient permissions for subprocess creation
            
            **Quick Fix:**
            - Restart the Streamlit application
            - Check browser console for errors
            - Try with a simpler solution description
            """)
    
    def cleanup(self):
        """Clean up MCP resources"""
        if hasattr(self, 'mcp_client') and self.mcp_client:
            self.mcp_client.stop_server()


# Main replacement function for seamless integration
@st.fragment  
def generate_arch(arch_messages: list):
    """
    Drop-in replacement for the original generate_arch function
    Uses MCP instead of Bedrock for diagram generation
    """
    # Initialize widget in session state to maintain state across reruns
    if 'devgenius_mcp_widget' not in st.session_state:
        st.session_state.devgenius_mcp_widget = DevGeniusMCPArchWidget()
    
    # Generate architecture using MCP
    st.session_state.devgenius_mcp_widget.generate_arch(arch_messages)
    
    # Cleanup on app shutdown (best effort)
    import atexit
    atexit.register(st.session_state.devgenius_mcp_widget.cleanup)


# For testing the widget independently
def main():
    """Test the DevGenius MCP widget standalone"""
    st.set_page_config(page_title="DevGenius MCP Architecture Widget Test")
    
    st.title("DevGenius MCP Architecture Widget Test")
    
    # Mock DevGenius session state and messages
    if st.button("Load Test DevGenius Session"):
        st.session_state.messages = [
            {
                "role": "user",
                "content": "I need a serverless solution for processing customer orders"
            },
            {
                "role": "assistant", 
                "content": """I'll help you design a serverless order processing solution.

                **Proposed Architecture:**
                
                1. **API Gateway** - REST API endpoints for order submission
                2. **Lambda Functions** - Order processing logic
                3. **DynamoDB** - Order storage and tracking
                4. **SQS** - Order queue for async processing
                5. **SNS** - Notifications for order status
                6. **S3** - Receipt and document storage
                7. **CloudWatch** - Monitoring and logging
                
                This solution provides scalability, cost-effectiveness, and reliability."""
            }
        ]
        
        st.session_state.interaction = [
            {
                "type": "Solution Design",
                "details": "Serverless order processing system with API Gateway, Lambda, DynamoDB"
            }
        ]
        
        st.success("Test DevGenius session loaded!")
    
    # Test the widget
    if 'messages' in st.session_state:
        st.subheader("Testing MCP Architecture Generation")
        generate_arch(st.session_state.messages)


if __name__ == "__main__":
    main()