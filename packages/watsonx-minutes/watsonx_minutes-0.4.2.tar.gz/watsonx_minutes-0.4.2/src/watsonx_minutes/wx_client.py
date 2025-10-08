from __future__ import annotations
import os
from typing import Optional, Tuple, Any

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.schema import (
    TextGenParameters,
    TextGenDecodingMethod,
)

from .prompt import build_prompt

DEFAULT_MODEL_ID = "meta-llama/llama-3-3-70b-instruct"

def _get_creds(api_key: Optional[str], url: Optional[str], project_id: Optional[str]) -> Tuple[str, str, str]:
    resolved_api_key = api_key or os.getenv("WATSONX_APIKEY") or os.getenv("WATSONX_API_KEY")
    resolved_url = url or os.getenv("WATSONX_URL")
    resolved_project_id = project_id or os.getenv("WATSONX_PROJECT_ID")

    missing = [name for name, val in (
        ("api_key", resolved_api_key),
        ("url", resolved_url),
        ("project_id", resolved_project_id),
    ) if not val]

    if missing:
        raise ValueError(f"Missing required credentials: {', '.join(missing)}. Provide flags or set env vars WATSONX_APIKEY, WATSONX_URL, WATSONX_PROJECT_ID.")

    return resolved_api_key, resolved_url, resolved_project_id

def _extract_text(response: Any) -> str:
    if response is None:
        return ""
    if isinstance(response, str):
        return response
    if isinstance(response, dict):
        if "generated_text" in response and isinstance(response["generated_text"], str):
            return response["generated_text"]
        results = response.get("results")
        if isinstance(results, list) and results:
            first = results[0]
            if isinstance(first, dict) and isinstance(first.get("generated_text"), str):
                return first["generated_text"]
        choices = response.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                if isinstance(first.get("text"), str):
                    return first["text"]
                msg = first.get("message")
                if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                    return msg["content"]
        for key in ("text", "output_text", "content"):
            val = response.get(key)
            if isinstance(val, str):
                return val
    try:
        return str(response)
    except Exception:
        return ""

def generate_todos_from_text(
    minutes_text: str,
    *,
    language: str,
    api_key: Optional[str] = None,
    url: Optional[str] = None,
    project_id: Optional[str] = None,
    model_id: str = DEFAULT_MODEL_ID,
    max_new_tokens: int = 700,
    temperature: float = 0.2,
    retry_on_empty: bool = True,
) -> str:
    api_key, url, project_id = _get_creds(api_key, url, project_id)

    def _make_model(temp: float):
        params = TextGenParameters(
            decoding_method=TextGenDecodingMethod.SAMPLE,
            temperature=temp,
            top_p=0.15,
            repetition_penalty=1.05,
            max_new_tokens=max_new_tokens,
        )
        return ModelInference(
            model_id=model_id,
            params=params,
            credentials=Credentials(api_key=api_key, url=url),
            project_id=project_id,
        )

    prompt = build_prompt(minutes_text, language)

    model = _make_model(temperature)
    response = model.generate_text(prompt=prompt)
    text = _extract_text(response).strip()
    if not text and retry_on_empty:
        model = _make_model(min(0.6, max(0.3, temperature + 0.2)))
        response = model.generate_text(prompt=prompt)
        text = _extract_text(response).strip()
    return text
