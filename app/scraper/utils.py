import html
import bleach
import re
from typing import Union
from datetime import datetime, timezone

ALLOWED_TAGS = [
    "p",
    "b",
    "i",
    "strong",
    "em",
    "u",
    "br",
    "ul",
    "ol",
    "li",
    "h1",
    "h2",
    "h3",
    "a",
]

ALLOWED_ATTRIBUTES = {"a": ["href", "target", "rel"]}


def clean_html(html_content: str) -> str:
    """
    Convert HTML entities and sanitize HTML.
    """
    if not html_content:
        return ""

    text = html.unescape(html_content)

    return bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )


def clean_remoteok_boilerplate(text: str) -> str:
    """
    Remove RemoteOK anti-spam blocks.
    """

    spam_pattern = (
        r"Please mention the word\s+\*\*?\w+\*\*?\s+and tag\s+"
        r"[A-Za-z0-9+/=]+.*?(?=(<\/p>|<\/div>|$))"
    )

    text = re.sub(
        spam_pattern,
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    text = re.sub(r"#\w+=*", "", text)

    text = re.sub(
        r"#LI-[\w\-\[\]\{\}\s:]+",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return text.strip()


def clean_jobicy_boilerplate(text: str) -> str:
    """
    Remove Jobicy boilerplate.
    """

    text = re.sub(
        r"#LI-[\w\-\[\]\{\}\s:]+",
        "",
        text,
        flags=re.IGNORECASE,
    )

    patterns = [
        r"Canonical is an equal opportunity employer.*?(?=(<\/p>|<\/div>|$))",
        r"We are proud to foster a workplace free from discrimination.*?(?=(<\/p>|<\/div>|$))",
        r"Whatever your identity, we will give your application fair consideration.*?(?=(<\/p>|<\/div>|$))",
    ]

    for pattern in patterns:
        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

    return text.strip()


def fix_mojibake(text: str) -> str:
    """
    Fixes Mojibake by re-encoding to Latin-1 and decoding to UTF-8.
    """
    if not isinstance(text, str):
        return text

    try:
        # This reverses the common misinterpretation of UTF-8 as Latin-1
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        # If it fails, return the original text as it might already be correct
        return text


def format_salary_range(min_val, max_val, currency="USD", period="annual") -> str:
    # Treat 0 or None as missing data
    if (min_val is None or min_val <= 0) and (max_val is None or max_val <= 0):
        return "Undisclosed"

    # Conversion rate for MXN to USD
    rate = 17.43

    def convert(val):
        if val is None or val == 0:
            return None
        if currency == "MXN":
            val = val / rate
        return val

    # Normalize to annual if monthly
    if period == "monthly":
        min_val = (min_val * 12) if min_val else None
        max_val = (max_val * 12) if max_val else None

    min_usd = convert(min_val)
    max_usd = convert(max_val)

    def fmt(val):
        return f"${int(val / 1000)}k" if val else ""

    # Logic: If both exist and are similar, show one value
    if min_usd and max_usd and abs(min_usd - max_usd) < 1.0:
        return f"{fmt(min_usd)}"

    if min_usd and max_usd:
        return f"{fmt(min_usd)} - {fmt(max_usd)}"
    elif min_usd:
        return f"From {fmt(min_usd)}"
    else:
        return f"Up to {fmt(max_usd)}"


def parse_datetime(date_str: str) -> datetime:
    """
    Parse ISO datetime safely with timezone normalization.
    """
    if not date_str:
        return datetime.now(timezone.utc)

    try:
        if re.search(r"[+-]\d{2}$", date_str):
            date_str = f"{date_str}:00"
        return datetime.fromisoformat(date_str)
    except ValueError:
        return datetime.now(timezone.utc)
def parse_timestamp(timestamp) -> datetime:
    """
    Parse Unix timestamp.
    """

    if not timestamp:
        return datetime.now(timezone.utc)

    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def normalize_location(location: str) -> str:
    """
    Remove duplicates and whitespace.
    """

    if not location:
        return "Remote"

    location = html.unescape(location).strip(", ")

    return ", ".join(
        sorted({part.strip() for part in location.split(",") if part.strip()})
    )


def format_salary(
    minimum,
    maximum,
    currency="$",
) -> str:
    """
    Format salary ranges.
    """

    if minimum is None and maximum is None:
        return "Undisclosed"

    if minimum is not None and maximum is not None:
        return f"{currency}{minimum:,} - {currency}{maximum:,}"

    if minimum is not None:
        return f"From {currency}{minimum:,}"

    return f"Up to {currency}{maximum:,}"


def normalize_company_name(
    company_name: str | None,
    company_slug: str | None,
) -> str:
    """
    Some APIs return 'name' instead of the actual company.
    Use the slug as a fallback.
    """

    if company_name and company_name != "name":
        return company_name

    if company_slug:
        return company_slug.replace("-", " ").title()

    return "Remote Company"
