"""Example usage of the resume restructuring chain."""

import os
from pathlib import Path
import sys
import json
# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.chains.resume_restructure_chain import ResumeRestructureChain
from src.chains.resume_formatter import ResumeFormatter
from src.models.resume_models import ResumeProcessingRequest


def main():
    """Example of resume restructuring."""
    
    # Set your Google API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Please set GOOGLE_API_KEY environment variable")
        return
    
    # Initialize both chains
    restructure_chain = ResumeRestructureChain(api_key=api_key)
    formatter = ResumeFormatter(api_key=api_key)
    
    # Example resume file path
    resume_file = "/Users/mac/projects/resume_project/data/pre/Christian Khairallah CV.pdf"
    
    if not Path(resume_file).exists():
        print(f"Resume file not found: {resume_file}")
        return
    
    # Create processing request
    request = ResumeProcessingRequest(
        file_path=resume_file,
        target_role="Software Engineer",
        template_style="professional",
        enhance_content=False,
        ats_optimize=False
    )
    
    try:
        print("=== Resume Restructuring Example ===\n")
        
        
        # Method 2: Two-step process (extract then restructure)
        print("2. Three-step process (extract then restructure):")
        print("-" * 50)
        
        # First, extract structured data using the main formatter
        result = formatter.format(request)
        extracted_data = result.extracted_data
        
        print(f"Extracted data for: {extracted_data.name}")
        print(f"Email: {extracted_data.email}")
        print(f"Experience entries: {len(extracted_data.experience)}")
        print(f"Skills: {', '.join(extracted_data.skills[:5])}...")
        
        # Then restructure using the extracted data
        restructured_from_data = restructure_chain.restructure_from_data(
            extracted_data, 
            reference_number="SDA02-AMH"
        )
        
        print("\nRestructured resume:")
        print(restructured_from_data)
        

        # Save the restructured resume from data
        output_file_data = f"/Users/mac/projects/resume_project/output/{extracted_data.name}_restructured_method2.txt"
        with open(output_file_data, 'w', encoding='utf-8') as f:
            f.write(restructured_from_data)

        print(f"\nRestructured resume from data saved to: {output_file_data}")

        request.content = restructured_from_data
        result = formatter.format(request)
        print(result.extracted_data.model_dump_json(indent=2))

        # Save the restructured resume from data in json format
        output_file_data_json = f"/Users/mac/projects/resume_project/output/{extracted_data.name}_restructured_method2.json"
        with open(output_file_data_json, 'w', encoding='utf-8') as f:
            json.dump(result.extracted_data.model_dump(), f, indent=2)

        
    except Exception as e:
        print(f"Error processing resume: {e}")


if __name__ == "__main__":
    main() 