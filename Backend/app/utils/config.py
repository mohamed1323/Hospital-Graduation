import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # MongoDB Configuration
    MONGODB_USERNAME = os.getenv('MONGODB_USERNAME', 'admin')
    MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', 'secure_password123')
    MONGODB_AUTH_SOURCE = os.getenv('MONGODB_AUTH_SOURCE', 'admin')
    MONGODB_HOST = os.getenv('MONGODB_HOST', 'mongodb://localhost:27017/hospital_db')
    MONGODB_DB = os.getenv('MONGODB_DB', 'hospital_db')
    
    @property
    def MONGODB_SETTINGS(self):
        """MongoDB connection settings with authentication"""
        return {
            'host': self.MONGODB_HOST,
            'db': self.MONGODB_DB,
            'username': self.MONGODB_USERNAME,
            'password': self.MONGODB_PASSWORD,
            'authentication_source': self.MONGODB_AUTH_SOURCE,
            'connect': True,
            'retryWrites': True
        }
    
    # ML Model Configuration
    MODEL_PATH = os.path.join('app', 'ml_models', 'readmission_model.pkl')
    MODEL_VERSION = os.getenv('MODEL_VERSION', '1.0.0')
    
    # Feature Configuration
    REQUIRED_FEATURES = [
        'age', 'gender', 'primary_diagnosis', 'num_procedures',
        'days_in_hospital', 'comorbidity_score', 'discharge_to'
    ]
    
    # Risk Level Thresholds
    RISK_THRESHOLDS = {
        'low': 0.3,    # Probability < 0.3
        'medium': 0.6  # 0.3 <= Probability < 0.6
        # high: Probability >= 0.6
    }
    
    # API Rate Limiting
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-here')
    JWT_EXPIRATION_DAYS = int(os.getenv('JWT_EXPIRATION_DAYS', '1'))
    
    # Feature Validation Rules
    VALIDATION_RULES = {
        'age': {
            'min': 0,
            'max': 120
        },
        'num_procedures': {
            'min': 0
        },
        'days_in_hospital': {
            'min': 0
        },
        'comorbidity_score': {
            'min': 0
        }
    }
    
    # Model Feature Groups
    CATEGORICAL_FEATURES = ['gender', 'primary_diagnosis', 'discharge_to']
    NUMERICAL_FEATURES = ['age', 'num_procedures', 'days_in_hospital', 'comorbidity_score']
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Security Configuration
    BCRYPT_ROUNDS = int(os.getenv('BCRYPT_ROUNDS', '12'))
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
    
    @staticmethod
    def init_app(app):
        """Initialize application with config settings"""
        app.config.from_object(Config)
        
        # Ensure required environment variables are set
        required_env_vars = [
            'SECRET_KEY',
            'MONGODB_HOST',
            'MONGODB_DB',
            'MONGODB_USERNAME',
            'MONGODB_PASSWORD'
        ]
        
        missing_vars = [var for var in required_env_vars 
                       if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(Config.LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    MONGODB_DB = os.getenv('MONGODB_DB', 'hospital_db')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGODB_DB = os.getenv('MONGODB_DB', 'hospital_db_test')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    RATELIMIT_DEFAULT = "100 per day"  # Stricter rate limiting in production

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 