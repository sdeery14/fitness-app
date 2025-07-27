#!/bin/bash

# GitHub Actions Setup Helper Script
# This script helps you configure the required secrets for GitHub Actions deployment

echo "🚀 GitHub Actions Setup Helper"
echo "==============================="
echo ""
echo "This script will help you gather the information needed to set up"
echo "automatic deployment to Hugging Face Spaces via GitHub Actions."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running in Git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "This script must be run in a Git repository"
    exit 1
fi

# Get repository information
REPO_URL=$(git remote get-url origin 2>/dev/null)
if [[ $REPO_URL =~ github\.com[:/]([^/]+)/([^/]+)(\.git)?$ ]]; then
    GITHUB_USERNAME="${BASH_REMATCH[1]}"
    REPO_NAME="${BASH_REMATCH[2]%.git}"
    print_success "Detected GitHub repository: $GITHUB_USERNAME/$REPO_NAME"
else
    print_warning "Could not detect GitHub repository information"
    echo "Please ensure this repository is connected to GitHub"
fi

echo ""
print_step "Step 1: Hugging Face Information"
echo "You'll need to provide your Hugging Face details:"
echo ""

# Get Hugging Face username
read -p "Enter your Hugging Face username: " HF_USERNAME
if [ -z "$HF_USERNAME" ]; then
    print_error "Hugging Face username is required"
    exit 1
fi

# Get Hugging Face space name
echo ""
echo "Enter your Hugging Face Space name (the space must already exist):"
echo "Example: fitness-ai-assistant"
read -p "Space name: " HF_SPACE_NAME
if [ -z "$HF_SPACE_NAME" ]; then
    print_error "Hugging Face space name is required"
    exit 1
fi

# Validate space exists
echo ""
print_step "Validating Hugging Face Space..."
SPACE_URL="https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME"
if curl -s --head "$SPACE_URL" | grep -q "200 OK"; then
    print_success "Space exists: $SPACE_URL"
else
    print_warning "Could not verify space exists. Please ensure you've created it first."
    echo "Create it at: https://huggingface.co/spaces"
fi

# Get Hugging Face token
echo ""
print_step "Step 2: Hugging Face Token"
echo "You need a WRITE token from Hugging Face:"
echo "1. Go to: https://huggingface.co/settings/tokens"
echo "2. Click 'New token'"
echo "3. Set Type to 'Write'"
echo "4. Copy the token"
echo ""
echo "⚠️  Important: The token will start with 'hf_' and should have WRITE permissions"
echo ""
read -s -p "Enter your Hugging Face token: " HF_TOKEN
echo ""

if [ -z "$HF_TOKEN" ]; then
    print_error "Hugging Face token is required"
    exit 1
fi

if [[ ! $HF_TOKEN =~ ^hf_ ]]; then
    print_warning "Token doesn't start with 'hf_' - please verify it's correct"
fi

# Test token
echo ""
print_step "Testing Hugging Face token..."
if curl -s -H "Authorization: Bearer $HF_TOKEN" "https://huggingface.co/api/whoami" | grep -q "name"; then
    print_success "Token appears to be valid"
else
    print_warning "Could not validate token. Please verify it has WRITE permissions."
fi

echo ""
print_step "Step 3: GitHub Repository Secrets"
echo "Now you need to add these secrets to your GitHub repository:"
echo ""
echo "Repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME/settings/secrets/actions"
echo ""
echo "Add these three secrets:"
echo ""
echo "┌─────────────────┬────────────────────────────────────┐"
echo "│ Secret Name     │ Value                              │"
echo "├─────────────────┼────────────────────────────────────┤"
echo "│ HF_TOKEN        │ ${HF_TOKEN:0:10}...                 │"
echo "│ HF_USERNAME     │ $HF_USERNAME                       │"
echo "│ HF_SPACE_NAME   │ $HF_SPACE_NAME                     │"
echo "└─────────────────┴────────────────────────────────────┘"
echo ""

print_step "Step 4: Adding Secrets to GitHub"
echo "Follow these steps:"
echo ""
echo "1. Go to your repository on GitHub"
echo "2. Click 'Settings' tab"
echo "3. Click 'Secrets and variables' > 'Actions'"
echo "4. Click 'New repository secret'"
echo "5. Add each secret with the exact name and value shown above"
echo ""

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo ""
    print_step "GitHub CLI Detected"
    echo "Would you like me to set the secrets automatically using GitHub CLI?"
    echo "This requires you to be logged in to GitHub CLI."
    echo ""
    read -p "Set secrets automatically? (y/N): " AUTO_SET
    
    if [[ $AUTO_SET =~ ^[Yy]$ ]]; then
        print_step "Setting secrets via GitHub CLI..."
        
        # Check if logged in
        if ! gh auth status > /dev/null 2>&1; then
            print_error "Please login to GitHub CLI first: gh auth login"
            exit 1
        fi
        
        # Set secrets
        echo "$HF_TOKEN" | gh secret set HF_TOKEN
        echo "$HF_USERNAME" | gh secret set HF_USERNAME
        echo "$HF_SPACE_NAME" | gh secret set HF_SPACE_NAME
        
        print_success "Secrets set successfully!"
    fi
else
    print_warning "GitHub CLI not found. You'll need to set secrets manually."
fi

echo ""
print_step "Step 5: Test the Setup"
echo "To test your GitHub Actions setup:"
echo ""
echo "1. Make a small change to your code"
echo "2. Commit and push to main branch:"
echo "   git add ."
echo "   git commit -m \"Test GitHub Actions deployment\""
echo "   git push origin main"
echo ""
echo "3. Check the Actions tab in your GitHub repository"
echo "4. Watch the deployment process"
echo ""
echo "Your app will be deployed to: $SPACE_URL"
echo ""

print_step "Summary"
echo "✅ Hugging Face Username: $HF_USERNAME"
echo "✅ Hugging Face Space: $HF_SPACE_NAME"
echo "✅ Space URL: $SPACE_URL"
echo "✅ GitHub Repository: $GITHUB_USERNAME/$REPO_NAME"
echo ""
print_success "Setup complete! Push to main branch to trigger deployment."
echo ""
echo "📚 For more details, see: GITHUB_ACTIONS_SETUP.md"
