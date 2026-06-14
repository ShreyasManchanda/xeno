import json
import os
import re
import httpx
import logging

logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)
GEMINI_STREAM_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:streamGenerateContent"
)


def _fix_truncated_json(text: str) -> str:
    """Attempt to repair common JSON truncation issues."""
    if not text:
        return text
    
    text = text.strip()
    
    open_braces = text.count('{')
    close_braces = text.count('}')
    open_brackets = text.count('[')
    close_brackets = text.count(']')
    
    in_string = False
    escape_next = False
    for i, char in enumerate(text):
        if escape_next:
            escape_next = False
            continue
        if char == '\\' and in_string:
            escape_next = True
            continue
        if char == '"':
            in_string = not in_string
    
    if in_string:
        last_quote = text.rfind('"')
        if last_quote > 0:
            text = text[:last_quote]
            if not text.rstrip().endswith(','):
                text = text.rstrip() + '"'
            else:
                text = text.rstrip()[:-1] + '"'
    
    while open_braces > close_braces:
        text += '}'
        close_braces += 1
    while open_brackets > close_brackets:
        text += ']'
        close_brackets += 1
    
    text = re.sub(r',\s*([}\]])', r'\1', text)
    
    return text


def parse_json_response(text: str, retry_count: int = 0) -> dict:
    """Extract and parse a JSON object from Gemini output with robust error handling."""
    cleaned = (text or "").strip()
    if not cleaned:
        logger.warning("Empty response from Gemini")
        raise ValueError("Empty response from Gemini")

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        cleaned = cleaned[start : end + 1]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse failed (attempt {retry_count + 1}): {e}")
        logger.debug(f"Input preview: {cleaned[:500]}...")
        
        if retry_count < 2:
            fixed = _fix_truncated_json(cleaned)
            if fixed != cleaned:
                logger.info("Attempting to repair truncated JSON")
                try:
                    result = json.loads(fixed)
                    logger.info("JSON repair successful")
                    return result
                except json.JSONDecodeError:
                    pass
        
        return {
            "error": f"JSON parsing failed: {str(e)}",
            "raw_response": cleaned[:1000],
        }


def _build_payload(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> dict:
    config: dict = {
        "temperature": temperature,
        "maxOutputTokens": max_tokens,
    }
    if json_mode:
        config["responseMimeType"] = "application/json"

    return {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": config,
    }


async def _publish_stream_delta(session_id: str | None, agent: str | None, delta: str) -> None:
    if not session_id or not agent or not delta:
        return
    from services.sse_bus import publish

    await publish(
        session_id,
        {
            "type": "agent_stream",
            "agent": agent,
            "delta": delta,
        },
    )


async def _non_stream_generate(payload: dict, headers: dict) -> str:
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(GEMINI_URL, headers=headers, json=payload)
        response.raise_for_status()
        raw = response.json()
        return raw["candidates"][0]["content"]["parts"][0]["text"]


async def call_gemini(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 1500,
    json_mode: bool = True,
    session_id: str | None = None,
    agent: str | None = None,
    stream: bool = True,
) -> dict:
    """
    Call Gemini with system + user prompts. Returns parsed JSON when json_mode=True.
    When stream=True and session_id is set, publishes agent_stream SSE deltas.
    Implements robust retry logic for truncated JSON responses.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")

    payload = _build_payload(system_prompt, user_prompt, temperature, max_tokens, json_mode)
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    use_stream = bool(stream and session_id and agent)
    text = ""

    if use_stream:
        text = await _stream_generate(payload, headers, session_id, agent)
    else:
        text = await _non_stream_generate(payload, headers)

    if not json_mode:
        return {"text": text}

    result = parse_json_response(text, retry_count=0)
    
    if "error" in result and use_stream:
        logger.warning("Retry with non-streaming due to JSON error")
        text = await _non_stream_generate(payload, headers)
        result = parse_json_response(text, retry_count=1)
    
    if "error" in result and max_tokens < 4000:
        logger.warning(f"Retry with increased token limit (was {max_tokens})")
        payload_larger = _build_payload(system_prompt, user_prompt, temperature, min(max_tokens * 2, 8000), json_mode)
        text = await _non_stream_generate(payload_larger, headers)
        result = parse_json_response(text, retry_count=2)
    
    return result


async def _stream_generate(payload: dict, headers: dict, session_id: str, agent: str) -> str:
    accumulated: list[str] = []

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{GEMINI_STREAM_URL}?alt=sse",
            headers=headers,
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                raw_line = line[6:].strip()
                if not raw_line or raw_line == "[DONE]":
                    continue
                try:
                    chunk = json.loads(raw_line)
                except json.JSONDecodeError:
                    continue
                for candidate in chunk.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        delta = part.get("text", "")
                        if delta:
                            accumulated.append(delta)
                            await _publish_stream_delta(session_id, agent, delta)

    text = "".join(accumulated)
    if not text:
        raise ValueError("Empty streaming response from Gemini")
    return text
