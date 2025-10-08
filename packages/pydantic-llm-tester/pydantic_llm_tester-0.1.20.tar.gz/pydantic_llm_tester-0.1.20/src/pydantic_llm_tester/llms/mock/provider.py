"""Mock provider implementation for testing purposes"""

import re
from typing import Dict, Any, Tuple, Union, Optional, List, Type # Added Type
import time
import random
import json # Added json for schema dump, though mock won't use it

from ..base import BaseLLM, ModelConfig, ProviderConfig, BaseModel # Added BaseModel
from pydantic_llm_tester.utils.cost_manager import UsageData

class MockProvider(BaseLLM):
    """Provider implementation for mocked responses"""
    
    def __init__(self, config=None, llm_models=None): # Added llm_models
        """Initialize the Mock provider"""
        super().__init__(config, llm_models=llm_models) # Pass llm_models to super
        self.logger.info("Mock provider initialized")
        self.last_received_files: Optional[List[str]] = None # For test inspection
        self.last_received_model_class: Optional[Type[BaseModel]] = None # For test inspection
        
        # Set up mock response registry
        self.response_registry = {}
        
    def register_mock_response(self, key: str, response: str) -> None:
        """
        Register a mock response for a specific key
        
        Args:
            key: The key to associate with this response
            response: The mock response text
        """
        self.response_registry[key] = response
        self.logger.debug(f"Registered mock response for key: {key}")
        
    def _call_llm_api(self, prompt: str, system_prompt: str, model_name: str, 
                     model_config: ModelConfig, model_class: Type[BaseModel], files: Optional[List[str]] = None) -> Tuple[str, Union[Dict[str, Any], UsageData]]:
        """Implementation-specific API call for mocked responses
        
        Args:
            prompt: The full prompt text to send
            system_prompt: System prompt from config
            model_name: Clean model name (without provider prefix)
            model_config: Model configuration
            model_class: The Pydantic model class for schema guidance.
            files: Optional list of file paths
            
        Returns:
            Tuple of (response_text, usage_data)
        """
        self.logger.info(f"Mock provider called with model {model_name}")
        self.last_received_files = files
        self.last_received_model_class = model_class # Store model_class
        if files:
            self.logger.info(f"Mock provider received files: {files}")
        if model_class:
            self.logger.info(f"Mock provider received model_class: {model_class.__name__}")
            # Optionally log the schema string if needed for debugging
            # try:
            #     schema_str = json.dumps(model_class.model_json_schema(), indent=2)
            # except AttributeError:
            #     schema_str = model_class.schema_json(indent=2)
            # self.logger.debug(f"Mock provider received model_class schema: {schema_str}")

        
        # Add simulated delay to mimic real API call
        delay = random.uniform(0.1, 0.5)
        time.sleep(delay)
        
        # Extract source text
        source_match = re.search(r'Source Text:\n(.*?)$', prompt, re.DOTALL)
        source_text = source_match.group(1).strip() if source_match else ""
        
        # Check for registered mock responses first
        for key, response in self.response_registry.items():
            if key in prompt or key in source_text:
                self.logger.info(f"Using registered mock response for key: {key}")
                mock_response = response
                break
        else:
            # If no registered response matches, generate a generic one
            self.logger.info("No registered mock response found, generating generic response")
            # Import here to avoid circular imports
            from ...utils.mock_responses import get_mock_response
            
            # Determine response type based on content
            if "Extract the animal" in prompt: # Check for the integration_tests/simple case
                mock_response = get_mock_response("integration_tests", source_text)
            elif "MACHINE LEARNING ENGINEER" in source_text or "job" in source_text.lower() or "software engineer" in source_text.lower() or "developer" in source_text.lower():
                mock_response = get_mock_response("job_ads", source_text)
            else:
                mock_response = get_mock_response("product_descriptions", source_text)
        
        # Calculate token counts for usage data
        prompt_tokens = len(prompt.split())
        completion_tokens = len(mock_response.split())
        total_tokens = prompt_tokens + completion_tokens
        
        # Create usage data
        usage_data = UsageData(
            provider="mock", # Or self.name, though "mock" is fine for mock provider
            model=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_input_rate=model_config.cost_input,
            cost_output_rate=model_config.cost_output
        )
        
        # Add elapsed time manually since it's not part of the standard UsageData fields
        usage_data.elapsed_time = delay
        
        return mock_response, usage_data
