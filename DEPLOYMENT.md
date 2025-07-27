# Deployment Guide for Hugging Face Spaces

## Quick Deployment Steps

### 1. Create a New Space on Hugging Face

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose:
   - **Space name**: `fitness-ai-assistant` (or your preferred name)
   - **License**: MIT
   - **SDK**: Gradio
   - **Space hardware**: CPU basic (free tier) or GPU if needed
   - **Visibility**: Public or Private

### 2. Clone Your New Space Repository

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME
```

### 3. Add Your Code

Copy all files from your fitness-app directory to the cloned space directory:

- `app.py` (root level entry point)
- `requirements.txt`
- `README.md` (with HF frontmatter)
- `fitness_agent/` directory with all your code
- `.env.example`

### 4. Set Environment Variables in Hugging Face

1. Go to your Space settings on Hugging Face
2. Navigate to "Repository secrets"
3. Add these secrets:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ANTHROPIC_API_KEY`: Your Anthropic API key (if using Claude)

### 5. Push to Hugging Face

```bash
git add .
git commit -m "Initial deployment of Fitness AI Assistant"
git push origin main
```

### 6. Wait for Build

- Hugging Face will automatically build and deploy your space
- Check the build logs for any errors
- Once successful, your app will be available at: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`

## Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **API Key Issues**: Verify environment variables are set correctly in Space settings
3. **Memory Issues**: Consider upgrading to a higher tier if using large models
4. **Timeout Issues**: Increase `startup_duration_timeout` in README frontmatter

### Testing Locally:

Before deploying, test your app locally:

```bash
pip install -r requirements.txt
python app.py
```

## Advanced Configuration

### Custom Hardware:
- For faster performance, consider upgrading to GPU hardware
- T4 small is good for most AI applications

### Private Spaces:
- Set visibility to private if you want to control access
- Can still share via direct links

### Custom Domain:
- Available for Pro subscribers
- Configure in Space settings

## Monitoring

- Check Space analytics in the Hugging Face dashboard
- Monitor usage and performance
- Set up notifications for errors

## Updates

To update your deployed app:
1. Make changes locally
2. Test thoroughly
3. Commit and push to the HF repository
4. HF will automatically redeploy
