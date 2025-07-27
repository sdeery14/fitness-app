# GitHub Actions Setup Helper Script (PowerShell)
# This script helps you configure the required secrets for GitHub Actions deployment

Write-Host "🚀 GitHub Actions Setup Helper" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will help you gather the information needed to set up"
Write-Host "automatic deployment to Hugging Face Spaces via GitHub Actions."
Write-Host ""

# Function to print colored output
function Write-Step($message) {
    Write-Host "📋 $message" -ForegroundColor Blue
}

function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "⚠️  $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
}

# Check if running in Git repository
try {
    $gitDir = git rev-parse --git-dir 2>$null
    if (-not $gitDir) {
        throw "Not a git repository"
    }
} catch {
    Write-Error "This script must be run in a Git repository"
    exit 1
}

# Get repository information
try {
    $repoUrl = git remote get-url origin 2>$null
    if ($repoUrl -match "github\.com[:/]([^/]+)/([^/]+)(\.git)?$") {
        $githubUsername = $matches[1]
        $repoName = $matches[2] -replace "\.git$", ""
        Write-Success "Detected GitHub repository: $githubUsername/$repoName"
    } else {
        Write-Warning "Could not detect GitHub repository information"
        Write-Host "Please ensure this repository is connected to GitHub"
    }
} catch {
    Write-Warning "Could not get repository information"
}

Write-Host ""
Write-Step "Step 1: Hugging Face Information"
Write-Host "You'll need to provide your Hugging Face details:"
Write-Host ""

# Get Hugging Face username
$hfUsername = Read-Host "Enter your Hugging Face username"
if (-not $hfUsername) {
    Write-Error "Hugging Face username is required"
    exit 1
}

# Get Hugging Face space name
Write-Host ""
Write-Host "Enter your Hugging Face Space name (the space must already exist):"
Write-Host "Example: fitness-ai-assistant"
$hfSpaceName = Read-Host "Space name"
if (-not $hfSpaceName) {
    Write-Error "Hugging Face space name is required"
    exit 1
}

# Validate space exists
Write-Host ""
Write-Step "Validating Hugging Face Space..."
$spaceUrl = "https://huggingface.co/spaces/$hfUsername/$hfSpaceName"
try {
    $response = Invoke-WebRequest -Uri $spaceUrl -Method Head -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Success "Space exists: $spaceUrl"
    } else {
        Write-Warning "Could not verify space exists. Please ensure you've created it first."
        Write-Host "Create it at: https://huggingface.co/spaces"
    }
} catch {
    Write-Warning "Could not verify space exists. Please ensure you've created it first."
    Write-Host "Create it at: https://huggingface.co/spaces"
}

# Get Hugging Face token
Write-Host ""
Write-Step "Step 2: Hugging Face Token"
Write-Host "You need a WRITE token from Hugging Face:"
Write-Host "1. Go to: https://huggingface.co/settings/tokens"
Write-Host "2. Click 'New token'"
Write-Host "3. Set Type to 'Write'"
Write-Host "4. Copy the token"
Write-Host ""
Write-Host "⚠️  Important: The token will start with 'hf_' and should have WRITE permissions" -ForegroundColor Yellow
Write-Host ""
$hfToken = Read-Host "Enter your Hugging Face token" -AsSecureString
$hfTokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($hfToken))

if (-not $hfTokenPlain) {
    Write-Error "Hugging Face token is required"
    exit 1
}

if (-not $hfTokenPlain.StartsWith("hf_")) {
    Write-Warning "Token doesn't start with 'hf_' - please verify it's correct"
}

# Test token
Write-Host ""
Write-Step "Testing Hugging Face token..."
try {
    $headers = @{ "Authorization" = "Bearer $hfTokenPlain" }
    $whoami = Invoke-RestMethod -Uri "https://huggingface.co/api/whoami" -Headers $headers -ErrorAction SilentlyContinue
    if ($whoami.name) {
        Write-Success "Token appears to be valid"
    } else {
        Write-Warning "Could not validate token. Please verify it has WRITE permissions."
    }
} catch {
    Write-Warning "Could not validate token. Please verify it has WRITE permissions."
}

