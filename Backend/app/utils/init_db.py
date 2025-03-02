import os
import sys
import logging
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_admin_user(client):
    """Create admin user in MongoDB"""
    try:
        admin_db = client.admin
        admin_db.command('createUser', os.getenv('MONGODB_USERNAME', 'admin'), pwd=os.getenv('MONGODB_PASSWORD', 'secure_password123'),
                        roles=[{'role': 'userAdminAnyDatabase', 'db': 'admin'},
                               {'role': 'readWriteAnyDatabase', 'db': 'admin'}])
        logger.info("MongoDB admin user created successfully")
    except Exception as e:
        logger.warning(f"Admin user creation failed (might already exist): {str(e)}")

def init_database():
    """Initialize the MongoDB database"""
    try:
        # Connect to MongoDB without authentication first
        client = MongoClient('mongodb://localhost:27017')
        
        # Create admin user if doesn't exist
        create_admin_user(client)
        
        # Reconnect with authentication
        client = MongoClient(
            host=os.getenv('MONGODB_HOST', 'mongodb://localhost:27017/hospital_db'),
            username=os.getenv('MONGODB_USERNAME', 'admin'),
            password=os.getenv('MONGODB_PASSWORD', 'secure_password123'),
            authSource=os.getenv('MONGODB_AUTH_SOURCE', 'admin')
        )
        
        # Get database
        db = client[os.getenv('MONGODB_DB', 'hospital_db')]
        
        # Create collections with validation
        db.create_collection('users')
        db.create_collection('patients')
        db.create_collection('predictions')
        
        # Create indexes
        db.users.create_index('email', unique=True)
        db.users.create_index('username', unique=True)
        db.patients.create_index('medical_record_number', unique=True)
        db.patients.create_index([('user', 1)])
        db.predictions.create_index([('patient', 1), ('created_at', -1)])
        
        # Create default admin user in the application
        default_admin = {
            'username': 'admin',
            'email': 'admin@hospital.com',
            'password_hash': generate_password_hash('admin123'),
            'role': 'admin',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        try:
            db.users.insert_one(default_admin)
            logger.info("Default admin user created successfully")
        except Exception as e:
            logger.warning(f"Default admin user creation failed (might already exist): {str(e)}")
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def main():
    """Main function to run database initialization"""
    try:
        success = init_database()
        if success:
            logger.info("Database setup completed successfully!")
            sys.exit(0)
        else:
            logger.error("Database setup failed!")
            sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 