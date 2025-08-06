#!/usr/bin/env python3
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
        print(f"\n--- {test_name} ---")
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 45)
    print("📊 TEST SUMMARY")
    print("=" * 45)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP integration is ready to use.")
    else:
        print("🚨 Some tests failed. Please address the issues before using MCP integration.")
        
        print("\n🔧 TROUBLESHOOTING:")
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
