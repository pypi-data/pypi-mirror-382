"""
Xiangxin AI guardrails client
"""
import requests
import time
import asyncio
import aiohttp
import base64
from typing import Optional, Dict, Any, List, Union
from .models import GuardrailRequest, GuardrailResponse, Message, GuardrailResult, ComplianceResult, SecurityResult
from .exceptions import (
    XiangxinAIError,
    AuthenticationError,
    RateLimitError,
    ValidationError
)


class XiangxinAI:
    """Xiangxin AI guardrails client - An LLM-based context-aware AI guardrail that understands conversation context for security, safety and data leakage detection.
    
    This client provides a simple interface for interacting with the Xiangxin AI guardrails API.
    The guardrail uses context-aware technology to understand the conversation context for security, safety and data leakage detection.
    
    Args:
        api_key: API key
        base_url: API base URL, default to cloud service
        timeout: Request timeout (seconds)
        max_retries: Maximum number of retries
        
    Example:
        >>> client = XiangxinAI(api_key="your-api-key")
        >>> # Check prompt
        >>> result = client.check_prompt("The user's question")
        >>> # Check conversation context
        >>> messages = [{"role": "user", "content": "The user's question"}, {"role": "assistant", "content": "The assistant's answer"}]
        >>> result = client.check_conversation(messages)
        >>> print(result.overall_risk_level)  # "high_risk/medium_risk/low_risk/no_risk"
        >>> print(result.suggest_action)  # "pass/reject/replace"
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.xiangxinai.cn/v1",
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"xiangxinai-python/2.6.2"
        })
    
    def _create_safe_response(self) -> GuardrailResponse:
        """创建无风险的默认响应"""
        return GuardrailResponse(
            id="guardrails-safe-default",
            result=GuardrailResult(
                compliance=ComplianceResult(
                    risk_level="no_risk",
                    categories=[]
                ),
                security=SecurityResult(
                    risk_level="no_risk", 
                    categories=[]
                )
                data=DataSecurityResult(
                    risk_level="no_risk",
                    categories=[]
                )
            ),
            overall_risk_level="no_risk",
            suggest_action="pass",
            suggest_answer=None,
            score=1.0
        )
    
    def check_prompt(
        self,
        content: str,
        user_id: Optional[str] = None
    ) -> GuardrailResponse:
        """Check the security of user input

        Args:
            content: The user input content to be checked
            user_id: Optional, tenant AI application user ID, for user-level risk control and audit tracking

        Returns:
            GuardrailResponse: The detection result, format as:
            {
                "id": "guardrails-xxx",
                "result": {
                    "compliance": {
                        "risk_level": "high_risk/medium_risk/low_risk/no_risk",
                        "categories": ["violent crime", "sensitive political topics"]
                    },
                    "security": {
                        "risk_level": "high_risk/medium_risk/low_risk/no_risk",
                        "categories": ["prompt attack"]
                    }
                },
                "overall_risk_level": "high_risk/medium_risk/low_risk/no_risk",
                "suggest_action": "pass/reject/replace",
                "suggest_answer": "Suggested response content"
            }

        Raises:
            ValidationError: Invalid input parameters
            AuthenticationError: Authentication failed
            RateLimitError: Exceeds rate limit
            XiangxinAIError: Other API errors

        Example:
            >>> result = client.check_prompt("I want to learn programming")
            >>> print(result.overall_risk_level)  # "no_risk"
            >>> print(result.suggest_action)  # "pass"
            >>> print(result.result.compliance.risk_level)  # "no_risk"
        """
        # If content is an empty string, return no risk
        if not content or not content.strip():
            return self._create_safe_response()

        request_data = {
            "input": content.strip()
        }

        if user_id:
            request_data["xxai_app_user_id"] = user_id

        return self._make_request("POST", "/guardrails/input", request_data)
    
    def check_conversation(
        self,
        messages: List[Dict[str, str]],
        model: str = "Xiangxin-Guardrails-Text",
        user_id: Optional[str] = None
    ) -> GuardrailResponse:
        """Check the security of conversation context - context-aware detection

        This is the core functionality of the guardrail, which can understand the complete conversation context for security detection.
        It is not to detect each message separately, but to analyze the security of the entire conversation.
        It is not to detect each message separately, but to analyze the security of the entire conversation.

        Args:
            messages: Conversation message list, containing the complete conversation between user and assistant
                      Each message contains role('user' or 'assistant') and content
            model: The name of the model used
            user_id: Optional, tenant AI application user ID, for user-level risk control and audit tracking
            
        Returns:
            GuardrailResponse: The detection result based on conversation context, format as:
            {
                "id": "guardrails-xxx",
                "result": {
                    "compliance": {
                        "risk_level": "high_risk/medium_risk/low_risk/no_risk",
                        "categories": ["violent crime", "sensitive political topics"]
                    },
                    "security": {
                        "risk_level": "high_risk/medium_risk/low_risk/no_risk",
                        "categories": ["prompt attack"]
                    }
                },
                "overall_risk_level": "high_risk/medium_risk/low_risk/no_risk",
                "suggest_action": "pass/reject/replace",
                "suggest_answer": "Suggested response content"
            }
            
        Example:
            >>> # Check the security of conversation context between user and assistant
            >>> messages = [
            ...     {"role": "user", "content": "The user's question"},
            ...     {"role": "assistant", "content": "The assistant's answer"}
            ... ]
            >>> print(result.overall_risk_level)  # "no_risk"
            >>> result = client.check_conversation(messages)
            >>> print(result.suggest_action)  # Suggested action based on conversation context
        """
        if not messages:
            raise ValidationError("Messages cannot be empty")
        
        # Validate message format
        validated_messages = []
        all_empty = True  # Mark whether all content are empty
        
        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                raise ValidationError("Each message must have 'role' and 'content' fields")
            
            content = msg["content"]
            # Check if there is non-empty content
            if content and content.strip():
                all_empty = False
                # Only add non-empty messages to validated_messages
                validated_messages.append(Message(role=msg["role"], content=content))
        
        # If all messages' content are empty, return no risk
        if all_empty:
            return self._create_safe_response()
        
        # Ensure at least one message
        if not validated_messages:
            return self._create_safe_response()
        
        request_data = GuardrailRequest(
            model=model,
            messages=validated_messages
        )

        request_dict = request_data.dict()
        if user_id:
            if "extra_body" not in request_dict:
                request_dict["extra_body"] = {}
            request_dict["extra_body"]["xxai_app_user_id"] = user_id

        return self._make_request("POST", "/guardrails", request_dict)

    def check_response_ctx(
        self,
        prompt: str,
        response: str,
        user_id: Optional[str] = None
    ) -> GuardrailResponse:
        """Check the security of user input and model output - context-aware detection

        This is the core functionality of the guardrail, which can understand the context of user input and model output for security detection.
        The guardrail will detect whether the model output is safe and compliant based on the context of the user's question.

        Args:
            prompt: The user input text content, used to help the guardrail understand the context semantics
            response: The model output text content, actual detection object
            user_id: Optional, tenant AI application user ID, for user-level risk control and audit tracking

        Returns:
            GuardrailResponse: The detection result based on context, format as:
            {
                "id": "guardrails-xxx",
                "result": {
                    "compliance": {
                        "risk_level": "high_risk/medium_risk/low_risk/no_risk",
                        "categories": ["violent crime", "sensitive political topics"]
                    },
                    "security": {
                        "risk_level": "high_risk/medium_risk/low_risk/no_risk",
                        "categories": ["prompt attack"]
                    }
                },
                "overall_risk_level": "high_risk/medium_risk/low_risk/no_risk",
                "suggest_action": "pass/reject/replace",
                "suggest_answer": "Suggested response content"
            }

        Raises:
            ValidationError: Invalid input parameters
            AuthenticationError: Authentication failed
            RateLimitError: Exceeds rate limit
            XiangxinAIError: Other API errors

        Example:
            >>> result = client.check_response_ctx(
            ...     "I want to learn programming",
            ...     "I can teach you how to make simple home cooking"
            ... )
            >>> print(result.overall_risk_level)  # "no_risk"
            >>> print(result.suggest_action)  # "pass"
        """
        # If prompt or response is an empty string, return no risk
        if (not prompt or not prompt.strip()) and (not response or not response.strip()):
            return self._create_safe_response()

        request_data = {
            "input": prompt.strip() if prompt else "",
            "output": response.strip() if response else ""
        }

        if user_id:
            request_data["xxai_app_user_id"] = user_id

        return self._make_request("POST", "/guardrails/output", request_data)

    def _encode_base64_from_path(self, image_path: str) -> str:
        """Encode image to base64 format

        Args:
            image_path: The local path or HTTP(S) link of the image

        Returns:
            str: The base64 encoded image content
        """
        if image_path.startswith(('http://', 'https://')):
            # Get image from URL
            response = self._session.get(image_path, timeout=self.timeout)
            response.raise_for_status()
            return base64.b64encode(response.content).decode('utf-8')
        else:
            # Read image from local file
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')

    def check_prompt_image(
        self,
        prompt: str,
        image: str,
        model: str = "Xiangxin-Guardrails-VL",
        user_id: Optional[str] = None
    ) -> GuardrailResponse:
        """Check the security of text prompt and image - multi-modal detection

        Combine text semantics and image content for security detection.

        Args:
            prompt: Text prompt (can be empty)
            image: The local path or HTTP(S) link of the image (cannot be empty)
            model: The name of the model used, default to multi-modal model
            user_id: Optional, tenant AI application user ID, for user-level risk control and audit tracking

        Returns:
            GuardrailResponse: The detection result

        Raises:
            ValidationError: Invalid input parameters
            AuthenticationError: Authentication failed
            RateLimitError: Exceeds rate limit
            XiangxinAIError: Other API errors

        Example:
            >>> # Check local image
            >>> result = client.check_prompt_image("Is this image safe?", "/path/to/image.jpg")
            >>> # Check network image
            >>> result = client.check_prompt_image("", "https://example.com/image.jpg")
            >>> print(result.overall_risk_level)
        """
        if not image:
            raise ValidationError("Image path cannot be empty")

        # 编码图片
        try:
            image_base64 = self._encode_base64_from_path(image)
        except FileNotFoundError:
            raise ValidationError(f"Image file not found: {image}")
        except Exception as e:
            raise XiangxinAIError(f"Failed to encode image: {str(e)}")

        # 构建消息
        content = []
        if prompt and prompt.strip():
            content.append({"type": "text", "text": prompt.strip()})
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
        })

        messages = [Message(role="user", content=content)]

        request_data = GuardrailRequest(
            model=model,
            messages=messages
        )

        request_dict = request_data.dict()
        if user_id:
            if "extra_body" not in request_dict:
                request_dict["extra_body"] = {}
            request_dict["extra_body"]["xxai_app_user_id"] = user_id

        return self._make_request("POST", "/guardrails", request_dict)

    def check_prompt_images(
        self,
        prompt: str,
        images: List[str],
        model: str = "Xiangxin-Guardrails-VL",
        user_id: Optional[str] = None
    ) -> GuardrailResponse:
        """Check the security of text prompt and multiple images - multi-modal detection

        Combine text semantics and multiple image content for security detection.

        Args:
            prompt: Text prompt (can be empty)
            images: The local path or HTTP(S) link list of the images (cannot be empty)
            model: The name of the model used, default to multi-modal model
            user_id: Optional, tenant AI application user ID, for user-level risk control and audit tracking

        Returns:
            GuardrailResponse: The detection result

        Raises:
            ValidationError: Invalid input parameters
            AuthenticationError: Authentication failed
            RateLimitError: Exceeds rate limit
            XiangxinAIError: Other API errors

        Example:
            >>> images = ["/path/to/image1.jpg", "https://example.com/image2.jpg"]
            >>> result = client.check_prompt_images("Are these images safe?", images)
            >>> print(result.overall_risk_level)
        """
        if not images or len(images) == 0:
            raise ValidationError("Images list cannot be empty")

        # Build message content
        content = []
        if prompt and prompt.strip():
            content.append({"type": "text", "text": prompt.strip()})

        # Encode all images
        for image_path in images:
            try:
                image_base64 = self._encode_base64_from_path(image_path)
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                })
            except FileNotFoundError:
                raise ValidationError(f"Image file not found: {image_path}")
            except Exception as e:
                raise XiangxinAIError(f"Failed to encode image {image_path}: {str(e)}")

        messages = [Message(role="user", content=content)]

        request_data = GuardrailRequest(
            model=model,
            messages=messages
        )

        request_dict = request_data.dict()
        if user_id:
            if "extra_body" not in request_dict:
                request_dict["extra_body"] = {}
            request_dict["extra_body"]["xxai_app_user_id"] = user_id

        return self._make_request("POST", "/guardrails", request_dict)

    def health_check(self) -> Dict[str, Any]:
        """Check API service health status
        
        Returns:
            Dict: Health status information
        """
        return self._make_request("GET", "/guardrails/health")
    
    def get_models(self) -> Dict[str, Any]:
        """Get available model list
        
        Returns:
            Dict: Model list information
        """
        return self._make_request("GET", "/guardrails/models")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Send HTTP request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
            
        Raises:
            XiangxinAIError: API request failed
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = self._session.get(url, timeout=self.timeout)
                elif method.upper() == "POST":
                    response = self._session.post(url, json=data, timeout=self.timeout)
                else:
                    raise XiangxinAIError(f"Unsupported HTTP method: {method}")
                
                # Handle HTTP status code
                if response.status_code == 200:
                    result_data = response.json()

                    # If it is a guardrail detection request, return structured response
                    if (endpoint in ["/guardrails", "/guardrails/input", "/guardrails/output"]) and isinstance(result_data, dict):
                        return GuardrailResponse(**result_data)

                    return result_data
                
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                
                elif response.status_code == 422:
                    error_detail = response.json().get("detail", "Validation error")
                    raise ValidationError(f"Validation error: {error_detail}")
                
                elif response.status_code == 429:
                    if attempt < self.max_retries:
                        # Exponential backoff retry
                        wait_time = (2 ** attempt) + 1
                        time.sleep(wait_time)
                        continue
                    raise RateLimitError("Rate limit exceeded")
                
                else:
                    error_msg = response.text
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", error_msg)
                    except:
                        pass
                    
                    raise XiangxinAIError(
                        f"API request failed with status {response.status_code}: {error_msg}"
                    )
            
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    time.sleep(1)
                    continue
                raise XiangxinAIError("Request timeout")
            
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries:
                    time.sleep(1)
                    continue
                raise XiangxinAIError("Connection error")
            
            except (AuthenticationError, ValidationError, RateLimitError):
                # These errors do not need to be retried
                raise
            
            except Exception as e:
                if attempt < self.max_retries:
                    time.sleep(1)
                    continue
                raise XiangxinAIError(f"Unexpected error: {str(e)}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if hasattr(self, '_session'):
            self._session.close()


class AsyncXiangxinAI:
    """Xiangxin AI guardrails asynchronous client - An LLM-based context-aware AI guardrail that understands conversation context for security, safety and data leakage detection.
    
    This asynchronous client provides an asynchronous interface for interacting with the Xiangxin AI guardrails API.
    The guardrail uses context-aware technology to understand the conversation context for security, safety and data leakage detection.
    
    Args:
        api_key: API key
        base_url: API base URL, default to cloud service
        timeout: Request timeout (seconds)
        max_retries: Maximum number of retries
        
    Example:
        >>> async with AsyncXiangxinAI(api_key="your-api-key") as client:
        ...     result = await client.check_prompt("The user's question")
        ...     print(result.overall_risk_level)
        >>> client = AsyncXiangxinAI(api_key="your-api-key")
        >>> result = await client.check_prompt("The user's question") 
        >>> await client.close()
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.xiangxinai.cn/v1",
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"xiangxinai-python/2.6.2"
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                headers=self._headers,
                timeout=timeout
            )
        return self._session
    
    def _create_safe_response(self) -> GuardrailResponse:
        """Create a safe default response"""
        return GuardrailResponse(
            id="guardrails-safe-default",
            result=GuardrailResult(
                compliance=ComplianceResult(
                    risk_level="no_risk",
                    categories=[]
                ),
                security=SecurityResult(
                    risk_level="no_risk", 
                    categories=[]
                )
            ),
            overall_risk_level="no_risk",
            suggest_action="pass",
            suggest_answer=None
        )
    
    async def check_prompt(
        self,
        content: str,
        user_id: Optional[str] = None
    ) -> GuardrailResponse:
        """Asynchronously check the security of user input

        Args:
            content: The user input content to be detected

        Returns:
            GuardrailResponse: The detection result, format as the same as the synchronous version

        Raises:
            ValidationError: Invalid input parameters
            AuthenticationError: Authentication failed
            RateLimitError: Exceeds rate limit
            XiangxinAIError: Other API errors

        Example:
            >>> async with AsyncXiangxinAI("your-api-key") as client:
            ...     result = await client.check_prompt("I want to learn programming")
            ...     print(result.overall_risk_level)  # "no_risk"
        """
        # If content is an empty string, return no risk
        if not content or not content.strip():
            return self._create_safe_response()

        request_data = {
            "input": content.strip()
        }

        if user_id:
            request_data["xxai_app_user_id"] = user_id

        return await self._make_request("POST", "/guardrails/input", request_data)
    
    async def check_conversation(
        self,
        messages: List[Dict[str, str]],
        model: str = "Xiangxin-Guardrails-Text",
        user_id: Optional[str] = None
    ) -> GuardrailResponse:
        """Asynchronously check the security of conversation context - context-aware detection
        
        This is the core functionality of the guardrail, which can understand the complete conversation context for security detection.
        It is not to detect each message separately, but to analyze the security of the entire conversation.
        
        Args:
            messages: Conversation message list, containing the complete conversation between user and assistant
                      Each message contains role('user' or 'assistant') and content
            model: The name of the model used
            
        Returns:
            GuardrailResponse: The detection result based on conversation context, format as the same as the synchronous version
            
        Example:
            >>> messages = [
            ...     {"role": "user", "content": "The user's question"},
            ...     {"role": "assistant", "content": "The assistant's answer"}
            ... ]
            >>> async with AsyncXiangxinAI("your-api-key") as client:
            ...     result = await client.check_conversation(messages)
            ...     print(result.overall_risk_level)
        """
        if not messages:
            raise ValidationError("Messages cannot be empty")
        
        # Validate message format
        validated_messages = []
        all_empty = True  # Mark whether all content are empty
        
        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                raise ValidationError("Each message must have 'role' and 'content' fields")
            
            content = msg["content"]
            # Check if there is non-empty content
            if content and content.strip():
                all_empty = False
                # Only add non-empty messages to validated_messages
                validated_messages.append(Message(role=msg["role"], content=content))
        
        # If all messages' content are empty, return no risk
        if all_empty:
            return self._create_safe_response()
        
        # Ensure at least one message
        if not validated_messages:
            return self._create_safe_response()
        
        request_data = GuardrailRequest(
            model=model,
            messages=validated_messages
        )

        request_dict = request_data.dict()
        if user_id:
            if "extra_body" not in request_dict:
                request_dict["extra_body"] = {}
            request_dict["extra_body"]["xxai_app_user_id"] = user_id

        return await self._make_request("POST", "/guardrails", request_dict)

    async def check_response_ctx(
        self,
        prompt: str,
        response: str,
        user_id: Optional[str] = None
    ) -> GuardrailResponse:
        """Asynchronously check the security of user input and model output - context-aware detection

        This is the core functionality of the guardrail, which can understand the context of user input and model output for security detection.
        The guardrail will detect whether the model output is safe and compliant based on the context of the user's question.

        Args:
            prompt: The user input text content, used to help the guardrail understand the context semantics
            response: The model output text content, actual detection object

        Returns:
            GuardrailResponse: The detection result based on context, format as the same as the synchronous version

        Example:
            >>> async with AsyncXiangxinAI("your-api-key") as client:
            ...     result = await client.check_response_ctx(
            ...         "I want to learn programming",
            ...         "I can teach you how to make simple home-cooked meals"
            ...     )
            ...     print(result.overall_risk_level)
        """
        # If prompt or response is an empty string, return no risk
        if (not prompt or not prompt.strip()) and (not response or not response.strip()):
            return self._create_safe_response()

        request_data = {
            "input": prompt.strip() if prompt else "",
            "output": response.strip() if response else ""
        }

        if user_id:
            request_data["xxai_app_user_id"] = user_id

        return await self._make_request("POST", "/guardrails/output", request_data)

    async def _encode_base64_from_path_async(self, image_path: str) -> str:
        """Asynchronously encode image to base64 format

        Args:
            image_path: The local path or HTTP(S) link of the image

        Returns:
            str: The base64 encoded image content
        """
        if image_path.startswith(('http://', 'https://')):
            # Get image from URL
            session = await self._get_session()
            async with session.get(image_path) as response:
                response.raise_for_status()
                content = await response.read()
                return base64.b64encode(content).decode('utf-8')
        else:
            # Read image from local file
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._encode_base64_from_file, image_path)

    def _encode_base64_from_file(self, file_path: str) -> str:
        """Encode base64 from local file (for asynchronous execution)"""
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    async def check_prompt_image(
        self,
        prompt: str,
        image: str,
        model: str = "Xiangxin-Guardrails-VL",
        user_id: Optional[str] = None
    ) -> GuardrailResponse:
        """Asynchronously check the security of text prompt and image - multi-modal detection

        Combine text semantics and image content for security detection.

        Args:
            prompt: Text prompt (can be empty)
            image: The local path or HTTP(S) link of the image (cannot be empty)
            model: The name of the model used, default to multi-modal model

        Returns:
            GuardrailResponse: The detection result

        Raises:
            ValidationError: Invalid input parameters
            AuthenticationError: Authentication failed
            RateLimitError: Exceeds rate limit
            XiangxinAIError: Other API errors

        Example:
            >>> async with AsyncXiangxinAI("your-api-key") as client:
            ...     result = await client.check_prompt_image("Is this image safe?", "/path/to/image.jpg")
            ...     print(result.overall_risk_level)
        """
        if not image:
            raise ValidationError("Image path cannot be empty")

        # Encode image
        try:
            image_base64 = await self._encode_base64_from_path_async(image)
        except FileNotFoundError:
            raise ValidationError(f"Image file not found: {image}")
        except Exception as e:
            raise XiangxinAIError(f"Failed to encode image: {str(e)}")

        # Build message
        content = []
        if prompt and prompt.strip():
            content.append({"type": "text", "text": prompt.strip()})
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
        })

        messages = [Message(role="user", content=content)]

        request_data = GuardrailRequest(
            model=model,
            messages=messages
        )

        return await self._make_request("POST", "/guardrails", request_data.dict())

    async def check_prompt_images(
        self,
        prompt: str,
        images: List[str],
        model: str = "Xiangxin-Guardrails-VL",
        user_id: Optional[str] = None
    ) -> GuardrailResponse:
        """Asynchronously check the security of text prompt and multiple images - multi-modal detection

        Combine text semantics and multiple image content for security detection.

        Args:
            prompt: Text prompt (can be empty)
            images: The local path or HTTP(S) link list of the images (cannot be empty)
            model: The name of the model used, default to multi-modal model

        Returns:
            GuardrailResponse: The detection result

        Raises:
            ValidationError: Invalid input parameters
            AuthenticationError: Authentication failed
            RateLimitError: Exceeds rate limit
            XiangxinAIError: Other API errors

        Example:
            >>> images = ["/path/to/image1.jpg", "https://example.com/image2.jpg"]
            >>> async with AsyncXiangxinAI("your-api-key") as client:
            ...     result = await client.check_prompt_images("Are these images safe?", images)
            ...     print(result.overall_risk_level)
        """
        if not images or len(images) == 0:
            raise ValidationError("Images list cannot be empty")

        # Build message content
        content = []
        if prompt and prompt.strip():
            content.append({"type": "text", "text": prompt.strip()})

        # Encode all images
        for image_path in images:
            try:
                image_base64 = await self._encode_base64_from_path_async(image_path)
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                })
            except FileNotFoundError:
                raise ValidationError(f"Image file not found: {image_path}")
            except Exception as e:
                raise XiangxinAIError(f"Failed to encode image {image_path}: {str(e)}")

        messages = [Message(role="user", content=content)]

        request_data = GuardrailRequest(
            model=model,
            messages=messages
        )

        request_dict = request_data.dict()
        if user_id:
            if "extra_body" not in request_dict:
                request_dict["extra_body"] = {}
            request_dict["extra_body"]["xxai_app_user_id"] = user_id

        return await self._make_request("POST", "/guardrails", request_dict)

    async def health_check(self) -> Dict[str, Any]:
        """Asynchronously check API service health status
        
        Returns:
            Dict: Health status information
        """
        return await self._make_request("GET", "/guardrails/health")
    
    async def get_models(self) -> Dict[str, Any]:
        """Asynchronously get available model list
        
        Returns:
            Dict: Model list information
        """
        return await self._make_request("GET", "/guardrails/models")
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Asynchronously send HTTP request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
            
        Raises:
            XiangxinAIError: API request failed
        """
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()
        
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == "GET":
                    async with session.get(url) as response:
                        return await self._handle_response(response, endpoint)
                elif method.upper() == "POST":
                    async with session.post(url, json=data) as response:
                        return await self._handle_response(response, endpoint)
                else:
                    raise XiangxinAIError(f"Unsupported HTTP method: {method}")
            
            except asyncio.TimeoutError:
                if attempt < self.max_retries:
                    await asyncio.sleep(1)
                    continue
                raise XiangxinAIError("Request timeout")
            
            except aiohttp.ClientError:
                if attempt < self.max_retries:
                    await asyncio.sleep(1)
                    continue
                raise XiangxinAIError("Connection error")
            
            except (AuthenticationError, ValidationError, RateLimitError):
                # These errors do not need to be retried
                raise
            
            except Exception as e:
                if attempt < self.max_retries:
                    await asyncio.sleep(1)
                    continue
                raise XiangxinAIError(f"Unexpected error: {str(e)}")
    
    async def _handle_response(
        self, 
        response: aiohttp.ClientResponse, 
        endpoint: str
    ) -> Any:
        """Handle HTTP response"""
        if response.status == 200:
            result_data = await response.json()
            
            # If it is a guardrail detection request, return structured response
            if (endpoint in ["/guardrails", "/guardrails/input", "/guardrails/output"]) and isinstance(result_data, dict):
                return GuardrailResponse(**result_data)
            
            return result_data
        
        elif response.status == 401:
            raise AuthenticationError("Invalid API key")
        
        elif response.status == 422:
            error_data = await response.json()
            error_detail = error_data.get("detail", "Validation error")
            raise ValidationError(f"Validation error: {error_detail}")
        
        elif response.status == 429:
            # Exponential backoff retry
            wait_time = (2 ** 0) + 1  # First retry wait 2 seconds
            await asyncio.sleep(wait_time)
            raise RateLimitError("Rate limit exceeded")
        
        else:
            error_msg = await response.text()
            try:
                error_data = await response.json()
                error_msg = error_data.get("detail", error_msg)
            except:
                pass
            
            raise XiangxinAIError(
                f"API request failed with status {response.status}: {error_msg}"
            )
    
    async def close(self):
        """Close asynchronous session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        """Asynchronous context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Asynchronous context manager exit"""
        await self.close()