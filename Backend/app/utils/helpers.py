from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re
import logging
from http import HTTPStatus

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is valid"

def format_error_response(message: str, status_code: int) -> tuple[Dict[str, Any], int]:
    """Format error response"""
    return {
        'error': message,
        'status': 'error',
        'timestamp': datetime.utcnow().isoformat()
    }, status_code

def format_success_response(data: Dict[str, Any], message: str = "Success") -> tuple[Dict[str, Any], int]:
    """Format success response"""
    return {
        'data': data,
        'message': message,
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat()
    }, HTTPStatus.OK

def calculate_age(birth_date: datetime) -> int:
    """Calculate age from birth date"""
    today = datetime.now()
    age = today.year - birth_date.year
    
    # Adjust age if birthday hasn't occurred this year
    if today.month < birth_date.month or \
       (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI from weight (kg) and height (cm)"""
    if height_cm <= 0:
        raise ValueError("Height must be greater than 0")
    
    height_m = height_cm / 100
    return round(weight_kg / (height_m * height_m), 1)

def get_bmi_category(bmi: float) -> str:
    """Get BMI category"""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def parse_medical_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string in various medical formats
    Returns None if parsing fails
    """
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m-%d-%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def calculate_days_between(start_date: datetime, end_date: datetime) -> int:
    """Calculate number of days between two dates"""
    return (end_date - start_date).days

def is_valid_medical_record_number(mrn: str) -> bool:
    """Validate Medical Record Number format"""
    # Example format: MRN-YYYYMMDD-XXXX
    pattern = r'^MRN-\d{8}-\d{4}$'
    return bool(re.match(pattern, mrn))

def generate_medical_record_number(patient_id: str) -> str:
    """Generate Medical Record Number"""
    date_str = datetime.now().strftime("%Y%m%d")
    sequence = patient_id[-4:].zfill(4)
    return f"MRN-{date_str}-{sequence}"

def calculate_readmission_window(discharge_date: datetime, 
                               window_days: int = 30) -> datetime:
    """Calculate readmission window end date"""
    return discharge_date + timedelta(days=window_days)

def format_phone_number(phone: str) -> str:
    """Format phone number to standard format"""
    # Remove all non-numeric characters
    numbers = re.sub(r'\D', '', phone)
    
    if len(numbers) == 10:
        return f"({numbers[:3]}) {numbers[3:6]}-{numbers[6:]}"
    elif len(numbers) == 11 and numbers[0] == '1':
        return f"({numbers[1:4]}) {numbers[4:7]}-{numbers[7:]}"
    else:
        raise ValueError("Invalid phone number format")

def sanitize_input(text: str) -> str:
    """Sanitize input text"""
    # Remove any potential script tags
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
    # Remove any HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove any potential SQL injection attempts
    text = re.sub(r'[\'";]', '', text)
    return text.strip()

def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log error with context"""
    error_data = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'timestamp': datetime.utcnow().isoformat(),
        'context': context or {}
    }
    logger.error(f"Error occurred: {error_data}")
    return error_data 