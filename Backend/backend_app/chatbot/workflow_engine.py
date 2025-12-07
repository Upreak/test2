"""
Chatbot Workflow Engine
Main dispatcher & state transitions for chatbot functionality
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime

from backend_app.chatbot.models.session_model import UserRole, ConversationState
from backend_app.chatbot.services.message_router import MessageRouter
from backend_app.chatbot.services.llm_service import LLMService
from backend_app.chatbot.services.skill_registry import SkillRegistry


class WorkflowState(Enum):
    """Workflow states for chatbot conversations"""
    INITIALIZED = "initialized"
    ONBOARDING = "onboarding"
    COLLECTING_INFO = "collecting_info"
    PROCESSING = "processing"
    WAITING_FOR_INPUT = "waiting_for_input"
    COMPLETED = "completed"
    ERROR = "error"


class WorkflowEngine:
    """Main workflow engine for chatbot state management and transitions"""
    
    def __init__(self):
        self.message_router = MessageRouter()
        self.llm_service = LLMService()
        self.skill_registry = SkillRegistry()
        self.state_transitions = self._initialize_state_transitions()
    
    def _initialize_state_transitions(self) -> Dict[str, List[str]]:
        """Initialize valid state transitions"""
        return {
            WorkflowState.INITIALIZED.value: [WorkflowState.ONBOARDING.value],
            WorkflowState.ONBOARDING.value: [
                WorkflowState.COLLECTING_INFO.value,
                WorkflowState.PROCESSING.value,
                WorkflowState.ERROR.value
            ],
            WorkflowState.COLLECTING_INFO.value: [
                WorkflowState.PROCESSING.value,
                WorkflowState.WAITING_FOR_INPUT.value,
                WorkflowState.ERROR.value
            ],
            WorkflowState.PROCESSING.value: [
                WorkflowState.WAITING_FOR_INPUT.value,
                WorkflowState.COMPLETED.value,
                WorkflowState.ERROR.value
            ],
            WorkflowState.WAITING_FOR_INPUT.value: [
                WorkflowState.PROCESSING.value,
                WorkflowState.COMPLETED.value,
                WorkflowState.ERROR.value
            ],
            WorkflowState.COMPLETED.value: [],
            WorkflowState.ERROR.value: [WorkflowState.INITIALIZED.value]
        }
    
    async def process_workflow_step(
        self,
        session_id: str,
        current_state: str,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a single workflow step and return next state
        
        Args:
            session_id: Session identifier
            current_state: Current workflow state
            message: User message
            context: Workflow context
            
        Returns:
            Dict containing next_state, response, and updated context
        """
        try:
            # Determine next state based on current state and message
            next_state = await self._determine_next_state(
                current_state, message, context
            )
            
            # Process the step
            response = await self._process_state_step(
                session_id, next_state, message, context
            )
            
            # Update context
            updated_context = await self._update_context(
                context, next_state, response
            )
            
            return {
                "next_state": next_state,
                "response": response,
                "context": updated_context,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "next_state": WorkflowState.ERROR.value,
                "response": f"An error occurred: {str(e)}",
                "context": context,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _determine_next_state(
        self,
        current_state: str,
        message: str,
        context: Dict[str, Any]
    ) -> str:
        """Determine the next workflow state"""
        
        # If current state is error, always go back to initialized
        if current_state == WorkflowState.ERROR.value:
            return WorkflowState.INITIALIZED.value
        
        # Analyze message intent
        intent = await self._analyze_message_intent(message, context)
        
        # State-specific logic
        if current_state == WorkflowState.INITIALIZED.value:
            return WorkflowState.ONBOARDING.value
        
        elif current_state == WorkflowState.ONBOARDING.value:
            if intent in ["info_provided", "ready_to_proceed"]:
                return WorkflowState.COLLECTING_INFO.value
            elif intent == "help":
                return WorkflowState.WAITING_FOR_INPUT.value
            else:
                return WorkflowState.ONBOARDING.value
        
        elif current_state == WorkflowState.COLLECTING_INFO.value:
            if intent == "info_complete":
                return WorkflowState.PROCESSING.value
            elif intent == "more_info_needed":
                return WorkflowState.WAITING_FOR_INPUT.value
            else:
                return WorkflowState.COLLECTING_INFO.value
        
        elif current_state == WorkflowState.PROCESSING.value:
            if intent == "processing_complete":
                return WorkflowState.COMPLETED.value
            else:
                return WorkflowState.PROCESSING.value
        
        elif current_state == WorkflowState.WAITING_FOR_INPUT.value:
            if intent == "input_received":
                return WorkflowState.PROCESSING.value
            else:
                return WorkflowState.WAITING_FOR_INPUT.value
        
        elif current_state == WorkflowState.COMPLETED.value:
            return WorkflowState.COMPLETED.value
        
        # Default fallback
        return current_state
    
    async def _analyze_message_intent(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> str:
        """Analyze message intent using LLM"""
        
        # Simple intent analysis based on keywords
        message_lower = message.lower().strip()
        
        # Completion indicators
        if any(word in message_lower for word in [
            "done", "completed", "finished", "that's all", "submit", "send"
        ]):
            return "info_complete"
        
        # Help indicators
        if any(word in message_lower for word in [
            "help", "how", "what", "why", "don't understand"
        ]):
            return "help"
        
        # Information provision indicators
        if any(word in message_lower for word in [
            "my name is", "i am", "email", "phone", "ctc", "experience"
        ]):
            return "info_provided"
        
        # Ready indicators
        if any(word in message_lower for word in [
            "ready", "proceed", "continue", "next"
        ]):
            return "ready_to_proceed"
        
        # More info needed
        if any(word in message_lower for word in [
            "what else", "anything else", "more information"
        ]):
            return "more_info_needed"
        
        # Input received
        if message and len(message) > 0:
            return "input_received"
        
        return "unknown"
    
    async def _process_state_step(
        self,
        session_id: str,
        state: str,
        message: str,
        context: Dict[str, Any]
    ) -> str:
        """Process a specific state step"""
        
        if state == WorkflowState.ONBOARDING.value:
            return await self._process_onboarding(session_id, context)
        
        elif state == WorkflowState.COLLECTING_INFO.value:
            return await self._process_info_collection(session_id, message, context)
        
        elif state == WorkflowState.PROCESSING.value:
            return await self._process_information(session_id, context)
        
        elif state == WorkflowState.WAITING_FOR_INPUT.value:
            return await self._process_waiting_for_input(session_id, context)
        
        elif state == WorkflowState.COMPLETED.value:
            return await self._process_completion(session_id, context)
        
        elif state == WorkflowState.ERROR.value:
            return "I apologize, but I encountered an error. Let's start over. How can I help you today?"
        
        return "I'm not sure how to proceed. Can you please provide more information?"
    
    async def _process_onboarding(
        self,
        session_id: str,
        context: Dict[str, Any]
    ) -> str:
        """Process onboarding state"""
        
        user_role = context.get("user_role", "candidate")
        
        if user_role == "candidate":
            return (
                "Welcome to the AI Recruitment Assistant! 🎯\n\n"
                "I'll help you find the perfect job opportunities. "
                "Let's start by collecting some basic information about you.\n\n"
                "Please provide the following:\n"
                "1. Your full name\n"
                "2. Email address\n"
                "3. Phone number\n"
                "4. Current role/position\n"
                "5. Years of experience\n\n"
                "You can provide this information one at a time or all together. "
                "How would you like to proceed?"
            )
        else:
            return (
                "Welcome Recruiter! 👋\n\n"
                "I'll help you manage candidates and job postings. "
                "What would you like to do today?\n\n"
                "Available options:\n"
                "- Create a new job posting\n"
                "- View candidates for a job\n"
                "- Send outreach to candidates\n"
                "- Export candidate data"
            )
    
    async def _process_info_collection(
        self,
        session_id: str,
        message: str,
        context: Dict[str, Any]
    ) -> str:
        """Process information collection state"""
        
        # Extract information from message
        extracted_info = await self._extract_information(message, context)
        
        # Update context with extracted info
        context.update(extracted_info)
        
        # Check if we have all required information
        required_fields = ["name", "email", "phone", "current_role", "experience"]
        collected_fields = [field for field in required_fields if field in context]
        
        if len(collected_fields) >= 3:
            return (
                f"Great! I've collected some information about you:\n"
                f"- Name: {context.get('name', 'Not provided')}\n"
                f"- Email: {context.get('email', 'Not provided')}\n"
                f"- Phone: {context.get('phone', 'Not provided')}\n\n"
                f"Would you like to provide more details or shall I proceed "
                f"with finding suitable job opportunities?"
            )
        else:
            missing_fields = [field for field in required_fields if field not in context]
            return (
                f"I've collected some information. Please provide:\n"
                f"- {', '.join(missing_fields[:2])}\n\n"
                f"What would you like to share next?"
            )
    
    async def _process_information(
        self,
        session_id: str,
        context: Dict[str, Any]
    ) -> str:
        """Process collected information"""
        
        # This is where you would integrate with matching algorithms
        # For now, return a placeholder response
        
        return (
            "Perfect! I'm now analyzing your profile and matching you with "
            "suitable job opportunities based on your skills and experience.\n\n"
            "This may take a moment while I search through our database...\n\n"
            "In the meantime, would you like to:\n"
            "1. Upload your resume\n"
            "2. Answer some prescreening questions\n"
            "3. Browse available jobs"
        )
    
    async def _process_waiting_for_input(
        self,
        session_id: str,
        context: Dict[str, Any]
    ) -> str:
        """Process waiting for user input"""
        
        return (
            "I'm ready when you are! Please provide the information or let me know "
            "what you'd like to do next.\n\n"
            "You can:\n"
            "- Answer the questions I asked\n"
            "- Ask me a question\n"
            "- Request help with something specific"
        )
    
    async def _process_completion(
        self,
        session_id: str,
        context: Dict[str, Any]
    ) -> str:
        """Process workflow completion"""
        
        return (
            "Excellent! 🎉\n\n"
            "I've successfully processed your information. Here's what happens next:\n\n"
            "1. Your profile has been updated in our system\n"
            "2. You've been matched with suitable job opportunities\n"
            "3. Our recruiters will review your profile\n"
            "4. You'll be contacted for suitable matches\n\n"
            "Is there anything else I can help you with today?"
        )
    
    async def _extract_information(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract structured information from user message"""
        
        extracted = {}
        
        # Simple regex-based extraction (in production, use NLP)
        import re
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message)
        if email_match:
            extracted['email'] = email_match.group()
        
        # Extract phone (simple pattern)
        phone_match = re.search(r'(\+\d{1,3}[- ]?)?\d{10}', message)
        if phone_match:
            extracted['phone'] = phone_match.group()
        
        # Extract name (simple heuristic)
        if 'name is' in message.lower():
            name_match = re.search(r'name is ([A-Za-z\s]+)', message, re.IGNORECASE)
            if name_match:
                extracted['name'] = name_match.group(1).strip()
        
        # Extract experience
        exp_match = re.search(r'(\d+)\s*years?\s*experience', message, re.IGNORECASE)
        if exp_match:
            extracted['experience'] = int(exp_match.group(1))
        
        return extracted
    
    async def _update_context(
        self,
        context: Dict[str, Any],
        state: str,
        response: str
    ) -> Dict[str, Any]:
        """Update workflow context"""
        
        updated_context = context.copy()
        updated_context['last_state'] = state
        updated_context['last_response'] = response
        updated_context['updated_at'] = datetime.utcnow().isoformat()
        
        return updated_context
    
    def get_valid_transitions(self, state: str) -> List[str]:
        """Get valid transitions from a given state"""
        return self.state_transitions.get(state, [])
    
    def is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a state transition is valid"""
        valid_transitions = self.get_valid_transitions(from_state)
        return to_state in valid_transitions