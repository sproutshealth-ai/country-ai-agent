"""
Test script for the Country Information AI Agent
Run this to verify the agent is working correctly
"""
import os
from dotenv import load_dotenv
from agent import CountryInfoAgent
import sys

# Load environment variables
load_dotenv()


def test_agent():
    """Run a series of test questions through the agent"""

    print("=" * 70)
    print("Country Information AI Agent - Test Suite")
    print("=" * 70)
    print()

    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: No API key found!")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        print()
        print("Example:")
        print("  OPENAI_API_KEY=your-key-here")
        print("  MODEL_NAME=gpt-4o-mini")
        sys.exit(1)

    try:
        # Initialize agent
        print("Initializing agent...")
        agent = CountryInfoAgent()
        print("✅ Agent initialized successfully!")
        print()

        # Test questions
        test_questions = [
            {
                "question": "What is the population of Germany?",
                "expected_fields": ["population"]
            },
            {
                "question": "What currency does Japan use?",
                "expected_fields": ["currency"]
            },
            {
                "question": "What is the capital and population of Brazil?",
                "expected_fields": ["capital", "population"]
            },
            {
                "question": "Tell me about France",
                "expected_fields": ["general_info"]
            },
            {
                "question": "What is the capital of InvalidCountryXYZ123?",
                "expected_fields": ["capital"],
                "expect_error": True
            }
        ]

        passed = 0
        failed = 0

        for i, test in enumerate(test_questions, 1):
            print(f"Test {i}/{len(test_questions)}")
            print(f"Question: {test['question']}")
            print("-" * 70)

            try:
                result = agent.run(test['question'])

                # Check if error was expected
                if test.get("expect_error"):
                    if not result["api_success"]:
                        print("✅ PASS: Error handled correctly")
                        passed += 1
                    else:
                        print("❌ FAIL: Expected error but got success")
                        failed += 1
                else:
                    if result["api_success"]:
                        print("✅ PASS: Query successful")
                        passed += 1
                    else:
                        print("❌ FAIL: Query failed unexpectedly")
                        print(f"Error: {result.get('error', 'Unknown error')}")
                        failed += 1

                print(f"\nAnswer: {result['answer']}")
                print(f"Intent: {result['intent']}")

            except Exception as e:
                print(f"❌ FAIL: Exception occurred: {str(e)}")
                failed += 1

            print()
            print("=" * 70)
            print()

        # Summary
        print()
        print("=" * 70)
        print("Test Summary")
        print("=" * 70)
        print(f"Total Tests: {len(test_questions)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/len(test_questions)*100):.1f}%")
        print("=" * 70)

        if failed == 0:
            print("\n🎉 All tests passed! The agent is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: Failed to initialize agent")
        print(f"Error: {str(e)}")
        print()
        print("Common issues:")
        print("1. Invalid API key in .env file")
        print("2. Missing dependencies (run: pip install -r requirements.txt)")
        print("3. Network connectivity issues")
        sys.exit(1)


if __name__ == "__main__":
    test_agent()
