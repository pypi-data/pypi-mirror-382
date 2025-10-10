"""
Unified Lexia Handler
=====================

Single, clean interface for all Lexia platform communication.
"""

import logging
from .centrifugo_client import CentrifugoClient
from .api_client import APIClient
from .response_handler import create_complete_response

logger = logging.getLogger(__name__)


class LexiaHandler:
    """Clean, unified interface for all Lexia communication."""
    
    def __init__(self):
        self.centrifugo = CentrifugoClient()
        self.api = APIClient()
    
    def update_centrifugo_config(self, stream_url: str, stream_token: str):
        """
        Update Centrifugo configuration with dynamic values from request.
        
        Args:
            stream_url: Centrifugo server URL from request
            stream_token: Centrifugo API key from request
        """
        if stream_url and stream_token:
            self.centrifugo.update_config(stream_url, stream_token)
            logger.info(f"Updated Centrifugo config - URL: {stream_url}")
        else:
            logger.warning("Stream URL or token not provided, using default configuration")
    
    def stream_chunk(self, data, content: str):
        """Stream a chunk of AI response via Centrifugo."""
        # Update config if dynamic values are provided
        if hasattr(data, 'stream_url') and hasattr(data, 'stream_token'):
            self.update_centrifugo_config(data.stream_url, data.stream_token)
        
        self.centrifugo.send_delta(data.channel, data.response_uuid, data.thread_id, content)
    
    def complete_response(self, data, full_response: str, usage_info=None, file_url=None):
        """Complete AI response and send to Lexia (all in one call)."""
        # Update config if dynamic values are provided
        if hasattr(data, 'stream_url') and hasattr(data, 'stream_token'):
            self.update_centrifugo_config(data.stream_url, data.stream_token)
        
        # Send completion via Centrifugo
        self.centrifugo.send_completion(data.channel, data.response_uuid, data.thread_id, full_response)
        
        # Create complete response with all required fields
        backend_data = create_complete_response(data.response_uuid, data.thread_id, full_response, usage_info, file_url)
        backend_data['conversation_id'] = data.conversation_id
        
        # Ensure required fields have proper values even if usage_info is missing
        if not usage_info or usage_info.get('prompt_tokens', 0) == 0:
            # Provide default values when usage info is missing
            backend_data['usage'] = {
                'input_tokens': 1,  # Minimum token count
                'output_tokens': len(full_response.split()) if full_response else 1,  # Estimate from response length
                'total_tokens': 1 + (len(full_response.split()) if full_response else 1),
                'input_token_details': {
                    'tokens': [{"token": "default", "logprob": 0.0}]
                },
                'output_token_details': {
                    'tokens': [{"token": "default", "logprob": 0.0}]
                }
            }
        
        # Extract headers from request data
        request_headers = {}
        if hasattr(data, 'headers') and data.headers:
            request_headers.update(data.headers)
            logger.info(f"Extracted headers from request: {request_headers}")
        
        logger.info(f"=== SENDING TO LEXIA API ===")
        logger.info(f"URL: {data.url}")
        logger.info(f"Headers: {request_headers}")
        logger.info(f"Data: {backend_data}")
        
        # Send to Lexia backend with headers
        response = self.api.post(data.url, backend_data, headers=request_headers)
        
        logger.info(f"=== LEXIA API RESPONSE ===")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.headers)}")
        logger.info(f"Response Content: {response.text}")
        
        if response.status_code != 200:
            logger.error(f"LEXIA API ERROR: {response.status_code} - {response.text}")
        else:
            logger.info("✅ LEXIA API SUCCESS: Response accepted")
        
        # Update if different URL
        # if data.url_update and data.url_update != data.url:
        #     update_data = create_complete_response(data.response_uuid, data.thread_id, full_response, usage_info)
        #     update_data['conversation_id'] = data.conversation_id
            
        #     # Ensure update data also has proper usage values
        #     if not usage_info or usage_info.get('prompt_tokens', 0) == 0:
        #         update_data['usage'] = {
        #             'input_tokens': 1,
        #             'output_tokens': len(full_response.split()) if full_response else 1,
        #             'total_tokens': 1 + (len(full_response.split()) if full_response else 1),
        #             'input_token_details': {
        #                 'tokens': [{"token": "default", "logprob": 0.0}]
        #             },
        #             'output_token_details': {
        #                 'tokens': [{"token": "default", "logprob": 0.0}]
        #             }
        #         }
            
        #     logger.info(f"=== SENDING UPDATE TO LEXIA API ===")
        #     logger.info(f"Update URL: {data.url_update}")
        #     logger.info(f"Update Headers: {request_headers}")
        #     logger.info(f"Update Data: {update_data}")
            
        #     update_response = self.api.put(data.url_update, update_data, headers=request_headers)
            
        #     logger.info(f"=== LEXIA UPDATE API RESPONSE ===")
        #     logger.info(f"Update Status Code: {update_response.status_code}")
        #     logger.info(f"Update Response Content: {update_response.text}")
            
        #     if update_response.status_code != 200:
        #         logger.error(f"LEXIA UPDATE API ERROR: {update_response.status_code} - {update_response.text}")
        #     else:
        #         logger.info("✅ LEXIA UPDATE API SUCCESS: Update accepted")
    
    def send_error(self, data, error_message: str):
        """
        Send error message via Centrifugo and persist to backend API.
        
        Args:
            data: Request data containing channel, UUID, thread_id, etc.
            error_message: Error message to send
        """
        # Update config if dynamic values are provided
        if hasattr(data, 'stream_url') and hasattr(data, 'stream_token'):
            self.update_centrifugo_config(data.stream_url, data.stream_token)
        
        # Send error notification via Centrifugo (real-time websocket)
        self.centrifugo.send_error(data.channel, data.response_uuid, data.thread_id, error_message)
        
        # Also persist error to backend API (like previous implementation)
        error_response = {
            'uuid': data.response_uuid,
            'conversation_id': data.conversation_id,
            'content': error_message,
            'role': 'developer',
            'status': 'FAILED',
            'usage': {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'input_token_details': {
                    'tokens': []
                },
                'output_token_details': {
                    'tokens': []
                }
            }
        }
        
        # Extract headers from request data
        request_headers = {}
        if hasattr(data, 'headers') and data.headers:
            request_headers.update(data.headers)
            logger.info(f"Extracted headers from request for error: {request_headers}")
        
        logger.info(f"=== SENDING ERROR TO LEXIA API ===")
        logger.info(f"URL: {data.url}")
        logger.info(f"Headers: {request_headers}")
        logger.info(f"Error Data: {error_response}")
        
        # Send error to Lexia backend with headers
        try:
            response = self.api.post(data.url, error_response, headers=request_headers)
            
            logger.info(f"=== LEXIA ERROR API RESPONSE ===")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            logger.info(f"Response Content: {response.text}")
            
            if response.status_code != 200:
                logger.error(f"LEXIA ERROR API FAILED: {response.status_code} - {response.text}")
            else:
                logger.info("✅ LEXIA ERROR API SUCCESS: Error persisted to backend")
        except Exception as e:
            logger.error(f"Failed to persist error to backend API: {e}")
