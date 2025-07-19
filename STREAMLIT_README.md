# Streamlit Resume Processing App

A web-based interface for processing resumes through the 3-step AI pipeline.

## Features

- 📁 **PDF Upload**: Upload resume PDFs directly through the web interface
- 🔄 **3-Step Processing**: 
  - Step 1: Extract structured data from PDF
  - Step 2: Restructure using AI templates
  - Step 3: Final formatting and enhancement
- ✏️ **Editable JSON**: Edit extracted data directly in the browser
- 📤 **Export Options**: Download results in JSON and TXT formats
- 🔒 **Secure**: API key input is password-protected

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Google API key:
   - Get a Google API key for Gemini access
   - You'll enter it in the Streamlit interface

## Running the App

1. Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```

2. Open your browser to the URL shown (usually `http://localhost:8501`)

3. Enter your Google API key in the sidebar

4. Upload a PDF resume and click "Process Resume (3 Steps)"

## Usage

### 1. Upload Resume
- Click "Browse files" to upload a PDF resume
- Supported format: PDF only

### 2. Process Resume
- Click the "Process Resume (3 Steps)" button
- Wait for the AI processing to complete

### 3. View Results
The results are displayed in 4 tabs:

- **📊 Step 1: Extracted Data**: Raw structured data from PDF
- **🔄 Step 2: Restructured Text**: AI-restructured content
- **✨ Step 3: Final Data**: Final extracted and processed data
- **📄 Final Formatted**: Complete formatted resume

### 4. Edit Data
- In Step 1 and Step 3 tabs, you can edit the JSON data
- Click "Save" to update the data
- Invalid JSON will show an error

### 5. Export Results
Multiple export options:
- **Step 1 Data (JSON)**: Raw extracted data
- **Step 3 Data (JSON)**: Final processed data
- **All Results (JSON)**: Complete processing results
- **Formatted Resume (TXT)**: Final formatted text

## File Structure

```
├── streamlit_app.py          # Main Streamlit application
├── src/                      # Core processing logic
│   ├── chains/              # AI processing chains
│   ├── models/              # Data models
│   └── ...
├── requirements.txt          # Python dependencies
└── STREAMLIT_README.md       # This file
```

## Troubleshooting

### API Key Issues
- Make sure your Google API key is valid
- Check that you have access to Gemini models

### File Upload Issues
- Ensure the file is a valid PDF
- Check file size (should be reasonable for processing)

### Processing Errors
- Check the console for detailed error messages
- Ensure all dependencies are installed correctly

## Development

To modify the app:
1. Edit `streamlit_app.py` for UI changes
2. Modify `src/` files for processing logic changes
3. Restart the Streamlit app to see changes

## Security Notes

- API keys are stored only in memory during the session
- Uploaded files are temporarily stored and automatically deleted
- No data is permanently stored on the server 