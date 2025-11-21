"""Utility functions for A2A agent communication and tag parsing."""

import re
import httpx
import asyncio
from typing import Dict, Optional
from a2a.types import SendMessageSuccessResponse, Message
from a2a.utils import get_text_parts


def parse_tags(text: str) -> Dict[str, str]:
    """
    Parse tags from text (e.g., <json>...</json>, <code>...</code>, etc.)
    
    Args:
        text: Text containing tagged content
        
    Returns:
        Dictionary mapping tag names to their content
    """
    tags = {}
    # Pattern to match <tag_name>content</tag_name>
    pattern = r'<(\w+)>(.*?)</\1>'
    
    for match in re.finditer(pattern, text, re.DOTALL):
        tag_name = match.group(1)
        tag_content = match.group(2).strip()
        tags[tag_name] = tag_content
    
    return tags


class A2AClient:
    """Client for sending messages via A2A protocol using the official A2A SDK."""
    
    def __init__(self):
        try:
            from a2a.client import A2AClient as OfficialA2AClient
            from a2a.utils import new_agent_text_message
            from a2a.types import Message, TextPart, Role
            self._use_official = True
            self._OfficialA2AClient = OfficialA2AClient
            self._new_agent_text_message = new_agent_text_message
            self._Message = Message
            self._TextPart = TextPart
            self._Role = Role
            # Create httpx client for A2A client
            self._httpx_client = httpx.AsyncClient(timeout=300.0)
        except ImportError as e:
            # Fallback to HTTP client if A2A SDK not available
            self._use_official = False
            self._import_error = e
            self.client = httpx.AsyncClient(timeout=300.0)
    
    async def send_message(
        self, 
        agent_url: str, 
        message: str, 
        context_id: Optional[str] = None
    ):
        """
        Send a message to another agent via A2A protocol.
        
        Args:
            agent_url: URL of the target agent
            message: Text message to send
            context_id: Optional context ID for the conversation
            
        Returns:
            Object with .root attribute containing SendMessageSuccessResponse
        """
        if self._use_official:
            # Use official A2A SDK client
            from a2a.types import SendMessageRequest, MessageSendParams
            
            # Create client for this agent URL
            client = self._OfficialA2AClient(httpx_client=self._httpx_client, url=agent_url)
            
            # Create message object using A2A utils
            msg = self._new_agent_text_message(message, context_id=context_id)
            
            # Send message - client.send_message expects SendMessageRequest
            import uuid
            params = MessageSendParams(message=msg)
            request = SendMessageRequest(id=str(uuid.uuid4()), params=params)
            response = await client.send_message(request)
            
            # Wrap response to match expected interface
            # The response is SendMessageResponse which has a result field
            # We need to convert it to match SendMessageSuccessResponse format
            from a2a.types import SendMessageSuccessResponse
            
            class ResponseWrapper:
                def __init__(self, resp):
                    # resp is SendMessageResponse with result field containing the Message
                    # Convert to SendMessageSuccessResponse format
                    resp_dict = resp.model_dump()
                    if 'result' in resp_dict and resp_dict['result'] is not None:
                        # resp.result is the Message, wrap it in SendMessageSuccessResponse
                        from a2a.types import Message
                        message = Message(**resp_dict['result'])
                        self.root = SendMessageSuccessResponse(result=message)
                    else:
                        # Fallback: try to use response as-is
                        self.root = resp
            
            return ResponseWrapper(response)
        else:
            # Fallback HTTP implementation (should not be used if A2A SDK available)
            raise ImportError(f"A2A SDK client not available: {self._import_error}. Please install a2a-sdk.")
    
    async def close(self):
        """Close the HTTP client."""
        if self._use_official and hasattr(self, '_httpx_client'):
            await self._httpx_client.aclose()
        elif not self._use_official and hasattr(self, 'client'):
            await self.client.aclose()


async def wait_agent_ready(agent_url: str, timeout: int = 30, check_interval: float = 0.5) -> bool:
    """
    Wait for an agent to become ready by checking its status endpoint.
    
    Args:
        agent_url: URL of the agent to check
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        
    Returns:
        True if agent is ready, False if timeout
    """
    import time
    import httpx
    
    start_time = time.time()
    check_url = agent_url.rstrip("/") + "/status"
    
    while time.time() - start_time < timeout:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(check_url)
                if response.status_code == 200:
                    return True
        except Exception:
            pass
        
        await asyncio.sleep(check_interval)
    
    return False


# Global instance
my_a2a = A2AClient()
