"""
Xiangxin AI guardrails Python SDK - An LLM-based context-aware AI guardrail that understands conversation context for security, safety and data leakage detection.

An LLM-based context-aware AI guardrail that understands conversation context for security, safety and data leakage detection.

This package provides a Python client library for interacting with the Xiangxin AI guardrails API.

Example:
    Basic usage:
    
    from xiangxinai import XiangxinAI
    
    # Use the cloud API
    client = XiangxinAI("your-api-key")
    
    # Check user input
    result = client.check_prompt("The user's question")

    # Check output content (based on context)
    result = client.check_response_ctx("The user's question", "The assistant's answer")

    # Check conversation context (user + assistant answer)
    messages = [
        {"role": "user", "content": "The user's question"},
        {"role": "assistant", "content": "The assistant's answer"}
    ]
    result = client.check_conversation(messages)
    print(result.overall_risk_level)  # Output: no_risk/high_risk/medium_risk/low_risk
    print(result.suggest_action)  # Output: pass/replace/reject
"""

from .client import XiangxinAI, AsyncXiangxinAI
from .models import (
    GuardrailRequest,
    GuardrailResponse,
    GuardrailResult,
    ComplianceResult,
    SecurityResult,
    Message
)
from .exceptions import (
    XiangxinAIError,
    AuthenticationError,
    RateLimitError,
    ValidationError
)

__version__ = "2.6.2"
__author__ = "XiangxinAI"
__email__ = "wanglei@xiangxinai.cn"

__all__ = [
    "XiangxinAI",
    "AsyncXiangxinAI",
    "GuardrailRequest",
    "GuardrailResponse", 
    "GuardrailResult",
    "ComplianceResult",
    "SecurityResult",
    "Message",
    "XiangxinAIError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
]