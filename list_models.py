import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = os.getenv("GOOGLE_API_KEY")

print(f"API Key found: {bool(api_key)}")

if api_key:
    genai.configure(api_key=api_key)
    print("✅ Configured Gemini")
    
    # List available models
    print("\n📋 Available models:")
    for m in genai.list_models():
        if 'embed' in m.name:
            print(f"  - {m.name}")
    
    print("\n✅ Ready to use!")
