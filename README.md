# Huffman File Compression System

This project implements a file compression system using Huffman coding algorithm. It consists of a React frontend and a Flask backend.

## Features

- File upload and download
- Huffman compression algorithm implementation
- File decompression
- User authentication (admin/normal user)
- Compressed file size reduction

## Setup Instructions

### Frontend Setup
1. Install Node.js dependencies:
```bash
npm install
```

2. Start the frontend development server:
```bash
npm run dev
```

### Backend Setup
1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a Python virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Start the Flask server:
```bash
python app.py
```

## Usage

1. Access the application at `http://localhost:5173` (or the port shown in your Vite dev server)
2. Login credentials:
   - Admin: username: "admin", password: "admin123"
   - Normal User: username: "normal", password: "user123"
3. Upload a file using the file input
4. Use the Compress/Decompress buttons (admin only) to process files
5. Download the processed files using the provided link

## Implementation Details

The project uses Huffman coding for file compression:
1. Builds a frequency table of characters
2. Creates a Huffman tree using a priority queue
3. Generates binary codes for each character
4. Compresses data using generated codes
5. Stores metadata for decompression
6. Implements efficient decompression using stored metadata

## File Structure

```
.
├── src/                    # Frontend React code
├── backend/               # Backend Flask code
│   ├── app.py            # Main server file
│   ├── requirements.txt  # Python dependencies
│   └── uploads/         # Uploaded files directory
└── README.md             # This file
```
