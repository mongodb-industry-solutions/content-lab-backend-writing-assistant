# main.py 

# This file sets up the FastAPI application and includes the main routes.

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any, Union
from bson import ObjectId
import logging

from writing_assistant.assistant import WritingAssistant
from db.mdb import MongoDBConnector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

USER_PROFILES_COLLECTION = os.getenv("USER_PROFILES_COLLECTION", "userProfiles")
app = FastAPI(title="Writing Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MongoDB connection

writing_assistant = WritingAssistant()
mongo_client = MongoDBConnector()

# MongoDB connection cache
_collection_cache = {}

def get_collection(collection_name: str):
    """
    Helper Function to get MongoDB collection with caching

    Args:
        collection_name (str): Name of the MongoDB collection

    Returns:
        Collection: MongoDB collection object
    
    """
    # Use cache to avoid repeated connection overhead
    if collection_name not in _collection_cache:
        logger.info(f"Cache miss: Connecting to collection '{collection_name}'")
        _collection_cache[collection_name] = mongo_client.get_collection(collection_name)
    else:
        logger.debug(f"Cache hit: Using cached connection to '{collection_name}'")
        
    return _collection_cache[collection_name]

# Pydantic models for request validation. 

class WritingRequest(BaseModel):
    profile: Dict[str, Any]
    draftContent: str # This is for the draft (A page where the user is writing)
    promptType: Optional[str]  = None
    message: str

# Test Check 

@app.get("/")
async def read_root(request: Request):
    """Test check endpoint"""
    return {"status": "Test_Check", "message": "Writing Assistant API is running"}


@app.post("/api/writing/assist")
async def assist_writing(request: WritingRequest):

    """Main Endpoint to process writing requests"""
    try: 
        tool_mapping = {
            "refine": "refine",
            "proofread": "proofread",
            "draft_layout": "outline",
            None: None  # This will go to the chat completion
        }
    
        selected_tool = tool_mapping.get(request.promptType)

        # Basic validation 
        if request.promptType and request.promptType not in tool_mapping:
            return {
                    "status": "error",
                    "message": f"Invalid promptType: {request.promptType}",
                    "available_tools": list(filter(None, tool_mapping.keys()))
                }
        
        # Extract additional context
        topic_details = ""
        brief = ""

        if request.promptType == "refine" and request.message:
            topic_details = request.message
        elif request.promptType == "draft_layout" and request.message:
            brief = request.message
    
        # Process the request with the writing assistant
        result = await writing_assistant.process_request(
                user_input=request.message,
                content=request.draftContent,
                user_profile=request.profile,
                selected_tool=selected_tool,
                topic_details=topic_details,
                brief=brief
            )
            
        return {
                "status": "success",
                "data": result
            }
    
    except Exception as e:
        logger.error(f"Error processing writing request: {e}")
        return {
            "status" : "error",
            "message": str(e),
        }
    

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)

