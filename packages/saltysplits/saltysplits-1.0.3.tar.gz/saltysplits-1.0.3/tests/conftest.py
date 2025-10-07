import pytest
import requests
import pathlib
from urllib.error import HTTPError
from lxml.etree import Element


LSS_DIR = pathlib.Path(__file__).parent / "run_files"
# names come from livesplit-core/tests/run_files/mod.rs
CELESTE = "Celeste - Any% (1.2.1.5).lss"
LIVESPLIT_1_0 = "livesplit1.0.lss"
LIVESPLIT_1_4 = "livesplit1.4.lss"
LIVESPLIT_1_5 = "livesplit1.5.lss"
LIVESPLIT_1_6_GAMETIME = "livesplit1.6_gametime.lss"
LIVESPLIT_1_6 = "livesplit1.6.lss"
LIVESPLIT_ATTEMPT_ENDED_BUG = "livesplit_attempt_ended_bug.lss"
LIVESPLIT_FUZZ_CRASH_UTF8 = "livesplit_fuzz_crash_utf8.lss"
LIVESPLIT_FUZZ_CRASH = "livesplit_fuzz_crash.lss"
LIVESPLIT_VICE_CITY = "Grand Theft Auto Vice City - Any% (No SSU).lss"

VALID_SPLITS = [
    CELESTE,
    LIVESPLIT_1_0,
    LIVESPLIT_1_4,
    LIVESPLIT_1_5,
    LIVESPLIT_1_6_GAMETIME,
    LIVESPLIT_1_6,
]
INVALID_SPLITS = [
    LIVESPLIT_ATTEMPT_ENDED_BUG,
    LIVESPLIT_FUZZ_CRASH_UTF8,
    LIVESPLIT_FUZZ_CRASH,
]

def drop_empty_tags(element: Element, top_level=True) -> None:
    """Removes empty XML tags from a given LXML ElementTree

    Args:
        element (Element): Root XML element from which empty elements should be removed
        top_level (bool, optional): Whether to only check direct children or all children (recursively)
    """
    # dropping empty tags before comparison, no way to catch that AND actually optional elements (e.g. real_time and/or game_time)
    children = list(element) if top_level else list(element.iter())
    for child in children:
        if len(child) == 0 and not child.text and not child.attrib:
            parent = child.getparent()
            if parent is not None:
                parent.remove(child)

def get_run_files(lss_dir: pathlib.Path) -> None:
    api_url = (
        "https://api.github.com/repos/LiveSplit/livesplit-core/contents/tests/run_files"
    )
    response = requests.get(api_url)
    files = response.json()

    lss_files = [file for file in files if file["name"].endswith(".lss")]
    for lss_file in lss_files:
        lss_src = lss_file["download_url"]
        lss_dst = lss_dir / lss_file["name"]

        if lss_dst.exists() and lss_dst.stat().st_size == lss_file["size"]:
            continue

        with requests.get(lss_src, stream=True) as response:
            response.raise_for_status()

            with open(lss_dst, "w", encoding="utf-8") as file:
                file.write(response.text)


@pytest.mark.skip(
    reason="Temporarily disabled due to formatting inconsistencies in livesplit-core's run_files (e.g., GameTime values missing nanoseconds)."
)
@pytest.fixture
def ensure_presence_splits() -> bool:
    lss_names = VALID_SPLITS + INVALID_SPLITS
    lss_files = [LSS_DIR / lss_name for lss_name in lss_names]
    lss_present = all([lss_file.exists() for lss_file in lss_files])

    if not lss_present:
        try:
            get_run_files(lss_dir=LSS_DIR)
        except HTTPError as e:
            raise e
    return all([lss_file.exists() for lss_file in lss_files])


@pytest.mark.skip(
    reason="Temporarily disabled due to formatting inconsistencies in livesplit-core's run_files (e.g., GameTime values missing nanoseconds)."
)
@pytest.fixture
def valid_splits(ensure_presence_splits):
    assert ensure_presence_splits
    return [LSS_DIR / split for split in VALID_SPLITS]


@pytest.mark.skip(
    reason="Temporarily disabled due to formatting inconsistencies in livesplit-core's run_files (e.g., GameTime values missing nanoseconds)."
)
@pytest.fixture
def invalid_splits(ensure_presence_splits):
    assert ensure_presence_splits
    return [LSS_DIR / split for split in INVALID_SPLITS]


@pytest.fixture
def livesplit_vicecity():
    return LSS_DIR / LIVESPLIT_VICE_CITY
