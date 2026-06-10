import pytest
from convert import extract_version_slug


def test_extract_standard_filename():
    assert extract_version_slug("Release-Notes-Nutanix-Enterprise-AI-v2_8.pdf") == "v2_8"


def test_extract_single_digit_minor():
    assert extract_version_slug("Release-Notes-NAI-v2_1.pdf") == "v2_1"


def test_extract_multi_digit_version():
    assert extract_version_slug("Release-Notes-v10_12.pdf") == "v10_12"


def test_raises_when_no_version_found():
    with pytest.raises(ValueError, match="Could not extract version"):
        extract_version_slug("Release-Notes-NAI.pdf")
