Document Retrieval Backend with FAISS and Redis Caching
This is a backend system for document retrieval built with FastAPI, using FAISS for efficient search through document embeddings, and Redis for caching search results. The backend supports user-based rate limiting and logs API call details.

Features
Search API: Search for documents using FAISS and retrieve results based on text embeddings.
Add Documents: Add new documents to the system and dynamically update the FAISS index.
Rate Limiting: Limits the number of API calls a user can make to prevent overuse.
Caching: Utilizes Redis to cache search results and speed up repeated queries.
Background Scraper: Runs a background scraper that collects data from external sources periodically (like news articles).
Dockerized: The entire application is containerized using Docker for easy deployment.
Project Structure
main.py: Contains the FastAPI application, including search, document addition, and rate limiting.
embedding.py: A utility to generate embeddings for documents.
requirements.txt: Lists the dependencies required for the project (FastAPI, Redis, FAISS, Uvicorn, etc.).
Dockerfile: Used to containerize the application for deployment.
docker-compose.yml (optional): Used to run FastAPI and Redis together.
README.md: This file, which provides instructions on how to set up and run the project.
Setup Instructions
Prerequisites
I made sure the following is installed:

Python 3.9+
Docker 
Redis 

Step 1: Clone the Repository

git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
Step 2: Install Dependencies
If you are not using Docker, you can install the Python dependencies by running:
pip install -r requirements.txt
This will install the required packages like FastAPI, Uvicorn, SQLAlchemy, Redis-py, and FAISS.

Step 3: Run Redis 
If you don't have Redis installed locally, you can run it in a Docker container:
docker run -d -p 6379:6379 redis
Step 4: Run the Application
To run the FastAPI application locally (without Docker):
\
uvicorn main:app --reload
The app will be available at: http://127.0.0.1:8000

Step 5: Dockerize the Application
If you prefer to run the application inside Docker, follow these steps:

Build the Docker image:


docker build -t my-fastapi-app .
Run the Docker container:

docker run -p 8000:8000 my-fastapi-app
Now, you can access the application at http://127.0.0.1:8000.

Step 6: Use the API
You can use the FastAPI Swagger UI at http://127.0.0.1:8000/docs to interact with the API. The following endpoints are available:

GET /search: Search for documents using a query. Parameters include:

text: The search query.
user_id: The ID of the user making the request.
top_k: The number of top results to return.
threshold: The threshold for similarity in the FAISS search.
POST /add_document: Add a new document to the system.

content: The content of the document.
GET /health: Check if the API is running.

Caching
Redis is used to cache search results, improving response times for repeated queries. Search results are cached by a key based on the search query and user ID. Cached results are returned directly when available.

Rate Limiting
Users can make up to 5 requests. After that, any additional requests will receive a 429 Too Many Requests error.

Background Scraping
A background thread scrapes data (e.g., news articles) every hour, automatically adding them to the document database. This functionality is handled in the scraper.py file.

Docker Compose (Optional)
You can use Docker Compose to run both Redis and FastAPI together:

Create a docker-compose.yml file like the one below:

yaml
Copy code
version: '3'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
  redis:
    image: "redis:latest"
    ports:
      - "6379:6379"
Start both services:

docker-compose up --build
