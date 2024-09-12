# API Gateway with Rate Limiting and Caching

## Overview

The API Gateway with Rate Limiting and Caching project is designed to manage, secure, and optimize API requests. It serves as a centralized gateway for handling authentication, enforcing rate limits, caching frequent requests, and load balancing traffic across multiple servers. This project aims to enhance API performance, security, and scalability by integrating key features like JWT authentication, Redis-based rate limiting and caching, and comprehensive logging.

## Features

**API Gateway:** Built with NGINX to route, balance, and secure incoming API requests.

**Authentication:** Secure API endpoints using JSON Web Tokens (JWT) for authentication.

**Rate Limiting:** Implement rate limiting using Redis to control the number of requests per client.

**Caching:** Cache API responses in Redis to reduce backend load and improve response times.

**Load Balancing:** Distribute incoming traffic across multiple application instances using NGINX.

**Logging:** Log critical errors and events using Python's logging module for effective monitoring.

## Prerequisites

Before installing the API Gateway with Rate Limiting and Caching, ensure you have the following installed:

- Python (version 3.10 or higher)
- NGINX (latest stable version)
- Redis (latest stable version)
- Docker (if you plan to run NGINX using Docker)

## Project Structure

```plaintext
api-gateway-rate-limiting-caching/
│
├── api/                           # Directory containing core application code.
│   ├── __init__.py                # Marks the directory as a Python package.
│   ├── auth.py                    # Handles authentication, JWT creation, and user verification.
│   ├── config.py                  # Manages environment variables and configuration settings.
│   ├── logger.py                  # Configures logging for capturing application errors and events.
│   ├── main.py                    # Entry point for the FastAPI application with route integration.
│   ├── models.py                  # Defines Pydantic models for data validation and serialization.
│   └── routers.py                 # Defines API routes and integrates rate limiting, caching, and authentication.
│
├── nginx/                         # Directory containing NGINX configuration files.
│   └── nginx.conf                 # NGINX configuration for reverse proxy and load balancing.
│
├── redis/                         # Directory containing Redis configuration files.
│   └── redis.conf                 # Redis configuration for caching and rate limiting.
│
├── .env                           # Environment file containing environment variables for the application.
├── .gitignore                     # Specifies files and directories to be ignored by Git.
├── requirements.txt               # Lists all Python dependencies needed for the project.
└── README.md                      # Provides an overview of the project and instructions for setup and usage.
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
    export LOG_FILE_PATH=./logs/error.log
```

- Create a "logs" folder and "error.log" file

```bash
    mkdir logs
```
- For Ubuntu

```bash
    touch logs/error.log
```

- For Windows

```bash
    echo log file > error.log 
```

## Running the Application

**1. Start Redis**
- Ensure Redis is running on your local machine. If not, you can start it with the following command:

```bash
    redis-server redis/redis.conf
```

**2. Run the FastAPI Application**

```bash
    uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

**3. Run NGINX**

```bash
    cd gateway
    bash start_nginx.sh
```