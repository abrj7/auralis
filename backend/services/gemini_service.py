"""
Gemini AI service - handles Google Gemini API interactions
"""
import os
from typing import Dict, List, Optional
import google.generativeai as genai


class GeminiService:
    """Service for interacting with Google Gemini API"""

    def __init__(self):
        """Initialize Gemini service with API key"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        # Configure Gemini API
        genai.configure(api_key=self.api_key)

        # Initialize the model
        self.model_name = "gemini-2.5-pro"
        self.model = genai.GenerativeModel(self.model_name)
        self.conversation_history = []

        # System prompt for AI doctor persona
        self.system_prompt = """You are an empathetic AI doctor conducting a video consultation.
Your role is to:
- Listen actively to patient concerns
- Ask relevant follow-up questions
- Provide preliminary health guidance
- Show empathy and understanding
- Recognize when professional medical attention is needed

Keep responses conversational and concise (2-3 sentences max)."""

    async def get_response(
        self,
        message: str,
        emotion: str,
        emotion_context: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Get AI response based on user message and detected emotion

        Args:
            message: User's message text
            emotion: Detected emotion (e.g., "happy", "sad", "anxious")
            emotion_context: Additional emotion analysis context

        Returns:
            Dict containing response text and metadata
        """
        try:
            # Build the prompt with emotion context
            prompt = self._build_prompt(message, emotion, emotion_context)

            # Generate response from Gemini
            response = self.model.generate_content(prompt)

            # Extract response text
            response_text = response.text.strip()

            # Add messages to conversation history
            self._add_to_history("user", message)
            self._add_to_history("assistant", response_text)

            # Determine if follow-up is needed (simple heuristic)
            followup_needed = "?" in response_text or len(self.conversation_history) < 6

            return {
                "text": response_text,
                "followup_needed": followup_needed
            }

        except Exception as e:
            # Log error and return fallback response
            print(f"Error calling Gemini API: {str(e)}")
            return {
                "text": "I'm having trouble processing that right now. Could you rephrase your concern?",
                "followup_needed": True,
                "error": str(e)
            }

    async def generate_summary(self, conversation: List[Dict]) -> str:
        """
        Generate conversation summary using Gemini

        Args:
            conversation: List of conversation messages

        Returns:
            Summary text
        """
        # TODO: Implement conversation summarization
        # - Format conversation history
        # - Request summary from Gemini
        # - Extract key health concerns and recommendations

        return "Conversation summary will be generated here."

    def _build_prompt(
        self,
        message: str,
        emotion: str,
        emotion_context: Optional[Dict] = None
    ) -> str:
        """
        Build prompt with emotion context

        Args:
            message: User message
            emotion: Detected emotion
            emotion_context: Additional context

        Returns:
            Formatted prompt string
        """
        # Start with system prompt
        prompt_parts = [self.system_prompt]

        # Add conversation history if exists
        if self.conversation_history:
            prompt_parts.append("\n\nConversation history:")
            for msg in self.conversation_history[-6:]:  # Keep last 6 messages for context
                role = "Patient" if msg["role"] == "user" else "Doctor"
                prompt_parts.append(f"{role}: {msg['content']}")

        # Add emotion context
        prompt_parts.append(f"\n\nCurrent patient emotion detected: {emotion}")

        # Add emotion mismatch context if present
        if emotion_context and emotion_context.get("mismatch_detected"):
            prompt_parts.append(
                f"Note: There's a mismatch between what the patient is saying and their facial expression. "
                f"They appear {emotion} but their words suggest {emotion_context.get('text_sentiment', 'different feelings')}. "
                f"Consider probing gently to understand their true feelings."
            )

        # Add current message
        prompt_parts.append(f"\n\nPatient: {message}")
        prompt_parts.append("\nDoctor:")

        return "\n".join(prompt_parts)

    def _add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
