from __future__ import annotations

import os
import re
import unicodedata
from contextlib import suppress
from importlib import resources as pkg_resources
from typing import Optional, Tuple, Any

try:
    from .guidelines_engine import create_guidelines_injector
    GUIDELINES_AVAILABLE = True
except ImportError:
    GUIDELINES_AVAILABLE = False


def load_instructions_from_prompt_md(variant: str, ascii_normalize: bool) -> Tuple[Optional[str], str]:
    """Extract the complete prompt from prompt.md.

    Returns (instructions, loaded_variant).
    """
    override_path = os.environ.get("ARM_PROMPT_FILE") or os.environ.get("ARM_PROMPT_PATH")

    candidates: list[Any] = []
    if override_path:
        candidates.append(os.path.abspath(os.path.expanduser(override_path)))

    try:
        workspace_root = os.path.abspath(os.path.join(os.getcwd(), "prompt.md"))
        candidates.append(workspace_root)
    except Exception:
        pass

    try:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        candidates.append(os.path.join(repo_root, "prompt.md"))
    except Exception:
        pass

    with suppress(Exception):
        packaged_prompt = pkg_resources.files("academic_research_mentor").joinpath("prompt.md")
        candidates.append(packaged_prompt)

    text: Optional[str] = None
    for candidate in candidates:
        text = _read_candidate(candidate)
        if text:
            break
    if text is None:
        return None, variant

    # Extract content after the main heading
    heading_re = r"^#\s+Research\s+Mentor\s+System\s+Prompt.*$"
    m = re.search(heading_re, text, flags=re.MULTILINE)
    if not m:
        return None, variant

    # Get all content after the main heading
    tail = text[m.end():].strip()
    
    # Normalize the content
    block = _normalize_whitespace(tail)
    if ascii_normalize:
        block = _ascii_normalize(block)

    if len(block) > 12000:
        block = _trim_low_signal_sections(block)

    # Inject guidelines if available and enabled
    if GUIDELINES_AVAILABLE:
        try:
            injector = create_guidelines_injector()
            block = injector.inject_guidelines(block)
        except Exception as e:
            # Log warning but don't break functionality
            print(f"Warning: Failed to inject guidelines: {e}")

    return block.strip(), "unified"


def _read_candidate(candidate: Any) -> Optional[str]:
    try:
        if hasattr(candidate, "read_text"):
            return candidate.read_text(encoding="utf-8")  # type: ignore[call-arg]
        path = str(candidate)
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except Exception:
        return None


def _normalize_whitespace(text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines()]
    out_lines = []
    blank = 0
    for ln in lines:
        if ln.strip() == "":
            blank += 1
            if blank <= 2:
                out_lines.append("")
        else:
            blank = 0
            out_lines.append(ln)
    return "\n".join(out_lines).strip()


def _ascii_normalize(text: str) -> str:
    replacements = {
        "–": "-",
        "—": "-",
        "→": "->",
        "←": "<-",
        "↔": "<->",
        "≈": "~=",
        "×": "x",
        "•": "-",
        "…": "...",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "\u00A0": " ",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = "".join(ch for ch in text if not _looks_like_emoji(ch))
    return text


def _looks_like_emoji(ch: str) -> bool:
    if ord(ch) > 0x1F000:
        cat = unicodedata.category(ch)
        if cat in {"So", "Sk"}:
            return True
    return False


def _trim_low_signal_sections(block: str) -> str:
    patterns = [r"^\s*Length guidance[\s\S]*?$", r"^\s*Citation format[\s\S]*?$"]
    trimmed = block
    for pat in patterns:
        trimmed = re.sub(pat, "", trimmed, flags=re.MULTILINE)
    return _normalize_whitespace(trimmed)
