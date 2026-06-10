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


from unittest.mock import MagicMock


def test_call_claude_calls_api_and_returns_text():
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="---\nversion: '2.8'\n---\nBody text.")]
    )

    from convert import call_claude
    result = call_claude("raw pdf text", mock_client)

    assert result == "---\nversion: '2.8'\n---\nBody text."
    mock_client.messages.create.assert_called_once()
    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-sonnet-4-6"
    assert call_kwargs["max_tokens"] == 4096
    assert any("raw pdf text" in str(m) for m in call_kwargs["messages"])
    from convert import SYSTEM_PROMPT
    assert call_kwargs["system"] == SYSTEM_PROMPT


def test_write_release_notes_creates_file(tmp_path):
    from convert import write_release_notes
    content = "---\nversion: '2.8'\n---\nBody."
    output_path = write_release_notes("v2_8", content, tmp_path)
    assert output_path == tmp_path / "v2_8.md"
    assert output_path.read_text(encoding="utf-8") == content


def test_write_release_notes_creates_output_dir(tmp_path):
    from convert import write_release_notes
    nested = tmp_path / "a" / "b" / "releases"
    write_release_notes("v2_8", "content", nested)
    assert (nested / "v2_8.md").exists()
