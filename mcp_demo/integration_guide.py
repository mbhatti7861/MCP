#!/usr/bin/env python3
"""
DevGenius MCP Integration Guide
Instructions for integrating MCP architecture widget into existing DevGenius application
"""

import os
import shutil
from pathlib import Path

def show_integration_steps():
    """Display step-by-step integration instructions"""
    
    print("🚀 DevGenius MCP Integration Guide")
    print("=" * 50)
    
    print("\n1. BACKUP ORIGINAL FILES")
    print("-" * 25)
    print("Before making changes, backup the original files:")
    print("cp sample-devgenius-aws-solution-builder/chatbot/generate_arch_widget.py generate_arch_widget.py.backup")
    
    print("\n2. COPY MCP FILES")
    print("-" * 18)
    print("Copy the MCP integration files to the DevGenius chatbot directory:")
    print("cp mcp_demo/mcp_client.py sample-devgenius-aws-solution-builder/chatbot/")
    print("cp mcp_demo/mcp_config.json sample-devgenius-aws-solution-builder/chatbot/")
    print("cp mcp_demo/devgenius_mcp_arch_widget.py sample-devgenius-aws-solution-builder/chatbot/")
    
    print("\n3. UPDATE IMPORTS")
    print("-" * 16)
    print("In sample-devgenius-aws-solution-builder/chatbot/agent.py:")
    print("Replace line 15:")
    print("  OLD: from generate_arch_widget import generate_arch")
    print("  NEW: from devgenius_mcp_arch_widget import generate_arch")
    
    print("\n4. UPDATE REQUIREMENTS")
    print("-" * 20)
    print("Add to sample-devgenius-aws-solution-builder/chatbot/requirements.txt:")
    print("# MCP Integration")
    print("asyncio-subprocess>=0.1.0")
    print("# Note: Other MCP dependencies should be installed separately")
    
    print("\n5. INSTALL MCP SERVER")
    print("-" * 19)
    print("Install the AWS Diagram MCP Server:")
    print("cd mcp/src/aws-diagram-mcp-server")
    print("uv pip install -e .")
    
    print("\n6. INSTALL GRAPHVIZ")
    print("-" * 18)
    print("Install GraphViz (required for diagram generation):")
    print("# macOS")
    print("brew install graphviz")
    print("# Ubuntu/Debian")
    print("sudo apt-get install graphviz")
    
    print("\n7. TEST THE INTEGRATION")
    print("-" * 21)
    print("Test the MCP widget independently:")
    print("cd sample-devgenius-aws-solution-builder/chatbot")
    print("python devgenius_mcp_arch_widget.py")
    
    print("\n8. RUN DEVGENIUS WITH MCP")
    print("-" * 24)
    print("Start the DevGenius application:")
    print("cd sample-devgenius-aws-solution-builder/chatbot")
    print("streamlit run agent.py --server.port 8501")
    
    print("\n9. CONFIGURATION")
    print("-" * 15)
    print("The MCP configuration is in mcp_config.json:")
    print('''{
  "mcpServers": {
    "aws-diagram": {
      "command": "python",
      "args": ["-m", "aws_diagram_mcp_server"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}''')
    
    print("\n10. TROUBLESHOOTING")
    print("-" * 18)
    print("If you encounter issues:")
    print("- Check that GraphViz is installed: dot -V")
    print("- Verify MCP server: python -m aws_diagram_mcp_server --help")
    print("- Check Python environment: python -c \"from diagrams import Diagram\"")
    print("- Review Streamlit logs for errors")
    
    print("\n✅ INTEGRATION COMPLETE")
    print("=" * 23)
    print("Your DevGenius application will now use the MCP-powered architecture widget!")
    print("The widget maintains the same UI/UX but generates diagrams using code instead of AI.")


