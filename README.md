# Resume Formatting LLM

An intelligent resume formatting system using LangChain and LLMs to automatically format and enhance resumes.

## Features

- PDF/Word document parsing
- Intelligent content extraction using Gemini 2.5 Flash
- Multiple formatting templates
- LLM-powered content enhancement
- **Predefined template restructuring** - Transform resumes to exact template format
- Batch processing capabilities

## Project Structure

```
src/
├── adapters/          # Data adapters for different input/output formats
├── prompts/           # LLM prompt templates
├── models/            # Pydantic models and data structures
├── chains/            # LangChain chains and workflows
├── utils/             # Utility functions and helpers
tests/                 # Test files
config/                # Configuration files
docs/                  # Documentation
examples/              # Usage examples
```

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp env.example .env
# Add your Google API key
```

3. Run the application:
```bash
python -m src.main
```

## Usage

### Basic Resume Formatting
```python
from src.chains.resume_formatter import ResumeFormatter

formatter = ResumeFormatter()
formatted_resume = formatter.format("path/to/resume.pdf")
```

### Resume Restructuring (Predefined Template)
```python
from src.chains.resume_restructure_chain import ResumeRestructureChain

restructure_chain = ResumeRestructureChain()
restructured_resume = restructure_chain.restructure(
    request, 
    reference_number="SDA01-AMH"
)
```

## Development

- Run tests: `pytest`
- Format code: `black src/`
- Type checking: `mypy src/` 