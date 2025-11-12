# ---main.py---

# This file contains the main application for the Writing Assistant API.

# Importing necessary libraries
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from writing_assistant.assistant import WritingAssistant
from dotenv import load_dotenv

load_dotenv()

# Setting up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Defining the FastAPI app
app = FastAPI(
    title="Writing Assistant API", 
    version="0.0.1",
    redirect_slashes=False
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers to the client
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Creating an instance of the WritingAssistant class
writing_assistant = WritingAssistant()

# Defining the WritingRequest model
class WritingRequest(BaseModel):
    profile: Dict[str, Any]
    draftContent: str 
    promptType: Optional[str]  = None
    message: str
    topicDetails: Optional[Dict[str, Any]] = None
    
    
# Health check endpoint
@app.get("/")
async def read_root():
    return {
        "message": "Contentlab Chat API is running",
        "version": "0.0.1",
        "status": "healthy",
        "service": "contentlab-chat"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "contentlab-chat"
    }

# Defining the assist_writing endpoint
@app.post("/api/writing/assist")
async def assist_writing(request: WritingRequest):
    """
    Main Endpoint to process writing requests
    :param request: A WritingRequest object containing the user's profile, draft content, prompt type, message, and topic details
    :return: A dictionary containing the status, message, and data
    """
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

        if request.promptType == "draft_layout":
            # Extract and format topic information for outline generation
            topic_info = request.topicDetails or {}
            topic_details = f"""
            Topic: {topic_info.get('topic', 'Unknown')}
            Category: {topic_info.get('label', 'General')}
            Description: {topic_info.get('description', '')}
            Keywords: {', '.join(topic_info.get('keywords', []))}
                        """.strip()
    
        # Process the request with the writing assistant
        result = await writing_assistant.process_request(
                user_input=request.message,
                content=request.draftContent,
                user_profile=request.profile,
                selected_tool=selected_tool,
                topic_details=topic_details
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