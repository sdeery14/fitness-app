---
title: Fitness App
emoji: 🏋️
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
dockerfile_path: Dockerfile
app_port: 7860
---

# Fitness App

Welcome to the Fitness App repository! This project is a chatbot application designed to assist users with achieving their fitness goals. The application leverages Gradio for the user interface and OpenAI for natural language processing. The app is hosted on Hugging Face Spaces and uses GitHub Actions for continuous integration and deployment.

## Features

- **Chatbot Interface**: Interact with the chatbot to get fitness-related information.
- **Gradio Integration**: User-friendly interface built with Gradio.
- **OpenAI Integration**: Advanced natural language processing with OpenAI.
- **Continuous Deployment**: Automated deployment to Hugging Face Spaces using GitHub Actions.

## Installation

To get started with the project, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/sdeery14/fitness-app.git
    cd fitness-app
    ```

2. **Install Poetry**:
    Follow the instructions at [Poetry's official website](https://python-poetry.org/docs/#installation) to install Poetry.

3. **Install dependencies**:
    ```bash
    poetry install
    ```

## Usage

To run the application locally, use the following command:
```bash
poetry run python app.py
```

## Deployment

The application is automatically deployed to Hugging Face Spaces using GitHub Actions. Ensure that your repository is connected to Hugging Face Spaces and that you have set up the necessary secrets in your GitHub repository.

## Contributing

We welcome contributions! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact the repository owner.
