import requests
from typing import Optional
import os
import uuid
from typing import Optional, Callable, Any
from functools import wraps
from dotenv import load_dotenv
load_dotenv()


class ApgardClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        """
        Initialize the AI SDK client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for your API
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })
        
        # Verify API key on initialization
        self._verify_api_key()
    
    def _verify_api_key(self) -> None:
        """
        Verify that the API key is valid by making a request to the auth endpoint.
        
        Raises:
            ValueError: If API key is invalid
            Exception: If verification request fails
        """
        try:
            response = self.session.get(f"{self.base_url}/auth/verify")
            
            if response.status_code == 401:
                raise ValueError("Invalid API key")
            
            response.raise_for_status()
            
            # Optionally store user info from verification response
            data = response.json()
            self.user_id = data.get('user_id')
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid API key") from e
            raise Exception(f"API key verification failed: {str(e)}") from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"Could not connect to API: {str(e)}") from e
    
    def track_input(self, content: str, thread_id: str, user_id: Optional[str] = None, metadata: Optional[dict] = None, interaction_id: Optional[str] = None):
        """
        Manually track an input message.
        
        Usage:
            interaction_id = apgard_client.track_input(
                content=user_message,
                user_id="user123"
            )
        
        Args:
            content: The user input/prompt
            user_id: Optional user identifier
            metadata: Optional metadata dict
            interaction_id: Optional custom interaction ID (SDK generates if not provided)
        
        Returns:
            interaction_id: UUID to link input with output
        """
        # Generate interaction_id if not provided
        if not interaction_id:
            interaction_id = str(uuid.uuid4())
        
        log_data = {
            'content': content,
            'interaction_id': interaction_id,
            'user_id': user_id,
            'metadata': metadata or {},
            'message_type': 'input',
            'thread_id': thread_id
        }

        try:
            self.session.post(
                f"{self.base_url}/models/messages",
                headers={"X-API-Key": self.api_key},
                json=log_data
            )
        except Exception as e:
            print(f"Warning: Failed to log input: {e}")
        
        return interaction_id


    def track_output(self, interaction_id: str, thread_id: str, func: Optional[Callable] = None, *, metadata: Optional[dict] = None):
        """
        Decorator to automatically log the output of a function.
        
        Can be used as:
            @client.log_output
            def my_function():
                return "result"
        
        Or with metadata:
            @client.log_output(metadata={"source": "data_pipeline"})
            def my_function():
                return "result"
        
        Args:
            func: Function to wrap (when used without parentheses)
            metadata: Additional metadata to include with the log
        
        Returns:
            Decorated function
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Execute the function
                result = f(*args, **kwargs)
                
                # Prepare log data
                log_data = {
                    'function_name': f.__name__,
                    'content': result,
                    'metadata': metadata or {},
                    'message_type': 'output',
                    'interaction_id': interaction_id,
                    'thread_id': thread_id
                }
                
                # Send to API
                try:
                    # self._send_log(log_data)
                    self.session.post(
                        f"{self.base_url}/models/messages", 
                        headers={"X-API-Key": self.api_key},
                        json=log_data)
                except Exception as e:
                    # Don't fail the original function if logging fails
                    print(f"Warning: Failed to log output: {e}")
                
                return result
            return wrapper
        
        if func is None:
            return decorator
        else:
            return decorator(func)


# Usage Example:
# if __name__ == "__main__":
#     try:
#         # Valid API key
#         client = ApgardClient(api_key="sk_live_abc123...")
#         print(f"✓ Connected as: {client.email}")
        
#     except ValueError as e:
#         print(f"✗ Authentication failed: {e}")
        
#     except Exception as e:
#         print(f"✗ Error: {e}")
    
#     @client.track_model_output(metadata={ "model": "gpt-5" })
#     def mock_model_response():
#         return "Hello, how can I help you?"
    
#     mock_model_response()