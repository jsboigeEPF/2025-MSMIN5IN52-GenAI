#!/usr/bin/env python3
"""
Test OCR Functionality
Simple script to test OCR on CV samples.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.parsers.ocr_parser import OCRParser
from config.settings import OCRSettings


def test_ocr():
    """Test OCR on sample CVs."""
    
    print("🚀 Testing OCR System")
    print("=" * 60)
    
    # Initialize OCR
    settings = OCRSettings(enable_ocr=True)
    parser = OCRParser(settings)
    
    # Find CV samples
    cv_folder = Path("data/cv_samples")
    pdf_files = list(cv_folder.glob("*.pdf"))
    
    if not pdf_files:
        print(f"\n⚠️  No PDF files found in {cv_folder}")
        print("Please add sample PDFs to test.")
        return
    
    print(f"\nFound {len(pdf_files)} PDF file(s)\n")
    
    # Test each PDF
    for pdf_path in pdf_files[:3]:  # Test first 3 files
        print(f"\n📄 Processing: {pdf_path.name}")
        print("-" * 60)
        
        result = parser.process_pdf(str(pdf_path))
        
        if result['success']:
            print(f"✓ Success!")
            print(f"  Confidence: {result['confidence']:.1%}")
            print(f"  Text length: {len(result['raw_text'])} chars")
            print(f"  Processing time: {result['processing_time']:.2f}s")
            
            # Show extracted data
            sd = result['structured_data']
            if sd.get('name'):
                print(f"  Name: {sd['name']}")
            if sd.get('email'):
                print(f"  Email: {sd['email']}")
            if sd.get('phone'):
                print(f"  Phone: {sd['phone']}")
            if sd.get('skills'):
                print(f"  Skills: {', '.join(sd['skills'][:5])}")
            if sd.get('languages'):
                print(f"  Languages: {', '.join(sd['languages'])}")
        else:
            print(f"✗ Failed: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")


if __name__ == "__main__":
    test_ocr()
