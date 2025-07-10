# Libs
import logging
import os
import json
import sys
import re

# Add parent directory to path so we can import from sibling directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from typing import Optional, Dict, Any, Tuple
from bedrock.anthropic_chat_completions import BedrockAnthropicChatCompletions

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class WritingTools:

    def __init__(self):
        self.claude_client = BedrockAnthropicChatCompletions()

    def _extract_profile_data(self, user_profile: dict) -> Tuple[str, str, list, str]:
        """Extract all needed profile data with defaults"""
        return (
            user_profile.get("persona", "Default Writer"),
            user_profile.get("tone", "Neutral"),
            user_profile.get("styleTraits", []),
            user_profile.get("sampleText", "")
        )

    def refine_content(self, content: str, user_profile: dict, topic_details: str = "") -> dict:
        """Refine content according to user's preferred writing style."""
        try: 
            persona, tone, style_traits, sample_text = self._extract_profile_data(user_profile)

            # Style Guidance
            style_guidance = f"""
            Writing Persona: {persona}
            Tone: {tone}
            Style Traits:
            {self._format_style_traits(style_traits)}
            
            Sample Text in This Style:
            {sample_text}
            """
            
            prompt = f"""
            You are a writing assistant that refines content according to specific style profiles.
            
            USER PROFILE:
            {style_guidance}
            
            CONTENT TO REFINE:
            {content}
            
            TOPIC DETAILS:
            {topic_details}
            
            Refine this content to perfectly match the user's writing style, tone, and persona.
            Be extremely careful to follow ALL style traits listed.
            
            Return your response as JSON with these fields only:
            - original_text: The original content you're working with
            - refined_content: The improved version that matches the style
            
            IMPORTANT: Do NOT include style_changes or suggestions fields.
            """
            
            logger.info(f"Sending refine request for persona: {persona}")
            response = self.claude_client.predict(prompt)
        
            try:
                result = json.loads(response)
                logger.info("Successfully parsed refine response as JSON")
                # Add the original content if it wasn't included in the response
                if "original_text" not in result:
                    result["original_text"] = content
                return result
            except json.JSONDecodeError:
                logger.error("Failed to parse response as JSON, returning raw text")
                return {
                    "original_text": content,
                    "refined_content": response
                }
            
        except Exception as e:
            logger.error(f"Error in refine tool: {e}")
            return {
                "original_text": content,
                "refined_content": content
            }


    def create_outline(self, topic: str, user_profile: dict, brief: str = "") -> dict:
        """Create an outline according to user's preferred writing style."""
        try: 
            # Extract style information
            persona, tone, style_traits, sample_text = self._extract_profile_data(user_profile)
            
            # Style Guidance
            style_guidance = f"""
            Writing Persona: {persona}
            Tone: {tone}
            Style Traits:
            {self._format_style_traits(style_traits)}

            Sample Text in This Style:
            {sample_text}
            """
            
            # Example HTML structure to follow
            html_example = """
            <h2>Introduction</h2>
            <p>Welcome to this comprehensive article about [TOPIC]. This introduction sets the stage for what readers can expect to learn.</p>
            <h2>Main Content</h2>
            <h3>Key Point 1</h3>
            <p>Detail your first major point here. Include supporting evidence, examples, and relevant data.</p>
            <h3>Key Point 2</h3>
            <p>Develop your second main argument. Connect it to your first point to build a cohesive narrative.</p>
            <h3>Key Point 3</h3>
            <p>Present your final key insight. This should tie everything together and lead naturally to your conclusion.</p>
            <h2>Conclusion</h2>
            <p>Summarize the main takeaways and provide a clear call to action for your readers.</p>
            <hr>
            <p><em>This draft structure is based on your topic selection and writing style preferences.</em></p>
            """

            prompt = f"""
            You are a writing assistant that creates outlines according to specific style profiles.

            USER PROFILE:
            {style_guidance}

            TOPIC:
            {topic}

            BRIEF:
            {brief}

            Create an outline that perfectly matches the user's writing style, tone, and persona.
            Be extremely careful to follow ALL style traits listed.
            
            FORMAT REQUIREMENTS:
            Return your outline as HTML with the following structure:
            
            1. Use HTML heading tags (<h2>, <h3>) for section titles
            2. Use paragraph tags (<p>) for descriptions
            3. Include an introduction, main sections with key points, and conclusion
            4. Follow this exact HTML format example:
            
            {html_example}
            
            Do not include any markdown or non-HTML formatting. Return ONLY clean, valid HTML that follows the example structure.
            Replace [TOPIC] with the actual topic provided.
            Adapt the number of sections and key points to fit the topic and brief.
            """

            logger.info(f"Sending HTML outline request for topic: {topic}")
            response = self.claude_client.predict(prompt)

            # Parse HTML response
            parsed_outline = self._parse_html_outline(response, topic)
            logger.info("Successfully parsed HTML outline")
            return parsed_outline
                
        except Exception as e:
            logger.error(f"Error in outline tool: {e}")
            return {
                "html_content": f"<p>Error occurred: {str(e)}</p>",
                "main_sections": [],
                "section_count": 0
            }
    
    def _parse_html_outline(self, html_content: str, topic: str) -> dict:
        """Parse HTML outline into structured format"""
        try:
            # Extract main sections (h2 headings)
            h2_pattern = re.compile(r'<h2>(.*?)<\/h2>', re.DOTALL)
            main_sections = h2_pattern.findall(html_content)
            
            # Clean up HTML - remove any non-HTML content before or after
            html_start = html_content.find("<h2")
            if html_start == -1:
                html_start = html_content.find("<p")
            
            html_end = html_content.rfind("</p>") + 4
            if html_end < 4:  # If "</p>" not found
                html_end = len(html_content)
                
            if html_start != -1:
                clean_html = html_content[html_start:html_end]
            else:
                clean_html = html_content
                
            # Simple validation - does it contain HTML tags?
            if "<h2>" not in clean_html and "<p>" not in clean_html:
                logger.warning("HTML parsing failed, response doesn't contain proper HTML tags")
                # Wrap plain text in HTML if needed
                clean_html = f"<h2>Outline for {topic}</h2><p>{clean_html}</p>"
            
            return {
                "html_content": clean_html,
                "main_sections": main_sections,
                "section_count": len(main_sections)
            }
        except Exception as e:
            logger.error(f"Error parsing HTML outline: {e}")
            return {
                "html_content": html_content,
                "main_sections": [],
                "section_count": 0
            }
        
    # Proof Read the Content
    def proofread_content(self, content: str, user_profile: dict) -> dict:
        """Proofread content while preserving user's preferred writing style."""
        try:
            # Extract style information
            persona, tone, style_traits, sample_text = self._extract_profile_data(user_profile)
            
            # Style Guidance
            style_guidance = f"""
            Writing Persona: {persona}
            Tone: {tone}
            Style Traits:
            {self._format_style_traits(style_traits)}
            
            Sample Text in This Style:
            {sample_text}
            """
            
            prompt = f"""
            You are a writing assistant that proofreads content while preserving specific writing styles.
            
            USER PROFILE:
            {style_guidance}
            
            CONTENT TO PROOFREAD:
            {content}
            
            Proofread this content for errors while PRESERVING the user's writing style, tone, and persona.
            Do NOT change the style - only fix actual errors like spelling, grammar, punctuation, etc.
            Be extremely careful to maintain ALL style traits listed.
            
            Return your response as JSON with these fields only:
            - original_text: The original content you're checking
            - corrections: List of specific errors found, each with "original" and "corrected" versions
            - improved_text: Corrected version of the text
            - error_count: Total number of errors found
            
            IMPORTANT: Do NOT include a suggestions field.
            Format each correction to clearly show what was changed.
            """
            
            logger.info(f"Sending proofread request for persona: {persona}")
            response = self.claude_client.predict(prompt)
            
            try:
                result = json.loads(response)
                logger.info("Successfully parsed proofread response as JSON")
                # Add the original content if it wasn't included in the response
                if "original_text" not in result:
                    result["original_text"] = content
                return result
            except json.JSONDecodeError:
                logger.error("Failed to parse response as JSON, returning raw text")
                return {
                    "original_text": content,
                    "corrections": [],
                    "improved_text": response,
                    "error_count": 0
                }
                
        except Exception as e:
            logger.error(f"Error in proofread tool: {e}")
            return {
                "original_text": content,
                "corrections": [],
                "improved_text": content,
                "error_count": 0
            }


    def chat_completion(self, query: str, user_profile: dict, context: str = "") -> dict:
        """Provide a chat response according to user's preferred writing style."""
        try:
            # Extract style information
            persona, tone, style_traits, sample_text = self._extract_profile_data(user_profile)
            
            # Style Guidance
            style_guidance = f"""
            Writing Persona: {persona}
            Tone: {tone}
            Style Traits:
            {self._format_style_traits(style_traits)}
            
            Sample Text in This Style:
            {sample_text}
            """
            
            prompt = f"""
            You are Claude, a helpful AI writing assistant that adapts your responses to match specific writing styles.
            
            USER'S PREFERRED WRITING STYLE:
            {style_guidance}
            
            USER QUERY:
            {query}
            
            ADDITIONAL CONTEXT:
            {context}
            
            Answer the user's query with helpful, accurate information.
            
            IMPORTANT WRITING INSTRUCTIONS:
            1. Write your ENTIRE response matching the user's preferred writing style
            2. Maintain the specified persona, tone and all style traits consistently
            3. Your writing should sound like it could have been written by the same person who wrote the sample text
            4. Do not mention or call attention to the fact that you're adopting a specific style
            5. Do not use generic phrases that don't match the style (like "I hope this helps")
            6. If the style is casual/informal, be conversational but still provide quality information
            7. If the style is formal/expert, maintain professionalism while being clear
            8. Adapt vocabulary, sentence structure, and pacing to match the style perfectly
            """
            
            logger.info(f"Sending chat completion request for persona: {persona}")
            response = self.claude_client.predict(prompt)
            
            return {
                "response": response,
                "query": query,
                "style_used": persona
            }
                
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return {
                "response": f"I'm sorry, I encountered an error: {str(e)}",
                "query": query,
                "style_used": "default"
            }
            
    def _format_style_traits(self, style_traits):
        """Format style traits for prompt inclusion"""
        if not style_traits:
            return "No specific style traits provided."
            
        formatted_traits = ""
        for trait in style_traits:
            formatted_traits += f"- {trait}\n"
        return formatted_traits