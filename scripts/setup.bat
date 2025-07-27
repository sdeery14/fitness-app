@echo off
REM Setup script for Windows

echo 🚀 Setting up Fitness App Monorepo...

REM Check if Poetry is installed
poetry --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Poetry is not installed. Please install Poetry first:
    echo    https://python-poetry.org/docs/#installation
    exit /b 1
)

REM Setup shared core library
echo 📦 Setting up shared core library...
cd shared
poetry install
cd ..

REM Setup Gradio app
echo 🎨 Setting up Gradio app...
cd apps\gradio-app
poetry install
cd ..\..

echo ✅ All environments set up successfully!
echo.
echo 💡 Next steps:
echo    - Copy your .env file to the root directory (if not already there)
echo    - Test the Gradio app: cd apps\gradio-app ^&^& poetry run fitness-gradio
echo    - Or use the run scripts in the scripts\ directory
