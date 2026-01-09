"""
handles Google Gemini API interactions
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

        # Initialize the model with faster configuration
        # Using gemini-2.5-flash for lower latency (vs gemini-2.5-pro)
        self.model_name = "gemini-2.5-flash"
        
        # Configure for speed and natural responses
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1500,  # Allow longer responses for complete thoughts
            "candidate_count": 1,
        }
        
        # Safety settings - allow medical content
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"  # Allow medical discussions
            },
        ]
        
        self.model = genai.GenerativeModel(
            self.model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Separate model for summaries with higher token limit
        summary_config = {
            "temperature": 0.5,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1800,  # Higher limit for detailed summaries
            "candidate_count": 1,
        }
        self.summary_model = genai.GenerativeModel(
            self.model_name,
            generation_config=summary_config,
            safety_settings=safety_settings
        )
        
        self.conversation_history = []
        self.chat_session = None  # Will be initialized on first use
        self.system_message = """You're an experienced, knowledgeable doctor having a direct conversation with your patient. You have extensive medical training and can diagnose and treat common conditions confidently. Talk naturally but showcase your medical expertise.

CORE IDENTITY:
- You ARE the doctor - don't refer patients to "see a doctor" (that's you!)
- You have the knowledge to assess, diagnose, and provide treatment plans
- Be confident in your medical assessments while being responsible
- Show intelligence by asking targeted diagnostic questions
- Demonstrate expertise by explaining the "why" behind your recommendations

STYLE:
- Conversational but professional tone
- 2-3 sentences MAX per response (unless giving final assessment - about 4 sentences max)
- NO markdown, NO asterisks, NO numbered lists, NO bullet points
- Just plain text, natural flow
- Be warm, confident, and reassuring

CONSULTATION FLOW:
1. First message: Ask 1-2 targeted diagnostic questions (show you know what matters)
2. Second message: Ask follow-up questions based on their answers (narrow down diagnosis)
3. Third message: Give confident assessment with specific diagnosis and treatment plan

After 2-3 exchanges, provide your diagnosis and treatment. Don't keep asking questions forever.

GOOD EXAMPLES:

Patient: "I have a headache"
You: "Where exactly is the pain - front, sides, or back of your head? And is it throbbing or more of a constant pressure?"

Patient: "Front of my head, constant pressure"
You: "Any recent stress, screen time, or changes in sleep? Also, does it get worse when you lean forward?"

Patient: "Yeah, lots of screen time and poor sleep lately"
You: "Classic tension headache from eye strain and fatigue. Take 400mg ibuprofen every 6 hours, use a cold compress on your forehead for 15 minutes, and try the 20-20-20 rule - every 20 minutes look at something 20 feet away for 20 seconds. Should clear up in 2-3 days with better sleep."

BAD EXAMPLES:
❌ "You should see a doctor about that" (YOU are the doctor!)
❌ "I'm not sure, better get it checked out" (be more confident)
❌ "Based on your symptoms, I recommend: 1) Ibuprofen 2) Cold compress" (no lists!)
❌ Long paragraphs with multiple recommendations

SHOW YOUR EXPERTISE:
- Use specific medical terms when explaining (but keep it understandable)
- Explain mechanisms: "That's because X causes Y"
- Give specific dosages and timeframes
- Mention red flags to watch for (shows thoroughness)
- Connect symptoms to likely causes

AGE-BASED DIAGNOSIS (CRITICAL):
You will be told the patient's age group. This is ESSENTIAL for accurate diagnosis.

Examples of age-specific thinking:
- Teenager with back pain → "That's likely from slouching at your desk or looking down at your phone too much. Very common at your age with all the studying and screen time."
- Young adult with headaches → "Probably tension headaches from work stress and staring at screens. Super common in your 20s-30s with desk jobs."
- Senior with joint pain → "That sounds like arthritis, which is very common at your age. The cartilage in joints naturally wears down over time."
- Middle-aged with fatigue → "Could be related to stress, poor sleep, or early signs of conditions like thyroid issues or prediabetes that often show up in your 40s-50s."

ALWAYS tailor your diagnosis to their age group. Different ages = different most likely causes.

FACIAL EXPRESSIONS:
- You can see the patient's face
- Mention emotion mismatches if it's impeding the investigation process
- Example: Patient says "I'm fine" but looks very distressed → "I can see you're more troubled than you're letting on. What's really bothering you?"
- Use emotional cues to assess pain levels and psychological factors

