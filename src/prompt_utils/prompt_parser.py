import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedDetect:
    # Exact args your function needs
    file_path: str
    is_url: bool
    return_MASK: bool
    return_GLASSES: bool
    # keep these for completeness (all False for this prompt)
    return_HEAD_POSE: bool = False
    return_OCCLUSION: bool = False
    return_BLUR: bool = False
    return_EXPOSURE: bool = False
    return_QUALITY_FOR_RECOGNITION: bool = False
    return_AGE: bool = False
    return_landmarks: bool = False


def parse_prompt_for_detect(prompt: str) -> ParsedDetect:
    """
    Only handles: 'Check all the faces inside detection1.jpg wearing the mask or glasses'
    """
    p = prompt.strip()
    m_local = re.search(r"inside\s+([^\s]+?\.(?:jpg|jpeg|png))", p, re.IGNORECASE)
    m_url = re.search(r"(https?://\S+?\.(?:jpg|jpeg|png))", p, re.IGNORECASE)

    if not (m_local or m_url):
        raise ValueError("Could not find image path or URL in prompt.")

    has_mask = "mask" in p.lower()
    has_glasses = "glasses" in p.lower()

    if m_local:
        return ParsedDetect(
            file_path=m_local.group(1),
            is_url=False,
            return_MASK=has_mask,
            return_GLASSES=has_glasses,
        )
    else:
        return ParsedDetect(
            file_path=m_url.group(1),
            is_url=True,
            return_MASK=has_mask,
            return_GLASSES=has_glasses,
        )
