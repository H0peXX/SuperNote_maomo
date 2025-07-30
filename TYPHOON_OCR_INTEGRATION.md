# Typhoon OCR Integration

This document explains the Typhoon OCR integration that has been added to the SuperNote project.

## What's New

### 🚀 **Advanced OCR Capabilities**
- **Typhoon OCR Service**: State-of-the-art OCR powered by the Typhoon API
- **Enhanced Accuracy**: Much better text extraction compared to traditional OCR
- **Multi-format Support**: PDFs, PNG, JPG, JPEG files
- **Intelligent Processing**: Context-aware text extraction with proper formatting

### 📁 **New Files Added**
```
backend/ocr/
├── typhoon_ocr_service.py          # Main service integration
├── ocr.py                         # Original OCR script from external repo
└── typhoon_ocr/                   # OCR utilities
    ├── __init__.py
    ├── ocr_utils.py               # OCR processing utilities
    └── pdf_utils.py               # PDF processing utilities
```

### 🔧 **Updated Files**
- `backend/routes/user_route.py` - Enhanced create_summary endpoint
- `requirements.txt` - Added new dependencies
- `.env.template` - Added Typhoon API key configuration

## How It Works

### 1. **Smart OCR Selection**
The system intelligently chooses the best OCR method:
- **Primary**: Typhoon OCR (when configured and available)
- **Fallback**: Tesseract OCR (existing functionality)

### 2. **Enhanced File Processing**
```python
# Supports multiple file types
supported_formats = ['.pdf', '.png', '.jpg', '.jpeg']

# Automatic format detection and processing
if use_typhoon_ocr:
    extracted_text = typhoon_ocr_service.process_uploaded_file(
        file, file.filename, task_type="default"
    )
```

### 3. **Graceful Degradation**
- If Typhoon OCR is not configured, falls back to Tesseract
- If Typhoon OCR fails, provides clear error messages
- No breaking changes to existing functionality

## Configuration

### 1. **Environment Setup**
Add to your `.env` file:
```bash
TYPHOON_API_KEY=your_typhoon_api_key_here
```

### 2. **Get Typhoon API Key**
1. Visit https://api.opentyphoon.ai/
2. Sign up for an account
3. Generate an API key
4. Add it to your environment variables

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

## New Dependencies Added
- `pypdf==5.8.0` - Modern PDF processing
- `openai==1.97.0` - Typhoon API client
- `ftfy==6.3.1` - Text fixing utilities

## Usage

### **Automatic Usage**
The OCR integration works automatically when uploading files through the create-summary endpoint:

1. Upload a PDF or image file
2. System automatically detects file type
3. Uses Typhoon OCR if available, otherwise falls back to Tesseract
4. Extracts text and creates summary using Gemini

### **API Endpoint**
```
POST /api/create-summary
Content-Type: multipart/form-data

Fields:
- title: Summary title
- files: File upload (PDF, PNG, JPG, JPEG)
```

## Benefits

### **Improved Accuracy**
- Better text recognition, especially for complex documents
- Handles tables, forms, and structured content
- Context-aware processing

### **Enhanced Format Support**  
- Full support for images (PNG, JPG, JPEG)
- Better PDF processing with page-by-page analysis
- Maintains document structure and formatting

### **Better Error Handling**
- Clear error messages for unsupported formats
- Graceful fallbacks when services are unavailable
- Detailed logging for troubleshooting

## Troubleshooting

### **Common Issues**

1. **"Typhoon OCR not available"**
   - Check if TYPHOON_API_KEY is set in your .env file
   - Verify API key is valid
   - System will fall back to Tesseract OCR

2. **"Only PDF files supported with fallback OCR"**
   - Typhoon OCR is not configured
   - Add API key to enable image processing

3. **Import errors**
   - Run `pip install -r requirements.txt`
   - Ensure all dependencies are installed

### **Testing**
You can test the integration by:
1. Starting the server: `.\run-dev.ps1`
2. Uploading a PDF or image through the create-summary page
3. Check console logs for OCR method being used

## Architecture

### **Service Layer**
```python
class TyphoonOCRService:
    def process_uploaded_file(file_obj, filename, task_type="default")
    def process_pdf_file(file_path, task_type="default")  
    def process_image_file(file_path, task_type="default")
    def is_available()  # Check if service is configured
```

### **Integration Points**
- Integrated into existing `/api/create-summary` endpoint
- Maintains backward compatibility
- No changes required to frontend

## Future Enhancements

Potential improvements that could be added:
- Batch processing for multiple files
- OCR confidence scoring
- Custom OCR task types ("structure" mode)
- Caching of OCR results
- Progress indicators for large files

---

**Need Help?**
If you encounter any issues with the Typhoon OCR integration, check the server logs for detailed error messages and ensure your API key is properly configured.
