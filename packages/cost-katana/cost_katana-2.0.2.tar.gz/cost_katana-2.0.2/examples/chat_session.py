#!/usr/bin/env python3
"""
Chat Session Example - Cost Katana Python SDK

This example demonstrates how to maintain a conversation
with context, similar to ChatGPT but with cost tracking
and automatic optimization.
"""

import cost_katana as ck
from cost_katana.exceptions import CostKatanaError


def main():
    print("💬 Cost Katana - Chat Session Example")
    print("=" * 50)

    # Configure with config file (recommended for production)
    try:
        ck.configure(config_file="config.json")
        print("✅ Loaded configuration from config.json")
    except FileNotFoundError:
        # Fallback to API key input
        api_key = input("Enter your Cost Katana API key: ").strip()
        ck.configure(api_key=api_key)
        print("✅ Configured with API key")

    # Create a model and start chat
    print("\n🤖 Starting chat with Gemini 2.0 Flash...")
    model = ck.GenerativeModel("gemini-2.0-flash")
    chat = model.start_chat()

    print(
        "\n💡 Type 'quit' to exit, 'cost' to see total cost, 'clear' to clear history"
    )
    print("🗨️  Chat started! Ask me anything...\n")

    total_cost = 0.0
    message_count = 0

    while True:
        try:
            # Get user input
            user_message = input("You: ").strip()

            if user_message.lower() in ["quit", "exit", "bye"]:
                break
            elif user_message.lower() == "cost":
                print(f"💰 Total conversation cost: ${total_cost:.4f}")
                print(f"📝 Messages exchanged: {message_count}")
                continue
            elif user_message.lower() == "clear":
                chat.clear_history()
                print("🧹 Chat history cleared!")
                total_cost = 0.0
                message_count = 0
                continue
            elif user_message.lower() == "help":
                print("Available commands:")
                print("  quit - Exit the chat")
                print("  cost - Show total cost")
                print("  clear - Clear chat history")
                print("  help - Show this help")
                continue

            if not user_message:
                continue

            # Send message and get response
            print("🤖 Assistant: ", end="", flush=True)
            response = chat.send_message(user_message)

            print(response.text)

            # Update stats
            total_cost += response.usage_metadata.cost
            message_count += 1

            # Show cost info (dim/quiet)
            cost_info = f"[${response.usage_metadata.cost:.4f}]"
            if response.usage_metadata.cache_hit:
                cost_info += " 💾"
            if response.usage_metadata.optimizations_applied:
                cost_info += " ⚡"

            print(f"\n{cost_info}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except CostKatanaError as e:
            print(f"\n❌ Error: {e}")
            print("💡 Continuing chat...\n")
            continue
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")
            break

    # Show final statistics
    print("\n📊 Chat Session Summary")
    print("-" * 30)
    print(f"💰 Total Cost: ${total_cost:.4f}")
    print(f"📝 Messages: {message_count}")
    print(f"💵 Cost per message: ${total_cost/max(message_count, 1):.4f}")

    # Get conversation history
    try:
        history = chat.get_history()
        print(f"💾 Messages in history: {len(history)}")
    except:
        print("💾 Could not retrieve server history")

    print("\n✨ Thanks for using Cost Katana!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        print("💡 Check your configuration and try again.")
