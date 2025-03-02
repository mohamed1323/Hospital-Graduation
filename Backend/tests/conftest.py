import pytest
from app import create_app
from app.models.user import User
from mongoengine import connect, disconnect
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture(scope='function')
def app():
    """Create application for the tests."""
    # Set up test database
    test_app = create_app('testing')
    
    # Setup test database
    test_db = os.getenv('MONGODB_DB', 'hospital_db') + '_test'
    test_app.config['MONGODB_DB'] = test_db
    
    # Create test client
    with test_app.test_client() as client:
        with test_app.app_context():
            # Connect to test database
            connect(test_db,
                   host=os.getenv('MONGODB_HOST', 'mongodb://localhost:27017/'),
                   username=os.getenv('MONGODB_USERNAME'),
                   password=os.getenv('MONGODB_PASSWORD'),
                   authentication_source=os.getenv('MONGODB_AUTH_SOURCE', 'admin'))
            yield client
            
            # Clean up
            disconnect()

@pytest.fixture
def auth_headers(app):
    """Create authentication headers for test requests."""
    # Create test admin user
    user = User(
        username='testadmin',
        email='testadmin@test.com',
        role='admin'
    ).save()
    
    # Generate token
    token = user.generate_token()
    
    return {'Authorization': f'Bearer {token}'} 