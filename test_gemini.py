from app.ai.gemini import generate_answer

if __name__ == "__main__":
    print("Testing Gemini API connection...")
    test_prompt = "Say 'Hello, the Gemini API connection is working!' in one sentence."
    response = generate_answer(test_prompt)
    print("\n--- Response ---")
    print(response)