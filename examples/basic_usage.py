"""Basic usage example for resume formatting."""

import os
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))  # Add project root

from src.chains.resume_formatter import ResumeFormatter
from src.models.resume_models import ResumeProcessingRequest


def main():
    """Basic usage example."""
    
    # Set your Google API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Please set GOOGLE_API_KEY environment variable")
        return
    
    # Initialize formatter
    formatter = ResumeFormatter(api_key=api_key)
    
    # Example resume file path (replace with your actual file)
    resume_file = "/Users/mac/projects/resume_project/data/pre/Ahmad Mahmoud CV.pdf"
    
    if not Path(resume_file).exists():
        print(f"Resume file not found: {resume_file}")
        return
    
    # Create processing request
    request = ResumeProcessingRequest(
        file_path=resume_file,
        target_role="Software Engineer",
        template_style="professional",
        enhance_content=True,
        ats_optimize=False
    )
    print(request)
    try:
        # Process the resume
        print("Processing resume...")
        result = formatter.format(request)
        
        # Display results
        print(f"\n=== Processing Results ===")
        print(f"Name: {result.extracted_data.name}")
        print(f"Email: {result.extracted_data.email}")
        print(f"Phone: {result.extracted_data.phone}")
        print(f"Location: {result.extracted_data.location}")
        print(f"Experience entries: {len(result.extracted_data.experience)}")
        print(f"Education entries: {len(result.extracted_data.education)}")
        print(f"Skills: {', '.join(result.extracted_data.skills[:10])}")
        
        # Save formatted resume
        output_file = f"output/{result.extracted_data.name}_formatted.txt"
        Path("output").mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.formatted_resume)
        
        print(f"\nFormatted resume saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing resume: {e}")


if __name__ == "__main__":
    main() 