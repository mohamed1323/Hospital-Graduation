import os
import sys
import signal
import logging
from pathlib import Path
from werkzeug.serving import run_simple
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

def create_log_directory():
    """Create log directory if it doesn't exist"""
    try:
        # Get the absolute path to the log file
        log_file = os.getenv('LOG_FILE', 'logs/app.log')
        log_path = Path(log_file)
        
        # Create all parent directories
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty log file if it doesn't exist
        if not log_path.exists():
            log_path.touch()
            
        return str(log_path.absolute())
    except Exception as e:
        print(f"Error creating log directory: {str(e)}")
        sys.exit(1)

# Create log directory before configuring logging
log_file_path = create_log_directory()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file_path, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}. Performing graceful shutdown...")
    sys.exit(0)

def setup_signal_handlers():
    """Setup handlers for various signals"""
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Handle termination
    if hasattr(signal, 'SIGBREAK'):  # Windows Ctrl+Break
        signal.signal(signal.SIGBREAK, signal_handler)

def validate_environment():
    """Validate required environment variables"""
    required_vars = [
        'SECRET_KEY',
        'MONGODB_HOST',
        'MONGODB_DB',
        'MONGODB_USERNAME',
        'MONGODB_PASSWORD'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

def main():
    """Main function to run the application"""
    try:
        # Initial setup
        setup_signal_handlers()
        validate_environment()
        
        # Create Flask application
        app = create_app()
        
        # Get configuration from environment
        host = os.getenv('FLASK_HOST', '127.0.0.1')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
        
        # Log startup information
        logger.info(f"Starting server on {host}:{port}")
        logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
        logger.info(f"Debug mode: {'enabled' if debug else 'disabled'}")
        logger.info(f"Log file: {log_file_path}")
        
        # Run the application
        if debug:
            # Development server with reloader
            logger.info("Running in development mode with reloader")
            app.run(
                host=host,
                port=port,
                debug=debug,
                use_reloader=True,
                threaded=True,
                use_debugger=True
            )
        else:
            # Production server
            logger.info("Running in production mode")
            run_simple(
                hostname=host,
                port=port,
                application=app,
                use_reloader=False,
                threaded=True,
                ssl_context='adhoc'  # Enable HTTPS in production
            )
            
    except OSError as e:
        if e.errno == 98:  # Address already in use
            logger.error(f"Port {port} is already in use. Please choose a different port.")
        else:
            logger.error(f"OS Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main() 