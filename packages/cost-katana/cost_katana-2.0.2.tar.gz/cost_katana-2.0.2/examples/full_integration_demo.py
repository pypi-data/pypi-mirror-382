#!/usr/bin/env python3
"""
Full Integration Demo - Cost Katana Python SDK

This comprehensive example showcases all the features of Cost Katana,
demonstrating how it provides enterprise-grade AI capabilities with
a simple interface.
"""

import cost_katana as ck
from cost_katana.exceptions import *
from cost_katana.models import GenerationConfig
import json
import time
from pathlib import Path


def banner(text):
    """Print a fancy banner"""
    print(f"\n{'='*60}")
    print(f"🚀 {text}")
    print(f"{'='*60}")


def section(text):
    """Print a section header"""
    print(f"\n{'-'*50}")
    print(f"📋 {text}")
    print(f"{'-'*50}")


def main():
    banner("COST KATANA - FULL INTEGRATION DEMO")
    print("This demo showcases the complete Cost Katana experience")
    print("From simple usage to advanced enterprise features")

    # Step 1: Configuration
    section("1. Configuration Setup")

    config_file = "demo_config.json"

    if not Path(config_file).exists():
        print("Creating sample configuration...")
        sample_config = {
            "api_key": "dak_your_api_key_here",
            "base_url": "https://cost-katana-backend.store",
            "default_model": "gemini-2.0-flash",
            "default_temperature": 0.7,
            "cost_limit_per_request": 2.0,
            "cost_limit_per_day": 50.0,
            "enable_optimization": True,
            "enable_failover": True,
            "model_mappings": {
                "fast": "gemini-2.0-flash",
                "smart": "claude-3-sonnet",
                "cheap": "claude-3-haiku",
                "powerful": "gpt-4",
            },
        }

        with open(config_file, "w") as f:
            json.dump(sample_config, f, indent=2)

        print(f"✅ Created {config_file}")
        print("🔑 Please edit the file and add your API key!")

        api_key = input(
            "\nEnter your Cost Katana API key now (or press Enter to use file): "
        ).strip()
        if api_key:
            sample_config["api_key"] = api_key
            with open(config_file, "w") as f:
                json.dump(sample_config, f, indent=2)
            print("✅ Updated configuration with your API key")

    try:
        ck.configure(config_file=config_file)
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        print("💡 Make sure your API key is correct in demo_config.json")
        return

    # Step 2: Simple Usage Demo
    section("2. Simple Usage (Like Google Gemini)")

    try:
        print("Creating a Gemini model (simple interface)...")
        model = ck.GenerativeModel("gemini-2.0-flash")

        response = model.generate_content("Explain quantum computing in one sentence")

        print(f"🤖 Response: {response.text}")
        print(f"💰 Cost: ${response.usage_metadata.cost:.4f}")
        print(f"⚡ Latency: {response.usage_metadata.latency:.2f}s")
        print("✅ Simple usage successful - just like google-generative-ai!")

    except Exception as e:
        print(f"❌ Simple usage failed: {e}")
        return

    # Step 3: Advanced Configuration Demo
    section("3. Advanced Generation Configuration")

    try:
        # Custom generation config
        config = GenerationConfig(
            temperature=0.3, max_output_tokens=500, candidate_count=1
        )

        model = ck.GenerativeModel("claude-3-sonnet", generation_config=config)
        response = model.generate_content(
            "Write a Python function to calculate fibonacci numbers",
            chat_mode="balanced",
        )

        print(f"🤖 Code Response: {response.text[:200]}...")
        print(f"💰 Cost: ${response.usage_metadata.cost:.4f}")
        print("✅ Advanced configuration successful!")

    except Exception as e:
        print(f"❌ Advanced config failed: {e}")

    # Step 4: Chat Session Demo
    section("4. Conversational Chat Session")

    try:
        print("Starting a multi-turn conversation...")

        chat_model = ck.GenerativeModel("fast")  # Using mapped name
        chat = chat_model.start_chat()

        conversation = [
            "Hi! What's your name?",
            "Can you help me plan a trip to Japan?",
            "What's the best time to visit for cherry blossoms?",
        ]

        total_chat_cost = 0

        for i, message in enumerate(conversation, 1):
            print(f"\n👤 User: {message}")
            response = chat.send_message(message)
            print(f"🤖 Assistant: {response.text}")

            total_chat_cost += response.usage_metadata.cost
            print(f"💰 Message cost: ${response.usage_metadata.cost:.4f}")

        print(f"\n💳 Total conversation cost: ${total_chat_cost:.4f}")
        print("✅ Chat session successful!")

    except Exception as e:
        print(f"❌ Chat session failed: {e}")

    # Step 5: Multi-Provider Comparison
    section("5. Multi-Provider Comparison")

    models_to_compare = [
        ("fast", "Gemini 2.0 Flash"),
        ("smart", "Claude 3 Sonnet"),
        ("cheap", "Claude 3 Haiku"),
    ]

    comparison_prompt = "What are the benefits of renewable energy? List 3 key points."
    comparison_results = []

    print("Testing the same prompt across different providers...")

    for model_key, display_name in models_to_compare:
        try:
            print(f"\n🔄 Testing {display_name}...")
            model = ck.GenerativeModel(model_key)

            start_time = time.time()
            response = model.generate_content(comparison_prompt)
            wall_time = time.time() - start_time

            result = {
                "name": display_name,
                "cost": response.usage_metadata.cost,
                "latency": response.usage_metadata.latency,
                "wall_time": wall_time,
                "tokens": response.usage_metadata.total_tokens,
                "response": response.text,
                "cache_hit": response.usage_metadata.cache_hit,
                "optimizations": response.usage_metadata.optimizations_applied,
            }
            comparison_results.append(result)

            print(f"   💰 Cost: ${result['cost']:.4f}")
            print(f"   ⚡ Latency: {result['latency']:.2f}s")
            print(f"   🔢 Tokens: {result['tokens']}")

            if result["cache_hit"]:
                print("   💾 Cache hit - saved money!")
            if result["optimizations"]:
                print(f"   ⚡ Optimizations: {', '.join(result['optimizations'])}")

        except Exception as e:
            print(f"   ❌ Failed: {e}")

    # Analysis
    if comparison_results:
        print("\n📊 Comparison Analysis:")
        cheapest = min(comparison_results, key=lambda x: x["cost"])
        fastest = min(comparison_results, key=lambda x: x["latency"])

        print(f"💰 Most cost-effective: {cheapest['name']} (${cheapest['cost']:.4f})")
        print(f"⚡ Fastest response: {fastest['name']} ({fastest['latency']:.2f}s)")

        total_comparison_cost = sum(r["cost"] for r in comparison_results)
        print(f"💳 Total comparison cost: ${total_comparison_cost:.4f}")

    # Step 6: Error Handling Demo
    section("6. Error Handling & Resilience")

    try:
        print("Testing error handling...")

        # Try an expensive operation that might hit limits
        expensive_model = ck.GenerativeModel("powerful")

        try:
            expensive_response = expensive_model.generate_content(
                "Write a comprehensive 5000-word essay about artificial intelligence history",
                max_tokens=5000,
            )
            print("✅ Expensive operation completed successfully")
            print(f"💰 Cost: ${expensive_response.usage_metadata.cost:.4f}")

        except CostLimitExceededError:
            print("💰 Cost limit protection activated - trying cheaper alternative")

            cheap_model = ck.GenerativeModel("cheap")
            fallback_response = cheap_model.generate_content(
                "Write a brief summary of AI history", max_tokens=200
            )
            print(
                f"✅ Fallback successful: ${fallback_response.usage_metadata.cost:.4f}"
            )

        except ModelNotAvailableError as e:
            print(f"🔄 Model unavailable - automatic failover would activate: {e}")

        except Exception as e:
            print(f"⚠️  Unexpected error handled gracefully: {e}")

    except Exception as e:
        print(f"❌ Error handling demo failed: {e}")

    # Step 7: Analytics & Insights
    section("7. Usage Analytics & Insights")

    print("📊 Session Analytics Summary:")
    print("  • Multiple providers tested seamlessly")
    print("  • Automatic cost tracking across all requests")
    print("  • Built-in optimization and caching")
    print("  • Consistent interface regardless of provider")
    print("  • Enterprise-grade error handling and failover")

    # Step 8: Best Practices Demo
    section("8. Production Best Practices")

    print("🏭 Production Configuration:")
    print(
        """
    {
      "api_key": "dak_prod_key_from_env",
      "cost_limit_per_day": 500.0,
      "enable_optimization": true,
      "enable_failover": true,
      "monitoring": {
        "track_usage": true,
        "alert_on_high_cost": true,
        "daily_spend_alert": 250.0
      },
      "providers": {
        "primary": {
          "priority": 1,
          "models": ["claude-3-sonnet"]
        },
        "fallback": {
          "priority": 2, 
          "models": ["gemini-2.0-flash"]
        }
      }
    }
    """
    )

    print("🔐 Security Best Practices:")
    print("  • Store API keys in environment variables")
    print("  • Use configuration files for settings")
    print("  • Set appropriate cost limits")
    print("  • Enable monitoring and alerts")
    print("  • Use team management for collaboration")

    # Final Summary
    banner("DEMO COMPLETE - COST KATANA ADVANTAGES")

    advantages = [
        "🎯 SIMPLE: One interface for all AI providers",
        "💰 SMART: Automatic cost optimization and tracking",
        "🔄 RELIABLE: Built-in failover and error handling",
        "📊 INSIGHTFUL: Comprehensive usage analytics",
        "🔒 SECURE: Enterprise-grade security and monitoring",
        "👥 COLLABORATIVE: Team management and sharing",
        "🚀 SCALABLE: From prototype to production",
        "💡 INNOVATIVE: Cutting-edge AI optimization algorithms",
    ]

    for advantage in advantages:
        print(advantage)

    print("\n🌟 What you get with Cost Katana:")
    print("  • Save 30-60% on AI costs through optimization")
    print("  • 99.9% uptime with automatic failover")
    print("  • 10x faster development with unified API")
    print("  • Complete visibility into AI usage and costs")
    print("  • Enterprise features: teams, approvals, budgets")

    print("\n🚀 Ready to transform your AI development?")
    print("   Visit: https://costkatana.com")
    print("   Docs: https://docs.costkatana.com")
    print("   Support: support@costkatana.com")

    # Cleanup
    try:
        Path(config_file).unlink()
        print(f"\n🧹 Cleaned up {config_file}")
    except:
        pass

    print("\n✨ Thank you for trying Cost Katana!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for trying Cost Katana!")
    except Exception as e:
        print(f"\n💥 Demo error: {e}")
        print("💡 For support, visit: https://costkatana.com/support")
