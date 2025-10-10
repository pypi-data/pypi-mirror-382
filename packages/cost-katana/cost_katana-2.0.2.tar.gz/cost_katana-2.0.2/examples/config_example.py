#!/usr/bin/env python3
"""
Configuration Example - Cost Katana Python SDK

This example shows different ways to configure Cost Katana
and demonstrates advanced features like cost limits,
model preferences, and provider priorities.
"""

import cost_katana as ck
from cost_katana.config import Config
from cost_katana.exceptions import CostLimitExceededError, ModelNotAvailableError
import json


def create_sample_config():
    """Create a sample configuration file"""
    config_data = {
        "api_key": "dak_your_api_key_here",
        "base_url": "https://cost-katana-backend.store",
        "default_model": "gemini-2.0-flash",
        "default_temperature": 0.7,
        "default_max_tokens": 2000,
        "cost_limit_per_request": 0.50,
        "cost_limit_per_day": 25.0,
        "enable_analytics": True,
        "enable_optimization": True,
        "enable_failover": True,
        "model_mappings": {
            "gemini": "gemini-2.0-flash-exp",
            "claude": "anthropic.claude-3-sonnet-20240229-v1:0",
            "gpt4": "gpt-4-turbo-preview",
            "nova": "amazon.nova-pro-v1:0",
        },
        "providers": {
            "google": {
                "priority": 1,
                "models": ["gemini-2.0-flash", "gemini-pro", "gemini-flash"],
                "preferred_for": ["creative_writing", "general_chat"],
            },
            "anthropic": {
                "priority": 2,
                "models": ["claude-3-sonnet", "claude-3-haiku", "claude-3.5-sonnet"],
                "preferred_for": ["analysis", "coding", "reasoning"],
            },
            "openai": {
                "priority": 3,
                "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "preferred_for": ["function_calling", "structured_output"],
            },
            "aws": {
                "priority": 4,
                "models": ["nova-pro", "nova-lite", "nova-micro"],
                "preferred_for": ["enterprise", "batch_processing"],
            },
        },
        "cost_optimization": {
            "enable_caching": True,
            "cache_ttl": 3600,
            "enable_compression": True,
            "auto_fallback": True,
            "smart_routing": True,
        },
    }

    return config_data


def demo_basic_config():
    """Demo basic configuration methods"""
    print("🔧 Basic Configuration Methods")
    print("-" * 40)

    # Method 1: Direct API key
    print("1. Direct API key configuration:")
    api_key = input("Enter your API key: ").strip()
    ck.configure(api_key=api_key)
    print("   ✅ Configured with API key")

    # Method 2: Environment variables (demo)
    print("\n2. Environment variables (example):")
    print("   export API_KEY=dak_your_key")
    print("   export COST_KATANA_DEFAULT_MODEL=claude-3-sonnet")

    # Method 3: Config file
    print("\n3. Configuration file:")
    config_data = create_sample_config()
    config_data["api_key"] = api_key  # Use the provided API key

    with open("example_config.json", "w") as f:
        json.dump(config_data, f, indent=2)

    print("   📄 Created example_config.json")
    print(
        "   💡 You can edit this file and use: ck.configure(config_file='example_config.json')"
    )


def demo_advanced_features():
    """Demo advanced configuration features"""
    print("\n⚡ Advanced Features Demo")
    print("-" * 40)

    try:
        # Load config from file
        ck.configure(config_file="example_config.json")
        config = Config.from_file("example_config.json")

        print(
            f"✅ Loaded config with {len(config.get_provider_config('google'))} Google models"
        )

        # Demo model mapping
        print("\n🗺️  Model Mapping:")
        friendly_names = ["gemini", "claude", "gpt4", "nova"]
        for name in friendly_names:
            mapped = config.get_model_mapping(name)
            print(f"   {name} → {mapped}")

        # Demo different models with preferences
        print("\n🤖 Testing different models:")

        models_to_test = [
            ("gemini", "Write a creative short story about AI"),
            ("claude", "Analyze the pros and cons of remote work"),
            ("gpt4", "Create a JSON schema for a user profile"),
        ]

        total_cost = 0.0

        for model_name, prompt in models_to_test:
            try:
                print(f"\n   Testing {model_name}...")
                model = ck.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt[:50] + "..."
                )  # Truncate for demo

                print(f"   ✅ Response: {response.text[:100]}...")
                print(f"   💰 Cost: ${response.usage_metadata.cost:.4f}")

                total_cost += response.usage_metadata.cost

                if response.usage_metadata.optimizations_applied:
                    print(
                        f"   ⚡ Optimizations: {', '.join(response.usage_metadata.optimizations_applied)}"
                    )

            except ModelNotAvailableError as e:
                print(f"   ❌ Model not available: {e}")
            except CostLimitExceededError as e:
                print(f"   💰 Cost limit exceeded: {e}")
                break
            except Exception as e:
                print(f"   ❌ Error: {e}")

        print(f"\n💳 Total demo cost: ${total_cost:.4f}")

    except FileNotFoundError:
        print("❌ Config file not found. Run demo_basic_config first.")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_cost_controls():
    """Demo cost control features"""
    print("\n💰 Cost Control Features")
    print("-" * 40)

    try:
        # Test cost limits
        print("Testing cost limits...")

        # Create a model with strict cost limits
        model = ck.GenerativeModel("gemini-2.0-flash")

        # This might hit cost limits with a complex prompt
        expensive_prompt = """
        Please write a comprehensive 10,000-word essay about the history of artificial intelligence,
        including detailed analysis of every major breakthrough, complete with citations and examples.
        Make sure to cover machine learning, deep learning, natural language processing, computer vision,
        and robotics in extreme detail with multiple examples for each concept.
        """

        try:
            response = model.generate_content(expensive_prompt)
            print(f"✅ Generated content (cost: ${response.usage_metadata.cost:.4f})")

        except CostLimitExceededError as e:
            print(f"💰 Cost limit protection worked: {e}")

            # Try with a cheaper model or smaller prompt
            print("   Trying with optimized settings...")
            response = model.generate_content(
                "Write a brief summary of AI history",
                temperature=0.3,  # Lower temperature = more focused = potentially cheaper
                max_tokens=500,  # Limit output length
            )
            print(
                f"✅ Optimized request successful (cost: ${response.usage_metadata.cost:.4f})"
            )

    except Exception as e:
        print(f"❌ Error testing cost controls: {e}")


def main():
    print("⚙️  Cost Katana Configuration Example")
    print("=" * 50)

    try:
        # Basic configuration demo
        demo_basic_config()

        # Advanced features demo
        demo_advanced_features()

        # Cost controls demo
        demo_cost_controls()

        print("\n✨ Configuration demo complete!")
        print("💡 Edit example_config.json to customize your settings")

    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n💥 Error: {e}")


if __name__ == "__main__":
    main()
