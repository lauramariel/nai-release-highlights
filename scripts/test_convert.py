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


def test_extract_pdf_text_returns_string(tmp_path):
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Test release notes content.")
    pdf_path = tmp_path / "test.pdf"
    doc.save(str(pdf_path))
    doc.close()

    from convert import extract_pdf_text
    result = extract_pdf_text(pdf_path)
    assert isinstance(result, str)
    assert "Test release notes content." in result


def test_extract_pdf_text_joins_pages(tmp_path):
    import fitz
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((72, 72), f"Page {i} content")
    pdf_path = tmp_path / "multipage.pdf"
    doc.save(str(pdf_path))
    doc.close()

    from convert import extract_pdf_text
    result = extract_pdf_text(pdf_path)
    assert "Page 0 content" in result
    assert "Page 2 content" in result
