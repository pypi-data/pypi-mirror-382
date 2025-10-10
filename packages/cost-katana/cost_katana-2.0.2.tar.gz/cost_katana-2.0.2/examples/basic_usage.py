#!/usr/bin/env python3
"""
Basic Usage Example - Cost Katana Python SDK

This example shows the simplest way to use Cost Katana,
similar to how you'd use google-generative-ai but with
automatic cost optimization and failover.
"""

import cost_katana as ck


def main():
    print("🤖 Cost Katana - Basic Usage Example")
    print("=" * 50)

    # Step 1: Configure Cost Katana with your API key
    # Get your API key from: https://costkatana.com/integrations
    api_key = input("Enter your Cost Katana API key (starts with 'dak_'): ").strip()

    if not api_key.startswith("dak_"):
        print("❌ Invalid API key format. Should start with 'dak_'")
        return

    ck.configure(api_key=api_key)
    print("✅ Cost Katana configured successfully!")

    # Step 2: Create a model instance (just like google-generative-ai)
    print("\n📱 Creating Gemini 2.0 Flash model...")
    model = ck.GenerativeModel("gemini-2.0-flash")

    # Step 3: Generate content
    print("\n💭 Generating content...")
    response = model.generate_content(
        "Explain the benefits of using AI cost optimization in simple terms"
    )

    # Step 4: Display results
    print("\n🤖 AI Response:")
    print("-" * 30)
    print(response.text)

    print("\n📊 Usage Stats:")
    print(f"💰 Cost: ${response.usage_metadata.cost:.4f}")
    print(f"⚡ Latency: {response.usage_metadata.latency:.2f}s")
    print(f"🔢 Tokens: {response.usage_metadata.total_tokens}")
    print(f"🤖 Model: {response.usage_metadata.model}")

    if response.usage_metadata.cache_hit:
        print("💾 Cache Hit: Yes (Saved money!)")

    if response.usage_metadata.optimizations_applied:
        print(
            f"⚡ Optimizations: {', '.join(response.usage_metadata.optimizations_applied)}"
        )

    # Step 5: Try a different model for comparison
    print("\n🔄 Now trying with Claude 3 Sonnet...")
    claude_model = ck.GenerativeModel("claude-3-sonnet")
    claude_response = claude_model.generate_content(
        "What makes Claude different from other AI models? Be brief."
    )

    print("\n🤖 Claude Response:")
    print("-" * 30)
    print(claude_response.text)
    print(f"💰 Cost: ${claude_response.usage_metadata.cost:.4f}")

    # Step 6: Show total session cost
    total_cost = response.usage_metadata.cost + claude_response.usage_metadata.cost
    print(f"\n💳 Total Session Cost: ${total_cost:.4f}")

    print("\n✨ That's it! You've successfully used multiple AI providers")
    print("   through one simple interface with automatic cost tracking.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure you have a valid API key and internet connection.")
