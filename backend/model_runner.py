import time

from google import genai
from openai import OpenAI
from anthropic import Anthropic

from backend.config import GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY


gemini_client = genai.Client(api_key= GEMINI_API_KEY)

openai_client = OpenAI(api_key= OPENAI_API_KEY)

anthropic_client = Anthropic(api_key= ANTHROPIC_API_KEY)


def build_prompt(question: str):
    return f"""
        Answer the following question.

        Rules:
        - Respond with only the answer.
        - Do not use Markdown.
        - Do not use bullet points.
        - Do not explain your reasoning unless explicitly asked.

        Question:
        {question}
        """


def run_model(question: str, model_name: str):
    if model_name == "gemini-2.5-flash":
        return ask_gemini(question)

    if model_name == "openai":
        return ask_openai(question)

    if model_name == "claude":
        return ask_claude(question)

    raise ValueError("Unsupported model name.")


def ask_gemini(question: str):
    start_time = time.time()

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=build_prompt(question)
    )

    latency = round(time.time() - start_time, 2)

    answer = response.text.strip()

    input_tokens = estimate_tokens(question)
    output_tokens = estimate_tokens(answer)
    cost = estimate_cost("gemini", input_tokens, output_tokens)

    return {
        "answer": response.text.strip(),
        "latency": latency,
        "token_usage": input_tokens + output_tokens,
        "estimated_cost": cost,
        "model_display_name": "Gemini 2.5 Flash"
    }


def ask_openai(question: str):
    if not openai_client:
        raise ValueError("OPENAI_API_KEY is missing.")

    start_time = time.time()

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": build_prompt(question)
            }
        ]
    )

    latency = round(time.time() - start_time, 2)

    answer = response.choices[0].message.content.strip()

    input_tokens = estimate_tokens(question)
    output_tokens = estimate_tokens(answer)
    cost = estimate_cost("openai", input_tokens, output_tokens)

    return {
        "answer": answer,
        "latency": latency,
        "token_usage": input_tokens + output_tokens,
        "estimated_cost": cost,
        "model_display_name": "GPT-4o Mini"
    }


def ask_claude(question: str):
    if not anthropic_client:
        raise ValueError("ANTHROPIC_API_KEY is missing")

    start_time = time.time()

    response = anthropic_client.messages.create(
        model= "claude-haiku-4-5-20251001",
        max_tokens= 100,
        messages=[
            {
                "role": "user",
                "content": build_prompt(question)
            }
        ]
    )

    latency = round(time.time() - start_time, 2)

    answer = response.content[0].text.strip()

    input_tokens = estimate_tokens(question)
    output_tokens = estimate_tokens(answer)
    cost = estimate_cost("claude", input_tokens, output_tokens)

    return {
        "answer": answer,
        "latency": latency,
        "token_usage": input_tokens + output_tokens,
        "estimated_cost": cost,
        "model_display_name": "Claude Haiku 4.5"
    }

def estimate_tokens(text: str):
    return max(1, len(text.split()) * 2)


def estimate_cost(model_name: str, input_tokens: int, output_tokens: int):
    pricing = {
        "gemini": {
            "input": 0.30,
            "output": 2.50
        },
        "openai": {
            "input": 0.15,
            "output": 0.60
        },
        "claude": {
            "input": 1.00,
            "output": 5.00
        }
    }

    rates = pricing.get(model_name)

    if not rates:
        return 0.0

    cost = (
        (input_tokens / 1_000_000) * rates["input"]
        + (output_tokens / 1_000_000) * rates["output"]
    )

    return round(cost, 6)

