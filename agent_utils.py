"""Shared, dependency-light helpers for the agent experiments."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path


class InputError(ValueError):
    """Raised when source input cannot be read or validated."""


class OutputValidationError(ValueError):
    """Raised when live model output is unsafe to return."""


MAX_SOURCE_BYTES = 100_000


_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
_NUMBER_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")
_ENTITY_RE = re.compile(r"\b(?:[A-Z][A-Za-z0-9'-]*)(?:\s+[A-Z][A-Za-z0-9'-]*)*\b")
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "have", "in", "is", "it", "of", "on", "or", "that", "the", "their", "this",
    "to", "was", "were", "will", "with",
}
_ENTITY_NOISE = {"A", "An", "The", "This", "That", "On", "In", "At", "For", "From"}


def read_source(path_value: str) -> str:
    """Read a non-empty UTF-8 text file within the configured byte limit."""
    path = Path(path_value).expanduser()
    if not path.exists():
        raise InputError(f"Input file not found: {path}")
    if not path.is_file():
        raise InputError(f"Input path is not a file: {path}")
    try:
        with path.open("rb") as source_file:
            raw = source_file.read(MAX_SOURCE_BYTES + 1)
    except OSError as exc:
        raise InputError(f"Could not read input file: {exc}") from exc
    if len(raw) > MAX_SOURCE_BYTES:
        raise InputError(
            f"Input exceeds the {MAX_SOURCE_BYTES:,}-byte UTF-8 input limit."
        )
    try:
        text = raw.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise InputError("Input must be a UTF-8 text file.") from exc
    if not text:
        raise InputError("Input file is empty.")
    return " ".join(text.split())


def validate_generated_output(
    output: str,
    source_text: str,
    headings: tuple[str, ...],
    bullet_headings: frozenset[str],
    ungrounded_headings: frozenset[str] = frozenset(),
) -> None:
    """Reject live output unless factual content is copied from the source."""
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    found_headings = [line for line in lines if line in headings]
    if not lines or lines[0] != headings[0] or found_headings != list(headings):
        raise OutputValidationError("Live output does not match the required section structure.")

    section_bodies: dict[str, list[str]] = {}
    for index, heading in enumerate(headings):
        start = lines.index(heading) + 1
        end = lines.index(headings[index + 1]) if index + 1 < len(headings) else len(lines)
        body = lines[start:end]
        section_bodies[heading] = body
        if not body:
            raise OutputValidationError("Live output does not match the required section structure.")
        if heading in bullet_headings and any(not line.startswith("- ") for line in body):
            raise OutputValidationError("Live output does not match the required section structure.")
        if heading not in bullet_headings and any(line.startswith("- ") for line in body):
            raise OutputValidationError("Live output does not match the required section structure.")

    normalized_source = " ".join(source_text.split())
    source_sentences = set(split_sentences(normalized_source))
    source_entities = set(extract_entities(source_text, limit=100))
    source_numbers = set(_NUMBER_RE.findall(source_text))
    for heading, body in section_bodies.items():
        if (
            heading == "Questions for Further Research"
            and heading in ungrounded_headings
        ):
            continue
        for line in body:
            content = " ".join(line.removeprefix("- ").split())
            phrases = split_sentences(content)
            numbers_supported = set(_NUMBER_RE.findall(content)) <= source_numbers
            if heading == "Important Entities":
                content_supported = content in source_entities
            else:
                content_supported = bool(phrases) and all(
                    phrase in source_sentences for phrase in phrases
                )
            if (
                not re.search(r"[A-Za-z0-9]", content)
                or not content_supported
                or not numbers_supported
            ):
                raise OutputValidationError("Live output is not sufficiently grounded in the source.")


def split_sentences(text: str) -> list[str]:
    """Split text into sentences without changing their wording."""
    normalized = " ".join(text.split())
    if not normalized:
        return []
    return [part.strip() for part in _SENTENCE_SPLIT_RE.split(normalized) if part.strip()]


def _sentence_score(sentence: str, frequencies: Counter[str]) -> float:
    words = [word.lower() for word in _WORD_RE.findall(sentence)]
    meaningful = [word for word in words if word not in _STOPWORDS]
    if not meaningful:
        return 0.0
    return sum(frequencies[word] for word in meaningful) / len(meaningful)


def select_key_sentences(text: str, limit: int = 3) -> list[str]:
    """Select high-signal source sentences and preserve source order."""
    sentences = split_sentences(text)
    if not sentences or limit <= 0:
        return []
    words = [word.lower() for word in _WORD_RE.findall(text)]
    frequencies = Counter(word for word in words if word not in _STOPWORDS)
    ranked = sorted(
        enumerate(sentences),
        key=lambda item: (_sentence_score(item[1], frequencies), -item[0]),
        reverse=True,
    )[:limit]
    return [sentences[index] for index, _ in sorted(ranked)]


def make_headline(text: str, max_length: int = 88) -> str:
    """Create a conservative headline from the first source sentence."""
    sentences = split_sentences(text)
    if not sentences:
        return "Untitled source"
    headline = sentences[0].rstrip(".!?")
    if len(headline) <= max_length:
        return headline
    shortened = headline[: max_length + 1].rsplit(" ", 1)[0].rstrip(" ,;:")
    return f"{shortened}…"


def extract_entities(text: str, limit: int = 8) -> list[str]:
    """Extract repeated or capitalized names exactly as written in the source."""
    entities: list[str] = []
    seen: set[str] = set()
    for match in _ENTITY_RE.finditer(text):
        entity = match.group(0).strip()
        if entity in _ENTITY_NOISE or entity.lower() in seen:
            continue
        seen.add(entity.lower())
        entities.append(entity)
        if len(entities) == limit:
            break
    return entities


def bullet_lines(items: list[str], empty_message: str = "None identified from the source.") -> str:
    """Format a list as readable terminal bullets."""
    if not items:
        return f"- {empty_message}"
    return "\n".join(f"- {item}" for item in items)
