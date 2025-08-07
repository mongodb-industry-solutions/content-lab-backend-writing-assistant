# ---tools.py---

# This file contains the WritingTools class, which is used to process writing requests and generate responses using the BedrockAnthropicChatCompletions class.

# Importing necessary libraries
import logging
import json
from dotenv import load_dotenv
from typing import Optional, Dict, Any, Tuple
from bedrock.anthropic_chat_completions import BedrockAnthropicChatCompletions

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class WritingTools:
    """A class to process writing requests and generate responses using the BedrockAnthropicChatCompletions class."""

    # Setting up logging
    logger = logging.getLogger(__name__)

    # Defining the WritingTools class
    def __init__(self):
        self.claude_client = BedrockAnthropicChatCompletions()

    def _extract_profile_data(self, user_profile: dict) -> Tuple[str, str, list, str]:
        """
        Extract all needed profile data with defaults
        :param user_profile: A dictionary containing the user's profile data
        :return: A tuple containing the user's persona, tone, style traits, and sample text
        """
        return (
            user_profile.get("persona", "Default Writer"),
            user_profile.get("tone", "Neutral"),
            user_profile.get("styleTraits", []),
            user_profile.get("sampleText", "")
        )

    def _create_style_guidance(self, user_profile: dict) -> str:
        """
        Create consistent style guidance string for all tools
        :param user_profile: A dictionary containing the user's profile data
        :return: A string containing the user's persona, tone, style traits, and sample text
        """
        persona, tone, style_traits, sample_text = self._extract_profile_data(user_profile)
        
        return f"""
        Writing Persona: {persona}
        Tone: {tone}
        Style Traits:
        {self._format_style_traits(style_traits)}
        
        Sample Text in This Style:
        {sample_text}
        """

    def refine_content(self, content: str, user_profile: dict, user_input: str) -> dict:
        """
        Refine content according to user's preferred writing style.
        :param content: A string containing the content to refine
        :param user_profile: A dictionary containing the user's profile data
        :param user_input: A string containing the user's input
        :return: A dictionary containing the refined content
        """
        try: 
            persona, tone, style_traits, sample_text = self._extract_profile_data(user_profile)
            style_guidance = self._create_style_guidance(user_profile)
            
            prompt = f"""
            You are a writing assistant that refines content according to specific style profiles.
            
            PRIMARY USER REQUEST (HIGHEST PRIORITY):
            {user_input}
            
            USER PROFILE:
            {style_guidance}
            
            CONTENT TO REFINE:
            {content}
            
            CRITICAL: The user's request above is the MOST IMPORTANT requirement. Follow it exactly.
            
            Rewrite this content to fulfill the user's specific request while matching their writing style.
            PRIORITIZE the user's request over everything else, including style consistency if there's a conflict.
            
            REQUIREMENTS (in priority order):
            1. FIRST AND FOREMOST: Follow the user's specific request exactly
            2. Preserve the original meaning and key information (unless user requests otherwise)
            3. Apply the user's writing style and tone where possible
            4. Return ONLY the refined HTML content - no JSON formatting needed
            5. If the original content has HTML formatting, preserve and enhance it
            6. If the original content is plain text, return well-formatted HTML
            
            Return the refined content directly without any wrapper text or explanations.
            """
            
            logger.info(f"Sending refine request for persona: {persona}")
            response = self.claude_client.predict(prompt)
        
            logger.info("Successfully generated refined content")
            return {
                "html_content": response
            }
            
        except Exception as e:
            logger.error(f"Error in refine tool: {e}")
            return {
                "html_content": f"<p>Error occurred: {str(e)}</p>"
            }

    def create_outline(self, topic_details: str, user_profile: dict, user_input: str) -> dict:
        """
        Create an outline according to user's preferred writing style using topic details.
        :param topic_details: A string containing the topic details
        :param user_profile: A dictionary containing the user's profile data
        :param user_input: A string containing the user's input
        :return: A dictionary containing the outline
        """
        try: 
            style_guidance = self._create_style_guidance(user_profile)
            
            # Example HTML structure for concise outline
            html_example = """
            <h2>1. Opening Hook</h2>
            <p><em>Start with: A compelling statistic, question, or scenario related to [TOPIC]</em></p>
            
            <h2>2. Introduction & Context</h2>
            <p><em>Brief overview: Define the topic and explain why it matters to your audience</em></p>
            
            <h2>3. Main Content Structure</h2>
            <h3>Key Point A: [Primary Aspect]</h3>
            <p><em>Focus on: Core concepts, supporting evidence, real-world examples</em></p>
            
            <h3>Key Point B: [Secondary Aspect]</h3>
            <p><em>Include: How it connects to Point A, practical applications</em></p>
            
            <h3>Key Point C: [Final Aspect]</h3>
            <p><em>Emphasize: Future implications, actionable insights</em></p>
            
            <h2>4. Conclusion & Call-to-Action</h2>
            <p><em>Wrap up with: Key takeaways summary, next steps for readers</em></p>
            
            """

            prompt = f"""
            You are a writing coach creating a CONCISE STRUCTURAL OUTLINE, not a full article.

            PRIMARY USER REQUEST (HIGHEST PRIORITY):
            {user_input}

            USER PROFILE:
            {style_guidance}

            TOPIC INFORMATION:
            {topic_details}

            CRITICAL: The user's request above is the MOST IMPORTANT requirement. Everything else is secondary.
            
            Create a brief structural outline that guides the user on HOW to write about this topic.
            PRIORITIZE fulfilling the user's specific request above all other considerations.
            
            OUTLINE REQUIREMENTS (in priority order):
            1. FIRST AND FOREMOST: Follow the user's specific request exactly
            2. Provide STRUCTURE and GUIDANCE, not full content
            3. Use brief instructional phrases like "Focus on...", "Include...", "Emphasize..."
            4. Give writing direction rather than complete sentences
            5. Keep sections concise - this is a roadmap, not the destination
            6. Adapt the structure to fit the specific topic provided
            7. Include writing tips specific to the user's style
            
            FORMAT REQUIREMENTS:
            Return your outline as HTML following this structure:
            
            {html_example}
            
            IMPORTANT: 
            - Replace [TOPIC] and [Aspects] with actual topic elements
            - Keep guidance brief and actionable
            - Focus on WHAT to write about, not writing the content itself
            - Provide 3-5 main sections maximum
            - Use italics for guidance text, bold for section labels
            
            Return ONLY clean HTML that serves as a writing guide, not a complete article.
            """

            logger.info("Sending HTML outline request for topic details")
            response = self.claude_client.predict(prompt)

            logger.info("Successfully generated HTML outline")
            return {
                "html_content": response
            }
                
        except Exception as e:
            logger.error(f"Error in outline tool: {e}")
            return {
                "html_content": f"<p>Error occurred: {str(e)}</p>"
            }
        
    def proofread_content(self, content: str, user_profile: dict, user_input: str) -> dict:
        """
        Proofread content while preserving user's preferred writing style.
        :param content: A string containing the content to proofread
        :param user_profile: A dictionary containing the user's profile data
        :param user_input: A string containing the user's input
        :return: A dictionary containing the proofread content
        """
        try:
            persona, tone, style_traits, sample_text = self._extract_profile_data(user_profile)
            style_guidance = self._create_style_guidance(user_profile)
            
            prompt = f"""
            You are a meticulous proofreader that identifies errors in text.
            
            PRIMARY USER INSTRUCTIONS (HIGHEST PRIORITY):
            {user_input}
            
            USER PROFILE:
            {style_guidance}
            
            CONTENT TO PROOFREAD:
            {content}
            
            CRITICAL: The user's instructions above are the MOST IMPORTANT. Follow them exactly.
            
            IMPORTANT: When user mentions specific letters (like "T and G"), apply case-insensitively (both "T/t" and "G/g").
            
            CRITICAL RULE: If user gives specific criteria (like "only fix words starting with X"), IGNORE ALL OTHER ERRORS. Only suggest corrections that meet the exact criteria.
            
            CRITICAL RULE: NEVER return a correction where "original" and "corrected" are identical!
            
            CRITICAL RULE: ONLY suggest corrections for text that actually appears in the content above. Do not make up or hallucinate errors.
            
            INSTRUCTIONS (in priority order):
            1. FIRST AND FOREMOST: Follow the user's specific instructions exactly (with case-insensitive interpretation)
            2. ONLY suggest corrections where the original text actually has an error AND needs to be changed
            3. If no special instructions, focus on spelling mistakes, grammar errors, punctuation errors, typos
            4. DO NOT suggest stylistic changes unless specifically requested by user
            5. BE CONSERVATIVE - when in doubt, don't suggest a correction (unless user asks for aggressive proofreading)
            6. Preserve the user's writing style completely (unless user requests style changes)
            7. DO NOT change contractions, colloquialisms, or informal language if they match the user's style
            
            Examples of CORRECT corrections:
            - "teh" → "the" (actual typo fix)
            - "recieve" → "receive" (actual spelling fix)
            - "Your correct" → "You're correct" (actual grammar fix)
            
            Examples of WRONG corrections (DO NOT DO THESE):
            - "challenges" → "challenges" (identical text - don't suggest!)
            - "critical" → "critical" (identical text - don't suggest!)
            - "word" → "word" (no actual error - don't suggest!)
            - Any correction where original = corrected
            
            VALIDATION CHECK: Before adding any correction, verify:
            1. "original" != "corrected" 
            2. The correction meets the user's specific criteria (if any)
            3. The original text actually exists in the content
            
            Return your response as JSON with only this field:
            - corrections: List of ACTUAL errors found where original ≠ corrected, each with "original" and "corrected" versions
            
            Example format:
            {{"corrections": [{{"original": "teh", "corrected": "the"}}, {{"original": "recieve", "corrected": "receive"}}]}}
            
            If no genuine errors are found, return: {{"corrections": []}}
            """
            
            logger.info(f"Sending proofread request for persona: {persona}")
            response = self.claude_client.predict(prompt)
            
            try:
                result = json.loads(response)
                logger.info("Successfully parsed proofread response as JSON")
                return result
            except json.JSONDecodeError:
                logger.error("Failed to parse response as JSON, returning empty corrections")
                return {"corrections": []}
                
        except Exception as e:
            logger.error(f"Error in proofread tool: {e}")
            return {"corrections": []}

    def chat_completion(self, query: str, user_profile: dict, content: str) -> dict:
        """
        Provide a chat response according to user's preferred writing style.
        :param query: A string containing the user's query
        :param user_profile: A dictionary containing the user's profile data
        :param content: A string containing the content to chat about
        :return: A dictionary containing the chat response
        """
        try:
            persona, tone, style_traits, sample_text = self._extract_profile_data(user_profile)
            style_guidance = self._create_style_guidance(user_profile)
            
            prompt = f"""
            You are Claude, a helpful AI writing assistant having a natural conversation with a user.
            
            USER'S PREFERRED WRITING STYLE:
            {style_guidance}
            
            DRAFT CONTENT FOR CONTEXT:
            {content}
            
            USER QUERY:
            {query}
            
            CRITICAL: Match the user's energy and length. Short query = short response.
            
            RESPONSE RULES:
            1. For greetings ("hi", "hello"): Respond with 1 brief, warm sentence only
            2. For simple questions: Give direct answers without elaboration
            3. Match their conversational tone and writing style naturally
            4. Use their persona, tone, and style traits
            5. Never mention you're adapting to their style
            6. Content is context only - reference if they ask about it
            7. Be conversational, not formal or essay-like
            8. KEEP RESPONSES SHORT - no multi-paragraph responses for simple interactions
            
            This is casual chat, not content creation. Be brief and natural.
            """
            
            logger.info(f"Sending chat completion request for persona: {persona}")
            response = self.claude_client.predict(prompt)
            
            return {
                "response": response
            }
                
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return {
                "response": f"I'm sorry, I encountered an error: {str(e)}"
            }
            
    def _format_style_traits(self, style_traits):
        """
        Format style traits for prompt inclusion
        :param style_traits: A list containing the user's style traits
        :return: A string containing the formatted style traits
        """
        if not style_traits:
            return "No specific style traits provided."
        
        return "\n".join(f"- {trait}" for trait in style_traits)