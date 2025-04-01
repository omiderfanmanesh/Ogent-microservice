#!/bin/bash
set -e

echo "================================================="
echo "Main cleanup script for langchain-agent service"
echo "================================================="

# Make sure all cleanup scripts are executable
chmod +x scripts/cleanup_scripts.sh
chmod +x scripts/cleanup_fixes.sh

# Run the organize script again to make sure everything is in the right place
if [ -f "organize.sh" ]; then
  echo "Running organize.sh to ensure proper directory structure..."
  chmod +x organize.sh
  ./organize.sh
fi

# Run cleanup scripts
echo "Running script cleanup..."
./scripts/cleanup_scripts.sh

echo "Running fixes cleanup..."
./scripts/cleanup_fixes.sh

# Remove the organize script since it's no longer needed
if [ -f "organize.sh" ]; then
  echo "Removing temporary organize.sh script..."
  rm organize.sh
fi

echo ""
echo "All cleanup completed!"
echo "The langchain-agent service directory is now properly organized."
echo "- Deployment scripts are in scripts/deploy.sh"
echo "- Fixes are in the fixes/ directory with clear names"
echo "- Test and verification tools are in the tools/ directory" 