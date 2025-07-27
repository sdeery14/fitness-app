# GitHub Actions CI/CD Setup Guide

This guide will help you set up automatic deployment from GitHub to Hugging Face Spaces using GitHub Actions.

## Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Hugging Face Space**: You need to create a Space on Hugging Face first
3. **Hugging Face Token**: You need a write token from Hugging Face

## Step 1: Create Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Configure your space:
   - **Space name**: `fitness-ai-assistant` (or your preferred name)
   - **License**: MIT
   - **SDK**: Gradio
   - **Hardware**: CPU basic (free) or upgrade as needed
   - **Visibility**: Public or Private
4. **Important**: Initialize with a README or empty repository
5. Note down your **username** and **space name**

## Step 2: Get Hugging Face Token

1. Go to [Hugging Face Settings > Access Tokens](https://huggingface.co/settings/tokens)
2. Click "New token"
3. Configure the token:
   - **Name**: `GitHub Actions Deploy`
   - **Type**: **Write** (required for pushing code)
   - **Scopes**: Leave default or select specific repositories
4. Copy the token (you won't see it again!)

## Step 3: Configure GitHub Repository Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret** and add these three secrets:

### Required Secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `HF_TOKEN` | Your Hugging Face write token | `hf_xxxxxxxxxxxxxxxxxxxx` |
| `HF_USERNAME` | Your Hugging Face username | `yourusername` |
| `HF_SPACE_NAME` | Your space name | `fitness-ai-assistant` |

### Adding Each Secret:
1. Click **New repository secret**
2. Enter the **Name** (exactly as shown above)
3. Enter the **Secret** (the actual value)
4. Click **Add secret**
5. Repeat for all three secrets

## Step 4: Choose Your Workflow

I've created two workflow options for you:

### Option 1: Simple Workflow (`deploy-to-hf.yml`)
- Basic deployment on push to main
- Suitable for most use cases
- Fewer validation steps

### Option 2: Advanced Workflow (`deploy-to-hf-advanced.yml`)
- Comprehensive validation and error handling
- Retry logic for failed deployments
- Manual trigger option
- More detailed logging
- **Recommended for production use**

## Step 5: Test the Setup

### Option A: Push to Main Branch
1. Make any change to your code
2. Commit and push to the main branch:
   ```bash
   git add .
   git commit -m "Test GitHub Actions deployment"
   git push origin main
   ```
3. Check the **Actions** tab in your GitHub repository
4. Watch the deployment process

### Option B: Manual Trigger (Advanced Workflow Only)
1. Go to **Actions** tab in your GitHub repository
2. Select "Deploy to Hugging Face Spaces (Advanced)"
3. Click **Run workflow**
4. Optionally enable "Force deployment"
5. Click **Run workflow**

## Step 6: Verify Deployment

1. Check that the GitHub Action completed successfully
2. Visit your Hugging Face Space: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`
3. Wait for the Space to build (may take a few minutes)
4. Test your deployed app

## Troubleshooting

### Common Issues:

#### 1. "Failed to clone HF Space"
- **Cause**: Incorrect `HF_USERNAME` or `HF_SPACE_NAME`
- **Solution**: Double-check the secrets match your actual HF username and space name

#### 2. "Permission denied"
- **Cause**: `HF_TOKEN` doesn't have write permissions
- **Solution**: Generate a new token with **Write** access

#### 3. "Space not found"
- **Cause**: Space doesn't exist or name is wrong
- **Solution**: Create the space first on Hugging Face, then update the secret

#### 4. "Build failed on Hugging Face"
- **Cause**: Missing dependencies or code errors
- **Solution**: Check the Hugging Face Space logs for specific errors

### Debugging Steps:

1. **Check GitHub Action Logs**:
   - Go to Actions tab > Click on failed run > Expand failed steps

2. **Verify Secrets**:
   - Go to Repository Settings > Secrets > Ensure all three secrets are set

3. **Test Locally**:
   - Run `python fitness_agent/app.py` locally to ensure it works
   - Check for any import errors

4. **Check Hugging Face Space Logs**:
   - Visit your space and check the "Logs" tab for build errors

## Advanced Configuration

### Customizing Deployment Triggers

You can modify when deployments happen by editing the workflow file:

```yaml
on:
  push:
    branches: [ main, develop ]  # Deploy from multiple branches
    paths-ignore:
      - 'docs/**'               # Ignore documentation changes
  release:
    types: [ published ]        # Deploy on releases
```

### Environment-Specific Deployments

For multiple environments (dev, staging, prod):

1. Create separate HF Spaces for each environment
2. Use different secret names: `HF_SPACE_NAME_DEV`, `HF_SPACE_NAME_PROD`
3. Modify the workflow to use different secrets based on branch

### Slack/Discord Notifications

Add notification steps to your workflow:

```yaml
- name: Notify on Success
  if: success()
  run: |
    curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"🚀 Fitness App deployed successfully!"}' \
    ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Security Best Practices

1. **Token Rotation**: Regularly rotate your HF tokens
2. **Scope Limitation**: Use minimal required token permissions
3. **Secret Management**: Never commit tokens to code
4. **Branch Protection**: Enable branch protection on main branch
5. **Review Required**: Require PR reviews for production deployments

## Workflow Features

### What the Workflow Does:

1. **Validates** your code structure and syntax
2. **Tests** critical imports
3. **Syncs** your code to Hugging Face Space
4. **Handles** errors gracefully with retries
5. **Provides** detailed logs and status updates

### Automatic Triggers:

- Push to main branch (excluding documentation changes)
- Manual workflow dispatch
- Merged pull requests to main

### Smart Deployment:

- Only deploys when there are actual code changes
- Skips deployment for documentation-only changes
- Provides force-deploy option for manual runs

## Support

If you encounter issues:

1. Check this troubleshooting guide
2. Review GitHub Action logs
3. Check Hugging Face Space logs
4. Verify all secrets are correctly configured

Happy deploying! 🚀
