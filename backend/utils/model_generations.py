import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_llm_response(prompt: str, model: str = "gpt-4o", max_tokens: int = 150):
    """Generate a response from the OpenAI language model."""
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except openai.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        return f"The server could not be reached: {e}"
    except openai.RateLimitError as e:
        print("A 429 status code was received; we should back off exponentially.")
        print(e)
        return f"A 429 status code was received: {e}"
    except openai.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e)
        return f"Another non-200-range status code was received: {e}"