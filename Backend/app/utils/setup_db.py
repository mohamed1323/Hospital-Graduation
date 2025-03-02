from mongoengine import connect, disconnect
from app.models.user import User
from app.models.patient import Patient
from app.models.prediction import Prediction
from app.utils.config import Config
import logging
from werkzeug.security import generate_password_hash

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_indexes():
    """Set up MongoDB indexes for all collections"""
    try:
        # Connect to MongoDB
        connect(
            db=Config.MONGODB_DB,
            host=Config.MONGODB_HOST
        )
        
        logger.info("Setting up MongoDB indexes...")
        
        # Create indexes for User collection
        logger.info("Creating User indexes...")
        User.ensure_indexes()
        
        # Create indexes for Patient collection
        logger.info("Creating Patient indexes...")
        Patient.ensure_indexes()
        
        # Create indexes for Prediction collection
        logger.info("Creating Prediction indexes...")
        Prediction.ensure_indexes()
        
        logger.info("All indexes created successfully!")
        
    except Exception as e:
        logger.error(f"Error setting up indexes: {str(e)}")
        raise
    finally:
        disconnect()

def create_admin_user(username: str, email: str, password: str):
    """Create an admin user if it doesn't exist"""
    try:
        # Connect to MongoDB
        connect(
            db=Config.MONGODB_DB,
            host=Config.MONGODB_HOST
        )
        
        # Check if admin user exists
        existing_admin = User.objects(username=username).first()
        if existing_admin:
            logger.info(f"Admin user '{username}' already exists")
            return
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            role='admin',
            is_active=True
        )
        admin.password_hash = generate_password_hash(password)
        admin.save()
        
        logger.info(f"Admin user '{username}' created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise
    finally:
        disconnect()

def main():
    """Main function to set up database"""
    try:
        # Setup indexes
        setup_indexes()
        
        # Create admin user
        create_admin_user(
            username="admin",
            email="admin@hospital.com",
            password="change_this_password"
        )
        
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 