# Libs
import logging
import json
from dotenv import load_dotenv
from typing import Optional, Dict, Any, Tuple
from bedrock.anthropic_chat_completions import BedrockAnthropicChatCompletions

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

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

    def _create_style_guidance(self, user_profile: dict) -> str:
        """Create consistent style guidance string for all tools"""
        persona, tone, style_traits, sample_text = self._extract_profile_data(user_profile)
        
        return f"""
        Writing Persona: {persona}
        Tone: {tone}
        Style Traits:
        {self._format_style_traits(style_traits)}
        
        Sample Text in This Style:
        {sample_text}
        """

    def refine_content(self, content: str, user_profile: dict) -> dict:
        """Refine content according to user's preferred writing style."""
        try: 
            persona, tone, style_traits, sample_text = self._extract_profile_data(user_profile)
            style_guidance = self._create_style_guidance(user_profile)
            
            prompt = f"""
            You are a writing assistant that refines content according to specific style profiles.
            
            USER PROFILE:
            {style_guidance}
            
            CONTENT TO REFINE:
            {content}
            
            Rewrite this content to perfectly match the user's writing style, tone, and persona.
            Be extremely careful to follow ALL style traits listed.
            
            IMPORTANT REQUIREMENTS:
            1. Preserve the original meaning and key information
            2. Rewrite in the user's specific writing style and tone
            3. Apply all the style traits consistently throughout
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

    def create_outline(self, topic_details: str, user_profile: dict) -> dict:
        """Create an outline according to user's preferred writing style using topic details."""
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
            
            <hr>
            <p><strong>Writing Tips:</strong> Adapt tone to match your style, use transition sentences between sections, include relevant data/examples throughout.</p>
            """

            prompt = f"""
            You are a writing coach creating a CONCISE STRUCTURAL OUTLINE, not a full article.

            USER PROFILE:
            {style_guidance}

            TOPIC INFORMATION:
            {topic_details}

            Create a brief structural outline that guides the user on HOW to write about this topic.
            
            OUTLINE REQUIREMENTS:
            1. Provide STRUCTURE and GUIDANCE, not full content
            2. Use brief instructional phrases like "Focus on...", "Include...", "Emphasize..."
            3. Give writing direction rather than complete sentences
            4. Keep sections concise - this is a roadmap, not the destination
            5. Adapt the structure to fit the specific topic provided
            6. Include writing tips specific to the user's style
            
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
        
    def proofread_content(self, content: str, user_profile: dict) -> dict:
        """Proofread content while preserving user's preferred writing style."""
        try:
            persona, tone, style_traits, sample_text = self._extract_profile_data(user_profile)
            style_guidance = self._create_style_guidance(user_profile)
            
            prompt = f"""
            You are a meticulous proofreader that only identifies genuine errors in text.
            
            USER PROFILE:
            {style_guidance}
            
            CONTENT TO PROOFREAD:
            {content}
            
            CRITICAL INSTRUCTIONS:
            1. ONLY flag actual errors: spelling mistakes, grammar errors, punctuation errors, typos
            2. DO NOT suggest stylistic changes - preserve the user's writing style completely
            3. DO NOT suggest corrections where the original and corrected text would be identical
            4. BE CONSERVATIVE - when in doubt, don't suggest a correction
            5. IGNORE style preferences - only fix objective errors
            6. DO NOT change contractions, colloquialisms, or informal language if they match the user's style
            
            ONLY return corrections for clear, objective errors like:
            ✓ "teh" → "the" (typo)
            ✓ "recieve" → "receive" (spelling)
            ✓ "Your correct" → "You're correct" (grammar)
            ✓ Missing punctuation at sentence end
            
            DO NOT return corrections for:
            ✗ Style preferences
            ✗ Word choice variations
            ✗ Sentence structure changes
            ✗ Tone adjustments
            ✗ Identical text
            
            Return your response as JSON with only this field:
            - corrections: List of ACTUAL errors found, each with "original" and "corrected" versions
            
            Example format:
            {{"corrections": [{{"original": "teh", "corrected": "the"}}, {{"original": "recieve", "corrected": "receive"}}]}}
            
            If no genuine errors are found, return: {{"corrections": []}}
            
            Remember: Only include corrections where the "original" and "corrected" are genuinely different and fix an actual error.
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

    def chat_completion(self, query: str, user_profile: dict) -> dict:
        """Provide a chat response according to user's preferred writing style."""
        try:
            persona, tone, style_traits, sample_text = self._extract_profile_data(user_profile)
            style_guidance = self._create_style_guidance(user_profile)
            
            prompt = f"""
            You are Claude, a helpful AI writing assistant having a natural conversation with a user.
            
            USER'S PREFERRED WRITING STYLE:
            {style_guidance}
            
            USER QUERY:
            {query}
            
            Respond naturally and conversationally, matching the user's writing style.
            
            RESPONSE GUIDELINES:
            1. Keep responses concise and conversational - match the length and energy of the user's message
            2. For simple greetings like "hi" or "hello", respond briefly and warmly in their style
            3. For questions, provide helpful answers but avoid unnecessary elaboration
            4. Write in the user's persona, tone, and style traits naturally
            5. Sound like the same person who wrote their sample text
            6. Don't be overly formal or verbose unless their style specifically calls for it
            7. Match their conversational energy - short query = short response, detailed query = detailed response
            8. Never mention that you're adapting to a style - just be natural
            
            Remember: This is a chat conversation, not an essay. Be helpful but conversational.
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
        """Format style traits for prompt inclusion"""
        if not style_traits:
            return "No specific style traits provided."
        
        return "\n".join(f"- {trait}" for trait in style_traits)