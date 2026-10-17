import os

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "digisearch")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "digisearch")

# Qdrant
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
VECTOR_SIZE = os.getenv("VECTOR_SIZE", 1024)

# Configuration
DEFAULT_THRESHOLD = float(os.getenv("DEFAULT_THRESHOLD", 0.4))
DEFAULT_BATCH_SIZE = int(os.getenv("DEFAULT_BATCH_SIZE", 8))
DEFAULT_MAX_LENGTH = int(os.getenv("DEFAULT_MAX_LENGTH",8192))
MODEL_NAME = os.getenv("MODEL_NAME", "BAAI/bge-m3")
REFETCH_AFTER_HOURS = float(os.getenv("REFETCH_AFTER_HOURS", "24"))