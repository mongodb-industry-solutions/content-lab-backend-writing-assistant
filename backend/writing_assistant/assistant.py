from .tools import WritingTools
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class WritingAssistant:
    def __init__(self):
        self.writing_tools = WritingTools()
    
    async def process_request(self, 
                    user_input: str, 
                    content: str, 
                    user_profile: dict,
                    selected_tool: Optional[str] = None,
                    topic_details: str = "",
                    brief: str = "") -> Dict[str, Any]:
        """
        Process a writing request using user's profile for style guidance
        
        Args:
            user_input: Description of what the user wants
            content: The text content to work with
            user_profile: The user's writing style/persona preferences
            selected_tool: Optional tool explicitly selected by the user
            topic_details: Additional context about the topic
            brief: Brief description for outline creation
            
        Returns:
            Response from the tool or agent
        """
        try:
            # DIRECT EXECUTION PATH - When user selects a specific tool
            if selected_tool:
                logger.info(f"User selected tool: {selected_tool}")
                
                if selected_tool == "refine":
                    result = self.writing_tools.refine_content(content, user_profile, topic_details)
                    return {
                        "result": result,
                        "tool_used": "refine",
                        "profile_used": user_profile.get("persona", "Unknown")
                    }
                    
                elif selected_tool == "outline":
                    result = self.writing_tools.create_outline(content, user_profile, brief)
                    return {
                        "result": result,
                        "tool_used": "outline",
                        "profile_used": user_profile.get("persona", "Unknown")
                    }
                    
                elif selected_tool == "proofread":
                    result = self.writing_tools.proofread_content(content, user_profile)
                    return {
                        "result": result,
                        "tool_used": "proofread",
                        "profile_used": user_profile.get("persona", "Unknown")
                    }
                    
                else:
                    logger.warning(f"Unknown tool: {selected_tool}")
                    return {
                        "error": f"Unknown tool: {selected_tool}",
                        "status": "error",
                        "available_tools": ["refine", "outline", "proofread", "chat"]
                    }
            
            # NO TOOL SPECIFIED - Use chat completion instead
            logger.info("No tool specified, using chat completion")
            
            # Build context from provided content and details
            context = ""
            if content:
                context += f"Content: {content}\n"
            if topic_details:
                context += f"Topic details: {topic_details}\n"
            if brief:
                context += f"Brief: {brief}\n"
                
            chat_result = self.writing_tools.chat_completion(user_input, user_profile, context)
            
            return {
                "result": chat_result,
                "tool_used": "chat",
                "profile_used": user_profile.get("persona", "Unknown")
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "error": str(e),
                "status": "error"
            }