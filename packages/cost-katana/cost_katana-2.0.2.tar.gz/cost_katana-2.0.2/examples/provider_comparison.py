#!/usr/bin/env python3
"""
Provider Comparison Example - Cost Katana Python SDK

This example demonstrates how to easily compare different AI providers
for the same task, with automatic cost and performance tracking.
"""

import cost_katana as ck
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def test_single_model(model_name, prompt, test_name):
    """Test a single model and return results"""
    try:
        start_time = time.time()
        model = ck.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        end_time = time.time()

        return {
            "model": model_name,
            "test": test_name,
            "success": True,
            "response": response.text,
            "cost": response.usage_metadata.cost,
            "tokens": response.usage_metadata.total_tokens,
            "latency": response.usage_metadata.latency,
            "wall_time": end_time - start_time,
            "actual_model": response.usage_metadata.model,
            "cache_hit": response.usage_metadata.cache_hit,
            "optimizations": response.usage_metadata.optimizations_applied or [],
        }
    except Exception as e:
        return {
            "model": model_name,
            "test": test_name,
            "success": False,
            "error": str(e),
            "cost": 0,
            "tokens": 0,
            "latency": 0,
            "wall_time": 0,
        }


def run_comparison_test(models, prompt, test_name):
    """Run the same prompt across multiple models"""
    print(f"\n🧪 Test: {test_name}")
    print("=" * 60)
    print(f"Prompt: {prompt[:100]}...")
    print("\n📊 Results:")

    results = []

    # Run tests in parallel for faster execution
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_model = {
            executor.submit(test_single_model, model, prompt, test_name): model
            for model in models
        }

        for future in as_completed(future_to_model):
            result = future.result()
            results.append(result)

    # Sort by success first, then by cost
    results.sort(key=lambda x: (not x["success"], x["cost"]))

    # Display results
    for result in results:
        if result["success"]:
            print(f"\n✅ {result['model']}:")
            print(f"   💰 Cost: ${result['cost']:.4f}")
            print(f"   ⚡ Latency: {result['latency']:.2f}s")
            print(f"   🔢 Tokens: {result['tokens']}")
            print(f"   🤖 Actual Model: {result['actual_model']}")

            if result["cache_hit"]:
                print("   💾 Cache Hit: Yes")
            if result["optimizations"]:
                print(f"   ⚡ Optimizations: {', '.join(result['optimizations'])}")

            # Show first few lines of response
            response_lines = result["response"].split("\n")[:3]
            print(f"   📝 Response: {response_lines[0][:80]}...")
        else:
            print(f"\n❌ {result['model']}: {result['error']}")

    return results


