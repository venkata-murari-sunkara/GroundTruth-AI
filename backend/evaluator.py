from google import genai

from backend.config import GEMINI_API_KEY

client = genai.Client(api_key= GEMINI_API_KEY)


def normalize_text(text: str) -> str:
    return text.strip().lower()


def calculate_exact_match(expected_answer: str, generated_answer: str) -> int:
    expected = normalize_text(expected_answer)
    generated = normalize_text(generated_answer)

    if expected == generated:
        return 1

    return 0


def calculate_semantic_score(expected_answer: str, generated_answer: str) -> float:
    prompt = f"""
        You are an LLM evaluation judge.

        Compare the expected answer and generated answer.

        Return only one decimal score between 0 and 1.
        Do not include explanations, labels, or Markdown.

        Scoring:
        1.0 = same meaning and fully correct
        0.7 = mostly correct
        0.4 = partially correct
        0.0 = incorrect

        Expected Answer:
        {expected_answer}

        Generated Answer:
        {generated_answer}
        """

    try:
        response = client.models.generate_content(
            model= "gemini-2.5-flash",
            contents= prompt
        )

        score = float(response.text.strip())

        score = max(0.0, min(score, 1.0))

        return round(score, 2)

    except Exception:
        if calculate_exact_match(expected_answer, generated_answer) == 1:
            return 1.0

        return 0.0