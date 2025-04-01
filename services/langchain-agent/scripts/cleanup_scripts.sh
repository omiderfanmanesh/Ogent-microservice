#!/bin/bash
set -e

echo "================================================="
echo "Cleaning up deployment scripts for langchain-agent"
echo "================================================="

# Navigate to the scripts directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create a backup directory for old scripts
mkdir -p .backup

# Move older deployment scripts to backup
echo "Moving older deployment scripts to backup..."
mv deploy_agent_fixes.sh .backup/ 2>/dev/null || :
mv deploy_fixes.sh .backup/ 2>/dev/null || :
mv final_deploy.sh .backup/ 2>/dev/null || :
mv final_deploy_2.sh .backup/ 2>/dev/null || :
mv final_deploy_3.sh .backup/ 2>/dev/null || :
mv final_deploy_5.sh .backup/ 2>/dev/null || :
mv final_deploy_6.sh .backup/ 2>/dev/null || :
mv simplified_deploy.sh .backup/ 2>/dev/null || :

# Keep only the main deploy.sh as the reference implementation
echo "Keeping only deploy.sh as the main deployment script"

# Update README to reflect changes
cat > README.md << 'EOF'
# LangChain Agent Service Scripts

This directory contains deployment and maintenance scripts for the LangChain Agent service.

## Scripts

- `deploy.sh` - Main deployment script for applying fixes to the agent service
- `run_no_migration.py` - Script to run the service without database migrations
- `cleanup_scripts.sh` - Script used to clean up redundant deployment scripts

## Usage

To deploy the latest fixes to the agent service:

```bash
./deploy.sh
```

To run the service without migrations:

```bash
python run_no_migration.py
```
EOF

echo ""
echo "Cleanup completed!"
echo "The main deployment script is now deploy.sh"
echo "Older scripts have been moved to .backup directory" 