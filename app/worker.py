from app.redis_client import redis_client
from app.db import documents_collection
import time
import json
from datetime import datetime
from bson import ObjectId


def process_documents():
    print("[WORKER] Worker started...")

    while True:
        doc_data = redis_client.lpop("document_queue")

        if doc_data:
            try:
                doc = json.loads(doc_data)

                print(f"[WORKER] Processing: {doc.get('title')}")

                # simulate processing
                time.sleep(2)

                # mark as completed
                doc["status"] = "completed"
                doc["summary"] = f"Summary of: {doc.get('content')}"
                doc["updated_at"] = datetime.utcnow().isoformat()

                # update in DB
                documents_collection.update_one(
                    {"_id": ObjectId(doc["_id"])},
                    {
                        "$set": {
                            "status": doc["status"],
                            "summary": doc["summary"],
                            "updated_at": doc["updated_at"]
                        }
                    }
                )

                # decrease active job count
                redis_client.decr(f"user_jobs:{doc['user_id']}")

                print("[WORKER] Done")

            except Exception as e:
                print(f"[WORKER] Error: {e}")

        else:
            time.sleep(1)


if __name__ == "__main__":
    process_documents()