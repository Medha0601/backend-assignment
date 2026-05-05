# Document Processing API

## Overview

This project is a backend service built using **FastAPI**, **MongoDB**, and **Redis** that processes documents asynchronously.

Users can submit documents, which are queued and processed by a background worker. The system tracks document status and returns results once processing is complete.


## Tech Stack

* **Python 3.11**
* **FastAPI** – API framework
* **MongoDB** – Database
* **Redis** – Queue + rate limiting
* **Pydantic** – Data validation

---

## Features

* Submit documents for async processing
* Background worker for processing queue
* Document status tracking (`queued → completed`)
* Rate limiting (max 3 active jobs per user)
* Pagination for user documents
* Clean API structure

---

## API Endpoints

### 1. Create Document

**POST** `/documents`

#### Request Body:

```json
{
  "user_id": "123",
  "title": "Sample",
  "content": "This is a test document"
}
```

#### Response:

```json
{
  "status": "queued",
  "document_id": "..."
}
```

---

### 2. Get Document Status

**GET** `/documents/{document_id}`

#### Response:

```json
{
  "id": "...",
  "status": "completed",
  "summary": "Summary of content"
}
```

---

### 3. Get User Documents

**GET** `/users/{user_id}/documents?page=1&page_size=5`

#### Response:

```json
{
  "page": 1,
  "page_size": 5,
  "documents": [...]
}
```

---

### 4. Health Check

**GET** `/health`

---

##  How It Works

1. User submits document
2. Document stored in MongoDB with status `queued`
3. Task pushed to Redis queue
4. Worker picks task and processes it
5. Status updated to `completed` with summary

---

##  Design Decisions

* Used **Redis queue (list)** for simplicity instead of external tools like Celery
* Stored documents first, then processed asynchronously
* Used **update instead of insert** in worker to avoid duplicates
* Implemented **rate limiting per user** using Redis

---

##  Assumptions

* Document processing is simulated (not real AI)
* Redis and MongoDB are running locally
* Single worker handles processing

---

##  How to Run

### 1. Start Environment Variables

Create a `.env` file in the root folder:

MONGO_URL=your_mongodb_connection_string
REDIS_HOST=localhost
REDIS_PORT=6379


### 2. Start Redis
If Docker is installed via WSL, run this command inside WSL (Ubuntu terminal)
docker run -d -p 6379:6379 redis


### 3. Install dependencies

```bash
pip install -r requirements.txt
```



### 3. Run FastAPI server

```bash
uvicorn app.main:app --reload
```


### 4. Run worker (separate terminal)

```bash
python -m app.worker
```


### 4. Run with Docker
To start all the services, run this command inside WSL (Ubuntu terminal)

```bash
docker-compose up --build
```

## Notes

* Simple and clean implementation focusing on core concepts
* Can be extended with:

  * Content caching
  * Retry mechanism
  * Multiple workers
  * Docker setup
