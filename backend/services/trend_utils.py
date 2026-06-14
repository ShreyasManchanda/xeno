"""Normalize Tavily / LLM trend text into clean UI bullet points."""
import re

_VALID_AGE_GROUPS = {"18-25", "26-35", "36-45", "45+"}
_AGE_GROUP_ALIASES = {
    "26-42": "26-35",
    "26-45": "26-35",
    "27-35": "26-35",
    "25-35": "26-35",
    "35-45": "36-45",
    "40+": "45+",
    "46+": "45+",
}

_SEASON_DEFAULTS: dict[str, list[str]] = {
    "summer": [
        "Breathable cotton kurtas and linen sets are leading Indian summer wear.",
        "Indo-western co-ord sets and light fusion silhouettes are gaining traction.",
        "Pastel and earthy tones are popular for everyday ethnic summer dressing.",
    ],
    "winter": [
        "Layered kurta sets and warm festive edits are trending for the season.",
        "Velvet and embroidered ethnic pieces are strong for winter occasions.",
        "Rich jewel tones and classic saree drapes remain in demand.",
    ],
    "festive": [
        "Pre-draped sarees and ready-to-wear lehengas are driving festive demand.",
        "Statement ethnic sets with modern cuts are popular for celebrations.",
        "Occasion-ready kurta sets in bold festive palettes are trending.",
    ],
}


def _strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .-*#|/")


def _first_sentence(text: str, max_len: int = 140) -> str:
    text = _strip_markdown(text)
    if not text:
        return ""

    # Drop SEO title noise before the real insight.
    if ": " in text[:80]:
        _, tail = text.split(": ", 1)
        if len(tail) > 30:
            text = tail

    match = re.search(r"^(.+?[.!?])(?:\s|$)", text)
    sentence = match.group(1) if match else text
    sentence = sentence.strip(" .")

    if len(sentence) > max_len:
        cut = sentence[: max_len - 1].rsplit(" ", 1)[0]
        sentence = f"{cut}…" if cut else sentence[: max_len - 1] + "…"

    if sentence and sentence[0].islower():
        sentence = sentence[0].upper() + sentence[1:]

    return sentence


def tavily_result_to_snippet(result: dict, max_len: int = 220) -> str:
    """Build a clean snippet from a Tavily search result for the LLM prompt."""
    title = _strip_markdown(result.get("title") or "")
    content = _strip_markdown(result.get("content") or "")

    if title and content:
        body = _first_sentence(content, max_len=max_len - len(title) - 2)
        snippet = f"{title}: {body}" if body else title
    else:
        snippet = title or _first_sentence(content, max_len=max_len)

    return snippet[:max_len].strip()


def normalize_trend_highlight(raw: str, max_len: int = 140) -> str:
    """Turn raw Tavily/LLM text into a single clean bullet."""
    cleaned = _first_sentence(raw, max_len=max_len)
    if len(cleaned) < 12:
        return ""
    if cleaned.count("/") > 4 or cleaned.count("|") > 2:
        return ""
    return cleaned


def normalize_trend_highlights(
    raw_items: list[str],
    season: str = "summer",
    limit: int = 3,
) -> list[str]:
    """Return 2–3 consistent, markdown-free trend bullets."""
    highlights: list[str] = []

    for item in raw_items or []:
        if isinstance(item, dict):
            item = item.get("text") or item.get("highlight") or str(item)
        if not isinstance(item, str):
            continue
        cleaned = normalize_trend_highlight(item)
        if cleaned and cleaned not in highlights:
            highlights.append(cleaned)
        if len(highlights) >= limit:
            break

    if len(highlights) < limit:
        for default in _SEASON_DEFAULTS.get(season, _SEASON_DEFAULTS["summer"]):
            if default not in highlights:
                highlights.append(default)
            if len(highlights) >= limit:
                break

    return highlights[:limit]


def normalize_variant_targets(variants: list[dict]) -> list[dict]:
    """Ensure variant age_group values match DB enums."""
    normalized: list[dict] = []
    for variant in variants or []:
        copy = dict(variant)
        targets = dict(copy.get("targets") or {})
        age = targets.get("age_group")
        if age:
            age = str(age).strip()
            age = _AGE_GROUP_ALIASES.get(age, age)
            if age not in _VALID_AGE_GROUPS:
                age = "26-35"
            targets["age_group"] = age
        copy["targets"] = targets
        normalized.append(copy)
    return normalized
