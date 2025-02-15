FROM python:3.12-slim

# Install Poetry
RUN pip install --upgrade poetry

# Set the working directory to /app (not /code)
WORKDIR /app

# Copy only dependency files first for caching
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --only main

# Create a user for security
RUN useradd -m -u 1000 user

# Switch to non-root user
USER user

# Set environment variables for poetry and path
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Copy project files into container
COPY --chown=user . .

# Expose port for Gradio
EXPOSE 7860

# Run the Gradio app
CMD ["poetry", "run", "python", "app.py"]
