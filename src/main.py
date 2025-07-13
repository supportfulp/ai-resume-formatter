"""Main application entry point."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from chains.resume_formatter import ResumeFormatter
from models.resume_models import ResumeProcessingRequest
from config.settings import settings


def main():
    """Main application function."""
    print(f"Welcome to {settings.app_name} v{settings.app_version}")
    
    # Check for API key
    if not settings.google_api_key:
        print("Error: Google API key not found. Please set GOOGLE_API_KEY environment variable.")
        return
    
    # Initialize formatter
    formatter = ResumeFormatter(api_key=settings.google_api_key)
    
    # Example usage
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
        # Create processing request
        request = ResumeProcessingRequest(
            file_path=file_path,
            target_role="Software Engineer",
            template_style="professional",
            enhance_content=True,
            ats_optimize=False
        )
        
        try:
            # Process resume
            result = formatter.format(request)
            
            # Print results
            print(f"\nProcessed resume for: {result.extracted_data.name}")
            print(f"Email: {result.extracted_data.email}")
            print(f"Experience entries: {len(result.extracted_data.experience)}")
            print(f"Skills: {', '.join(result.extracted_data.skills[:5])}...")
            
            # Save formatted resume
            output_path = Path(settings.output_dir) / f"{result.extracted_data.name}_formatted.txt"
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(result.formatted_resume)
            
            print(f"\nFormatted resume saved to: {output_path}")
            
        except Exception as e:
            print(f"Error processing resume: {e}")
    else:
        print("Usage: python main.py <path_to_resume>")
        print("Example: python main.py data/resume.pdf")


if __name__ == "__main__":
    main() 