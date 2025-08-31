# Resume Processor React App

A modern React application that replicates all the functionality of the Streamlit resume processing tool with an enhanced user interface.

## Features

### 🔐 Authentication System
- User login/registration
- Demo mode for testing
- Secure API key management
- Session persistence

### 📁 Resume Processing
- **Drag & Drop File Upload** - Intuitive PDF upload interface
- **3-Step AI Pipeline**:
  1. Extract structured data from PDF
  2. Restructure using AI templates
  3. Final formatting and enhancement
- **Real-time Progress Tracking** - Visual progress indicators
- **Token Usage Monitoring** - Track API consumption and costs

### ✏️ Data Editing
- **Interactive JSON Editor** - Edit extracted data directly
- **Multi-step Results View** - See results from each processing step
- **Real-time Validation** - JSON syntax checking

### 📤 Export Options
- **Multiple Formats**: JSON, TXT, DOCX
- **Quick Actions** - Sidebar export buttons
- **Batch Export** - Export all processing results

### 🔧 Prompt Management
- **Custom Prompts** - Create and manage custom AI prompts
- **Prompt Templates** - Use placeholders for dynamic content
- **Prompt Library** - Save and reuse successful prompts

### 📊 Processing History
- **Session History** - View past processing sessions
- **Result Loading** - Reload previous results for editing
- **History Management** - Delete old records

### 💰 Consumption Dashboard
- **Usage Statistics** - Track token consumption over time
- **Cost Analysis** - Monitor API costs and trends
- **Pricing Information** - Current API pricing details

## Tech Stack

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Radix UI** for accessible components
- **Zustand** for state management
- **React Hook Form** for form handling
- **React Dropzone** for file uploads
- **Axios** for API communication
- **Sonner** for notifications

## Installation

1. **Install dependencies:**
```bash
cd resume-processor-react
npm install
```

2. **Set up environment variables:**
```bash
# Create .env file in the project root
REACT_APP_API_URL=http://localhost:8000
```

3. **Start the development server:**
```bash
npm start
```

The app will open at `http://localhost:3000`

## Backend API Requirements

The React app expects a REST API backend with the following endpoints:

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/verify-api-key` - API key validation

### Resume Processing
- `POST /process/resume` - Process resume file (multipart/form-data)
- `POST /export/docx` - Export resume as DOCX

### History Management
- `GET /history/{userId}` - Get processing history
- `GET /history/result/{historyId}` - Get specific result
- `DELETE /history/{historyId}` - Delete history record

### Prompt Management
- `GET /prompts/{userId}` - Get custom prompts
- `POST /prompts` - Save custom prompt
- `DELETE /prompts/{promptId}` - Delete custom prompt

### Token Usage
- `GET /tokens/{userId}` - Get token usage history
- `GET /tokens/stats/{userId}` - Get usage statistics

## Project Structure

```
src/
├── components/
│   ├── auth/              # Authentication components
│   ├── layout/            # Layout components (Header, Sidebar)
│   ├── processing/        # Resume processing components
│   ├── prompts/           # Prompt management
│   ├── history/           # Processing history
│   ├── dashboard/         # Consumption dashboard
│   └── ui/                # Reusable UI components
├── store/                 # Zustand state management
├── services/              # API service functions
├── types/                 # TypeScript type definitions
├── lib/                   # Utility functions
└── App.tsx                # Main application component
```

## Key Differences from Streamlit Version

### Enhanced UX
- **Modern UI Design** - Clean, responsive interface with Tailwind CSS
- **Better Navigation** - Intuitive sidebar navigation
- **Real-time Feedback** - Progress indicators and toast notifications
- **Drag & Drop** - Modern file upload experience

### Improved Performance
- **Client-side State Management** - Faster UI updates
- **Optimized Rendering** - React's efficient rendering
- **Better Error Handling** - Comprehensive error states

### Additional Features
- **Responsive Design** - Works on all device sizes
- **Dark Mode Ready** - CSS custom properties for theming
- **Accessibility** - Radix UI components with built-in accessibility
- **Type Safety** - Full TypeScript support

## Usage

### 1. Authentication
- Login with existing credentials or create a new account
- Demo mode available with username: `demo`, password: `demo123`
- Set up your Google API key for AI processing

### 2. Process Resume
- Upload PDF resume using drag & drop or file picker
- Select custom prompt (optional)
- Click "Process Resume (3 Steps)" to start AI processing
- Monitor progress with real-time status updates

### 3. Edit Results
- View and edit extracted data in JSON format
- See results from each processing step
- Save changes and export in multiple formats

### 4. Manage Prompts
- Create custom prompts with placeholders
- Save and reuse successful prompt templates
- Switch between default and custom prompts

### 5. Track Usage
- Monitor token consumption and costs
- View processing history
- Export usage statistics

## Development

### Available Scripts
- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Environment Variables
- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:8000)

## Deployment

1. **Build the production version:**
```bash
npm run build
```

2. **Deploy the `build` folder** to your hosting service

3. **Configure environment variables** in your hosting platform

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Resume Processing Tool suite and follows the same license as the main project.