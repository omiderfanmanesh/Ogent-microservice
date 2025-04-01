#!/bin/bash
set -e

echo "================================================="
echo "Final cleanup for langchain-agent service"
echo "================================================="

# Navigate to the fixes directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
FIXES_DIR="$ROOT_DIR/fixes"
cd "$FIXES_DIR"

# Move the *_fix.py files to backup as they're duplicates now
echo "Moving duplicate *_fix.py files to backup..."
mv *_fix.py .backup/ 2>/dev/null || :

echo ""
echo "Final cleanup completed!"
echo "The langchain-agent service directory is now fully organized." 