FROM python:3.12-slim

# Install Poetry
RUN pip install --upgrade poetry

# Configure Poetry to create virtualenvs inside the project directory
ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true

# Set the working directory
WORKDIR /app

# Copy dependency files first (for Docker cache efficiency)
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --only main

# Create a user for security
RUN useradd -m -u 1000 user

# Switch to non-root user
USER user

# Set environment variables for poetry and path
ENV PATH="/app/.venv/bin:$PATH"

# Copy project files into container
COPY --chown=user . .

# Expose port for Gradio
EXPOSE 7860

# Run the Gradio app
CMD ["python", "app.py"]
