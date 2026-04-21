import os
import json
from datetime import datetime, timezone
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def generate_review_response(
    review_text: str,
    review_rating: int,
    business_name: str,
) -> str:
    """Generate an AI response draft for a Google Maps review.

    Returns the generated response text in Spanish.
    """
    if not client:
        raise AIServiceError("Servicio de IA no configurado. Falta la clave de API.")

    if review_rating >= 4:
        tone = "agradecido y personalizado"
    elif review_rating == 3:
        tone = "amable y constructivo"
    else:
        tone = "profesional, empático y orientado a resolver el problema"

    system_prompt = (
        "Eres un asistente que genera respuestas profesionales para reseñas de Google Maps "
        "en nombre de un negocio. Las respuestas deben ser en español, concisas (2-4 oraciones), "
        "y apropiadas para publicar directamente en Google Maps."
    )

    user_prompt = (
        f"Negocio: {business_name}\n"
        f"Calificación: {review_rating}/5 estrellas\n"
        f"Reseña: {review_text or '(Sin texto, solo calificación)'}\n\n"
        f"Genera una respuesta con tono {tone}. "
        "No uses emojis excesivos. Sé genuino y específico al contenido de la reseña."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=300,
        temperature=0.7,
    )

    return response.choices[0].message.content or ""


def generate_business_summary(
    reviews: list[dict],
    business_name: str,
) -> dict:
    """Generate an AI summary analyzing all reviews for a business.

    Returns a dict with: overall_sentiment, positive_themes, negative_themes,
    recommendations, review_count_analyzed, generated_at.
    """
    if not client:
        raise AIServiceError("Servicio de IA no configurado. Falta la clave de API.")

    # Build a condensed review digest
    review_texts = []
    for r in reviews[:100]:  # Cap at 100 reviews to fit context
        rating = r.get("review_rating", "?")
        text = r.get("review_text", "(sin texto)")
        review_texts.append(f"- {rating}⭐: {text}")

    reviews_digest = "\n".join(review_texts)

    system_prompt = (
        "Eres un analista de negocios que genera resúmenes ejecutivos basados en reseñas "
        "de Google Maps. Responde SIEMPRE en formato JSON válido en español."
    )

    user_prompt = (
        f"Negocio: {business_name}\n"
        f"Total de reseñas analizadas: {len(reviews)}\n\n"
        f"Reseñas:\n{reviews_digest}\n\n"
        "Genera un análisis en formato JSON con exactamente estas claves:\n"
        '{\n'
        '  "overall_sentiment": "positivo" | "neutro" | "negativo",\n'
        '  "positive_themes": ["tema1", "tema2", "tema3"],\n'
        '  "negative_themes": ["tema1", "tema2", "tema3"],\n'
        '  "recommendations": ["recomendación1", "recomendación2", "recomendación3"]\n'
        '}\n'
        "Identifica los 3 temas positivos y negativos más mencionados. "
        "Las recomendaciones deben ser accionables y específicas."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=500,
        temperature=0.5,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    result = json.loads(content)

    result["review_count_analyzed"] = len(reviews)
    result["generated_at"] = datetime.now(timezone.utc).isoformat()

    return result


class AIServiceError(Exception):
    pass
