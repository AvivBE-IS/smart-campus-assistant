import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def test_gemini_3():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    try:
        # Note the exact name: gemini-3-flash-preview
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents="Confirming Gemini 3 is active and responding!"
        )
        print(f"✅ Connection Successful!")
        print(f"🤖 Gemini 3 says: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_gemini_3()