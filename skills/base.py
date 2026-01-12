"""
Base Skill - Abstract interface for all skills
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.context import AssistantContext
import logging


class BaseSkill(ABC):
    """
    Abstract base class for all skills.
    
    Design Rules:
    1. Skills MUST NOT speak directly - return text only
    2. Skills MUST NOT touch GUI - return data only
    3. Skills MUST NOT access globals - use context parameter
    4. Skills MUST handle their own errors gracefully
    5. Skills SHOULD be stateless (state in context)
    """
    
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def execute(
        self, 
        context: AssistantContext, 
        query: str, 
        **params
    ) -> Dict[str, Any]:
        """
        Execute skill logic.
        
        Args:
            context: Assistant context with state
            query: Original user query
            **params: Additional parsed parameters
        
        Returns:
            Dict with:
                - response: Text to speak/display
                - data: Optional structured data
                - action: Optional special action
                - error: Optional error flag
        """
        pass
    
    def error_response(self, message: str) -> Dict[str, Any]:
        """Helper to create error response"""
        self._logger.error(message)
        return {
            "response": message,
            "error": True
        }
    
    def success_response(
        self, 
        message: str, 
        data: Optional[Dict] = None,
        action: Optional[str] = None
    ) -> Dict[str, Any]:
        """Helper to create success response"""
        result = {"response": message}
        if data:
            result["data"] = data
        if action:
            result["action"] = action
        return result
    
    def validate_param(
        self, 
        params: Dict, 
        key: str, 
        required: bool = True,
        param_type: type = str
    ) -> Optional[Any]:
        """
        Validate and extract parameter.
        
        Args:
            params: Parameters dictionary
            key: Parameter key
            required: If True, raises error if missing
            param_type: Expected type
        
        Returns:
            Parameter value or None
        
        Raises:
            ValueError: If required param missing or wrong type
        """
        value = params.get(key)
        
        if value is None and required:
            raise ValueError(f"Missing required parameter: {key}")
        
        if value is not None and not isinstance(value, param_type):
            raise ValueError(
                f"Parameter '{key}' must be {param_type.__name__}, "
                f"got {type(value).__name__}"
            )
        
        return value


class SkillResult:
    """
    Fluent builder for skill results.
    
    Usage:
        return SkillResult()
            .with_message("Task complete")
            .with_data({"count": 5})
            .build()
    """
    
    def __init__(self):
        self._result = {}
    
    def with_message(self, message: str):
        """Set response message"""
        self._result["response"] = message
        return self
    
    def with_data(self, data: Dict[str, Any]):
        """Set result data"""
        self._result["data"] = data
        return self
    
    def with_action(self, action: str):
        """Set special action"""
        self._result["action"] = action
        return self
    
    def as_error(self):
        """Mark as error"""
        self._result["error"] = True
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build final result dictionary"""
        return self._result