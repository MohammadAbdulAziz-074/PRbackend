import json
import os
from typing import Any, Protocol
from urllib import request


class AIConfigurationError(Exception):
    """Raised when the AI provider cannot be configured."""


class AIProviderError(Exception):
    """Raised when the AI provider returns an unusable response."""


class AIProvider(Protocol):
    def predict(self, symptoms: str, animal: Any, temperature: Any = None,
                image: Any = None) -> dict:
        """Return a disease prediction and optional provider confidence."""


class OpenAICompatibleProvider:
    """Small provider adapter kept separate from the route and domain rules."""

    endpoint = "https://api.openai.com/v1/chat/completions"

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def predict(self, symptoms: str, animal: Any, temperature: Any = None,
                image: Any = None) -> dict:
        animal_details = {
            "species": animal.species,
            "breed": animal.breed,
            "age": animal.age,
            "gender": animal.gender,
        }
        prompt = (
            "Assess the animal symptoms as a veterinary triage assistant. "
            "Return JSON only with disease and confidence (0-100). "
            f"Animal: {json.dumps(animal_details)}. Symptoms: {symptoms}."
        )
        if temperature is not None:
            prompt += f" Temperature: {temperature}."
        if image is not None:
            prompt += " An animal image was provided and may be considered."

        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }
        http_request = request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=30) as response:
                provider_response = json.load(response)
            content = provider_response["choices"][0]["message"]["content"]
            prediction = json.loads(content)
            disease = str(prediction.get("disease") or "Unknown condition").strip()
            confidence = float(prediction.get("confidence", 75))
        except (OSError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise AIProviderError("AI provider request failed") from error

        return {"disease": disease, "confidence": max(0.0, min(100.0, confidence))}


def predict_disease(symptoms: str, animal: Any, temperature: Any = None,
                    image: Any = None, provider: AIProvider | None = None) -> dict:
    """Predict disease through the configured provider."""
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        raise AIConfigurationError("AI API key not configured")

    selected_provider = provider or OpenAICompatibleProvider(
        api_key=api_key,
        model=os.getenv("AI_MODEL") or "gpt-4o-mini",
    )
    return selected_provider.predict(symptoms, animal, temperature, image)