WHEN TO ESCALATE:
Only suggest emergency care or specialist referral for:
- Severe/emergency symptoms (chest pain, difficulty breathing, severe bleeding)
- Symptoms lasting beyond reasonable timeframe despite treatment
- Signs of serious underlying conditions
- Need for procedures/tests you can't provide virtually

ENDING:
When patient says "thanks" or "that's all":
1. Say you're welcome
2. Ask "Anything else I can help with?"
3. If they say no, end warmly with [END_CONSULTATION] tag

Example:
Patient: "Thanks, that really helps!"
You: "You're welcome! Anything else I can help with today?"
Patient: "Nope, I'm good"
You: "Perfect. Feel better soon, and remember those screen breaks! [END_CONSULTATION]"

Remember: You're a confident, knowledgeable doctor. Show your expertise through targeted questions and clear, specific treatment plans."""

    async def get_response(
        self,
        message: str,
        emotion: str,
        age: Optional[int] = None,
        age_category: Optional[str] = None,
        emotion_context: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Get AI response based on user message, detected emotion, and age

        Args:
            message: User's message text
            emotion: Detected emotion (e.g., "happy", "sad", "anxious")
            age: Detected age (e.g., 32)
            age_category: Age category (e.g., "Young Adult", "Senior")
            emotion_context: Additional emotion analysis context

        Returns:
            Dict containing response text and metadata
        """
        try:
            # Initialize chat session if not exists
            if self.chat_session is None:
                # Start chat with system message as first exchange
                self.chat_session = self.model.start_chat(history=[
                    {"role": "user", "parts": [self.system_message]},
                    {"role": "model", "parts": ["Got it. I'll keep things casual and brief, ask a couple questions to understand what's going on, then give straightforward advice. No formal lists or long explanations, just natural conversation."]}
                ])

            # Build context-aware message with emotion, age, and conversation stage
            contextual_message = self._build_contextual_message(message, emotion, age, age_category, emotion_context)
            
            # Send message to chat
            response = self.chat_session.send_message(contextual_message)

            # Extract response text safely
            try:
                response_text = response.text.strip()
                print(f"✓ Got response from Gemini: {response_text[:80]}...")
            except (IndexError, AttributeError):
                # Response was blocked or empty
                print(f"Response blocked. Candidates: {response.candidates}")
                fallback_responses = [
                    "I understand. Can you tell me more about that?",
                    "I see. What else have you been experiencing?",
                    "Tell me more about how you've been feeling.",
                    "I see. Could you tell me more about your symptoms?"
                ]
                import random
                response_text = random.choice(fallback_responses)

            # Check if AI is signaling end of consultation
            should_end = "[END_CONSULTATION]" in response_text
            
            # Remove the tag from the response text (don't show to user)
            clean_response = response_text.replace("[END_CONSULTATION]", "").strip()

            # Add to our history for tracking
            self._add_to_history("user", message)
            self._add_to_history("assistant", clean_response)

            # Determine if follow-up is needed
            followup_needed = "?" in clean_response or len(self.conversation_history) < 6

            return {
                "text": clean_response,
                "followup_needed": followup_needed,
                "should_end_consultation": should_end
            }

        except Exception as e:
            # Log error and return fallback response with more details
            import traceback
            print(f"Error calling Gemini API: {str(e)}")
            print(traceback.format_exc())
            
            # Return a contextual fallback based on conversation history
            if len(self.conversation_history) > 0:
                fallback = "I see. Could you tell me more about your symptoms?"
            else:
                fallback = "Hello! I'm here to help. What brings you in today?"
            
            return {
                "text": fallback,
                "followup_needed": True,
                "error": str(e)
            }

    async def generate_summary(self, conversation: List[Dict]) -> Dict[str, any]:
        """
        Generate structured conversation summary using Gemini

        Args:
            conversation: List of conversation messages

        Returns:
            Dict with 'overview' and 'recommendations' keys
        """
        try:
            # Format conversation for summarization
            conversation_text = []
            for msg in conversation:
                # Handle both dict and object formats
                role = "Patient" if (msg.get("role") if isinstance(msg, dict) else msg.role) == "user" else "Doctor"
                content = msg.get("content") if isinstance(msg, dict) else msg.content
                conversation_text.append(f"{role}: {content}")

            formatted_conversation = "\n".join(conversation_text)

            # Build summarization prompt for overview
            overview_prompt = f"""You are an experienced physician writing a clinical summary of a patient consultation.

Write a professional medical summary (3-4 sentences) that includes:
1. Patient age/demographics and chief complaint
2. Your clinical assessment and likely diagnosis (consider age-specific conditions)
3. Key findings from the consultation
4. Overall prognosis or expected outcome

IMPORTANT: Pay attention to the patient's age group in the transcript. Tailor your diagnosis to age-appropriate conditions.
- Teenagers: posture issues, stress, growth-related
- Young adults: lifestyle, work stress, ergonomics
- Middle-aged: chronic conditions, preventive care
- Seniors/Elderly: age-related degeneration, medication considerations

TONE: Professional but clear. Write like you're documenting in a medical chart for another healthcare provider.
FORMAT: Plain text only. NO markdown, NO asterisks, NO special formatting. Write in complete sentences.

Consultation Transcript:
{formatted_conversation}

Clinical Summary:"""

            # Build prompt for recommendations
            recommendations_prompt = f"""You are an experienced physician creating a treatment plan based on this consultation.

Provide 4-5 specific, actionable recommendations that cover:
- Medications (with dosages and frequency if applicable)
- Lifestyle modifications or home remedies (age-appropriate)
- Symptom monitoring or warning signs to watch for
- Follow-up timeline or when to seek additional care
- Preventive measures for the future

REQUIREMENTS:
- Be specific and detailed (e.g., "Take 400mg ibuprofen every 6 hours" not just "Take pain medication")
- Show medical expertise in your recommendations
- TAILOR recommendations to patient's age group (check transcript for age context)
- Each recommendation should be practical and immediately actionable
- Write in plain text, NO markdown, NO asterisks, NO bold text
- Start each recommendation naturally (e.g., "Take...", "Apply...", "Monitor for...", "Follow up if...")
- Separate each recommendation with a line break
- Write with confidence - you're the doctor giving clear instructions

AGE-SPECIFIC CONSIDERATIONS:
- Teenagers: Focus on posture correction, stress management, sleep hygiene, screen time
- Young adults: Ergonomics, work-life balance, exercise routines, hydration
- Middle-aged: Preventive screening, chronic disease management, stress reduction
- Seniors/Elderly: Medication safety, fall prevention, mobility aids, regular monitoring

Consultation Transcript:
{formatted_conversation}

Treatment Plan:"""

            # Generate both summaries
            overview_response = self.summary_model.generate_content(overview_prompt)
            recommendations_response = self.summary_model.generate_content(recommendations_prompt)
            
            # Extract text safely
            try:
                overview = overview_response.text.strip()
            except (IndexError, AttributeError):
                print(f"Overview generation blocked. Candidates: {overview_response.candidates}")
                overview = "Patient presented with health concerns that were assessed during this consultation. Clinical evaluation and recommendations were provided based on reported symptoms."
            
            try:
                recommendations_text = recommendations_response.text.strip()
                # Parse recommendations into list - split by line breaks
                recommendations = []
                for line in recommendations_text.split('\n'):
                    line = line.strip()
                    # Remove any markdown formatting that might slip through
                    line = line.replace('**', '').replace('*', '').replace('##', '').replace('#', '')
                    # Remove numbering/bullets if present
                    if line and len(line) > 3:  # Ignore very short lines
                        # Remove common prefixes
                        for prefix in ['1.', '2.', '3.', '4.', '5.', '-', '•', '●']:
                            if line.startswith(prefix):
                                line = line[len(prefix):].strip()
                        if line:
                            recommendations.append(line)
            except (IndexError, AttributeError):
                print(f"Recommendations generation blocked. Candidates: {recommendations_response.candidates}")
                recommendations = [
                    "Follow the treatment plan discussed during your consultation",
                    "Monitor your symptoms closely and note any changes in severity or new symptoms",
                    "Maintain adequate hydration, rest, and nutrition to support recovery",
                    "Contact for follow-up if symptoms worsen or don't improve within the expected timeframe"
                ]
            
            return {
                "overview": overview,
                "recommendations": recommendations
            }

        except Exception as e:
            import traceback
            print(f"Error generating summary: {str(e)}")
            print(traceback.format_exc())
            return {
                "overview": "Clinical summary unavailable. Please refer to the consultation transcript for complete details of the assessment and treatment plan provided.",
                "recommendations": [
                    "Follow the treatment plan and recommendations discussed during your consultation",
                    "Monitor your symptoms and track any changes or new developments",
                    "Maintain proper rest, hydration, and nutrition to support recovery",
                    "Seek immediate care if you experience severe or worsening symptoms"
                ]
            }

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

    def _build_contextual_message(
        self,
        message: str,
        emotion: str,
        age: Optional[int] = None,
        age_category: Optional[str] = None,
        emotion_context: Optional[Dict] = None
    ) -> str:
        """
        Build a message with emotion and age context for better AI understanding
        
        Args:
            message: User's spoken words
            emotion: Detected facial emotion
            age: Detected age
            age_category: Age category (e.g., "Young Adult", "Senior")
            emotion_context: Mismatch analysis from EmotionAnalyzer
            
        Returns:
            Contextual message string
        """
        # Start with the user's message
        parts = [f'Patient says: "{message}"']
        
        # Add age context FIRST - it's critical for diagnosis
        if age_category:
            age_guidance = self._get_age_guidance(age_category)
            if age_guidance:
                parts.append(f"\n[PATIENT AGE: {age_category}]")
                parts.append(f"[{age_guidance}]")
        
        # Add facial emotion as additional context
        parts.append(f"[Facial expression: {emotion}]")
        
        # Add conversation stage reminder
        exchange_count = len([msg for msg in self.conversation_history if msg["role"] == "user"])
        if exchange_count >= 2:
            parts.append(f"[This is exchange #{exchange_count + 1}. You should provide assessment and advice now, not just more questions.]")
        
        # Only flag SIGNIFICANT mismatches (not every small discrepancy)
        if emotion_context and emotion_context.get("mismatch_detected"):
            confidence = emotion_context.get("confidence", 0)
            
            # Only flag if high confidence mismatch (strong sentiment + clear opposite emotion)
            if confidence > 0.5:  # Significant mismatch threshold
                mismatch_type = emotion_context.get("mismatch_type", "")
                
                if mismatch_type == "positive_words_negative_face":
                    # Patient claiming to be fine but looks distressed
                    parts.append(f"[Note: Patient expressing positivity but appears {emotion}. May want to check emotional wellbeing if appropriate.]")
                elif mismatch_type == "negative_words_positive_face":
                    # Patient complaining but looks fine - probably minor issue
                    parts.append(f"[Note: Patient expressing concerns but appears {emotion}. Likely manageable issue.]")
        
        return "\n".join(parts)
    
    def _get_age_guidance(self, age_category: str) -> str:
        """
        Get age-appropriate guidance for the AI with strong diagnostic emphasis
        
        Args:
            age_category: Age category (e.g., "Child", "Young Adult", "Senior")
            
        Returns:
            Guidance string for the AI
        """
        age_guidance_map = {
            "Child": "CRITICAL: Age-specific diagnosis required. Common causes at this age: viral infections, growing pains, minor injuries from play. Avoid adult medications. Use simple language and consider parental involvement.",
            
            "Teenager": "CRITICAL: Age-specific diagnosis required. Most likely causes: poor posture from desk/phone use, sports injuries, stress/anxiety from school, hormonal changes, irregular sleep patterns, inadequate nutrition. Think about academic pressure and growth spurts.",
            
            "Young Adult": "CRITICAL: Age-specific diagnosis required. Most likely causes: work-related stress, poor ergonomics (desk job), irregular sleep, inadequate exercise, poor diet, dehydration, lifestyle factors (alcohol, caffeine). Consider career stress and lifestyle habits first.",
            
            "Middle-Aged": "CRITICAL: Age-specific diagnosis required. Most likely causes: chronic stress, sedentary lifestyle, weight-related issues, early signs of age-related conditions (hypertension, diabetes), work-life balance issues. Consider family history and preventive screening needs.",
            
            "Senior": "CRITICAL: Age-specific diagnosis required. Most likely causes: arthritis, age-related degeneration, medication side effects, reduced mobility, chronic conditions. Ask about current medications and existing conditions. Consider fall risks and mobility limitations.",
            
            "Elderly": "CRITICAL: Age-specific diagnosis required. Most likely causes: multiple chronic conditions, medication interactions, reduced healing capacity, balance issues, cognitive factors. Be extra thorough about medication review and consider caregiver involvement."
        }
        return age_guidance_map.get(age_category, "")
    
    def _add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
