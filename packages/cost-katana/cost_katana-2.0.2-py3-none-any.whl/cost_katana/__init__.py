"""
Cost Katana - Unified AI Interface with Cost Optimization

Simple interface for AI models that routes through Cost Katana for:
- Cost optimization and tracking
- Automatic failover between providers
- Usage analytics and insights
- No API key management needed in your code

Example:
    import cost_katana as ck

    # Configure once
    ck.configure(config_file='config.json')

    # Use like any AI library
    model = ck.GenerativeModel('gemini-2.0-flash')
    chat = model.start_chat()
    response = chat.send_message("Hello!")
    print(response.text)
"""

from .client import CostKatanaClient, get_global_client
from .models import ChatSession
from .exceptions import (
    CostKatanaError,
    AuthenticationError,
    ModelNotAvailableError,
    RateLimitError,
    CostLimitExceededError,
)
from .config import Config

__version__ = "2.0.2"
__all__ = [
    "configure",
    "create_generative_model",
    "ChatSession",
    "CostKatanaClient",
    "CostKatanaError",
    "AuthenticationError",
    "ModelNotAvailableError",
    "RateLimitError",
    "CostLimitExceededError",
    "Config",
]

# Import configure function from client
from .client import configure


def create_generative_model(model_name: str, **kwargs):
    """
    Create a generative model instance.

    Args:
        model_name: Name of the model (e.g., 'gemini-2.0-flash', 'claude-3-sonnet', 'gpt-4')
        **kwargs: Additional model configuration

    Returns:
        GenerativeModel instance

    Example:
        model = cost_katana.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Hello, world!")
    """
    client = get_global_client()

    from .models import GenerativeModel as GM

    return GM(client, model_name, **kwargs)
