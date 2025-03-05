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

## Calculations for Calories and Macros

### Example Calculation
For a 25-year-old male, 180 cm, 80 kg, moderately active, bulking (+300 kcal surplus):

**BMR Calculation:**
BMR=(10×80)+(6.25×180)−(5×25)+5
BMR=800+1125−125+5=1805 kcal

**TDEE Calculation:**
TDEE=1805×1.55=2798 kcal

**Bulking Calories:**
2798+300=3098 kcal

**Macronutrient Breakdown:**

**Protein:** 30% of 3098 kcal
3098×0.30=929.4 kcal÷4=232.4 g

**Fats:** 20% of 3098 kcal
3098×0.20=619.6 kcal÷9=68.8 g

**Carbs:** Remaining calories (3098 - (929.4 + 619.6))
1549 kcal÷4=387.3 g

**Final Plan:**

- Calories: 3098 kcal
- Protein: 232g
- Fats: 69g
- Carbs: 387g

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
