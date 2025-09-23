#!/usr/bin/env python3
"""
Script to verify Gemini API quota and billing status
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def verify_gemini_api():
    """Test Gemini API and check quota status"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return

    print(f"🔑 Using API key: {api_key[:10]}...{api_key[-4:]}")

    try:
        # Configure the API
        genai.configure(api_key=api_key)

        # List available models to verify API access
        print("\n📋 Available models:")
        for model in genai.list_models():
            if 'gemini' in model.name.lower():
                print(f"  - {model.name}")

        # Try to use gemini-2.5-flash
        print("\n🧪 Testing gemini-2.5-flash model...")
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Simple test prompt
        response = model.generate_content("Say 'API working!' in 3 words")
        print(f"✅ Response: {response.text}")

        print("\n✨ API is working with gemini-2.5-flash!")
        print("\nNote: If you're still hitting quotas, you may need to:")
        print("1. Wait 24 hours for quota reset (free tier resets daily)")
        print("2. Enable billing on the correct Google Cloud project")
        print("3. Check if your API key is from the right project")

    except Exception as e:
        print(f"\n❌ Error: {e}")

        error_str = str(e)
        if "quota" in error_str.lower():
            print("\n⚠️ QUOTA ERROR DETECTED!")
            print("This means your API key is working but hitting limits.")
            print("\nTo fix this:")
            print("1. Go to https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas")
            print("2. Check your project's quota limits")
            print("3. Make sure billing is enabled for THIS project")
            print("4. Consider creating a new project with billing if needed")
        elif "not found" in error_str.lower():
            print("\n⚠️ MODEL NOT FOUND!")
            print("Try using 'gemini-1.5-flash' instead of 'gemini-2.5-flash'")
        else:
            print("\nCheck:")
            print("1. Your API key is valid")
            print("2. The Generative Language API is enabled in your project")
            print("3. Your billing account is properly linked")

if __name__ == "__main__":
    verify_gemini_api()