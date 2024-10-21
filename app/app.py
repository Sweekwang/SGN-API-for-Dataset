from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os
import logging

from membership_service import MembershipService
from dynamo_db_handler import DynamoDBHandler

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

class Config:
    """App configuration settings."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')
    REDIS_URL = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/{os.getenv('REDIS_DB', '0')}"
    API_KEY = os.getenv('API_KEY', 'default_api_key')
    AWS_REGION = os.getenv('AWS_REGION', 'us-west-2')
    DYNAMODB_ENDPOINT = os.getenv('DYNAMODB_ENDPOINT', None)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Set up rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=Config.REDIS_URL
)
limiter.init_app(app)

# Initialize services
membership_service = MembershipService()
dynamodb_handler = DynamoDBHandler(
    table_name='MembershipData',
    region=Config.AWS_REGION,
    endpoint_url=Config.DYNAMODB_ENDPOINT
)

# Middleware to enforce API key authentication
def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key or api_key != Config.API_KEY:
            return jsonify({'error': 'Unauthorized access'}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/memberships', methods=['POST'])
@require_api_key
@limiter.limit("10 per minute")
@csrf.exempt
def submit_data():
    """
    Endpoint to submit membership data.
    """
    data = request.get_json()

    # Validate input data
    try:
        full_name = data.get('full_name')
        email = data.get('email')
        phone = data.get('phone')
        is_newsletter_subscribed = data.get('is_newsletter_subscribed')

        membership_service.validate_full_name(full_name)
        membership_service.validate_email(email)
        membership_service.validate_phone(phone)

        if not isinstance(is_newsletter_subscribed, bool):
            raise ValueError("is_newsletter_subscribed must be a boolean.")

        # Encrypt data
        encrypted_data = {
            'email': membership_service.encrypt_data(email),
            'full_name': membership_service.encrypt_data(full_name),
            'phone': membership_service.encrypt_data(phone),
            'is_newsletter_subscribed': is_newsletter_subscribed
        }

        # Insert data into DynamoDB
        dynamodb_handler.insert_data(encrypted_data)

        return jsonify({'message': 'Data submitted successfully'}), 200

    except ValueError as ve:
        logging.error(f"Validation Error: {str(ve)}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging.error(f"Submission Error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/memberships', methods=['GET'])
@require_api_key
@limiter.limit("5 per minute")
def retrieve_data():
    """
    Endpoint to retrieve paginated membership data.
    """
    limit = int(request.args.get('limit', 10))
    last_evaluated_key = request.args.get('last_evaluated_key')

    # Prepare scan parameters
    scan_kwargs = {'Limit': limit}
    if last_evaluated_key:
        scan_kwargs['ExclusiveStartKey'] = {'email': last_evaluated_key}

    try:
        # Scan DynamoDB for data
        response = dynamodb_handler.scan_data(scan_kwargs)
        items = response.get('Items', [])
        decrypted_items = [
            {
                'full_name': membership_service.decrypt_data(item['full_name']),
                'email': membership_service.decrypt_data(item['email']),
                'phone': membership_service.decrypt_data(item['phone']),
                'is_newsletter_subscribed': item['is_newsletter_subscribed']
            } for item in items
        ]
        next_start_key = response.get('LastEvaluatedKey', {}).get('email')

        return jsonify({'data': decrypted_items, 'next_start_key': next_start_key}), 200

    except Exception as e:
        logging.error(f"Retrieval Error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
