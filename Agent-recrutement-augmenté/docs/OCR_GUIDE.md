# OCR System Documentation

## Overview

The OCR system provides automatic text extraction from scanned PDFs using Tesseract OCR. It integrates seamlessly with the CV parser and provides structured data extraction.

## Features

- ✅ **Automatic Fallback**: Uses OCR when standard PDF extraction fails
- ✅ **High Accuracy**: ~92% confidence on quality documents
- ✅ **Structured Extraction**: Extracts name, email, phone, skills, languages
- ✅ **Multi-page Support**: Processes multiple pages efficiently
- ✅ **Multi-language**: Supports French and English

## Installation

### System Dependencies

```bash
# Install Tesseract and Poppler
brew install tesseract tesseract-lang poppler
```

### Python Dependencies

```bash
# Install required packages
pip install pytesseract pdf2image Pillow
```

## Usage

### 1. Direct OCR Usage

```python
from src.parsers.ocr_parser import OCRParser
from config.settings import OCRSettings

# Initialize OCR
settings = OCRSettings(enable_ocr=True)
parser = OCRParser(settings)

# Process PDF
result = parser.process_pdf("path/to/cv.pdf")

# Access results
print(f"Success: {result['success']}")
print(f"Confidence: {result['confidence']:.1%}")
print(f"Text: {result['raw_text']}")
print(f"Email: {result['structured_data']['email']}")
```

### 2. Integrated with CV Parser

The OCR system automatically activates when standard PDF extraction fails:

```python
from src.parsers.cv_parser import extract_text_from_pdf

# Extract text with OCR fallback
text = extract_text_from_pdf("path/to/cv.pdf", use_ocr=True)
```

## Configuration

Edit `config/settings.py`:

```python
@dataclass
class OCRSettings:
    enable_ocr: bool = True
    min_text_threshold: int = 100  # Trigger OCR if text < 100 chars
    max_pages_per_pdf: int = 10
    languages: tuple = ('fra', 'eng')  # Tesseract languages
    dpi: int = 300  # Image resolution
```

## Structured Data Extraction

The OCR system automatically extracts:

### Personal Information
- **Name**: First lines with capital letters
- **Email**: Pattern matching for email addresses
- **Phone**: French phone number formats (+33, 0)

### Professional Information
- **Skills**: Common technical keywords (Python, Java, React, etc.)
- **Languages**: French, English, Spanish, German, etc.
- **Education**: Degrees (Master, Licence, PhD, Ingénieur, etc.)
- **Experience**: Job titles (Développeur, Engineer, Manager, etc.)

## Testing

```bash
# Test OCR on sample CVs
python test_ocr.py
```

Expected output:
```
✓ Success!
  Confidence: 92.0%
  Text length: 3152 chars
  Processing time: 4.94s
  Name: Abdellah Sofi
  Email: abdellah.sofil@epfedu.fr
  Skills: Python, Java, JavaScript, C++, C#
  Languages: Français, Anglais, Arabe
```

## Performance

- **Processing Time**: ~5 seconds per page (300 DPI)
- **Accuracy**: 85-95% depending on document quality
- **Memory**: ~500MB per process
- **Languages**: French + English supported

## Troubleshooting

### Tesseract not found

```bash
# Verify installation
tesseract --version

# If not found, reinstall
brew reinstall tesseract
```

### Low confidence scores

- Increase DPI: `dpi=600` (slower but more accurate)
- Check document quality
- Ensure correct language codes

### Import errors

```bash
# Reinstall Python packages
pip install --upgrade pytesseract pdf2image Pillow
```

## API Reference

### OCRParser

#### `__init__(settings: OCRSettings = None)`
Initialize OCR parser with configuration.

#### `process_pdf(pdf_path: str) -> Dict[str, Any]`
Process a PDF file and return results.

**Returns:**
```python
{
    'success': bool,
    'raw_text': str,
    'structured_data': {
        'name': str,
        'email': str,
        'phone': str,
        'education': list,
        'experience': list,
        'skills': list,
        'languages': list
    },
    'confidence': float,  # 0.0 to 1.0
    'processing_time': float,  # seconds
    'page_count': int,
    'ocr_model': str  # 'tesseract'
}
```

## Best Practices

1. **Use OCR as fallback only**: Standard PDF extraction is faster
2. **Limit pages**: Set `max_pages_per_pdf` to avoid long processing
3. **Check confidence**: Scores < 70% may have errors
4. **Validate extracted data**: Always verify email/phone formats
5. **Monitor processing time**: Adjust DPI if too slow

## Integration with Main App

The OCR system is integrated into the Streamlit app. When a PDF is uploaded:

1. Standard extraction is attempted first (PyPDF2)
2. If text < 100 characters, OCR is triggered
3. Results are displayed with confidence scores
4. Structured data is automatically extracted

## Future Enhancements

- [ ] Support for more languages
- [ ] Image preprocessing (deskew, denoise)
- [ ] Confidence-based quality warnings
- [ ] Batch processing support
- [ ] Custom entity training

---

**Version**: 3.0  
**Last Updated**: November 2025  
**Author**: Abdellah Sofi