Write-Host ""
Write-Step "Step 3: GitHub Repository Secrets"
Write-Host "Now you need to add these secrets to your GitHub repository:"
Write-Host ""
if ($githubUsername -and $repoName) {
    Write-Host "Repository: https://github.com/$githubUsername/$repoName/settings/secrets/actions"
}
Write-Host ""
Write-Host "Add these three secrets:"
Write-Host ""
Write-Host "┌─────────────────┬────────────────────────────────────┐"
Write-Host "│ Secret Name     │ Value                              │"
Write-Host "├─────────────────┼────────────────────────────────────┤"
Write-Host "│ HF_TOKEN        │ $($hfTokenPlain.Substring(0, [Math]::Min(10, $hfTokenPlain.Length)))...                 │"
Write-Host "│ HF_USERNAME     │ $hfUsername                       │"
Write-Host "│ HF_SPACE_NAME   │ $hfSpaceName                     │"
Write-Host "└─────────────────┴────────────────────────────────────┘"
Write-Host ""

Write-Step "Step 4: Adding Secrets to GitHub"
Write-Host "Follow these steps:"
Write-Host ""
Write-Host "1. Go to your repository on GitHub"
Write-Host "2. Click 'Settings' tab"
Write-Host "3. Click 'Secrets and variables' > 'Actions'"
Write-Host "4. Click 'New repository secret'"
Write-Host "5. Add each secret with the exact name and value shown above"
Write-Host ""

# Check if GitHub CLI is available
$ghCliAvailable = $false
try {
    $ghVersion = gh --version 2>$null
    if ($ghVersion) {
        $ghCliAvailable = $true
    }
} catch {
    $ghCliAvailable = $false
}

if ($ghCliAvailable) {
    Write-Host ""
    Write-Step "GitHub CLI Detected"
    Write-Host "Would you like me to set the secrets automatically using GitHub CLI?"
    Write-Host "This requires you to be logged in to GitHub CLI."
    Write-Host ""
    $autoSet = Read-Host "Set secrets automatically? (y/N)"
    
    if ($autoSet -match "^[Yy]$") {
        Write-Step "Setting secrets via GitHub CLI..."
        
        # Check if logged in
        try {
            gh auth status | Out-Null
        } catch {
            Write-Error "Please login to GitHub CLI first: gh auth login"
            exit 1
        }
        
        # Set secrets
        try {
            $hfTokenPlain | gh secret set HF_TOKEN
            $hfUsername | gh secret set HF_USERNAME
            $hfSpaceName | gh secret set HF_SPACE_NAME
            
            Write-Success "Secrets set successfully!"
        } catch {
            Write-Error "Failed to set secrets via GitHub CLI: $_"
        }
    }
} else {
    Write-Warning "GitHub CLI not found. You'll need to set secrets manually."
    Write-Host "Install it from: https://cli.github.com/"
}

Write-Host ""
Write-Step "Step 5: Test the Setup"
Write-Host "To test your GitHub Actions setup:"
Write-Host ""
Write-Host "1. Make a small change to your code"
Write-Host "2. Commit and push to main branch:"
Write-Host "   git add ."
Write-Host "   git commit -m `"Test GitHub Actions deployment`""
Write-Host "   git push origin main"
Write-Host ""
Write-Host "3. Check the Actions tab in your GitHub repository"
Write-Host "4. Watch the deployment process"
Write-Host ""
Write-Host "Your app will be deployed to: $spaceUrl"
Write-Host ""

Write-Step "Summary"
Write-Host "✅ Hugging Face Username: $hfUsername" -ForegroundColor Green
Write-Host "✅ Hugging Face Space: $hfSpaceName" -ForegroundColor Green
Write-Host "✅ Space URL: $spaceUrl" -ForegroundColor Green
if ($githubUsername -and $repoName) {
    Write-Host "✅ GitHub Repository: $githubUsername/$repoName" -ForegroundColor Green
}
Write-Host ""
Write-Success "Setup complete! Push to main branch to trigger deployment."
Write-Host ""
Write-Host "📚 For more details, see: GITHUB_ACTIONS_SETUP.md" -ForegroundColor Cyan

# Clear the token from memory
$hfTokenPlain = $null
$hfToken = $null
