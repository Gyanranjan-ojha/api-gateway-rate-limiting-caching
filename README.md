# API Gateway with Rate Limiting and Caching

## Overview

The API Gateway with Rate Limiting and Caching project is designed to manage, secure, and optimize API requests. It serves as a centralized gateway for handling authentication, enforcing rate limits, caching frequent requests, and load balancing traffic across multiple servers. This project aims to enhance API performance, security, and scalability by integrating key features like JWT authentication, Redis-based rate limiting and caching, and comprehensive logging.

## Features

**API Gateway:** Built for route, balance, and secure incoming API requests.

**Authentication:** Secure API endpoints using JSON Web Tokens (JWT) for authentication.

**Rate Limiting:** Implement rate limiting using Redis to control the number of requests per client.

**Caching:** Cache API responses in Redis to reduce backend load and improve response times.

**Logging:** Log critical errors and events using Python's logging module for effective monitoring.

## Prerequisites

Before installing the API Gateway with Rate Limiting and Caching, ensure you have the following installed:

- Python (version 3.10 or higher)
- Redis (latest stable version)

## Project Structure

```plaintext
api-gateway-rate-limiting-caching/
│
├── api/                           # Core application code.
│   ├── auth/                      # Authentication-related modules.
│   │   ├── __init__.py            # Marks the directory as a Python package.
│   │   ├── hashing.py             # Password hashing and verification.
│   │   ├── jwt_manager.py         # JWT token creation and verification.
│   │   ├── oauth2.py              # OAuth2 configuration and user retrieval.
│   │   └── users.py               # User authentication and retrieval.
│   ├── config/                    # Configuration and environment management.
│   │   ├── __init__.py            # Marks the directory as a Python package.
│   │   └── settings.py            # Manages environment variables and settings.
│   ├── core/                      # Core app logic and FastAPI setup.
│   │   ├── __init__.py            # Marks the directory as a Python package.
│   │   ├── main.py                # FastAPI app entry point and route integration.
│   │   └── routers.py             # Defines API routes and integrates features.
│   ├── db/                        # Database setup and related modules.
│   │   ├── __init__.py            # Marks the directory as a Python package.
│   │   └── fake_db.py             # Fake users database for demonstration.
│   ├── models/                    # Pydantic models for data validation.
│   │   ├── __init__.py            # Marks the directory as a Python package.
│   │   ├── tokens.py              # Defines JWT token-related models.
│   │   └── users.py               # Defines user-related models.
│   ├── seed/                      # Database seeding logic.
│   │   ├── __init__.py            # Marks the directory as a Python package.
│   │   └── product_seeder.py      # Seeds the database with fake product data.
│   ├── caching.py                 # Implements caching logic with Redis.
│   ├── load_balancer.py           # Load balancing logic.
│   ├── logger.py                  # Configures application logging.
│   └── rate_limiter.py            # Implements rate limiting using Redis.
│
├── logs/                          # Directory for application logs.
│   └── app.log                    # Application log file.
│
├── .env                           # Environment variables for the application.
├── .gitignore                     # Specifies files to be ignored by Git.
├── requirements.txt               # Python dependencies.
└── README.md                      # Project overview and setup instructions.
```

## Installation

**1. Clone the project**

```bash
  git clone https://github.com/Gyanranjan-ojha/api-gateway-rate-limiting-caching.git
```

**2. Navigate to the api-gateway-rate-limiting-caching directory**

```bash
    cd api-gateway-rate-limiting-caching
```

## Project Setup

- Create a virtual environment

```bash
    python -m venv .venv
```

- Activate the virtual environment

- For Ubuntu

```bash
    source .venv/bin/activate
```

- For Windows

```bash
    .venv/Scripts/activate
```

- Install python dependencies

```bash
    pip install -r requirements.txt
```

- .env Configuration

Create a `.env` file in the src directory and provide the necessary environment variables:

```bash
    export CURRENT_ENVIRONMENT='<env (development/test/production)>'
    export DEBUG=1
    export SECRET_KEY=your_secret_key_here
    export JWT_SECRET=your_jwt_secret_here
    export REDIS_HOST=localhost
    export REDIS_PORT=6379
    export LOG_FILE_PATH=./app/error.log
```

## Running the Application

**1. Start Redis**
- Ensure Redis is running on your local machine.

```bash
    redis-server
```

**2. Run the 'seed' command to generate 1000 fake products data and insertion into redis**

```bash
     python -m api.core.main seed
```

**3. Run the FastAPI Application**
```bash
    uvicorn api.core.main:app --host 0.0.0.0 --port 8080 --reload
```