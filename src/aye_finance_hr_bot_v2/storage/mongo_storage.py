"""Custom MongoDB storage for CrewAI External Memory."""

from crewai.memory.storage.interface import Storage
from pymongo import MongoClient
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class UserSpecificMongoStorage(Storage):
    """MongoDB storage with user-specific collections."""
    
    def __init__(self, user_id: str):
        """
        Initialize MongoDB storage for a specific user.
        
        Args:
            user_id: Unique user identifier
        """
        self.user_id = user_id
        
        # Connect to MongoDB
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            raise ValueError("MONGODB_URI not set in environment variables")
        
        self.client = MongoClient(mongo_uri)
        db_name = os.getenv("MONGODB_DATABASE", "hr_bot")
        self.db = self.client[db_name]
        
        # User-specific collection
        self.collection = self.db[f"user_{user_id}_memories"]
        
        # Create indexes for faster searches
        self.collection.create_index("value")
        self.collection.create_index("timestamp")
        self.collection.create_index("metadata.type")
        
        logger.info(f"MongoDB storage initialized for user: {user_id}")
    
    def save(self, value, metadata=None, agent=None):
        """
        Save memory to MongoDB.
        
        Args:
            value: Memory content to save
            metadata: Optional metadata dictionary
            agent: Optional agent identifier
        
        Returns:
            Inserted document ID
        """
        memory_doc = {
            "user_id": self.user_id,
            "value": value,
            "metadata": metadata or {},
            "agent": agent,
            "timestamp": datetime.now()
        }
        
        result = self.collection.insert_one(memory_doc)
        logger.info(f"💾 Saved to MongoDB: {value[:50]}... (ID: {result.inserted_id})")
        return result.inserted_id
    
    def search(self, query, limit=10, score_threshold=0.5):
        """
        Search user's memories in MongoDB.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            score_threshold: Minimum score threshold (not used in basic search)
        
        Returns:
            List of matching memory documents
        """
        if not query:
            # Return recent memories if no query
            results = list(
                self.collection.find()
                .sort("timestamp", -1)
                .limit(limit)
            )
        else:
            # Text search (case-insensitive)
            results = list(
                self.collection.find({
                    "value": {"$regex": query, "$options": "i"}
                })
                .sort("timestamp", -1)
                .limit(limit)
            )
        
        # Format results
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "value": doc["value"],
                "metadata": doc.get("metadata", {}),
                "agent": doc.get("agent"),
                "timestamp": doc.get("timestamp")
            })
        
        logger.info(f"🔍 Found {len(formatted_results)} memories for query: '{query}'")
        return formatted_results
    
    def reset(self):
        """Clear all memories for this user."""
        result = self.collection.delete_many({"user_id": self.user_id})
        logger.info(f"🗑️ Cleared {result.deleted_count} memories for user: {self.user_id}")
    
    def __del__(self):
        """Close MongoDB connection on cleanup."""
        if hasattr(self, 'client'):
            self.client.close()
