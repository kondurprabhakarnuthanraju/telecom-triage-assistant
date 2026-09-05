import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Try both variable names
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

print(f"API Key found: {bool(api_key)}")

if api_key:
    print(f"Key starts with: {api_key[:10]}...")
    os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure(api_key=api_key)
    print("✅ Configured Gemini")
    
    # Use the correct model
    try:
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=["Hello world"],
            task_type="retrieval_document"
        )
        print(f"✅ Embedding successful! Vector length: {len(result['embedding'][0])}")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ No API key found in .env!")
