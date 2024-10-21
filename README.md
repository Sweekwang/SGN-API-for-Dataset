# Membership API

This is a Flask-based REST API for managing membership data, including secure storage and retrieval of user information using AWS DynamoDB. 
The API is built with encryption, rate limiting, and CSRF protection for enhanced security.


## Prerequisites

Ensure you have the following installed on your local machine:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Environment Variables

Modify  `.env` file in the env directory of the project with the following variables for local setup
and replace the placeholder values with your actual configuration.:

```env
AWS_ACCESS_KEY_ID=local
AWS_SECRET_ACCESS_KEY=local

# AWS DynamoDB Configuration
AWS_REGION=ap-southeast-1
DYNAMODB_ENDPOINT=http://host.docker.internal:8000

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Leave empty if no password is set for local Redis

# JWT Secret Key (for local development)
JWT_SECRET_KEY=local_secret_key

# API Key for Authentication (for local development)
API_KEY=your_secure_api_key_here

# Flask Secret Key for CSRF Protection (for local development)
SECRET_KEY=your_flask_secret_key_here
```

## Installation

1. Clone the repository:
```
git clone https://github.com/Sweekwang/SGN-API-for-Dataset.git
cd SGN-API-for-Dataset
```

2. Set up the .env file:

Ensure the .env file is created and filled as described above.

## Running the Server Locally
To start the server locally using Docker Compose, follow these steps:

1. Build and start the containers:
```
docker compose up -d
```

2. Verify that the containers are running:
```
docker compose ps
```

3. Access the API:
The API will be accessible at http://localhost:5000.

You can try: `http://localhost/health`

