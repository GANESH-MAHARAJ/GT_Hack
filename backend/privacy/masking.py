import re
from typing import Dict, Tuple, Any, Iterable, Optional


PiiMapping = Dict[str, Dict[str, str]]
# Example:
# {
#   "[PHONE_1]": {"value": "+91-9876543210", "kind": "PHONE"},
#   "[EMAIL_1]": {"value": "user@example.com", "kind": "EMAIL"},
# }


def _mask_pattern(
    text: str,
    pattern: str,
    kind: str,
    mapping: PiiMapping,
    counter: Dict[str, int],
) -> str:
    """
    Internal helper to mask all matches of a regex pattern with tokens like [KIND_1].
    """

    def repl(match: re.Match) -> str:
        counter[kind] = counter.get(kind, 0) + 1
        token = f"[{kind}_{counter[kind]}]"
        mapping[token] = {"value": match.group(0), "kind": kind}
        return token

    return re.sub(pattern, repl, text)


def mask_pii(text: str) -> Tuple[str, PiiMapping]:
    """
    Mask basic PII from the given text.

    Currently masks:
    - PHONE: phone-like number strings
    - EMAIL: email addresses
    - ORDER: order IDs like ORD1234, ORD-1234, ORDER_5678

    Returns:
        masked_text, mapping
    """
    mapping: PiiMapping = {}
    counter: Dict[str, int] = {}

    # Phone numbers: crude but works well enough for hackathon
    phone_pattern = r"\+?\d[\d\-\s]{8,15}"
    text = _mask_pattern(text, phone_pattern, "PHONE", mapping, counter)

    # Emails
    email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    text = _mask_pattern(text, email_pattern, "EMAIL", mapping, counter)

    # Order IDs like ORD1234 / ORD-1234 / ORDER_5678
    order_pattern = r"\b(?:ORD|ORDER)[-_]?\d+\b"
    text = _mask_pattern(text, order_pattern, "ORDER", mapping, counter)

    # You can add more patterns here if you want (addresses, card numbers, etc.)

    return text, mapping


def safe_unmask(
    text: str,
    mapping: PiiMapping,
    allowed_kinds: Optional[Iterable[str]] = None,
) -> str:
    """
    Safely unmask tokens in `text` using `mapping`.

    - If allowed_kinds is None → unmask everything.
    - Else → only unmask tokens whose `kind` is in allowed_kinds.
      (e.g. allowed_kinds = {"NAME"} to avoid re-inserting phones/emails.)

    NOTE: Right now we don't generate NAME tokens; you can add that later
    if you want name-detection.
    """

    if allowed_kinds is None:
        allowed_kinds = {m["kind"] for m in mapping.values()}

    # Simple replace; in a more hardcore scenario, you might want a more
    # robust algorithm for overlapping tokens, but here it's fine.
    for token, info in mapping.items():
        if info["kind"] in allowed_kinds:
            text = text.replace(token, info["value"])
    return text


def mask_dict(obj: Any) -> Tuple[Any, PiiMapping]:
    """
    Utility: recursively walk a dict/list structure and mask PII
    in all string fields.

    Useful when you later want to mask user profile fields before
    sending them to LLMs.

    Returns:
        masked_obj, mapping
    """
    mapping: PiiMapping = {}

    def _mask_any(x: Any) -> Any:
        nonlocal mapping
        if isinstance(x, str):
            masked, local_map = mask_pii(x)
            # merge local_map into global mapping
            for token, info in local_map.items():
                mapping[token] = info
            return masked
        elif isinstance(x, dict):
            return {k: _mask_any(v) for k, v in x.items()}
        elif isinstance(x, list):
            return [_mask_any(v) for v in x]
        else:
            return x

    masked_obj = _mask_any(obj)
    return masked_obj, mapping
