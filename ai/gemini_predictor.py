import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError

# Load backend/.env
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class AIConfigurationError(Exception):
    """Raised when Gemini API key is missing."""
    pass


class AIProviderError(Exception):
    """Raised when Gemini fails to return a valid prediction."""
    pass


ALLOWED_DISEASES = {
    "Mastitis",
    "Milk Fever",
    "Fungal Dermatitis",
    "Foot Rot",
    "Lumpy Skin Disease",
    "Respiratory Infection",
    "Brucellosis",
}

ALLOWED_SEVERITIES = {"Low", "Medium", "High"}


def _build_prompt(symptoms: str, animal: Any,
                  temperature=None, milk_reduction=None):

    animal_info = {
        "species": animal.species,
        "breed": animal.breed,
        "age": animal.age,
        "gender": animal.gender,
    }

    extra = []
    if temperature:
        extra.append(f"Temperature: {temperature}°C")
    if milk_reduction:
        extra.append(f"Milk reduction: {milk_reduction}%")

    return f"""
You are an expert livestock veterinary AI.

Analyze the case and return ONLY valid JSON.

Animal:
{json.dumps(animal_info)}

Symptoms:
{symptoms}

{' '.join(extra)}

Rules:
- Disease must be one of:
  Mastitis, Milk Fever, Fungal Dermatitis,
  Foot Rot, Lumpy Skin Disease,
  Respiratory Infection, Brucellosis
- Confidence: 0-100
- Severity: Low, Medium or High
- Recommendations: array of strings

Return exactly:

{{
  "disease":"Mastitis",
  "confidence":94.8,
  "severity":"High",
  "recommendations":[
    "Isolate the animal",
    "Clean the udder",
    "Contact a veterinarian within 24 hours"
  ]
}}
"""


def _parse_prediction(response):

    raw = (response.text or "").strip()

    try:
        data = json.loads(raw)

        disease = str(data["disease"]).strip()
        confidence = float(data["confidence"])
        severity = str(data["severity"]).title()
        recommendations = data["recommendations"]

    except Exception as e:
        raise AIProviderError(
            f"Gemini returned malformed JSON:\n{raw}"
        ) from e

    if disease not in ALLOWED_DISEASES:
        raise AIProviderError(f"Unsupported disease: {disease}")

    if severity not in ALLOWED_SEVERITIES:
        raise AIProviderError(f"Unsupported severity: {severity}")

    if not 0 <= confidence <= 100:
        raise AIProviderError("Invalid confidence score")

    return {
        "disease": disease,
        "confidence": round(confidence, 2),
        "severity": severity,
        "recommendations": recommendations,
    }


def predict_disease(
    symptoms,
    animal,
    temperature=None,
    milk_reduction=None,
    image=None,
):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise AIConfigurationError("Gemini API not configured")

    client = genai.Client(api_key=api_key)

    contents = [
        _build_prompt(symptoms, animal, temperature, milk_reduction)
    ]

    if image:
        contents.append(
            types.Part.from_bytes(
                data=image.read(),
                mime_type=image.mimetype or "image/jpeg",
            )
        )

    # Retry for temporary Gemini overload
    for attempt in range(3):

        try:
            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                ),
            )

            return _parse_prediction(response)

        except ServerError as e:

            # Retry only for temporary 503 errors
            if attempt < 2:
                wait = 2 ** attempt
                print(f"Gemini busy. Retrying in {wait}s...")
                time.sleep(wait)
                continue

            raise AIProviderError(
                "AI service is temporarily busy. Please try again in a few seconds."
            )

        except Exception as e:
            print("Gemini Error:", str(e))
            raise AIProviderError(str(e))