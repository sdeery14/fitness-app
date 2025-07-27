# Hugging Face Space Environment Variables Setup

After your GitHub Actions deploys your app to Hugging Face Spaces, you need to configure the API keys directly in your Hugging Face Space.

## Step 1: Go to Your Space Settings

1. Visit your deployed space: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`
2. Click the **"Settings"** tab (next to "App", "Files", etc.)

## Step 2: Add Environment Variables

In the Settings page, scroll down to find the **"Repository secrets"** or **"Variables and secrets"** section.

### Add these secrets:

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `OPENAI_API_KEY` | `sk-...` | Your OpenAI API key (if using OpenAI models) |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Your Anthropic API key (if using Claude) |

## Step 3: How to Add Each Secret

1. Click **"New secret"**
2. **Name**: Enter the variable name exactly (e.g., `OPENAI_API_KEY`)
3. **Value**: Enter your API key
4. Click **"Add secret"**
5. Repeat for each API key

## Step 4: Restart Your Space

After adding the secrets:
1. Go back to the **"App"** tab
2. Your space should automatically restart
3. If not, click the **"⟳ Restart"** button

## Important Notes:

- ✅ **Secrets are secure** - They won't be visible in logs or to other users
- ✅ **Environment variables override .env** - Even if there's a .env file, the Space secrets take priority
- ✅ **No need to redeploy** - Changes take effect immediately after restart
- ⚠️ **Case sensitive** - Variable names must match exactly

## Verification:

Your app should now work with the API keys. Check the Space logs:
1. Go to your Space
2. Click **"Logs"** tab
3. Look for successful API connections

## Troubleshooting:

If your app still shows API key errors:

1. **Check variable names** - Must be exactly `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
2. **Check API key format** - OpenAI keys start with `sk-`, Anthropic with `sk-ant-`
3. **Restart the space** - Changes may require a restart
4. **Check logs** - Look for specific error messages in the Logs tab

## Alternative: Using Hugging Face CLI (Advanced)

You can also set secrets via CLI if you have `huggingface_hub` installed:

```bash
# Install the CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Add secrets
huggingface-cli repo add-secret YOUR_USERNAME/YOUR_SPACE_NAME OPENAI_API_KEY "your_key_here"
huggingface-cli repo add-secret YOUR_USERNAME/YOUR_SPACE_NAME ANTHROPIC_API_KEY "your_key_here"
```

---

**Once you've set up these environment variables in your Hugging Face Space, your fitness app should work perfectly!** 🎉