def analyze_results(all_results):
    """Analyze results across all tests"""
    print("\n📈 Overall Analysis")
    print("=" * 60)

    # Group by model
    model_stats = {}
    for result in all_results:
        if not result["success"]:
            continue

        model = result["model"]
        if model not in model_stats:
            model_stats[model] = {
                "total_cost": 0,
                "total_tokens": 0,
                "total_latency": 0,
                "test_count": 0,
                "successes": 0,
                "cache_hits": 0,
            }

        stats = model_stats[model]
        stats["total_cost"] += result["cost"]
        stats["total_tokens"] += result["tokens"]
        stats["total_latency"] += result["latency"]
        stats["test_count"] += 1
        stats["successes"] += 1
        if result["cache_hit"]:
            stats["cache_hits"] += 1

    # Calculate averages and display
    print("\n🏆 Model Performance Summary:")

    for model, stats in model_stats.items():
        if stats["successes"] == 0:
            continue

        avg_cost = stats["total_cost"] / stats["successes"]
        avg_latency = stats["total_latency"] / stats["successes"]
        avg_tokens = stats["total_tokens"] / stats["successes"]
        cache_rate = stats["cache_hits"] / stats["successes"] * 100

        print(f"\n📊 {model}:")
        print(f"   💰 Avg Cost: ${avg_cost:.4f}")
        print(f"   ⚡ Avg Latency: {avg_latency:.2f}s")
        print(f"   🔢 Avg Tokens: {avg_tokens:.0f}")
        print(f"   💾 Cache Hit Rate: {cache_rate:.1f}%")
        print(f"   ✅ Success Rate: {stats['successes']}/{stats['test_count']}")

    # Find best performers
    successful_models = {k: v for k, v in model_stats.items() if v["successes"] > 0}

    if successful_models:
        # Best for cost
        cheapest = min(
            successful_models.items(),
            key=lambda x: x[1]["total_cost"] / x[1]["successes"],
        )
        print(
            f"\n💰 Most Cost-Effective: {cheapest[0]} (${cheapest[1]['total_cost'] / cheapest[1]['successes']:.4f} avg)"
        )

        # Best for speed
        fastest = min(
            successful_models.items(),
            key=lambda x: x[1]["total_latency"] / x[1]["successes"],
        )
        print(
            f"⚡ Fastest: {fastest[0]} ({fastest[1]['total_latency'] / fastest[1]['successes']:.2f}s avg)"
        )

        # Best cache performance
        best_cache = max(
            successful_models.items(),
            key=lambda x: x[1]["cache_hits"] / x[1]["successes"],
        )
        cache_pct = best_cache[1]["cache_hits"] / best_cache[1]["successes"] * 100
        print(f"💾 Best Cache Performance: {best_cache[0]} ({cache_pct:.1f}% hit rate)")


def main():
    print("🔄 Cost Katana Provider Comparison")
    print("=" * 50)

    # Configure Cost Katana
    try:
        ck.configure(config_file="config.json")
        print("✅ Loaded configuration from config.json")
    except FileNotFoundError:
        api_key = input("Enter your Cost Katana API key: ").strip()
        ck.configure(api_key=api_key)
        print("✅ Configured with API key")

    # Models to compare
    models_to_test = [
        "gemini-2.0-flash",
        "claude-3-sonnet",
        "claude-3-haiku",
        "gpt-4",
        "nova-pro",
    ]

    print(f"\n🤖 Testing {len(models_to_test)} models:")
    for model in models_to_test:
        print(f"   • {model}")

    # Test scenarios
    test_scenarios = [
        {
            "name": "Creative Writing",
            "prompt": "Write a short, engaging story about a robot learning to paint. Keep it under 200 words.",
        },
        {
            "name": "Code Generation",
            "prompt": "Write a Python function that finds the longest palindrome in a string. Include comments and error handling.",
        },
        {
            "name": "Analysis Task",
            "prompt": "Analyze the pros and cons of remote work for software developers. Provide 3 key points for each side.",
        },
        {
            "name": "Simple Q&A",
            "prompt": "What is the capital of France? Explain why it became the capital.",
        },
    ]

    print(f"\n🧪 Running {len(test_scenarios)} test scenarios...")

    all_results = []

    # Run all tests
    for scenario in test_scenarios:
        results = run_comparison_test(
            models_to_test, scenario["prompt"], scenario["name"]
        )
        all_results.extend(results)

        # Show cost for this test
        successful_results = [r for r in results if r["success"]]
        if successful_results:
            total_test_cost = sum(r["cost"] for r in successful_results)
            print(f"\n💳 Test cost: ${total_test_cost:.4f}")

    # Analyze all results
    analyze_results(all_results)

    # Final summary
    total_cost = sum(r["cost"] for r in all_results if r["success"])
    total_tests = len([r for r in all_results if r["success"]])

    print(f"\n🎯 Final Summary:")
    print(f"   💰 Total Cost: ${total_cost:.4f}")
    print(f"   🧪 Successful Tests: {total_tests}")
    print(f"   📊 Average Cost per Test: ${total_cost/max(total_tests, 1):.4f}")

    print(
        "\n✨ Comparison complete! Use these insights to choose the best model for your use case."
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Comparison interrupted. Goodbye!")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        print("💡 Make sure you have a valid API key and internet connection.")
