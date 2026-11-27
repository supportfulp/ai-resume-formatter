"""Tests for resume formatter."""

import pytest
from unittest.mock import Mock, patch
from src.chains.resume_formatter import ResumeFormatter
from src.models.resume_models import ResumeProcessingRequest, ResumeData


class TestResumeFormatter:
    """Test cases for ResumeFormatter."""
    
    @pytest.fixture
    def formatter(self):
        """Create formatter instance for testing."""
        with patch('src.chains.resume_formatter.make_llm'):
            return ResumeFormatter(api_key="test_key")
    
    @pytest.fixture
    def sample_request(self):
        """Create sample processing request."""
        return ResumeProcessingRequest(
            file_path="test_resume.pdf",
            target_role="Software Engineer",
            template_style="professional",
            enhance_content=True,
            ats_optimize=False
        )
    
    def test_formatter_initialization(self, formatter):
        """Test formatter initialization."""
        assert formatter is not None
        assert formatter.pdf_adapter is not None
        assert formatter.docx_adapter is not None
    
    def test_get_adapter_pdf(self, formatter):
        """Test getting PDF adapter."""
        adapter = formatter._get_adapter("test.pdf")
        assert adapter == formatter.pdf_adapter
    
    def test_get_adapter_docx(self, formatter):
        """Test getting DOCX adapter."""
        adapter = formatter._get_adapter("test.docx")
        assert adapter == formatter.docx_adapter
    
    def test_get_adapter_unsupported(self, formatter):
        """Test getting adapter for unsupported file type."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            formatter._get_adapter("test.txt")
    
    @patch('src.chains.resume_formatter.PDFAdapter.extract_text')
    def test_extract_text(self, mock_extract, formatter):
        """Test text extraction."""
        mock_extract.return_value = "Sample resume text"
        result = formatter._extract_text("test.pdf")
        assert result == "Sample resume text"
    
    def test_extract_structured_data(self, formatter):
        """Test structured data extraction."""
        formatter.extract_chain = Mock()
        formatter.extract_chain.invoke.return_value = Mock(
            content='```json\n{"name": "John Doe", "email": "john@example.com"}\n```',
            usage_metadata={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
        )
        result = formatter._extract_structured_data("Sample text")
        assert isinstance(result, ResumeData)
        assert result.name == "John Doe"
        assert result.email == "john@example.com" 

def test_response_text_handles_gemini3_content_blocks():
    """Gemini 3.x returns a list of content blocks instead of a string."""
    from src.llm import response_text
    blocks = [{"type": "text", "text": '{"name": '}, {"type": "text", "text": '"Jo"}', "extras": {"signature": "x"}}]
    assert response_text(Mock(content=blocks)) == '{"name": "Jo"}'
    assert response_text(Mock(content="plain")) == "plain"


def test_null_strings_become_none():
    from src.chains.resume_formatter import ResumeFormatter
    data = {"email": "null", "phone": "N/A", "skills": ["Go", "null"], "experience": [{"company": "None"}]}
    assert ResumeFormatter._normalize_null_strings(data) == {
        "email": None, "phone": None, "skills": ["Go"], "experience": [{"company": None}]}
