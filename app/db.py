from pymongo import MongoClient
import os
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

# initialize MongoDB client
client = MongoClient(MONGO_URL)

# select database
db = client["backend_db"]

# collection for storing documents
documents_collection = db["documents"]

# create index 
documents_collection.create_index("title")