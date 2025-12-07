"""
Chatbot LLM Adapter Stub
Placeholder for LLM integration - returns disabled
"""

from typing import Dict, Any, List, Optional
import logging


class LLMAdapterStub:
    """Stub adapter for LLM integration - returns disabled"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.enabled = False
    
    async def is_enabled(self) -> bool:
        """Check if LLM adapter is enabled"""
        return self.enabled
    
    async def set_enabled(self, enabled: bool) -> None:
        """Set enabled state"""
        self.enabled = enabled
        self.logger.info(f"LLM Adapter enabled: {enabled}")
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response from LLM
        
        Args:
            prompt: Input prompt
            context: Additional context
            model: Model to use (optional)
            
        Returns:
            Response dictionary
        """
        if not self.enabled:
            return {
                "enabled": False,
                "response": None,
                "error": "LLM adapter is disabled",
                "model": model,
                "timestamp": None
            }
        
        # This would integrate with actual LLM providers
        # For now, return placeholder response
        return {
            "enabled": True,
            "response": "This is a placeholder response from the LLM adapter.",
            "error": None,
            "model": model,
            "timestamp": None
        }
    
    async def analyze_text(
        self,
        text: str,
        analysis_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze text using LLM
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis (intent, sentiment, etc.)
            context: Additional context
            
        Returns:
            Analysis result
        """
        if not self.enabled:
            return {
                "enabled": False,
                "analysis": None,
                "error": "LLM adapter is disabled",
                "analysis_type": analysis_type,
                "timestamp": None
            }
        
        # Placeholder analysis
        return {
            "enabled": True,
            "analysis": {
                "type": analysis_type,
                "result": "Placeholder analysis result"
            },
            "error": None,
            "analysis_type": analysis_type,
            "timestamp": None
        }
    
    async def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract entities from text
        
        Args:
            text: Text to extract entities from
            entity_types: List of entity types to extract
            
        Returns:
            Extracted entities
        """
        if not self.enabled:
            return {
                "enabled": False,
                "entities": None,
                "error": "LLM adapter is disabled",
                "entity_types": entity_types,
                "timestamp": None
            }
        
        # Placeholder entity extraction
        return {
            "enabled": True,
            "entities": {
                "names": [],
                "locations": [],
                "organizations": [],
                "skills": []
            },
            "error": None,
            "entity_types": entity_types,
            "timestamp": None
        }
    
    async def get_supported_models(self) -> List[str]:
        """Get list of supported models"""
        return ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"]
    
    async def get_current_model(self) -> Optional[str]:
        """Get current model"""
        return "gpt-4o-mini" if self.enabled else None


# Global LLM adapter stub instance
llm_adapter_stub = LLMAdapterStub()