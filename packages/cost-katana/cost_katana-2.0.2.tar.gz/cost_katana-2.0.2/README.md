# Cost Katana Python SDK

A unified AI SDK with cost optimization, failover, and analytics. Use any AI provider through one consistent API with built-in cost tracking and optimization.

## 🚀 Quick Start

### Installation

```bash
pip install cost-katana
```

### Get Your API Key

1. Visit [Cost Katana Dashboard](https://costkatana.com/dashboard)
2. Create an account or sign in
3. Go to API Keys section
4. Generate a new API key (starts with `dak_`)

### Basic Usage

```python
import cost_katana as ck

# Configure once with your API key
ck.configure(api_key='dak_your_key_here')

# Use any AI model with the same simple interface
model = ck.GenerativeModel('nova-lite')
response = model.generate_content("Explain quantum computing in simple terms")
print(response.text)
print(f"Cost: ${response.usage_metadata.cost:.4f}")
```

### Chat Sessions

```python
import cost_katana as ck

ck.configure(api_key='dak_your_key_here')

# Start a conversation
model = ck.GenerativeModel('claude-3-sonnet')
chat = model.start_chat()

# Send messages back and forth
response1 = chat.send_message("Hello! What's your name?")
print("AI:", response1.text)

response2 = chat.send_message("Can you help me write a Python function?")
print("AI:", response2.text)

# Get total conversation cost
total_cost = sum(msg.get('metadata', {}).get('cost', 0) for msg in chat.history)
print(f"Total conversation cost: ${total_cost:.4f}")
```

## 🎯 Key Features

### Multi-Provider Support
- **OpenAI**: GPT-4, GPT-3.5, GPT-4o
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Haiku, Claude 3 Opus
- **Google**: Gemini Pro, Gemini Ultra
- **AWS Bedrock**: Claude, Llama, Titan models
- **And more**: 50+ models across 10+ providers

### Cost Optimization
- **Automatic failover**: Switch providers when one is down or expensive
- **Cost tracking**: Real-time cost monitoring and analytics
- **Smart routing**: Choose the best model for your budget and needs
- **Usage analytics**: Detailed insights into your AI spending

### Developer Experience
- **Unified API**: Same interface for all AI providers
- **No API key management**: Secure key storage and rotation
- **Error handling**: Robust error handling with automatic retries
- **Type hints**: Full type support for better IDE experience

## 📊 Usage Examples

### Cost-Aware Model Selection

```python
import cost_katana as ck

ck.configure(api_key='dak_your_key_here')

# Get available models with cost information
client = ck.CostKatanaClient()
models = client.get_available_models()

for model in models:
    print(f"{model['name']}: ${model['cost_per_1k_tokens']:.4f}/1k tokens")

# Use the most cost-effective model
cheapest_model = min(models, key=lambda x: x['cost_per_1k_tokens'])
model = ck.GenerativeModel(cheapest_model['id'])
```

### Batch Processing

```python
import cost_katana as ck

ck.configure(api_key='dak_your_key_here')

# Process multiple requests efficiently
queries = [
    "Explain machine learning",
    "Write a Python function",
    "What is quantum computing?"
]

model = ck.GenerativeModel('claude-3-haiku')  # Fast and cost-effective
responses = []

for query in queries:
    response = model.generate_content(query)
    responses.append({
        'query': query,
        'response': response.text,
        'cost': response.usage_metadata.cost
    })

total_cost = sum(r['cost'] for r in responses)
print(f"Processed {len(queries)} queries for ${total_cost:.4f}")
```

### Advanced Configuration

```python
import cost_katana as ck

# Configure with custom settings
ck.configure(
    api_key='dak_your_key_here',
    base_url='https://api.costkatana.com',  # Custom endpoint
    timeout=60,  # Custom timeout
    max_retries=3,  # Retry failed requests
    cost_limit=10.0  # Daily cost limit
)

# Use with specific model parameters
model = ck.GenerativeModel('gpt-4')
response = model.generate_content(
    "Write a comprehensive guide to Python",
    temperature=0.7,
    max_tokens=2000,
    chat_mode='balanced'  # balanced, fastest, cheapest
)
```

## 🔧 Configuration

### Environment Variables

```bash
export COST_KATANA_API_KEY="dak_your_key_here"
export COST_KATANA_BASE_URL="https://api.costkatana.com"
export COST_KATANA_TIMEOUT="30"
```

### Configuration File

Create a `config.json` file:

```json
{
  "api_key": "dak_your_key_here",
    "base_url": "https://api.costkatana.com",
    "timeout": 30,
    "max_retries": 3,
    "cost_limit": 10.0,
    "default_model": "claude-3-haiku"
}
```

Then use it:

```python
import cost_katana as ck

ck.configure(config_file='config.json')
```

## 📈 Analytics & Monitoring

### Usage Analytics

```python
import cost_katana as ck

ck.configure(api_key='dak_your_key_here')
client = ck.CostKatanaClient()

# Get usage statistics
stats = client.get_usage_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Total cost: ${stats['total_cost']:.4f}")
print(f"Average cost per request: ${stats['avg_cost_per_request']:.4f}")

# Get cost breakdown by model
breakdown = client.get_cost_breakdown()
for model, cost in breakdown.items():
    print(f"{model}: ${cost:.4f}")
```

### Real-time Monitoring

```python
# Monitor costs in real-time
def monitor_costs():
    client = ck.CostKatanaClient()
    while True:
        stats = client.get_usage_stats()
        if stats['total_cost'] > 5.0:  # Alert if cost exceeds $5
            print(f"⚠️ Cost alert: ${stats['total_cost']:.4f}")
        time.sleep(60)  # Check every minute
```

## 🛠️ Advanced Features

### Custom Error Handling

```python
import cost_katana as ck
from cost_katana.exceptions import CostKatanaError, RateLimitError

try:
    model = ck.GenerativeModel('gpt-4')
    response = model.generate_content("Your prompt here")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    # Implement backoff strategy
except CostKatanaError as e:
    print(f"API error: {e}")
    # Handle other API errors
```

### Model Comparison

```python
import cost_katana as ck

ck.configure(api_key='dak_your_key_here')

# Compare different models on the same task
models_to_test = ['gpt-4', 'claude-3-sonnet', 'gemini-pro']
prompt = "Explain the concept of recursion in programming"

results = []
for model_name in models_to_test:
    model = ck.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    results.append({
        'model': model_name,
        'response': response.text,
        'cost': response.usage_metadata.cost,
        'tokens': response.usage_metadata.total_tokens
    })

# Find the best model for your needs
best_model = min(results, key=lambda x: x['cost'])
print(f"Most cost-effective: {best_model['model']} (${best_model['cost']:.4f})")
```

## 📚 API Reference

### Core Classes

- **`CostKatanaClient`**: Main client for API interactions
- **`GenerativeModel`**: Model interface for generating content
- **`ChatSession`**: Chat conversation management
- **`Config`**: Configuration management

### Key Methods

- **`configure()`**: Global configuration
- **`get_available_models()`**: List all available models
- **`send_message()`**: Send a message to a model
- **`create_conversation()`**: Start a new conversation
- **`get_usage_stats()`**: Get usage analytics

### Exceptions

- **`CostKatanaError`**: Base exception class
- **`AuthenticationError`**: Authentication failures
- **`ModelNotAvailableError`**: Model not found
- **`RateLimitError`**: Rate limit exceeded
- **`CostLimitExceededError`**: Cost limit exceeded

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/Hypothesize-Tech/cost-katana-python/blob/main/CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/Hypothesize-Tech/cost-katana-python.git
cd cost-katana-python
pip install -e .
pip install -r requirements-dev.txt
```

### Running Tests

```bash
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://docs.costkatana.com](https://docs.costkatana.com)
- **Issues**: [GitHub Issues](https://github.com/Hypothesize-Tech/cost-katana-python/issues)
- **Email**: support@costkatana.com
- **Discord**: [Join our community](https://discord.gg/costkatana)

## 🚀 What's Next?

- **More AI providers**: We're constantly adding new AI providers
- **Advanced analytics**: Enhanced cost tracking and optimization
- **Enterprise features**: Team management, advanced security
- **SDK improvements**: Better error handling, more features

---

**Cost Katana** - Making AI accessible, affordable, and reliable for everyone.