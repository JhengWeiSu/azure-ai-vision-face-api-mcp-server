from importlib import import_module
from typing import Any
from .prompt_parser import parse_prompt_for_detect, ParsedDetect


def dispatch_prompt_detect(prompt: str) -> Any:
    """
    Parse the prompt and call tools.AzureFaceAttrib.get_face_dect(...)
    with the exact kwargs expected by that function.
    """
    intent: ParsedDetect = parse_prompt_for_detect(prompt)

    mod = import_module("tools.AzureFaceAttrib")
    fn = getattr(mod, "get_face_dect")

    return fn(
        file_path=intent.file_path,
        is_url=intent.is_url,
        return_HEAD_POSE=intent.return_HEAD_POSE,
        return_GLASSES=intent.return_GLASSES,
        return_OCCLUSION=intent.return_OCCLUSION,
        return_BLUR=intent.return_BLUR,
        return_EXPOSURE=intent.return_EXPOSURE,
        return_MASK=intent.return_MASK,
        return_QUALITY_FOR_RECOGNITION=intent.return_QUALITY_FOR_RECOGNITION,
        return_AGE=intent.return_AGE,
        return_landmarks=intent.return_landmarks,
    )
