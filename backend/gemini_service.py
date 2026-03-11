import os
from google import genai
from dotenv import load_dotenv

# Load environment variables from a .env file in the project root
load_dotenv()

# --- System Analysis & Project Management Integration ---
# This service is a core component of the System Development phase, implementing the AI logic defined
# in the System Analysis stage. It directly addresses the backlog item "Implement AI Query Processing."
# By fetching the API key from an environment variable, it adheres to Infrastructure best practices for
# secret management, making it secure and ready for deployment.

def get_gemini_response(user_query: str, db_context: list[dict]) -> str:
    """
    Generates a response from the Gemini model based on a user query and database context.

    Args:
        user_query: The natural language query from the user.
        db_context: A list of dictionaries representing data retrieved from the database.

    Returns:
        A string containing the AI-generated response.
    """
    try:
        # 1. Retrieve API Key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set or empty.")
        
        genai.configure(api_key=api_key)

        # 2. Define the system instruction for the model
        system_instruction = (
            "You are a professional university data analyst. "
            "Your sole purpose is to answer questions based *only* on the database context provided below. "
            "Do not invent information, do not use external knowledge, and do not offer opinions. "
            "If the answer cannot be found in the provided context, you must state that the information is not available in the database."
        )

        model = genai.GenerativeModel(
            model_name='gemini-3-flash-preview',
            system_instruction=system_instruction
        )

        # 4. Format the database context and user query into a single prompt
        prompt = f"""
        Database Context:
        ```json
        {db_context}
        ```

        User Query:
        "{user_query}"
        """

        # 5. Generate and return the response
        try:
            response = model.generate_content(prompt)
            raw_text = response.text
        except Exception as e:
            # Fallback to stable model if primary fails
            print(f"Warning: Primary model 'gemini-3-flash-preview' failed with error: {e}. Falling back to 'gemini-2.5-flash'.")
            fallback_model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                system_instruction=system_instruction
            )
            response = fallback_model.generate_content(prompt)
            raw_text = response.text

        # Clean the text by removing markdown backticks if present
        cleaned_text = raw_text.strip('`').strip()

        return cleaned_text

    except Exception as e:
        # In a production environment, you would log this error to a monitoring service.
        print(f"[GEMINI_SERVICE_ERROR] An error occurred: {e}")
        # Return a user-friendly error message
        return "I'm sorry, but I encountered an internal error while processing your request. Please try again later."
