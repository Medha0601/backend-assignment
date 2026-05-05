import redis
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# Redis configuration (defaults for local development)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# initialize Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True  # ensures we get strings instead of bytes
)


