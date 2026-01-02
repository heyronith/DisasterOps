#!/bin/bash
# Setup script for DisasterOps environment variables

echo "DisasterOps Environment Setup"
echo "=============================="
echo ""
echo "Please enter your OpenAI API key:"
echo "(Get it from: https://platform.openai.com/api-keys)"
echo ""
read -s API_KEY

if [ -z "$API_KEY" ]; then
    echo "Error: API key cannot be empty"
    exit 1
fi

# Export for current session
export OPENAI_API_KEY="$API_KEY"
echo ""
echo "✓ OPENAI_API_KEY set for current session"
echo ""
echo "To make this permanent, add to your ~/.zshrc:"
echo "  export OPENAI_API_KEY=\"$API_KEY\""
echo ""

