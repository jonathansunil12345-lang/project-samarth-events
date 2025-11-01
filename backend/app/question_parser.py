import re
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class ParsedQuestion:
    intent: str
    params: Dict


# Match state names (up to 6 words) - more restrictive but case insensitive
STATE_NAME_PATTERN = r"[A-Za-z]+(?:\s+[A-Za-z]+){0,5}"

KNOWN_STATE_NAMES = {
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Delhi",
    "Jammu And Kashmir",
    "Ladakh",
    "Puducherry",
    "Chandigarh",
    "Andaman And Nicobar Islands",
    "Dadra And Nagar Haveli And Daman And Diu",
    "Lakshadweep",
}
STATE_PAIR_REGEX = re.compile(
    rf"in\s+({STATE_NAME_PATTERN})\s+(?:and|vs\.?|versus|&)\s+({STATE_NAME_PATTERN})\b",
    re.IGNORECASE
)
STATE_BETWEEN_REGEX = re.compile(
    rf"between\s+({STATE_NAME_PATTERN})\s+(?:and|vs\.?|versus|&)\s+({STATE_NAME_PATTERN})\b",
    re.IGNORECASE
)
STATE_FOR_REGEX = re.compile(
    rf"for\s+({STATE_NAME_PATTERN})\s+(?:and|vs\.?|versus|&)\s+({STATE_NAME_PATTERN})\b",
    re.IGNORECASE
)
# For "compare X and Y" or "compare rainfall in X and Y"
COMPARE_STATES_REGEX = re.compile(
    rf"compare\s+(?:.*?\s+(?:in|for)\s+)?({STATE_NAME_PATTERN})\s+(?:and|vs\.?|versus|&)\s+({STATE_NAME_PATTERN})\b",
    re.IGNORECASE
)
# For "in State1 compare to State2" pattern (e.g., "in Kerala compare to Punjab")
COMPARE_TO_REGEX = re.compile(
    rf"in\s+({STATE_NAME_PATTERN})\s+compare\s+to\s+({STATE_NAME_PATTERN})\b",
    re.IGNORECASE
)


