from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
import json
import hashlib
from bson import ObjectId
from bson.errors import InvalidId

from app.db import documents_collection
from app.models import Document
from app.redis_client import redis_client

app = FastAPI()


# CREATE DOCUMENT (QUEUE)
@app.post("/documents")
def create_document(doc: Document, request: Request):
    user_id = doc.user_id

    # generate hash for content (for caching)
    content_hash = hashlib.md5(doc.content.encode()).hexdigest()

    # check if same content already processed
    cached = redis_client.get(f"content:{content_hash}")

    if cached:
        return json.loads(cached)

    # Rate limit: max 3 active jobs per user
    key = f"user_jobs:{user_id}"
    count = redis_client.get(key)

    if count and int(count) >= 3:
        raise HTTPException(status_code=429, detail="Too many active jobs for this user")

    redis_client.incr(key)
    # redis_client.expire(key, 60)

    doc_data = doc.model_dump()

    # Add metadata
    doc_data["status"] = "queued"
    doc_data["created_at"] = datetime.utcnow().isoformat()
    doc_data["updated_at"] = datetime.utcnow().isoformat()

    # Insert into DB first
    result = documents_collection.insert_one(doc_data)
    document_id = str(result.inserted_id)

    # store in cache so duplicate content is not processed again
    redis_client.set(
        f"content:{content_hash}",
        json.dumps({
            "status": "queued",
            "document_id": document_id
        })
    )

    # Attach ID to payload for worker
    doc_data["_id"] = document_id

    # Push to Redis queue
    redis_client.rpush("document_queue", json.dumps(doc_data))

    return {
        "status": "queued",
        "document_id": document_id
    }


# GET DOCUMENT STATUS
@app.get("/documents/{document_id}")
def get_document(document_id: str):
    try:
        obj_id = ObjectId(document_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID")

    doc = documents_collection.find_one({"_id": obj_id})

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc["_id"] = str(doc["_id"])

    return {
        "id": doc["_id"],
        "status": doc["status"],
        "summary": doc.get("summary")
    }


# GET USER DOCUMENTS (with pagination)
@app.get("/users/{user_id}/documents")
def get_user_documents(user_id: str, page: int = 1, page_size: int = 5):
    skip = (page - 1) * page_size

    docs = list(
        documents_collection
        .find({"user_id": user_id})
        .skip(skip)
        .limit(page_size)
    )

    for doc in docs:
        doc["_id"] = str(doc["_id"])

    return {
        "page": page,
        "page_size": page_size,
        "documents": docs
    }


# HEALTH CHECK
@app.get("/health")
def health_check():
    return {"status": "ok"}


# ROOT
@app.get("/")
def read_root():
    return {"message": "Backend is running"}