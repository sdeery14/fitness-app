#!/bin/bash
# Setup script for all Poetry environments

echo "🚀 Setting up Fitness App Monorepo..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Setup shared core library
echo "📦 Setting up shared core library..."
cd shared
poetry install
cd ..

# Setup Gradio app
echo "🎨 Setting up Gradio app..."
cd apps/gradio-app
poetry install
cd ../..

echo "✅ All environments set up successfully!"
echo ""
echo "💡 Next steps:"
echo "   - Copy your .env file to the root directory (if not already there)"
echo "   - Test the Gradio app: cd apps/gradio-app && poetry run fitness-gradio"
echo "   - Or use the run scripts in the scripts/ directory"