def _extract_years(text: str) -> Optional[int]:
    # Support multiple phrasings for year ranges
    patterns = [
        r"(?:last|past|previous|recent)\s+(\d+)\s+years?",
        r"over\s+(?:the\s+)?(?:last|past|previous)?\s*(\d+)\s+years?",
        r"during\s+(?:the\s+)?(?:last|past|previous)?\s*(\d+)\s+years?",
        r"for\s+(?:the\s+)?(?:last|past|previous)?\s*(\d+)\s+years?",
        r"in\s+(?:the\s+)?(?:last|past|previous)?\s*(\d+)\s+years?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def _extract_top_m(text: str) -> int:
    # Support multiple phrasings for top N
    patterns = [
        r"(?:top|first|best|leading|main)\s+(\d+)",
        r"(\d+)\s+(?:most|top|best|leading|main)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return 3


def _clean_token(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return re.sub(r"\s+", " ", value.strip())


def _normalize_state_name(state: Optional[str]) -> Optional[str]:
    """Normalize state name to title case for consistency."""
    if not state:
        return None
    # Handle special cases like "Tamil Nadu"
    words = state.split()
    return " ".join(word.capitalize() for word in words)


def _sanitize_state_candidate(state: Optional[str]) -> Optional[str]:
    """Normalize and validate a potential state name."""
    normalized = _normalize_state_name(_clean_token(state))
    if not normalized:
        return None
    tokens = normalized.split()
    # Trim leading/trailing filler tokens
    while tokens and tokens[0].lower() in STATE_EXCLUDE_TOKENS:
        tokens.pop(0)
    while tokens and tokens[-1].lower() in STATE_EXCLUDE_TOKENS:
        tokens.pop()
    if not tokens:
        return None
    cleaned = " ".join(tokens)
    lowered_tokens = [t.lower() for t in tokens]
    if any(token in STATE_EXCLUDE_TOKENS for token in lowered_tokens):
        return None
    if cleaned not in KNOWN_STATE_NAMES:
        return None
    return cleaned


def _sanitize_crop_candidate(value: Optional[str]) -> Optional[str]:
    """Clean crop strings and drop fillers."""
    candidate = _clean_token(value)
    if not candidate:
        return None
    tokens = candidate.split()
    # Remove obvious filler tokens
    tokens = [tok for tok in tokens if tok.lower() not in CROP_EXCLUDE_TOKENS]
    if not tokens:
        return None
    cleaned = " ".join(tok.title() for tok in tokens)
    return cleaned


def _extract_state_pair(text: str) -> tuple[Optional[str], Optional[str]]:
    # Try "in State1 compare to State2" pattern first (e.g., "in Kerala compare to Punjab")
    compare_to = COMPARE_TO_REGEX.search(text)
    if compare_to:
        return _sanitize_state_candidate(compare_to.group(1)), _sanitize_state_candidate(compare_to.group(2))

    # Try "for State1 and State2" pattern (e.g., "for Kerala vs Punjab")
    state_for = STATE_FOR_REGEX.search(text)
    if state_for:
        return _sanitize_state_candidate(state_for.group(1)), _sanitize_state_candidate(state_for.group(2))
    
    # Try direct "in State1 and State2" pattern
    direct = STATE_PAIR_REGEX.search(text)
    if direct:
        return _sanitize_state_candidate(direct.group(1)), _sanitize_state_candidate(direct.group(2))

    # Try "between State1 and State2" pattern
    between = STATE_BETWEEN_REGEX.search(text)
    if between:
        return _sanitize_state_candidate(between.group(1)), _sanitize_state_candidate(between.group(2))

    # Try "compare State1 and State2" pattern
    compare = COMPARE_STATES_REGEX.search(text)
    if compare:
        return _sanitize_state_candidate(compare.group(1)), _sanitize_state_candidate(compare.group(2))

    # Fallback: look for placeholder patterns
    placeholders = re.findall(r"state[_\s]?([A-Za-z]+)", text, re.IGNORECASE)
    if len(placeholders) >= 2:
        return _sanitize_state_candidate(placeholders[0]), _sanitize_state_candidate(placeholders[1])

    return None, None


def _extract_region(text: str) -> Optional[str]:
    # Try "in State" pattern (more specific, stops at keywords)
    match = re.search(r"in\s+([A-Za-z\s]+?)(?:\s+(?:over|during|across|based|for|with)|,|\.|\?|$)", text, re.IGNORECASE)
    if match:
        state = _normalize_state_name(_clean_token(match.group(1)))
        # Exclude common non-state words
        if state and state.lower() not in ["the", "last", "past", "recent", "years"]:
            return state
    match = re.search(r"region[_\s]?([A-Za-z]+)", text, re.IGNORECASE)
    if match:
        return _normalize_state_name(_clean_token(match.group(1)))
    return None


def _extract_crop(text: str) -> Optional[str]:
    # Try "for Crop in State" pattern (e.g., "for Soybean in Karnataka")
    match = re.search(r"for\s+([A-Za-z\s]+?)\s+in\s+", text, re.IGNORECASE)
    if match:
        candidate = _sanitize_crop_candidate(match.group(1))
        if candidate:
            return candidate
    # Try "production trend of Crop" pattern
    match = re.search(r"production trend of\s+([A-Za-z\s]+?)\s+in", text, re.IGNORECASE)
    if match:
        candidate = _sanitize_crop_candidate(match.group(1))
        if candidate:
            return candidate
    # Try "production of Crop" pattern
    match = re.search(r"production of\s+([A-Za-z\s]+?)(?:\s+in|\s+over|,|\.|\?|$)", text, re.IGNORECASE)
    if match:
        candidate = _sanitize_crop_candidate(match.group(1))
        if candidate:
            return candidate
    # Try "Crop in State" pattern for district extremes (e.g., "Pearl Millet in Maharashtra")
    match = re.search(r"([A-Za-z\s]+?)\s+in\s+([A-Za-z\s]+?)(?:\s+and|\s+in|\s+,|\s+\.|\s+\?|$)", text, re.IGNORECASE)
    if match:
        potential_crop = _clean_token(match.group(1))
        # Check if it's a known crop name (multi-word like "Pearl Millet", "Tamil Nadu")
        if potential_crop and len(potential_crop.split()) <= 3:
            # If the next part is a state name pattern, this is likely the crop
            next_part = match.group(2).strip()
            if any(state_word in next_part.lower() for state_word in ["maharashtra", "tamil", "nadu", "kerala", "karnataka", "punjab"]):
                candidate = _sanitize_crop_candidate(potential_crop)
                if candidate:
                    return candidate
    # Try "crop_type" pattern
    match = re.search(r"crop(?:_type)?[_\s]?([A-Za-z]+)", text, re.IGNORECASE)
    if match:
        candidate = _sanitize_crop_candidate(match.group(1))
        if candidate and len(candidate) > 1:
            return candidate
    return None


def _extract_crop_pair(text: str) -> list[str]:
    crops = re.findall(r"crop[_\s]?type[_\s]?([A-Za-z]+)", text, re.IGNORECASE)
    if crops:
        sanitized = [_sanitize_crop_candidate(c) for c in crops]
        return [c for c in sanitized if c]
    promote_match = re.search(
        r"promote\s+([A-Za-z\s]+?)\s+over\s+([A-Za-z\s]+?)(?:\s+in|\s+across|\.|$)",
        text,
        re.IGNORECASE,
    )
    if promote_match:
        candidates = [
            _sanitize_crop_candidate(promote_match.group(1)),
            _sanitize_crop_candidate(promote_match.group(2)),
        ]
        return [c for c in candidates if c]
    return []


def parse_question(question: str) -> ParsedQuestion:
    text = question.strip()
    lowered = text.lower()

    if "rainfall" in lowered and ("top" in lowered or "list" in lowered) and "crop" in lowered:
        state_a, state_b = _extract_state_pair(text)
        crop_filter = None
        # Try "top X and Y crops" pattern (e.g., "top Wheat and Maize crops")
        crop_list_match = re.search(r"top\s+([A-Za-z\s]+?)\s+and\s+([A-Za-z\s]+?)\s+crops?", text, re.IGNORECASE)
        if crop_list_match:
            # For multiple crops, use the first one as filter
            crop_filter = _sanitize_crop_candidate(crop_list_match.group(1))
        else:
            # Try "X and Y crops" pattern (e.g., "Wheat and Maize crops by district")
            crop_and_match = re.search(r"([A-Za-z\s]+?)\s+and\s+([A-Za-z\s]+?)\s+crops?", text, re.IGNORECASE)
            if crop_and_match:
                crop_filter = _sanitize_crop_candidate(crop_and_match.group(1))
            else:
                # Try "crops of X" pattern
                crop_phrase = re.search(r"crops of ([A-Za-z\s]+?)(?:\(|for|in|,|\.|$)", text, re.IGNORECASE)
                if crop_phrase:
                    crop_filter = _sanitize_crop_candidate(crop_phrase.group(1))
                else:
                    # Try to extract single crop or crop mentioned before "crops"
                    crop_before = re.search(r"([A-Za-z\s]+?)\s+crops?\s+by", text, re.IGNORECASE)
                    if crop_before:
                        crop_filter = _sanitize_crop_candidate(crop_before.group(1))
                    else:
                        crop_filter = _extract_crop(text)
        params = {
            "state_a": state_a,
            "state_b": state_b,
            "years": _extract_years(lowered),
            "top_m": _extract_top_m(lowered),
            "crop_filter": crop_filter,
        }
        return ParsedQuestion(intent="compare_rainfall_and_crops", params=params)

    # Check for district extremes with various keywords
    has_high = any(word in lowered for word in ["highest", "max", "maximum", "peak", "best", "top"])
    has_low = any(word in lowered for word in ["lowest", "min", "minimum", "worst", "bottom"])

    if "district" in lowered and (has_high or has_low):
        state_a, state_b = _extract_state_pair(text)
        
        # Try to extract states from "for Crop in State1 and State2" pattern
        if not state_a or not state_b:
            state_in_pattern = re.search(r"in\s+([A-Za-z\s]+?)\s+and\s+([A-Za-z\s]+?)(?:\s+in|\s+,|\s+\.|\s+\?|$)", text, re.IGNORECASE)
            if state_in_pattern:
                if not state_a:
                    state_a = _sanitize_state_candidate(state_in_pattern.group(1))
                if not state_b:
                    state_b = _sanitize_state_candidate(state_in_pattern.group(2))

        # Fallback: extract states inline
        if not state_a or not state_b:
            inline_states = [
                _sanitize_state_candidate(s)
                for s in re.findall(
                    r"\bin\s+([A-Za-z\s]+?)(?=(?:\s+(?:and|with|having|showing|that|had|for)|\s*,|\s*\?|\.|$))",
                    text,
                    re.IGNORECASE,
                )
                if _clean_token(s)
            ]
            inline_states = [
                s
                for s in inline_states
                if s
            ]
            if not state_a and inline_states:
                state_a = inline_states[0]
            if (not state_b) and len(inline_states) > 1:
                state_b = inline_states[1]
        
        # Try "for Crop in State" pattern
        crop = None
        for_crop_match = re.search(r"for\s+([A-Za-z\s]+?)\s+in\s+([A-Za-z\s]+?)(?:\s+and|\s+,|\s+\.|\s+\?|$)", text, re.IGNORECASE)
        if for_crop_match:
            crop = _sanitize_crop_candidate(for_crop_match.group(1))
        else:
            crop = _extract_crop(text)
        if not crop:
            crop_phrase = re.search(
                r"(?:production of|for)\s+([A-Za-z\s]+?)\s+in", text, re.IGNORECASE
            )
            if crop_phrase:
                crop = _sanitize_crop_candidate(crop_phrase.group(1))
        year_match = re.search(r"most recent year|(\d{4})", lowered)
        year = None
        if year_match and year_match.group(1):
            year = int(year_match.group(1))
        params = {
            "state_a": state_a,
            "state_b": state_b,
            "crop": crop,
            "year": year,
        }
        return ParsedQuestion(intent="district_extremes", params=params)

    # Production trend - catch "trend" or "show" with crop and region
    if "trend" in lowered or "show" in lowered:
        region = _extract_region(text)
        crop = _extract_crop(text)
        # If we have both region and crop, it's likely a trend query
        if region and crop:
            params = {
                "region": region,
                "crop": crop.title() if crop else None,
                "years": _extract_years(lowered),
            }
            return ParsedQuestion(intent="production_trend_with_climate", params=params)

    # Policy arguments - catch "policy", "scheme", or "promote"
    if "policy" in lowered or "scheme" in lowered or "promote" in lowered:
        crops = [c for c in _extract_crop_pair(text) if c]
        region = _extract_region(text)
        params = {
            "region": region,
            "crop_a": crops[0] if crops else None,
            "crop_b": crops[1] if len(crops) > 1 else None,
            "years": _extract_years(lowered),
        }
        return ParsedQuestion(intent="policy_arguments", params=params)

    # Fallback heuristics for looser phrasing
    state_a, state_b = _extract_state_pair(text)
    crop = _extract_crop(text)

    if "rainfall" in lowered and state_a and state_b:
        params = {
            "state_a": state_a,
            "state_b": state_b,
            "years": _extract_years(lowered),
            "top_m": _extract_top_m(lowered),
            "crop_filter": crop,
        }
        return ParsedQuestion(intent="compare_rainfall_and_crops", params=params)

    if "district" in lowered and state_a and state_b and crop:
        params = {
            "state_a": state_a,
            "state_b": state_b,
            "crop": crop,
            "year": None,
        }
        return ParsedQuestion(intent="district_extremes", params=params)

    if "trend" in lowered and (crop or "production" in lowered):
        region = _extract_region(text)
        params = {
            "region": region,
            "crop": crop.title() if crop else None,
            "years": _extract_years(lowered),
        }
        return ParsedQuestion(intent="production_trend_with_climate", params=params)

    if ("promote" in lowered or "compare" in lowered) and crop:
        crops = _extract_crop_pair(text)
        params = {
            "region": _extract_region(text),
            "crop_a": crops[0] if crops else crop,
            "crop_b": crops[1] if len(crops) > 1 else None,
            "years": _extract_years(lowered),
        }
        return ParsedQuestion(intent="policy_arguments", params=params)

    return ParsedQuestion(intent="unknown", params={"raw": question})
STATE_EXCLUDE_TOKENS = {
    "most",
    "recent",
    "year",
    "years",
    "available",
    "lowest",
    "highest",
    "district",
    "compare",
    "that",
    "with",
    "the",
    "over",
    "vs",
    "versus",
    "in",
    "for",
    "past",
    "previous",
    "list",
    "top",
    "state",
    "states",
    "crop",
    "crops",
    "rainfall",
    "production",
    "yield",
    "average",
    "annual",
    "trend",
    "policy",
    "best",
    "worst",
    "performing",
    "performance",
    "question",
    "had",
    "having",
}
CROP_EXCLUDE_TOKENS = {
    "annual",
    "average",
    "best",
    "compare",
    "crops",
    "crop",
    "data",
    "district",
    "districts",
    "list",
    "most",
    "over",
    "past",
    "performance",
    "performing",
    "policy",
    "previous",
    "production",
    "question",
    "rainfall",
    "recent",
    "state",
    "states",
    "the",
    "top",
    "trend",
    "with",
    "worst",
    "years",
    "year",
}
