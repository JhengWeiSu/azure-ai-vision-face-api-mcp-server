import os
import pathlib
import sys
import pytest
from pprint import pprint

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from prompt_utils.prompt_dispatch import dispatch_prompt_enroll
from tools.CreateLPG import create_large_person_group
from tools.ListPersonsInLPG import list_persons_in_group

endpoint = os.getenv("AZURE_FACE_ENDPOINT")
key = os.getenv("AZURE_FACE_API_KEY")

if not (endpoint and key):
    print(
        "❌ Live test skipped: Set AZURE_FACE_ENDPOINT and AZURE_FACE_API_KEY environment variables."
    )

LIVE = pytest.mark.skipif(
    not (endpoint and key),
    reason="Set AZURE_FACE_ENDPOINT and AZURE_FACE_API_KEY to run live tests",
)


def _find_file_upwards(filename: str, start: pathlib.Path) -> pathlib.Path | None:
    """Search upwards and in common sample folders for the given file."""
    candidates = [
        start / filename,
        start / "example" / filename,
        start / "examples" / filename,
        start / "samples" / filename,
        start / "assets" / filename,
        start / "testdata" / filename,
    ]
    for c in candidates:
        if c.is_file():
            return c
    for p in start.rglob(filename):
        if p.is_file():
            return p
    return None


@LIVE
def test_live_enroll_face_from_local(monkeypatch):
    group_id = "test-group-local"
    create_large_person_group(group_id)
    prompt = f"Enroll the face in detection1.jpg to the person group '{group_id}' as 'test-person-local'"
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    img_path = _find_file_upwards("detection1.jpg", repo_root)
    if img_path is None:
        pytest.skip("detection1.jpg not found in repo")

    old_cwd = pathlib.Path.cwd()
    try:
        os.chdir(img_path.parent)
        result_raw = dispatch_prompt_enroll(prompt)
    finally:
        os.chdir(old_cwd)

    pprint(result_raw)
    result_str = str(result_raw)
    assert "Create the person name:" in result_str
    assert "Add image file:" in result_str


@LIVE
def test_live_enroll_face_from_url(monkeypatch):
    group_id = "test-group-url"
    create_large_person_group(group_id)
    image_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/Face/images/detection1.jpg"
    prompt = f"Enroll the face in {image_url} to the person group '{group_id}' as 'test-person-url'"
    result_raw = dispatch_prompt_enroll(prompt)
    result_str = str(result_raw)
    assert "Create the person name:" in result_str
    assert "Add image file:" in result_str


@LIVE
def test_live_list_persons_in_group(monkeypatch):
    group_id = "test-group-list"
    create_large_person_group(group_id)
    image_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/Face/images/detection1.jpg"
    enroll_prompt = f"Enroll the face in {image_url} to the person group '{group_id}' as 'test-person-list'"
    dispatch_prompt_enroll(enroll_prompt)

    persons = list_persons_in_group(group_id)
    result_str = str(persons)
    assert "Name: test-person-list" in result_str
    assert "Number of faces: 1" in result_str
