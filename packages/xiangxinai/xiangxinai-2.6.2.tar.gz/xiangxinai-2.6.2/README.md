# Xiangxin AI Guardrails Python Client

[![PyPI version](https://badge.fury.io/py/xiangxinai.svg)](https://badge.fury.io/py/xiangxinai)
[![Python Support](https://img.shields.io/pypi/pyversions/xiangxinai.svg)](https://pypi.org/project/xiangxinai/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

An LLM-based context-aware AI guardrail that understands conversation context for security, safety and data leakage detection.

## Features

* 🧠 **Context Awareness** – Based on LLM conversation understanding rather than simple batch detection
* 🔍 **Prompt Injection Detection** – Detects malicious prompt injections and jailbreak attacks
* 📋 **Content Compliance Detection** – Complies with generative AI safety requirements
* 🔐 **Sensitive Data Leak Prevention** – Detects and prevents personal or corporate data leaks
* 🧩 **User-level Ban Policy** – Supports user-granular risk recognition and blocking strategies
* 🖼️ **Multimodal Detection** – Supports image content safety detection
* 🛠️ **Easy Integration** – OpenAI-compatible API format; plug in with one line of code
* ⚡ **OpenAI-style API** – Familiar interface design for rapid adoption
* 🚀 **Sync/Async Support** – Supports both synchronous and asynchronous calls for different scenarios

## Installation

```bash
pip install xiangxinai
```

## Quick Start

### Basic Usage

```python
from xiangxinai import XiangxinAI

# Create a client
client = XiangxinAI(
    api_key="your-api-key",
    base_url="https://api.xiangxinai.cn/v1"  # Cloud API
)

# Check user input
result = client.check_prompt("I want to learn Python programming", user_id="user-123")
print(result.suggest_action)        # Output: pass
print(result.overall_risk_level)    # Output: no_risk
print(result.score)                 # Confidence score, e.g. 0.9993114447238793

# Check model response (context-aware)
result = client.check_response_ctx(
    prompt="Teach me how to cook",
    response="I can teach you some simple home dishes",
    user_id="user-123"  # Optional user-level risk control
)
print(result.suggest_action)      # Output: pass
print(result.overall_risk_level)  # Output: no_risk
```

### Context-Aware Detection (Core Feature)

```python
# Context-based conversation detection - Core feature
messages = [
    {"role": "user", "content": "I want to learn chemistry"},
    {"role": "assistant", "content": "Chemistry is an interesting subject. What part would you like to learn?"},
    {"role": "user", "content": "Teach me reactions for making explosives"}
]

result = client.check_conversation(messages, user_id="user-123")
print(result.overall_risk_level)
print(result.suggest_action)  # Result based on full conversation context
if result.suggest_answer:
    print(f"Suggested answer: {result.suggest_answer}")
```

### Asynchronous API (Recommended)

```python
import asyncio
from xiangxinai import AsyncXiangxinAI

async def main():
    async with AsyncXiangxinAI(api_key="your-api-key") as client:
        # Async prompt check
        result = await client.check_prompt("I want to learn Python programming")
        print(result.suggest_action)  # Output: pass
        
        # Async conversation context check
        messages = [
            {"role": "user", "content": "I want to learn chemistry"},
            {"role": "assistant", "content": "Chemistry is an interesting subject. What part would you like to learn?"},
            {"role": "user", "content": "Teach me reactions for making explosives"}
        ]
        result = await client.check_conversation(messages)
        print(result.overall_risk_level)

asyncio.run(main())
```

### Concurrent Processing

```python
import asyncio
from xiangxinai import AsyncXiangxinAI

async def batch_check():
    async with AsyncXiangxinAI(api_key="your-api-key") as client:
        # Handle multiple requests concurrently
        tasks = [
            client.check_prompt("Content 1"),
            client.check_prompt("Content 2"),
            client.check_prompt("Content 3")
        ]
        results = await asyncio.gather(*tasks)
        
        for i, result in enumerate(results):
            print(f"Content {i+1}: {result.overall_risk_level}")

asyncio.run(batch_check())
```

### Multimodal Image Detection

Supports multimodal detection for image content safety. The system analyzes both text prompt semantics and image semantics for risk.

```python
from xiangxinai import XiangxinAI

client = XiangxinAI(api_key="your-api-key")

# Check a single local image
result = client.check_prompt_image(
    prompt="Is this image safe?",
    image="/path/to/image.jpg"
)
print(result.overall_risk_level)
print(result.suggest_action)

# Check an image from URL
result = client.check_prompt_image(
    prompt="",  # prompt can be empty
    image="https://example.com/image.jpg"
)

# Check multiple images
images = [
    "/path/to/image1.jpg",
    "https://example.com/image2.jpg",
    "/path/to/image3.png"
]
result = client.check_prompt_images(
    prompt="Are all these images safe?",
    images=images
)
print(result.overall_risk_level)
```

Async version:

```python
import asyncio
from xiangxinai import AsyncXiangxinAI

async def check_images():
    async with AsyncXiangxinAI(api_key="your-api-key") as client:
        # Async check for a single image
        result = await client.check_prompt_image(
            prompt="Is this image safe?",
            image="/path/to/image.jpg"
        )
        print(result.overall_risk_level)

        # Async check for multiple images
        images = ["/path/to/image1.jpg", "/path/to/image2.jpg"]
        result = await client.check_prompt_images(
            prompt="Are these images safe?",
            images=images
        )
        print(result.overall_risk_level)

asyncio.run(check_images())
```

### On-Premise Deployment

```python
# Sync client connecting to local deployment
client = XiangxinAI(
    api_key="your-local-api-key",
    base_url="http://localhost:5000/v1"
)

# Async client connecting to local deployment
async with AsyncXiangxinAI(
    api_key="your-local-api-key",
    base_url="http://localhost:5000/v1"
) as client:
    result = await client.check_prompt("Test content")
```

## API Reference

### XiangxinAI Class (Synchronous)

#### Initialization Parameters

* `api_key` (str): API key
* `base_url` (str): Base API URL, defaults to the cloud endpoint
* `timeout` (int): Request timeout, default 30 seconds
* `max_retries` (int): Maximum retry count, default 3

#### Methods

##### check_prompt(content: str, user_id: Optional[str] = None) -> GuardrailResponse

Checks the safety of a single prompt.

**Parameters:**

* `content`: Text content to be checked
* `user_id`: Optional tenant user ID for per-user risk control and auditing

**Returns:** `GuardrailResponse` object

##### check_conversation(messages: List[Message], model: str = "Xiangxin-Guardrails-Text", user_id: Optional[str] = None) -> GuardrailResponse

Checks conversation context safety (core feature).

**Parameters:**

* `messages`: List of messages, each containing `role` and `content`
* `model`: Model name (default: "Xiangxin-Guardrails-Text")
* `user_id`: Optional tenant user ID

**Returns:** `GuardrailResponse` object

### AsyncXiangxinAI Class (Asynchronous)

Same initialization parameters as the synchronous version.

#### Methods

##### async check_prompt(content: str) -> GuardrailResponse

Asynchronously checks a single prompt.

##### async check_conversation(messages: List[Message]) -> GuardrailResponse

Asynchronously checks conversation context safety (core feature).

##### async health_check() -> Dict[str, Any]

Checks API service health.

##### async get_models() -> Dict[str, Any]

Retrieves available model list.

##### async close()

Closes async session (automatically handled with `async with`).

### GuardrailResponse Class

Represents detection results.

#### Attributes

* `id`: Unique request ID
* `result.compliance.risk_level`: Compliance risk level
* `result.security.risk_level`: Security risk level
* `result.data.risk_level`: Data leak risk level (added in v2.4.0)
* `result.data.categories`: Detected sensitive data types (added in v2.4.0)
* `overall_risk_level`: Overall risk level (none / low / medium / high)
* `suggest_action`: Suggested action (pass / block / substitute)
* `suggest_answer`: Suggested response (optional, includes redacted content if applicable)
* `score`: Confidence score of the results

#### Helper Methods

* `is_safe`: Whether the content is safe
* `is_blocked`: Whether the content is blocked
* `has_substitute`: Whether a substitute answer is provided
* `all_categories`: Get all detected risk categories

## Safety Detection Capabilities

### Risk Levels

* **High Risk:** Sensitive political topics, national image damage, violent crime, prompt attacks
* **Medium Risk:** General political topics, harm to minors, illegal acts, sexual content
* **Low Risk:** Hate speech, insults, privacy violations, commercial misconduct
* **No Risk:** Safe content

### Handling Strategies

* **High Risk:** Recommend blocking
* **Medium Risk:** Recommend substitution with a safe reply
* **Low Risk:** Recommend substitution or business-dependent handling
* **No Risk:** Recommend pass

## Error Handling

### Synchronous Error Handling

```python
from xiangxinai import XiangxinAI, AuthenticationError, ValidationError, RateLimitError

try:
    result = client.check_prompt("Test content")
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Input validation failed: {e}")
except RateLimitError:
    print("Rate limit exceeded")
except Exception as e:
    print(f"Other error: {e}")
```

### Asynchronous Error Handling

```python
import asyncio
from xiangxinai import AsyncXiangxinAI, AuthenticationError, ValidationError, RateLimitError

async def safe_check():
    try:
        async with AsyncXiangxinAI(api_key="your-api-key") as client:
            result = await client.check_prompt("Test content")
            return result
    except AuthenticationError:
        print("Invalid API key")
    except ValidationError as e:
        print(f"Input validation failed: {e}")
    except RateLimitError:
        print("Rate limit exceeded")
    except Exception as e:
        print(f"Other error: {e}")

asyncio.run(safe_check())
```

## Development

```bash
# Clone the project
git clone https://github.com/xiangxinai/xiangxin-guardrails
cd xiangxin-guardrails/client

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black xiangxinai
isort xiangxinai

# Type checking
mypy xiangxinai
```

## License

This project is open-sourced under the [Apache 2.0](https://opensource.org/licenses/Apache-2.0) license.

## Support

* 📧 Technical Support: [wanglei@xiangxinai.cn](mailto:wanglei@xiangxinai.cn)
* 🌐 Official Website: [https://xiangxinai.cn](https://xiangxinai.cn)
* 📖 Documentation: [https://docs.xiangxinai.cn](https://docs.xiangxinai.cn)
* 🐛 Issue Tracker: [https://github.com/xiangxinai/xiangxin-guardrails/issues](https://github.com/xiangxinai/xiangxin-guardrails/issues)

---

Made with ❤️ by [Xiangxin AI](https://xiangxinai.cn)

---