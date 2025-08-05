from docx import Document
from docx.shared import Inches, RGBColor, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import OxmlElement, qn
import json
import os

######## ADD python-docx=1.2.0 TO REQUIREMENTS.TXT ########

class ResumeDocumentGenerator:
    """A class to generate professional resume documents in DOCX format."""
    
    def __init__(self, page_height=14):
        """
        Initialize the ResumeDocumentGenerator.
        
        Args:
            page_height (int): Page height in inches (default: 14)
        """
        self.page_height = page_height
        self.document = None
        self.resume_data = None
    
    def _add_cell_borders(self, cell, borders_to_add=['top', 'right']):
        """
        Add specific borders to a table cell.
        
        Args:
            cell: The table cell to add borders to
            borders_to_add (list): List of border types to add
        """
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        
        # Create or get borders element
        tcBorders = tcPr.find(qn('w:tcBorders'))
        if tcBorders is None:
            tcBorders = OxmlElement('w:tcBorders')
            tcPr.append(tcBorders)
        
        # Add specified borders
        for border_name in borders_to_add:
            border_element = OxmlElement(f'w:{border_name}')
            border_element.set(qn('w:val'), 'single')
            border_element.set(qn('w:sz'), '18')  # Border thickness
            border_element.set(qn('w:color'), '#638276')  # Border color
            tcBorders.append(border_element)
    
    def _setup_document(self):
        """Set up the document with proper margins and page size."""
        self.document = Document()
        
        # Set document margins and page size
        sections = self.document.sections
        for section in sections:
            # Set margins based on Page Setup screenshot
            section.top_margin = Inches(0.1)
            section.bottom_margin = Inches(0.79)
            section.left_margin = Inches(0.6)
            section.right_margin = Inches(0.59)
            
            # Set page size to Letter (8.5" x 11")
            section.page_width = Inches(8.5)
            section.page_height = Inches(self.page_height)
    
    def _add_logo(self):
        """Add the logo image at the top left of the document."""
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, 's.png')
        
        if os.path.exists(logo_path):
            logo_para = self.document.add_paragraph()
            logo_para.paragraph_format.space_after = Pt(6)
            run = logo_para.add_run()
            run.add_picture(logo_path, width=Inches(1))
    
    def _create_header(self):
        """Create the header section with name and reference number."""
        # Header with name and title
        header = self.document.add_paragraph(self.resume_data['name'])
        header.alignment = WD_ALIGN_PARAGRAPH.CENTER
        name_run = header.runs[0]
        name_run.font.size = Pt(32)
        name_run.font.name = 'Georgia'

        title_para = self.document.add_paragraph("Ref#: BED1-AMD")
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_para.runs[0]
        title_run.font.size = Pt(9)
        title_run.font.italic = True
        title_run.font.name = 'Arial'
    
    def _create_main_table(self, skills_column_width=2.25, exp_column_width=5.25):
        """Create the main table structure for the resume layout."""
        # Create main table structure
        main_table = self.document.add_table(rows=2, cols=4)
        main_table.autofit = False

        # Merge cells for layout
        main_table.cell(0, 0).merge(main_table.cell(1, 0))  # Skills column
        main_table.cell(0, 1).merge(main_table.cell(0, 2))  # Experience row 1
        main_table.cell(0, 1).merge(main_table.cell(0, 3))  # Experience row 1
        main_table.cell(1, 1).merge(main_table.cell(1, 2))  # Education row 2
        main_table.cell(1, 1).merge(main_table.cell(1, 3))  # Education row 2

        # Set column widths properly
        main_table.columns[0].width = Inches(skills_column_width)  # Skills column
        main_table.columns[1].width = Inches(exp_column_width)  # Experience column
        main_table.columns[2].width = Inches(0.1)  # Minimal width for merged columns
        main_table.columns[3].width = Inches(0.1)  # Minimal width for merged columns

        # Apply borders
        self._add_cell_borders(main_table.cell(0, 0), ['top', 'right'])  # Skills cell
        self._add_cell_borders(main_table.cell(0, 1), ['top'])  # Experience cell
        self._add_cell_borders(main_table.cell(1, 1), ['top', 'left'])  # Education cell
        
        return main_table
    
    def _add_skills_section(self, skills_cell):
        """Add the skills section to the left sidebar."""
        # Summary section
        summary = self.resume_data['summary'].split('. ')
        for summ in summary:
            sum_para = skills_cell.add_paragraph(summ)
            sum_para.runs[0].font.name = 'Arial'

        # Key Skills section
        skills_heading = skills_cell.add_paragraph()
        skills_heading.add_run("Key Skills").bold = True
        skills_heading.runs[0].font.size = Pt(14)
        skills_heading.runs[0].font.color.rgb = RGBColor(99, 130, 118)
        skills_heading.runs[0].font.name = 'Georgia'
        skills_heading.paragraph_format.line_spacing = 1.1
        skills_heading.paragraph_format.space_after = Pt(1.5)

        for skill in self.resume_data['skills']:
            skill_para = skills_cell.add_paragraph(skill)
            skill_para.runs[0].font.name = 'Arial'
            skill_para.paragraph_format.space_before = Pt(0)
            skill_para.paragraph_format.space_after = Pt(0.5)
    
    def _add_experience_section(self, exp_cell):
        """Add the experience section to the main content area."""
        exp_heading = exp_cell.add_paragraph("Experience")
        exp_heading.runs[0].font.bold = True
        exp_heading.runs[0].font.size = Pt(14)
        exp_heading.runs[0].font.color.rgb = RGBColor(99, 130, 118)
        exp_heading.runs[0].font.name = 'Georgia'
        exp_heading.paragraph_format.space_after = Pt(1.5)

        # Loop through experience data
        for exp in self.resume_data['experience']:
            # Format dates
            end_date = exp['end_date'] if exp['end_date'] else 'Present'
            date_range = f"{exp['start_date']} – {end_date}"

            # Job header with dates
            job_header = exp_cell.add_paragraph(date_range)
            job_header.runs[0].font.bold = False
            job_header.runs[0].font.italic = True
            job_header.runs[0].font.name = 'Arial'
            job_header.runs[0].font.size = Pt(10)
            job_header.runs[0].font.color.rgb = RGBColor(64, 64, 64)
            job_header.paragraph_format.space_before = Pt(0)
            job_header.paragraph_format.space_after = Pt(0)
            job_header.paragraph_format.line_spacing = 1.0
            
            
            # Job title and company
            job_title = exp_cell.add_paragraph(f"{exp['title']} • {exp['company']}")
            job_title.runs[0].font.bold = False
            job_title.runs[0].font.name = 'Arial'
            job_title.runs[0].font.color.rgb = RGBColor(64, 64, 64)
            job_title.paragraph_format.space_before = Pt(0)
            job_title.paragraph_format.space_after = Pt(2)
            job_title.paragraph_format.line_spacing = 1.0
            
            # Job description
            if exp['achievements']:
                description_lines = exp['achievements']
                for line in description_lines:
                    if line.strip().startswith('*'):
                        # Remove the * and create bullet point
                        clean_line = line.strip()[1:].strip()
                        duty_para = exp_cell.add_paragraph(clean_line)
                        duty_para.style = 'List Bullet'
                        duty_para.runs[0].font.name = 'Arial'
                        duty_para.paragraph_format.left_indent = Inches(0.5)  # Indent bullets to the right
                    elif line.strip():
                        # Regular paragraph
                        desc_para = exp_cell.add_paragraph(line.strip())
                        desc_para.style = 'List Bullet'
                        desc_para.runs[0].font.name = 'Arial'
                        desc_para.paragraph_format.left_indent = Inches(0.5)  # Indent bullets to the right
    
    def _add_education_section(self, edu_cell):
        """Add the education section to the bottom area."""
        edu_heading = edu_cell.add_paragraph("Education")
        edu_heading.runs[0].font.bold = True
        edu_heading.runs[0].font.size = Pt(14)
        edu_heading.runs[0].font.color.rgb = RGBColor(99, 130, 118)
        edu_heading.runs[0].font.name = 'Georgia'
        edu_heading.space_after = Pt(1)
        edu_heading.paragraph_format.space_after = Pt(1.5)

        # Loop through education data
        for edu in self.resume_data['education']:
            # Format education entry
            start_date = edu.get('start_date', '') or edu.get('dates', '') or edu.get('end_date', '') or 'N/A'
            edu_year = edu_cell.add_paragraph(str(start_date))
            if edu_year.runs:
                edu_year.runs[0].font.bold = True
                edu_year.runs[0].font.italic = True
                edu_year.runs[0].font.name = 'Arial'

            edu_year.paragraph_format.space_before = Pt(0)
            edu_year.paragraph_format.space_after = Pt(0.5)

            edu_text = f"{edu['degree']}, {edu['institution']}"
            edu_para = edu_cell.add_paragraph(edu_text)
            edu_para.runs[0].font.name = 'Arial'
            edu_para.paragraph_format.space_before = Pt(0.5)
            edu_para.paragraph_format.space_after = Pt(0.5)
    
    def generate_docx(self, request_json, output_file):
        """
        Generate a DOCX resume document from JSON data.
        
        Args:
            request_json (str): JSON string containing resume data
            output_file (str): Path where the DOCX file should be saved
            
        Returns:
            str: Path to the generated DOCX file
        """
        # Parse JSON data
        self.resume_data = json.loads(request_json)
        
        # Set up document
        self._setup_document()
        
        # Add logo
        self._add_logo()
        
        # Create header
        self._create_header()
        
        # Create main table structure
        main_table = self._create_main_table()
        
        # Add content sections
        self._add_skills_section(main_table.cell(0, 0))
        self._add_experience_section(main_table.cell(0, 1))
        self._add_education_section(main_table.cell(1, 1))
        
        # Save document
        self.document.save(output_file)
        
        return output_file


def create_resume_document(request_json, output_file, page_height=14):
    """
    Legacy function for backward compatibility.
    
    Args:
        request_json (str): JSON string containing resume data
        output_file (str): Path where the DOCX file should be saved
        page_height (int): Page height in inches (default: 14)
        
    Returns:
        str: Path to the generated DOCX file
    """
    generator = ResumeDocumentGenerator(page_height=page_height)
    return generator.generate_docx(request_json, output_file)