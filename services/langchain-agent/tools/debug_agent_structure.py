#!/usr/bin/env python3
"""
Debug script to explore the agent service structure.
This helps understand the code organization to fix issues.
"""

import sys
import os

def list_module_structure(base_path, indent=0):
    """List the module structure in a directory."""
    indent_str = '  ' * indent
    if os.path.isdir(base_path):
        print(f"{indent_str}{os.path.basename(base_path)}/")
        for item in sorted(os.listdir(base_path)):
            if item.startswith('__'):
                continue
            item_path = os.path.join(base_path, item)
            list_module_structure(item_path, indent + 1)
    elif base_path.endswith('.py'):
        # Print Python files
        filename = os.path.basename(base_path)
        print(f"{indent_str}{filename}")
        
        # For key files, print their content summary
        key_files = [
            'agent.py', 
            'base_agent.py', 
            'factory.py', 
            'conversational_agent.py',
            'agent_service.py'
        ]
        
        if os.path.basename(base_path) in key_files:
            try:
                with open(base_path, 'r') as f:
                    content = f.read()
                    classes = [line.strip() for line in content.split('\n') 
                              if line.strip().startswith('class ')]
                    if classes:
                        for class_def in classes:
                            print(f"{indent_str}  - {class_def}")
                    
                    imports = [line.strip() for line in content.split('\n') 
                              if line.strip().startswith('from ') or line.strip().startswith('import ')]
                    if imports and len(imports) < 10:
                        for import_line in imports[:5]:
                            print(f"{indent_str}  > {import_line}")
                        if len(imports) > 5:
                            print(f"{indent_str}  > ...and {len(imports)-5} more imports")
            except Exception as e:
                print(f"{indent_str}  ! Error reading file: {str(e)}")

def main():
    """Main function to explore the code structure."""
    print("Exploring Agent Service Code Structure")
    print("======================================\n")
    
    # Search for source files
    app_dir = '/app'
    if os.path.exists(app_dir):
        print("Exploring app directory structure:\n")
        list_module_structure(os.path.join(app_dir, 'app'))
    else:
        print(f"Path {app_dir} does not exist!")
        
    # Print environment info
    print("\nEnvironment Information:")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check for specific imports
    print("\nTesting imports:")
    try:
        import app.core.entities.agent
        print("✅ Successfully imported app.core.entities.agent")
        print(f"Available items: {dir(app.core.entities.agent)}")
    except ImportError as e:
        print(f"❌ Failed to import app.core.entities.agent: {str(e)}")
    
    try:
        import app.core.agents.base_agent
        print("✅ Successfully imported app.core.agents.base_agent")
        print(f"Available items: {dir(app.core.agents.base_agent)}")
    except ImportError as e:
        print(f"❌ Failed to import app.core.agents.base_agent: {str(e)}")
        
    try:
        import app.core.agents.factory
        print("✅ Successfully imported app.core.agents.factory")
        print(f"Available items: {dir(app.core.agents.factory)}")
    except ImportError as e:
        print(f"❌ Failed to import app.core.agents.factory: {str(e)}")
    
if __name__ == "__main__":
    main() 