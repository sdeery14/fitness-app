FROM python:3.12-slim

# Install Poetry
RUN pip install --upgrade poetry

# Set the working directory
WORKDIR /code

# Copy pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock /code/

# Install dependencies
RUN poetry install --no-root --only main

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copy the current directory contents into the container at $HOME/app setting the owner to the user
COPY --chown=user . $HOME/app

# Expose the port that Gradio will run on
EXPOSE 7860

# Run the Gradio app
CMD ["poetry", "run", "python", "app.py"]
