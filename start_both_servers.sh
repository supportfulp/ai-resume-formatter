#!/bin/bash

# Resume Processor - Start Both Servers
# This script starts both the API server and React frontend

echo "🚀 Starting Resume Processor Application"
echo "========================================"

# Check if conda environment 'rf' exists and activate it
if conda info --envs | grep -q "rf"; then
    echo "📦 Activating conda environment 'rf'..."
    eval "$(conda shell.bash hook)"
    conda activate rf
else
    echo "⚠️  Conda environment 'rf' not found, using current environment"
fi

# Start API server in background
echo "🖥️  Starting API server on port 8000..."
python start_api_server.py &
API_PID=$!

# Wait a moment for API server to start
sleep 3

# Start React frontend in background
echo "⚛️  Starting React frontend on port 3000..."
cd resume-processor-react
npm start &
REACT_PID=$!

# Go back to root directory
cd ..

echo ""
echo "✅ Both servers are starting up!"
echo "📍 API Server: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo "📍 React App: http://localhost:3000"
echo ""
echo "🛑 Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $API_PID 2>/dev/null
    kill $REACT_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for background processes
wait