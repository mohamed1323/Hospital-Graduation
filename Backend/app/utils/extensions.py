import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flasgger import Swagger
from limits.storage import RedisStorage, MemoryStorage
import redis

# Initialize extensions
ma = Marshmallow()
swagger = Swagger()

def get_limiter(app):
    """Create rate limiter with appropriate storage"""
    try:
        # Try to use Redis if available
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        storage = RedisStorage(redis.from_url(redis_url))
    except Exception as e:
        app.logger.warning(f"Redis not available, falling back to memory storage: {str(e)}")
        storage = MemoryStorage()

    return Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.getenv('RATE_LIMIT_STORAGE_URL', 'memory://'),
        storage=storage
    )

def init_extensions(app):
    """Initialize Flask extensions"""
    # Initialize CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('ALLOWED_ORIGINS', ["http://localhost:3000"]),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Initialize rate limiter
    app.limiter = get_limiter(app)
    
    # Initialize Marshmallow
    ma.init_app(app)
    
    # Initialize Swagger documentation
    swagger.init_app(app, config={
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs",
        "title": "Hospital Readmission API",
        "version": "1.0.0",
        "description": "API for Hospital Readmission Prediction System",
    }) 