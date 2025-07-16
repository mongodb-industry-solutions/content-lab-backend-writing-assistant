from .tools import WritingTools
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class WritingAssistant:
    # Available tools for validation
    AVAILABLE_TOOLS = ["refine", "outline", "proofread", "chat"]
    
    def __init__(self):
        self.writing_tools = WritingTools()
    
    async def process_request(self, 
                    user_input: str, 
                    content: str, 
                    user_profile: dict,
                    selected_tool: Optional[str] = None,
                    topic_details: str = "") -> Dict[str, Any]:
        """
        Process a writing request using user's profile for style guidance
        
        Args:
            user_input: Description of what the user wants
            content: The text content to work with
            user_profile: The user's writing style/persona preferences
            selected_tool: Optional tool explicitly selected by the user
            topic_details: Additional context about the topic
            
        Returns:
            Response from the tool or agent
        """
        try:
            if selected_tool == "refine":
                logger.info("Using refine tool")
                result = self.writing_tools.refine_content(content, user_profile)
                
            elif selected_tool == "outline":
                logger.info("Using outline tool")
                result = self.writing_tools.create_outline(topic_details, user_profile)
                
            elif selected_tool == "proofread":
                logger.info("Using proofread tool")
                result = self.writing_tools.proofread_content(content, user_profile)
                
            elif selected_tool:
                # Unknown tool
                logger.warning(f"Unknown tool: {selected_tool}")
                return {
                    "error": f"Unknown tool: {selected_tool}",
                    "status": "error",
                    "available_tools": self.AVAILABLE_TOOLS
                }
            
            else:
                # No tool specified - use chat completion
                logger.info("No tool specified, using chat completion")
                result = self.writing_tools.chat_completion(user_input, user_profile, content)
                selected_tool = "chat"
            
            return {"result": result, "tool_used": selected_tool}
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "error": str(e),
                "status": "error"
            }