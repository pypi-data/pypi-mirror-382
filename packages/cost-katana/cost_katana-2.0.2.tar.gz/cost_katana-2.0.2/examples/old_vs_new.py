#!/usr/bin/env python3
"""
Before vs After Comparison - Cost Katana Python SDK

This script demonstrates the difference between using traditional
AI provider SDKs vs Cost Katana's unified interface.
"""

print("🔄 Old Way vs New Way - AI Provider Comparison")
print("=" * 60)

print("\n📚 OLD WAY: Managing Multiple Provider SDKs")
print("-" * 50)

print(
    """
# Install multiple packages
pip install google-generativeai
pip install anthropic  
pip install openai
pip install boto3

# Manage multiple API keys
import google.generativeai as genai
import anthropic
import openai
from boto3 import Session

# Configure each provider separately
genai.configure(api_key="your-google-key")
anthropic_client = anthropic.Anthropic(api_key="your-anthropic-key")
openai.api_key = "your-openai-key"
bedrock = Session().client('bedrock-runtime', region_name='us-east-1')

# Different APIs for each provider
def old_way_example():
    # Google Gemini
    google_model = genai.GenerativeModel('gemini-2.0-flash')
    google_response = google_model.generate_content("Hello")
    
    # Anthropic Claude  
    claude_response = anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        messages=[{"role": "user", "content": "Hello"}]
    )
    
    # OpenAI GPT
    openai_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
    
    # AWS Bedrock (complex setup)
    bedrock_response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": "Hello"}]
        })
    )
    
    # No cost tracking, no optimization, no failover
    # Different response formats to handle
    # Provider lock-in and complex management

"""
)

print("\n✨ NEW WAY: Cost Katana Unified Interface")
print("-" * 50)

print(
    """
# Install one package
pip install cost-katana

# One API key for everything
import cost_katana as ck

# Configure once
ck.configure(api_key='dak_your_key_here')

# Same interface for all providers
def new_way_example():
    # Google Gemini
    gemini = ck.GenerativeModel('gemini-2.0-flash')
    gemini_response = gemini.generate_content("Hello")
    
    # Anthropic Claude
    claude = ck.GenerativeModel('claude-3-sonnet')
    claude_response = claude.generate_content("Hello")
    
    # OpenAI GPT
    gpt = ck.GenerativeModel('gpt-4')
    gpt_response = gpt.generate_content("Hello")
    
    # AWS Bedrock
    nova = ck.GenerativeModel('nova-pro')
    nova_response = nova.generate_content("Hello")
    
    # Automatic cost tracking for all
    total_cost = (gemini_response.usage_metadata.cost + 
                  claude_response.usage_metadata.cost +
                  gpt_response.usage_metadata.cost +
                  nova_response.usage_metadata.cost)
    
    print(f"Total cost: ${total_cost:.4f}")
    
    # Built-in optimization and failover
    # Consistent response format
    # No provider lock-in

"""
)

# Let's demo the actual new way if user has configured Cost Katana
print("\n🚀 LIVE DEMO: Cost Katana in Action")
print("-" * 50)

try:
    import cost_katana as ck

    # Try to configure
    try:
        ck.configure(config_file="config.json")
        print("✅ Using config.json")
    except FileNotFoundError:
        print("ℹ️  No config.json found")
        api_key = input(
            "Enter your Cost Katana API key (or press Enter to skip): "
        ).strip()
        if api_key:
            ck.configure(api_key=api_key)
            print("✅ Configured with API key")
        else:
            print("⏭️  Skipping live demo")
            exit()

    print("\n🧪 Testing the same prompt with different providers...")

    test_prompt = "Explain what makes you unique in exactly one sentence."
    models_to_test = [
        ("gemini-2.0-flash", "Google Gemini"),
        ("claude-3-haiku", "Anthropic Claude"),
        ("nova-micro", "AWS Nova"),
    ]

    total_cost = 0

    for model_id, display_name in models_to_test:
        try:
            print(f"\n🤖 {display_name} ({model_id}):")
            model = ck.GenerativeModel(model_id)
            response = model.generate_content(test_prompt)

            print(f"   Response: {response.text}")
            print(f"   💰 Cost: ${response.usage_metadata.cost:.4f}")
            print(f"   ⚡ Latency: {response.usage_metadata.latency:.2f}s")
            print(f"   🔢 Tokens: {response.usage_metadata.total_tokens}")

            total_cost += response.usage_metadata.cost

            if response.usage_metadata.cache_hit:
                print("   💾 Cache Hit: Saved money!")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print(f"\n💳 Total Demo Cost: ${total_cost:.4f}")
    print("\n✨ Key Benefits Demonstrated:")
    print("   • Same simple interface for all providers")
    print("   • Automatic cost tracking and optimization")
    print("   • Consistent response format")
    print("   • Built-in error handling and failover")
    print("   • No need to manage multiple API keys")

except ImportError:
    print("❌ Cost Katana not installed. Run: pip install cost-katana")
except Exception as e:
    print(f"❌ Demo error: {e}")

print("\n📊 COMPARISON SUMMARY")
print("-" * 50)

comparison_table = """
| Feature                    | Old Way (Multiple SDKs) | New Way (Cost Katana) |
|----------------------------|--------------------------|----------------------|
| Installation               | 4+ packages              | 1 package           |
| API Keys                   | Multiple keys needed     | 1 key for all       |
| Interface Consistency      | Different for each       | Same for all        |
| Cost Tracking             | Manual implementation    | Built-in automatic  |
| Failover/Redundancy       | Custom code required     | Automatic           |
| Performance Optimization  | Not available            | Intelligent routing |
| Response Format           | Different per provider   | Consistent          |
| Provider Lock-in          | High risk                | No lock-in          |
| Configuration Management  | Multiple config files    | Single config       |
| Error Handling            | Provider-specific        | Unified             |
| Analytics & Insights      | Build your own           | Built-in dashboard  |
| Team Collaboration        | Complex setup            | Simple sharing      |
"""

print(comparison_table)

print("\n🎯 CONCLUSION")
print("-" * 50)
print(
    """
Cost Katana transforms AI development by providing:

✅ SIMPLICITY: One interface, one API key, one package
✅ FLEXIBILITY: Switch providers without code changes  
✅ OPTIMIZATION: Automatic cost and performance tuning
✅ RELIABILITY: Built-in failover and error handling
✅ VISIBILITY: Complete usage tracking and analytics
✅ SCALABILITY: Enterprise features for team management

Stop managing multiple AI SDKs. Start optimizing with Cost Katana!
"""
)

print("🚀 Get started: https://costkatana.com")
print("📚 Documentation: https://docs.costkatana.com")
print("💬 Community: https://discord.gg/Wcwzw8wM")
