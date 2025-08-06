#!/usr/bin/env python3
"""
MCP-powered Architecture Widget
Replacement for generate_arch_widget using aws-diagram-mcp-server
"""

import streamlit as st
import json
import base64
import io
from typing import Dict, Any, Optional
import logging
from mcp_client import MCPDiagramClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPArchitectureWidget:
    """Streamlit widget for MCP-powered architecture generation"""
    
    def __init__(self):
        """Initialize the MCP architecture widget"""
        self.mcp_client = MCPDiagramClient()
        self.is_server_running = False
    
    def _ensure_server_running(self) -> bool:
        """Ensure MCP server is running"""
        if not self.is_server_running:
            self.is_server_running = self.mcp_client.start_server()
        return self.is_server_running
    
    def _extract_solution_requirements(self) -> str:
        """Extract solution requirements from session state"""
        # Get from various possible session state keys
        requirements_sources = [
            'current_solution',
            'solution_description', 
            'architecture_requirements',
            'user_requirements'
        ]
        
        requirements = []
        for key in requirements_sources:
            if key in st.session_state and st.session_state[key]:
                requirements.append(str(st.session_state[key]))
        
        if requirements:
            return " ".join(requirements)
        else:
            return "No specific requirements found in session"
    
    def _parse_components(self, requirements: str) -> list:
        """Parse AWS components from requirements text"""
        # Simple keyword-based component detection
        aws_services = {
            'api gateway': 'APIGateway',
            'lambda': 'Lambda', 
            'dynamodb': 'DynamoDB',
            'rds': 'RDS',
            's3': 'S3',
            'cloudfront': 'CloudFront',
            'ec2': 'EC2',
            'ecs': 'ECS',
            'eks': 'EKS',
            'sqs': 'SQS',
            'sns': 'SNS',
            'cloudwatch': 'CloudWatch'
        }
        
        components = []
        requirements_lower = requirements.lower()
        
        for keyword, service in aws_services.items():
            if keyword in requirements_lower:
                components.append(service)
        
        return components
    
    def render_widget(self):
        """Render the MCP architecture widget"""
        st.subheader("🏗️ AWS Architecture Diagram (MCP Powered)")
        
        # Widget controls
        col1, col2 = st.columns([2, 1])
        
        with col1:
            generate_diagram = st.button(
                "Generate Architecture Diagram", 
                key="generate_mcp_arch",
                type="primary"
            )
        
        with col2:
            show_requirements = st.checkbox("Show Requirements", key="show_reqs")
        
        # Show current requirements if requested
        if show_requirements:
            requirements = self._extract_solution_requirements()
            st.text_area(
                "Current Solution Requirements:",
                value=requirements,
                height=100,
                key="current_reqs_display",
                disabled=True
            )
        
        # Generate diagram
        if generate_diagram:
            self._generate_and_display_diagram()
    
    def _generate_and_display_diagram(self):
        """Generate and display the architecture diagram"""
        with st.spinner("Generating architecture diagram via MCP server..."):
            try:
                # Ensure server is running
                if not self._ensure_server_running():
                    st.error("❌ Failed to start MCP server. Please check your setup.")
                    return
                
                # Get requirements
                requirements = self._extract_solution_requirements()
                
                if not requirements or "no specific requirements" in requirements.lower():
                    st.warning("⚠️ No solution requirements found. Please complete solution generation first.")
                    return
                
                # Parse components
                components = self._parse_components(requirements)
                
                # Generate diagram
                logger.info(f"Generating diagram with requirements: {requirements[:100]}...")
                result = self.mcp_client.generate_aws_diagram(requirements, components)
                
                # Handle result
                if "error" in result:
                    st.error(f"❌ Diagram generation failed: {result['error']}")
                    self._show_troubleshooting()
                else:
                    self._display_diagram_result(result)
                    
            except Exception as e:
                logger.error(f"Widget error: {e}")
                st.error(f"❌ Unexpected error: {str(e)}")
                self._show_troubleshooting()
    
    def _display_diagram_result(self, result: Dict[str, Any]):
        """Display the generated diagram result"""
        st.success("✅ Architecture diagram generated successfully!")
        
        # Display diagram if available
        if "result" in result and "diagram" in result["result"]:
            diagram_data = result["result"]["diagram"]
            
            # If it's base64 encoded image
            if isinstance(diagram_data, str) and diagram_data.startswith("data:image"):
                st.image(diagram_data, caption="Generated Architecture Diagram")
            elif isinstance(diagram_data, str):
                # Assume it's base64 without header
                try:
                    image_data = base64.b64decode(diagram_data)
                    st.image(image_data, caption="Generated Architecture Diagram")
                except Exception as e:
                    st.error(f"Failed to decode image: {e}")
        
        # Show diagram code if available
        if "result" in result and "code" in result["result"]:
            with st.expander("View Generated Diagram Code"):
                st.code(result["result"]["code"], language="python")
        
        # Show raw result for debugging
        with st.expander("View Raw MCP Response (Debug)"):
            st.json(result)
        
        # Provide download option
        if "result" in result and "diagram" in result["result"]:
            try:
                diagram_data = result["result"]["diagram"]
                if isinstance(diagram_data, str):
                    if diagram_data.startswith("data:image"):
                        # Extract base64 part
                        b64_data = diagram_data.split(',')[1]
                        image_bytes = base64.b64decode(b64_data)
                    else:
                        # Assume raw base64
                        image_bytes = base64.b64decode(diagram_data)
                    
                    st.download_button(
                        label="📥 Download Diagram",
                        data=image_bytes,
                        file_name="aws_architecture_diagram.png",
                        mime="image/png"
                    )
            except Exception as e:
                logger.error(f"Download button error: {e}")
    
    def _show_troubleshooting(self):
        """Show troubleshooting information"""
        with st.expander("🔧 Troubleshooting"):
            st.markdown("""
            **Common Issues:**
            
            1. **MCP Server Not Running:**
               - Ensure `aws-diagram-mcp-server` is installed
               - Check that Python and required dependencies are available
               
            2. **Connection Issues:**
               - Verify MCP configuration in `mcp_config.json`
               - Check server logs for error messages
               
            3. **Diagram Generation Errors:**
               - Ensure GraphViz is installed on your system
               - Verify that the `diagrams` Python package is available
               
            4. **No Requirements Found:**
               - Complete the solution generation process first
               - Check that solution data is saved in session state
            
            **Quick Fixes:**
            - Try refreshing the page and regenerating
            - Check the browser console for JavaScript errors
            - Verify that all MCP dependencies are installed
            """)
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'mcp_client') and self.mcp_client:
            self.mcp_client.stop_server()


def show_mcp_architecture_widget():
    """Main function to display the MCP architecture widget"""
    # Initialize widget in session state
    if 'mcp_widget' not in st.session_state:
        st.session_state.mcp_widget = MCPArchitectureWidget()
    
    # Render the widget
    st.session_state.mcp_widget.render_widget()
    
    # Cleanup on app shutdown (best effort)
    import atexit
    atexit.register(st.session_state.mcp_widget.cleanup)


# For testing purposes
def main():
    """Test the widget standalone"""
    st.set_page_config(page_title="MCP Architecture Widget Test")
    
    st.title("MCP Architecture Widget Test")
    
    # Mock some session state data for testing
    if st.button("Load Test Requirements"):
        st.session_state.current_solution = """
        Create a serverless web application that processes user uploads.
        The system should use API Gateway for REST endpoints,
        Lambda functions for processing logic,
        S3 for file storage,
        and DynamoDB for metadata storage.
        Include CloudWatch for monitoring.
        """
        st.success("Test requirements loaded!")
    
    # Show the widget
    show_mcp_architecture_widget()


if __name__ == "__main__":
    main()