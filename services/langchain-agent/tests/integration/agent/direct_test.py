#!/usr/bin/env python3
"""
Direct test script for the OpenAI API.

This script tests direct connectivity to the OpenAI API with the API key and model.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv("services/langchain-agent/.env")

# Set OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in environment")
    exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=api_key)
print(f"Using API key: {api_key[:12]}...")

# Test model
model = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
print(f"Using model: {model}")

def test_openai_chat():
    """Test OpenAI chat completion."""
    print("\n=== Testing OpenAI Chat Completion ===")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": "Hello, who are you?"}
            ],
            max_tokens=100
        )
        
        print("API Response Status: Success")
        
        # Extract and print the assistant's message
        assistant_message = response.choices[0].message.content.strip()
        print(f"Assistant's response: {assistant_message}")
        
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_openai_chat()
    if success:
        print("\nOpenAI API test completed successfully.")
    else:
        print("\nOpenAI API test failed.") 