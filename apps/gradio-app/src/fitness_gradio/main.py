"""
Main entry point for the Gradio fitness app.
"""
import sys
import json
from pathlib import Path

# Add the shared library to the Python path if needed
shared_path = Path(__file__).parent.parent.parent.parent / "shared" / "src"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from fitness_core import setup_logging, Config, get_logger
from .ui import create_fitness_app

# Configure logging
setup_logging(level=Config.LOG_LEVEL, log_file=Config.LOG_FILE)
logger = get_logger(__name__)


def main():
    """Main entry point for the Gradio application."""
    try:
        # Validate configuration
        config_status = Config.validate_config()
        
        if not config_status["valid"]:
            logger.error("Configuration validation failed:")
            for error in config_status["errors"]:
                logger.error(f"  - {error}")
            sys.exit(1)
        
        # Show warnings
        for warning in config_status["warnings"]:
            logger.warning(warning)
        
        # Create and launch the Gradio app
        logger.info("🎨 Starting Fitness Gradio App...")
        
        app = create_fitness_app()
        gradio_config = Config.get_gradio_config()
        
        # Add custom route for manifest.json after the app is created
        @app.app.get("/manifest.json")
        async def get_manifest():
            """Serve the manifest.json file."""
            manifest = {
                "name": "Fitness AI Assistant",
                "short_name": "Fitness AI",
                "description": "AI-powered fitness assistant for personalized health and wellness guidance",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#ffffff",
                "theme_color": "#000000",
                "icons": [
                    {
                        "src": "/favicon.ico",
                        "sizes": "any",
                        "type": "image/x-icon"
                    }
                ]
            }
            from fastapi.responses import JSONResponse
            return JSONResponse(content=manifest)
        
        logger.info(f"🚀 Launching on http://{gradio_config['server_name']}:{gradio_config['server_port']}")
        
        app.launch(**gradio_config)
        
    except Exception as e:
        import traceback
        logger.error(f"Failed to start Gradio app: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