def create_integration_script():
    """Create an automated integration script"""
    script_content = '''#!/bin/bash
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
cp sample-devgenius-aws-solution-builder/chatbot/generate_arch_widget.py \\
   sample-devgenius-aws-solution-builder/chatbot/generate_arch_widget.py.backup

# 2. Copy MCP files
echo "📋 Copying MCP integration files..."
cp mcp_demo/mcp_client.py sample-devgenius-aws-solution-builder/chatbot/
cp mcp_demo/mcp_config.json sample-devgenius-aws-solution-builder/chatbot/
cp mcp_demo/devgenius_mcp_arch_widget.py sample-devgenius-aws-solution-builder/chatbot/

# 3. Update imports in agent.py
echo "🔄 Updating imports in agent.py..."
sed -i.bak 's/from generate_arch_widget import generate_arch/from devgenius_mcp_arch_widget import generate_arch/' \\
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
'''
    
    with open('mcp_demo/integrate_mcp.sh', 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod('mcp_demo/integrate_mcp.sh', 0o755)
    
    print("📜 Created automated integration script: mcp_demo/integrate_mcp.sh")


def create_test_script():
    """Create a comprehensive test script"""
    test_content = '''#!/usr/bin/env python3
"""
Comprehensive test script for DevGenius MCP integration
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def test_mcp_server_installation():
    """Test if MCP server is properly installed"""
    print("🔍 Testing MCP Server Installation...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "aws_diagram_mcp_server", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ MCP server is installed and accessible")
            return True
        else:
            print(f"❌ MCP server installation issue: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

def test_graphviz_installation():
    """Test GraphViz installation"""
    print("🔍 Testing GraphViz Installation...")
    
    try:
        result = subprocess.run(["dot", "-V"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ GraphViz is installed")
            print(f"   Version: {result.stderr.strip()}")
            return True
        else:
            print("❌ GraphViz not found")
            return False
    except Exception as e:
        print(f"❌ GraphViz test failed: {e}")
        return False

def test_python_dependencies():
    """Test Python dependencies"""
    print("🔍 Testing Python Dependencies...")
    
    dependencies = [
        ("diagrams", "from diagrams import Diagram"),
        ("streamlit", "import streamlit"),
        ("boto3", "import boto3"),
    ]
    
    results = []
    for name, import_test in dependencies:
        try:
            exec(import_test)
            print(f"✅ {name} is available")
            results.append(True)
        except ImportError:
            print(f"❌ {name} is missing")
            results.append(False)
    
    return all(results)

def test_file_integration():
    """Test if files are properly integrated"""
    print("🔍 Testing File Integration...")
    
    devgenius_path = Path("sample-devgenius-aws-solution-builder/chatbot")
    required_files = [
        "devgenius_mcp_arch_widget.py",
        "mcp_client.py", 
        "mcp_config.json"
    ]
    
    results = []
    for filename in required_files:
        filepath = devgenius_path / filename
        if filepath.exists():
            print(f"✅ {filename} is present")
            results.append(True)
        else:
            print(f"❌ {filename} is missing")
            results.append(False)
    
    # Check if agent.py import was updated
    agent_path = devgenius_path / "agent.py"
    if agent_path.exists():
        with open(agent_path, 'r') as f:
            content = f.read()
            if "from devgenius_mcp_arch_widget import generate_arch" in content:
                print("✅ agent.py import updated correctly")
                results.append(True)
            else:
                print("❌ agent.py import not updated")
                results.append(False)
    else:
        print("❌ agent.py not found")
        results.append(False)
    
    return all(results)

def test_mcp_widget():
    """Test MCP widget functionality"""
    print("🔍 Testing MCP Widget...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, "sample-devgenius-aws-solution-builder/chatbot")
        
        from devgenius_mcp_arch_widget import DevGeniusMCPArchWidget
        
        # Test widget initialization
        widget = DevGeniusMCPArchWidget()
        print("✅ MCP widget initializes successfully")
        
        # Test component parsing
        test_text = "Create a serverless application with API Gateway, Lambda, and DynamoDB"
        components = widget._parse_aws_components(test_text)
        
        if components and len(components) > 0:
            print(f"✅ Component parsing works: {components}")
            return True
        else:
            print("❌ Component parsing failed")
            return False
            
    except Exception as e:
        print(f"❌ MCP widget test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 DevGenius MCP Integration Test Suite")
    print("=" * 45)
    
    tests = [
        ("MCP Server Installation", test_mcp_server_installation),
        ("GraphViz Installation", test_graphviz_installation),
        ("Python Dependencies", test_python_dependencies),
        ("File Integration", test_file_integration),
        ("MCP Widget", test_mcp_widget)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\\n--- {test_name} ---")
        results[test_name] = test_func()
    
    # Summary
    print("\\n" + "=" * 45)
    print("📊 TEST SUMMARY")
    print("=" * 45)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP integration is ready to use.")
    else:
        print("🚨 Some tests failed. Please address the issues before using MCP integration.")
        
        print("\\n🔧 TROUBLESHOOTING:")
        if not results.get("MCP Server Installation"):
            print("- Install MCP server: cd mcp/src/aws-diagram-mcp-server && uv pip install -e .")
        if not results.get("GraphViz Installation"):
            print("- Install GraphViz: brew install graphviz (macOS) or sudo apt-get install graphviz (Ubuntu)")
        if not results.get("Python Dependencies"):
            print("- Install missing Python packages using pip or uv")
        if not results.get("File Integration"):
            print("- Run the integration script: ./mcp_demo/integrate_mcp.sh")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
'''
    
    with open('mcp_demo/test_integration.py', 'w') as f:
        f.write(test_content)
    
    os.chmod('mcp_demo/test_integration.py', 0o755)
    print("🧪 Created comprehensive test script: mcp_demo/test_integration.py")


if __name__ == "__main__":
    show_integration_steps()
    print("\n" + "=" * 50)
    create_integration_script()
    create_test_script()
    print("\n🎯 Integration guide complete!")
    print("Run ./mcp_demo/integrate_mcp.sh to automate the integration process.")