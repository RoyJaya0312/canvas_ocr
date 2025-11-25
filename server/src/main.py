from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
import pdfplumber
import io
import os
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set tesseract path
TESSERACT_PATH = r"C:\Users\Jayasmita\Desktop\pytesseract\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_text_from_image(image_file):
    """Extract text from image file using Tesseract OCR"""
    try:
        image = Image.open(image_file)
        # Custom config for better OCR accuracy: OEM 3 (default engine + neural nets), PSM 6 (uniform block of text)
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=custom_config)
        # Normalize to uppercase to reduce case-related OCR errors
        text = text.upper()
        return text
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")


def extract_text_from_image_aadhar_pan(image_file):
    """Extract text from image file using Tesseract OCR with resolution enhancement"""
    try:
        image = Image.open(image_file)
        
        # Get current DPI (default to 72 if not set)
        current_dpi = image.info.get('dpi', (72, 72))[0]
        
        # Target DPI
        target_dpi = 450
        
        # If current DPI is less than target, upscale the image
        if current_dpi < target_dpi:
            scale_factor = target_dpi / current_dpi
            new_width = int(image.width * scale_factor)
            new_height = int(image.height * scale_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"DEBUG: Upscaled image from {current_dpi} DPI to {target_dpi} DPI")
        
        # Custom config for better OCR accuracy
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=custom_config)
        text = text.upper()
        return text
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")



def extract_formatted_text_from_image(image_file):
    """Extract formatted text from image file using Tesseract OCR with PSM 3 for line-based output"""
    try:
        image = Image.open(image_file)
        # Use PSM 3 for raw line recognition to preserve line breaks
        custom_config = r'--oem 3 --psm 3'
        text = pytesseract.image_to_string(image, config=custom_config)
        # Normalize to uppercase to reduce case-related OCR errors
        text = text.upper()
        return text
    except Exception as e:
        raise Exception(f"Error processing image for formatted text: {str(e)}")

def process_pdf_page_ocr(page):
    """Helper function to process a single PDF page for OCR"""
    try:
        # Increased resolution to 450 for better accuracy
        page_image = page.to_image(resolution=800).original
        # Custom config for better OCR accuracy: OEM 3 (default engine + neural nets), PSM 6 (uniform block of text)
        custom_config = r'--oem 3 --psm 6'
        page_text = pytesseract.image_to_string(page_image, config=custom_config)
        # Normalize to uppercase to reduce case-related OCR errors
        page_text = page_text.upper()
        return page_text if page_text else ""
    except Exception as e:
        print(f"Warning: Skipping page due to error - {str(e)}")
        return ""

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file using pdfplumber, fallback to Tesseract for image-based PDFs"""
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # Normalize the extracted text to uppercase
        text = text.upper()

        # If no text was extracted, assume it's an image-based PDF and use Tesseract
        if not text.strip():
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    page_texts = list(executor.map(process_pdf_page_ocr, pdf.pages))
                for page_text in page_texts:
                    if page_text:
                        text += page_text + "\n"

        return text
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")

def extract_text_from_pdf_first_page(pdf_file):
    """Extract text from first page of PDF file only, using pdfplumber, fallback to Tesseract for image-based PDFs"""
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            if len(pdf.pages) > 0:
                page = pdf.pages[0]
                page_text = page.extract_text()
                if page_text:
                    text = page_text

        # If no text was extracted, assume it's an image-based PDF and use Tesseract
        if not text.strip():
            with pdfplumber.open(pdf_file) as pdf:
                if len(pdf.pages) > 0:
                    page = pdf.pages[0]
                    page_image = page.to_image(resolution=800).original
                    # Custom config for better OCR accuracy: OEM 3 (default engine + neural nets), PSM 6 (uniform block of text)
                    custom_config = r'--oem 3 --psm 6'
                    page_text = pytesseract.image_to_string(page_image, config=custom_config)
                    if page_text:
                        text = page_text

        # Normalize the extracted text to uppercase
        text = text.upper()

        print(f"DEBUG: Extracted text length from first page: {len(text)} characters")
        print(f"DEBUG: First 1000 characters: {text[:1000]}")

        return text
    except Exception as e:
        raise Exception(f"Error processing PDF first page: {str(e)}")
    


def extract_text_first_and_last_page(pdf_file):
    """Extract text from first and last page of PDF file, using pdfplumber, fallback to Tesseract for image-based PDFs"""
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            total_pages = len(pdf.pages)
            
            if total_pages == 0:
                return ""
            
            # Extract first page
            first_page = pdf.pages[0]
            first_page_text = first_page.extract_text()
            if first_page_text:
                text += first_page_text + "\n\n--- PAGE BREAK ---\n\n"
            
            # Extract last page (only if it's different from first page)
            if total_pages > 1:
                last_page = pdf.pages[-1]
                last_page_text = last_page.extract_text()
                if last_page_text:
                    text += last_page_text

        # If no text was extracted, assume it's an image-based PDF and use Tesseract
        if not text.strip():
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                total_pages = len(pdf.pages)
                
                if total_pages == 0:
                    return ""
                
                # OCR first page
                first_page = pdf.pages[0]
                first_page_image = first_page.to_image(resolution=800).original
                custom_config = r'--oem 3 --psm 6'
                first_page_text = pytesseract.image_to_string(first_page_image, config=custom_config)
                if first_page_text:
                    text += first_page_text + "\n\n--- PAGE BREAK ---\n\n"
                
                # OCR last page (only if it's different from first page)
                if total_pages > 1:
                    last_page = pdf.pages[-1]
                    last_page_image = last_page.to_image(resolution=800).original
                    last_page_text = pytesseract.image_to_string(last_page_image, config=custom_config)
                    if last_page_text:
                        text += last_page_text

        # Normalize the extracted text to uppercase
        text = text.upper()

        print(f"DEBUG: Extracted text length from first and last page: {len(text)} characters")
        print(f"DEBUG: First 1000 characters: {text[:1000]}")

        return text
    except Exception as e:
        raise Exception(f"Error processing PDF first and last page: {str(e)}")



import re

def extract_dob(file_input, file_type='pdf'):
    try:
        # Extract text based on file type
        if file_type.lower() == 'pdf':
            text = extract_text_from_pdf(file_input)
        elif file_type.lower() == 'image':
            text = extract_text_from_image_aadhar_pan(file_input)
        else:
            print(f"ERROR: Unsupported file type: {file_type}")
            return None
        
        if not text:
            print("ERROR: No text extracted from file")
            return None
        
        print(f"DEBUG: Extracted text (first 500 chars): {text[:500]}")
        
        # Date patterns for DOB extraction
        # Priority order: most specific to least specific
        date_patterns = [
            # dd-mm-yyyy (with various separators)
            (r'\b(\d{2})[-/.](\d{2})[-/.](\d{4})\b', 'dd-mm-yyyy'),
            # dd-mm-yy
            (r'\b(\d{2})[-/.](\d{2})[-/.](\d{2})\b', 'dd-mm-yy'),
            # yyyy-mm-dd (ISO format)
            (r'\b(\d{4})[-/.](\d{2})[-/.](\d{2})\b', 'yyyy-mm-dd'),
            # dd month yyyy (e.g., 15 August 1990)
            (r'\b(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[,\s]+(\d{4})\b', 'dd-month-yyyy'),
            # month dd, yyyy (e.g., August 15, 1990)
            (r'\b(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\s+(\d{1,2})[,\s]+(\d{4})\b', 'month-dd-yyyy'),
        ]
        
        # Common DOB keywords to look for context
        dob_keywords = [
            r'date\s+of\s+birth',
            r'dob',
            r'birth\s+date',
            r'date\s+of\s+brith',  # common typo
            r'born',
            r'd\.?o\.?b\.?',
        ]
        
        # Search for DOB with context
        for keyword in dob_keywords:
            # Look for keyword followed by date within 50 characters
            keyword_pattern = rf'(?i){keyword}[:\s]{{0,50}}'
            
            for date_pattern, format_type in date_patterns:
                combined_pattern = keyword_pattern + date_pattern
                match = re.search(combined_pattern, text, re.IGNORECASE)
                
                if match:
                    # Extract the date part (exclude the keyword)
                    date_match = re.search(date_pattern, match.group(), re.IGNORECASE)
                    if date_match:
                        dob = date_match.group().strip()
                        print(f"DEBUG: Found DOB with context - {dob}")
                        return {
                            'dob': dob,
                            'format': format_type,
                            'confidence': 'high'
                        }
        
        # If no DOB found with context, try to find dates without context
        # (lower confidence, return first valid-looking date)
        print("DEBUG: No DOB found with context, searching for dates without context...")
        
        for date_pattern, format_type in date_patterns:
            matches = re.finditer(date_pattern, text, re.IGNORECASE)
            
            for match in matches:
                dob = match.group().strip()
                
                # Basic validation: check if it looks like a reasonable birth date
                # (avoid matching other dates like transaction dates, expiry dates, etc.)
                if format_type == 'dd-mm-yyyy':
                    parts = re.split(r'[-/.]', dob)
                    day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                    
                    # Reasonable birth year range (1900-2024)
                    if 1900 <= year <= 2024 and 1 <= month <= 12 and 1 <= day <= 31:
                        print(f"DEBUG: Found potential DOB (no context) - {dob}")
                        return {
                            'dob': dob,
                            'format': format_type,
                            'confidence': 'low'
                        }
        
        print("DEBUG: No DOB found in document")
        return None
    
    except Exception as e:
        print(f"ERROR: Exception while extracting DOB: {str(e)}")
        return None



def extract_aadhar_number(file_input, file_type='pdf'):
    """
    Extract Aadhaar number from image or PDF file.
    Uses extract_text_from_image_aadhar_pan for images,
    extract_text_from_pdf for PDFs.
    Aadhaar format expected: 
    - Standard: xxxx xxxx xxxx (3 sets of 4 digits) OR
    - Full: xxxx xxxx xxxx xxxx (4 sets of 4 digits)
    
    Params:
      - file_input: file-like object or file path
      - file_type: 'image' or 'pdf' (default 'pdf')
      
    Returns:
      - Aadhaar number string if found, else None
    """
    try:
        if file_type.lower() == 'image':
            text = extract_text_from_image_aadhar_pan(file_input)
        elif file_type.lower() == 'pdf':
            text = extract_text_from_pdf(file_input)
        else:
            print(f"ERROR: Unsupported file type: {file_type}")
            return None

        if not text:
            print("ERROR: No text extracted from file")
            return None

        print(f"DEBUG: Extracted text (first 500 chars): {text[:500]}")

        # Pattern 1: Standard Aadhaar format - 3 sets of 4 digits (12 digits total)
        # Example: 7723 2356 1747
        aadhar_pattern_3 = re.compile(r'\b(\d{4})\s+(\d{4})\s+(\d{4})\b')
        
        # # Pattern 2: Full Aadhaar format - 4 sets of 4 digits (16 digits total, less common)
        # # Example: 1234 5678 9012 3456
        # aadhar_pattern_4 = re.compile(r'\b(\d{4})\s+(\d{4})\s+(\d{4})\s+(\d{4})\b')
        
        # Pattern 3: Aadhaar with variable spacing (handles OCR errors)
        # Example: 7723  2356   1747 (multiple spaces)
        aadhar_pattern_flex = re.compile(r'\b(\d{4})\s{1,5}(\d{4})\s{1,5}(\d{4})\b')

        # # Try to find 4-part Aadhaar first (more specific)
        # match = aadhar_pattern_4.search(text)
        # if match:
        #     aadhar_number = ' '.join(match.groups())
        #     print(f"DEBUG: Found 4-part Aadhaar Number: {aadhar_number}")
        #     return aadhar_number

        # Try to find 3-part Aadhaar (standard format)
        match = aadhar_pattern_3.search(text)
        if match:
            aadhar_number = ' '.join(match.groups())
            print(f"DEBUG: Found 3-part Aadhaar Number: {aadhar_number}")
            return aadhar_number

        # Try flexible spacing pattern as fallback
        match = aadhar_pattern_flex.search(text)
        if match:
            aadhar_number = ' '.join(match.groups())
            print(f"DEBUG: Found Aadhaar Number (flexible spacing): {aadhar_number}")
            return aadhar_number

        # Pattern 4: Look for Aadhaar near "UID" keyword (common in Aadhaar cards)
        # Example: "UID : 9176 0790 6943 5824" or "UID: 7723 2356 1747"
        uid_pattern = re.compile(
            r'(?i)(?:uid|uidai|enrollment|enrolment|aadhaar|aadhar)[\s:]*'
            r'(\d{4})\s+(\d{4})\s+(\d{4})(?:\s+(\d{4}))?',
            re.IGNORECASE
        )
        
        match = uid_pattern.search(text)
        if match:
            groups = [g for g in match.groups() if g is not None]
            aadhar_number = ' '.join(groups)
            print(f"DEBUG: Found Aadhaar Number near UID keyword: {aadhar_number}")
            return aadhar_number

        # Pattern 5: Look for 12 consecutive digits (no spaces) and format them
        # Example: 772323561747 → 7723 2356 1747
        consecutive_pattern = re.compile(r'\b(\d{12})\b')
        match = consecutive_pattern.search(text)
        if match:
            aadhar_raw = match.group(1)
            # Format as xxxx xxxx xxxx
            aadhar_number = f"{aadhar_raw[0:4]} {aadhar_raw[4:8]} {aadhar_raw[8:12]}"
            print(f"DEBUG: Found 12-digit sequence, formatted as: {aadhar_number}")
            return aadhar_number

        print("DEBUG: No Aadhaar number found in text")
        return None

    except Exception as e:
        print(f"ERROR: Exception while extracting Aadhaar number: {str(e)}")
        return None



@app.route('/extract-text-first-last-page', methods=['POST'])
def extract_text_first_last_page():
    """Endpoint to extract text from first and last page of uploaded PDF file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext != '.pdf':
            return jsonify({'error': 'First and last page extraction is only supported for PDF files'}), 400

        extracted_text = extract_text_from_pdf_first_and_last_page(file)

        return jsonify({
            'extracted_text': extracted_text,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
def extract_formatted_text_from_pdf(pdf_file):
    """Extract formatted text from PDF file using pdfplumber, fallback to Tesseract for image-based PDFs"""
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # Normalize the extracted text to uppercase
        text = text.upper()

        # If no text was extracted, assume it's an image-based PDF and use Tesseract with PSM 3
        if not text.strip():
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    page_texts = list(executor.map(process_formatted_pdf_page_ocr, pdf.pages))
                for page_text in page_texts:
                    if page_text:
                        text += page_text + "\n"

        return text
    except Exception as e:
        raise Exception(f"Error processing PDF for formatted text: {str(e)}")

def process_formatted_pdf_page_ocr(page):
    """Helper function to process a single PDF page for formatted OCR"""
    try:
        # Increased resolution to 450 for better accuracy
        page_image = page.to_image(resolution=800).original
        # Use PSM 3 for raw line recognition to preserve line breaks
        custom_config = r'--oem 3 --psm 3'
        page_text = pytesseract.image_to_string(page_image, config=custom_config)
        # Normalize to uppercase to reduce case-related OCR errors
        page_text = page_text.upper()
        return page_text if page_text else ""
    except Exception as e:
        print(f"Warning: Skipping page due to error - {str(e)}")
        return ""

def extract_tables_from_pdf(pdf_file):
    """Extract tables from PDF file using pdfplumber"""
    try:
        all_tables = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        df = pd.DataFrame(table)
                        df = df.fillna('')
                        all_tables.append(df)
        if all_tables:
            combined_df = pd.concat(all_tables, ignore_index=True)
            combined_df = combined_df.fillna('')
            return combined_df.values.tolist()
        else:
            return []
    except Exception as e:
        raise Exception(f"Error processing PDF tables: {str(e)}")

def extract_pan_number(text):
    """Extract PAN number from text using improved regex patterns"""
    print(f"DEBUG: Searching for PAN in text (first 500 chars): {text[:500]}")

    # 1️⃣ Labeled PAN (looks for "PAN", "PAN No", "PAN Number")
    labeled_pan_pattern = re.compile(
        r'(?i)\b(?:pan(?:\s*(?:no\.?|number)?)?)\b[:\-\s]*'
        r'([A-Z]{3}[ABCFGHLJPTK][A-Z]\s*[0-9]{4}\s*[A-Z])',
        re.IGNORECASE
    )

    # 2️⃣ Fallback pattern (general PAN match with stricter rules)
    generic_pan_pattern = re.compile(
        r'\b(?<![A-Za-z])'
        r'[A-Z]{3}'
        r'[ABCFGHLJPTK]'
        r'[A-Z]'
        r'\s*'
        r'[0-9]{4}'
        r'\s*'
        r'[A-Z]'
        r'(?![A-Za-z0-9])\b',
        re.IGNORECASE
    )

    # Try labeled pattern first
    lbl_match = labeled_pan_pattern.search(text)
    if lbl_match:
        raw_pan = lbl_match.group(1).replace(" ", "").upper()
        print(f"DEBUG: Found labeled PAN: {raw_pan}")
    else:
        # Try generic pattern
        pan_match = generic_pan_pattern.search(text)
        raw_pan = pan_match.group(0).replace(" ", "").upper() if pan_match else ""
        if raw_pan:
            print(f"DEBUG: Found generic PAN: {raw_pan}")

    if raw_pan and len(raw_pan) == 10:
        # Normalize OCR misreads in digits only (positions 5–8)
        letters_first3 = raw_pan[:3]
        fourth_char = raw_pan[3]
        fifth_char = raw_pan[4]
        digits = list(raw_pan[5:9])
        last = raw_pan[9]

        # Clean up digit misreads
        for i, ch in enumerate(digits):
            if ch == 'O':
                digits[i] = '0'
            if ch in ('I', 'L'):
                digits[i] = '1'

        pan_number = letters_first3 + fourth_char + fifth_char + ''.join(digits) + last
        print(f"DEBUG: Final PAN after normalization: {pan_number}")
        return pan_number
    elif raw_pan:
        print(f"DEBUG: Returning raw PAN (length {len(raw_pan)}): {raw_pan}")
        return raw_pan

    print("DEBUG: No PAN found")
    return None

def extract_opening_balance(text):
    """Extract Opening Balance from text using regex patterns"""
    print(f"DEBUG: Searching for Opening Balance in text (first 500 chars): {text[:500]}")
    
    # Helper function to check if a number is part of a date/timestamp
    def is_part_of_date_context(full_text, number_str, position):
        """Check if the number appears within a date/timestamp context"""
        # Get context around the number (30 chars before and after)
        start = max(0, position - 30)
        end = min(len(full_text), position + len(number_str) + 30)
        context = full_text[start:end]
        
        # Check if this specific number is part of a date pattern
        # Look for patterns like: 18-08-25, 18/08/25, 18:10:49
        date_time_in_context = [
            r'\b' + re.escape(number_str) + r'[-/:]\d{1,2}[-/:]\d{2,4}',  # 18-08-25
            r'\d{1,2}[-/:]+' + re.escape(number_str) + r'[-/:]\d{2,4}',  # 08-18-25
            r'\d{2,4}[-/:]\d{1,2}[-/:]+' + re.escape(number_str) + r'\b',  # 2025-08-18
            r'\b' + re.escape(number_str) + r':\d{2}:\d{2}',  # 18:10:49
            r'\d{1,2}:+' + re.escape(number_str) + r':\d{2}',  # 16:18:49
        ]
        
        for pattern in date_time_in_context:
            if re.search(pattern, context):
                return True
        
        return False
    
    # Pattern 1: Labeled opening balance with amount on same line
    # Matches both spaced and non-spaced variations
    # Spaced: "OPENING BALANCE : 22.38(CR)" or "Opening Balance: 42,650.00"
    # Non-spaced: "OpeningBalance:22.38" or "OPENINGBALANCE22.38"
    labeled_pattern = re.compile(
        r'(?i)(?:'
        r'(opening\s+balance|openingbalance)(?:\s+amount)?'
        r'|openingbal\.?'
        r'|opening\s+ledger\s+balance|openingledgerbalance'
        r'|opening\s+available\s+balance|openingavailablebalance'
        r'|balance\s+brought\s+forward|balancebroughtforward'
        r'|brought\s+forward(?:\s+balance)?|broughtforward(?:balance)?'
        r'|balance\s+b/f|balanceb/f'
        r'|b/f\s+balance|b/fbalance'
        r'|opening\s+book\s+balance|openingbookbalance'
        r')\s*[:\-]?\s*'
        r'([0-9,]*\.?[0-9]+)\s*(?:\((?:CR|DR)\))?',
        re.IGNORECASE
    )
    
    match = labeled_pattern.search(text)
    if match:
        opening_balance = match.group(2).replace(',', '')
        credit_debit = match.group(0)
        is_credit = 'CR' in credit_debit.upper()
        is_debit = 'DR' in credit_debit.upper()
        print(f"DEBUG: Found Opening Balance (labeled): {opening_balance} {'(CR)' if is_credit else '(DR)' if is_debit else ''}")
        return {
            'amount': opening_balance,
            'type': 'CR' if is_credit else 'DR' if is_debit else 'UNKNOWN',
            'raw': match.group(0)
        }
    
    # Pattern 2: Table format - headers in one line, values in next line
    # Supports both spaced and non-spaced variations
    header_pattern = re.compile(
        r'(?i)('
        r'(opening\s+balance|openingbalance)(?:\s+amount)?'
        r'|opening\s+bal\.?|openingbal\.?'
        r'|opening\s+ledger\s+balance|openingledgerbalance'
        r'|opening\s+available\s+balance|openingavailablebalance'
        r'|balance\s+brought\s+forward|balancebroughtforward'
        r'|brought\s+forward(?:\s+balance)?|broughtforward(?:balance)?'
        r'|balance\s+b/f|balanceb/f'
        r'|b/f\s+balance|b/fbalance'
        r'|opening\s+book\s+balance|openingbookbalance'
        r')',
        re.IGNORECASE
    )
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        header_match = header_pattern.search(line)
        if header_match:
            # Found header line, now find the position of "opening balance" in the header
            header_position = header_match.start()
            
            # Check if there's a number on the same line (inline format)
            inline_number_pattern = re.compile(
                r'(?i)(?:'
                r'opening\s+balance(?:\s+amount)?|openingbalance(?:amount)?'
                r'|opening\s+bal\.?|openingbal\.?'
                r'|opening\s+ledger\s+balance|openingledgerbalance'
                r'|opening\s+available\s+balance|openingavailablebalance'
                r'|balance\s+brought\s+forward|balancebroughtforward'
                r'|brought\s+forward(?:\s+balance)?|broughtforward(?:balance)?'
                r'|balance\s+b/f|balanceb/f'
                r'|b/f\s+balance|b/fbalance'
                r'|opening\s+book\s+balance|openingbookbalance'
                r')\s*[:\-]?\s*([0-9,]+\.?\d*)',
                re.IGNORECASE
            )
            
            inline_match = inline_number_pattern.search(line)
            if inline_match:
                opening_balance = inline_match.group(1).replace(',', '')
                print(f"DEBUG: Found Opening Balance (inline table): {opening_balance}")
                return {
                    'amount': opening_balance,
                    'type': 'UNKNOWN',
                    'raw': inline_match.group(0)
                }
            
            # Look for numbers in the next few lines (up to 3 lines down)
            for j in range(1, 4):
                if i + j < len(lines):
                    value_line = lines[i + j]
                    
                    # First, skip the entire line if it starts with date-related keywords
                    if re.match(r'^\s*(?:AS\s+ON|DATE|ON)\s+\d', value_line, re.IGNORECASE):
                        print(f"DEBUG: Line {j} starts with date context, extracting numbers after date")
                        # Remove the date portion and continue with remaining numbers
                        # Remove everything up to and including "PM" or "AM" or time pattern
                        cleaned_line = re.sub(r'^.*?(?:\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)\s*', '', value_line, flags=re.IGNORECASE)
                        if cleaned_line:
                            value_line = cleaned_line
                            print(f"DEBUG: Cleaned line: {cleaned_line[:100]}")
                    
                    # Extract all numbers from the value line
                    numbers = re.findall(r'[0-9,]+\.?\d*', value_line)
                    if numbers:
                        # Filter out numbers that are part of dates
                        for num in numbers:
                            num_clean = num.replace(',', '')
                            # Find position of this number in the value line
                            num_pos = value_line.find(num)
                            
                            # Check if it's part of a date/time in this specific line
                            if is_part_of_date_context(value_line, num, num_pos):
                                print(f"DEBUG: Skipping number '{num}' - part of date/time")
                                continue
                            
                            # Found a valid opening balance
                            opening_balance = num_clean
                            print(f"DEBUG: Found Opening Balance (table format, line {j} below): {opening_balance}")
                            return {
                                'amount': opening_balance,
                                'type': 'UNKNOWN',
                                'raw': num
                            }
    
    # Pattern 3: Generic fallback - find any number near "opening balance"
    # Supports both spaced and non-spaced variations
    generic_pattern = re.compile(
        r'(?i)(?:'
        r'opening\s+balance(?:\s+amount)?|openingbalance(?:amount)?'
        r'|opening\s+bal\.?|openingbal\.?'
        r'|opening\s+ledger\s+balance|openingledgerbalance'
        r'|opening\s+available\s+balance|openingavailablebalance'
        r'|balance\s+brought\s+forward|balancebroughtforward'
        r'|brought\s+forward(?:\s+balance)?|broughtforward(?:balance)?'
        r'|balance\s+b/f|balanceb/f'
        r'|b/f\s+balance|b/fbalance'
        r'|opening\s+book\s+balance|openingbookbalance'
        r')'
        r'[\s\S]{0,50}?'  # Look ahead up to 50 characters
        r'([0-9,]+\.?\d*)',
        re.IGNORECASE
    )
    
    match = generic_pattern.search(text)
    if match:
        opening_balance = match.group(1).replace(',', '')
        print(f"DEBUG: Found Opening Balance (generic): {opening_balance}")
        return {
            'amount': opening_balance,
            'type': 'UNKNOWN',
            'raw': match.group(0)
        }
    
    print("DEBUG: No Opening Balance found")
    return None
def extract_closing_balance(text):
    """Extract Closing Balance from text using regex patterns"""
    print(f"DEBUG: Searching for Closing Balance in text : {text[:]}")

    # Pattern 1: Labeled closing balance with amount on same line
    # Matches: "CLOSING BALANCE : 2,983.38(CR)" or "Closing Balance: 10,77,026.42" or "Closing Balance: .00"
    labeled_pattern = re.compile(
        r'(?:'
        r'(?:closingbalance|closing\s+balance)(?:\s+amount)?'
        r'|(?:closingbal|closing\s+bal\.?)'
        r'|(?:closingledgerbalance|closing\s+ledger\s+balance)'
        r'|(?:closingavailablebalance|closing\s+available\s+balance)'
        r'|(?:balancecarriedforward|balance\s+carried\s+forward)'
        r'|(?:carriedforward(?:balance)?|carried\s+forward(?:\s+balance)?)'
        r'|(?:balancec/f|balance\s+c\/f)'
        r'|(?:c/fbalance|c\/f\s+balance)'
        r'|(?:bookclosingbalance|book\s+closing\s+balance)'
        r')\s*[:\-]?\s*'
        r'([0-9,]*\.?\d*)\s*(?:\((?:CR|DR)\))?',
        re.IGNORECASE
    )

    match = labeled_pattern.search(text)
    if match:
        closing_balance = match.group(1).replace(',', '')
        credit_debit = match.group(0)
        is_credit = 'CR' in credit_debit.upper()
        is_debit = 'DR' in credit_debit.upper()
        
        print(f"DEBUG: Found Closing Balance (labeled): {closing_balance} {'(CR)' if is_credit else '(DR)' if is_debit else ''}")
        return {
            'amount': closing_balance,
            'type': 'CR' if is_credit else 'DR' if is_debit else 'UNKNOWN',
            'raw': match.group(0)
        }

    # ----------------------------
    # Pattern 2 (Improved): Table format extraction using column positions
    # ----------------------------
    # header_pattern finds possible closing-balance header (with/without spaces)
    header_pattern = re.compile(
        r'(closing\s*balance|closingbalance|closing\s*bal\.?|closingbal|closingledgerbalance|closing\s*ledger\s*balance|'
        r'closingavailablebalance|closing\s*available\s*balance|balancecarriedforward|balance\s*carried\s*forward|'
        r'carriedforward|carried\s*forward|balancec/f|balance\s*c/f|c/fbalance|c/f\s*balance|'
        r'bookclosingbalance|book\s*closing\s*balance)',
        re.IGNORECASE
    )

    lines = text.split("\n")

    for i, line in enumerate(lines):
        header_match = header_pattern.search(line)
        if header_match:
            # First — check if there's a number on the same header line (inline number)
            inline_number_pattern = re.compile(
                r'(?:'
                r'(?:closingbalance|closing\s+balance)(?:\s+amount)?'
                r'|(?:closingbal|closing\s+bal\.?)'
                r'|(?:closingledgerbalance|closing\s+ledger\s+balance)'
                r'|(?:closingavailablebalance|closing\s+available\s+balance)'
                r'|(?:balancecarriedforward|balance\s+carried\s+forward)'
                r'|(?:carriedforward(?:balance)?|carried\s+forward(?:\s+balance)?)'
                r'|(?:balancec/f|balance\s+c\/f)'
                r'|(?:c/fbalance|c\/f\s+balance)'
                r'|(?:bookclosingbalance|book\s+closing\s+balance)'
                r')\s+([0-9,]+\.?\d*)',
                re.IGNORECASE
            )
            inline_match = inline_number_pattern.search(line)
            if inline_match:
                closing_balance = inline_match.group(1).replace(',', '')
                print(f"DEBUG: Found Closing Balance (inline table): {closing_balance}")
                return {
                    'amount': closing_balance,
                    'type': 'UNKNOWN',
                    'raw': inline_match.group(0)
                }

            # Collect positions of the closing header occurrences (handles 'closingbalance' and 'closing balance')
            header_keywords = list(re.finditer(header_pattern, line))

            header_cols = []
            for hk in header_keywords:
                header_cols.append({
                    "keyword": hk.group(),
                    "start": hk.start(),
                    "end": hk.end()
                })

            # Choose the first closing header occurrence as the column reference
            closing_col = None
            for h in header_cols:
                if "closing" in h["keyword"].lower():
                    closing_col = h
                    break

            if not closing_col:
                # if somehow none, continue scanning next lines
                continue

            # Look below for numbers (within next 3 lines)
            for j in range(1, 4):
                if i + j >= len(lines):
                    break

                value_line = lines[i + j]

                # Find all numbers + their positions in the value line
                number_matches = list(re.finditer(r'[0-9,]+\.?\d*', value_line))

                best_number = None
                best_distance = float("inf")

                # Pick the number whose horizontal center is closest to the closing header center
                header_pos = (closing_col["start"] + closing_col["end"]) / 2
                for nm in number_matches:
                    num_pos = (nm.start() + nm.end()) / 2
                    dist = abs(num_pos - header_pos)

                    if dist < best_distance:
                        best_distance = dist
                        best_number = nm.group()

                if best_number:
                    closing_balance = best_number.replace(",", "")
                    print(f"DEBUG: Found Closing Balance (table column detection): {closing_balance}")
                    return {
                        "amount": closing_balance,
                        "type": "UNKNOWN",
                        "raw": best_number
                    }

    # Pattern 3: Generic fallback - find any number near "closing balance"
    generic_pattern = re.compile(
        r'(?:'
        r'(?:closing\s+balance|closingbalance)(?:\s+amount)?'
        r'|(?:closingbal|closing\s+bal\.?)'
        r'|(?:closing\s+ledger\s+balance|closingledgerbalance)'
        r'|(?:closing\s+available\s+balance|closingavailablebalance)'
        r'|(?:balance\s+carried\s+forward|balancecarriedforward)'
        r'|(?:carried\s+forward(?:\s+balance)?|carriedforward(?:balance)?)'
        r'|(?:balance\s+c\/f|balancec\/f|c\/f\s+balance|c\/fbalance)'
        r'|(?:book\s+closing\s+balance|bookclosingbalance)'
        r')'
        r'[\s\S]{0,50}?'
        r'([0-9,]+\.?\d*)',
        re.IGNORECASE
    )

    match = generic_pattern.search(text)
    if match:
        closing_balance = match.group(1).replace(',', '')
        print(f"DEBUG: Found Closing Balance (generic): {closing_balance}")
        return {
            'amount': closing_balance,
            'type': 'UNKNOWN',
            'raw': match.group(0)
        }

    print("DEBUG: No Closing Balance found")
    return None

def extract_customer_id(text):
    """Extract Customer ID from text using regex patterns"""
    print(f"DEBUG: Searching for Customer ID in text (first 500 chars): {text[:500]}")

    customer_id_pattern = re.compile(
        r'(?i)((?:'
        r'customer\s*id'            # Customer ID
        r'|cust\.?\s*id'            # Cust ID / Cust. ID
        r'|customer\s*no\.?'        # Customer No / Customer No.
        r'|customer\s*number'       # Customer Number
        r'|cif\s*no\.?'             # CIF No / CIF No.
        r'|cif\s*id'                # CIF ID
        r'|cif\s*number'            # CIF Number
        r'|user\s*id'               # User ID
        r'|relationship\s*no\.?'    # Relationship No / Relationship No.
        r'|cust\.?\s*reln\.?\s*no\.?' # Cust Reln No / Cust. Reln. No.
        r'|crn'                     # CRN
        r'|client\s*id'             # Client ID (added)
        r'|customer\s*code'         # Customer Code (added)
        r'|customer\s*no\.?\s*/\s*cif\s*id'  # Customer No/CIF ID
        r'|cif\s*id\s*/\s*customer\s*no\.?'  # CIF ID/Customer No
        r'|custid'                  # CustID
        r'|client\s*no\.?'          # Client No
        r'|user\s*no\.?'            # User No
        r'|ckyc\s*id'               # CKYC ID
        r'))\s*[:\-=\s/]*\s*([A-Za-z0-9\-/]+)(?=\s|$)'
    )

    match = customer_id_pattern.search(text)
    if match:
        customer_id = match.group(2).strip().replace(" ", "").replace("-", "").replace("/", "")
        print(f"DEBUG: Found Customer ID: {customer_id}")
        return customer_id

    # Additional pattern for "CustID : 290556726" format
    alt_pattern = re.compile(r'(?i)custid\s*[:\-]?\s*([A-Za-z0-9]+)')
    alt_match = alt_pattern.search(text)
    if alt_match:
        customer_id = alt_match.group(1).strip()
        print(f"DEBUG: Found Customer ID (alt pattern): {customer_id}")
        return customer_id

    print("DEBUG: No Customer ID found")
    return None

def extract_ifsc_code(text):
    """Extract IFSC Code from text using regex patterns"""
    print(f"DEBUG: Searching for IFSC Code in text (first 500 chars): {text[:500]}")

    # IFSC Code pattern: 4 letters + 0 + 6 alphanumeric characters
    # Format: XXXX0YYYYYY where X = letters, Y = letters or numbers
    # Allow digits in first 4 positions to handle OCR misreads (e.g., B as 8)
    ifsc_pattern = re.compile(
        r'(?i)(?:ifsc(?:\s*code)?)\s*[:\-]?\s*([A-Z0-9]{4}0[A-Z0-9]{6})',
        re.IGNORECASE
    )

    match = ifsc_pattern.search(text)
    if match:
        ifsc_code = match.group(1).upper().strip()
        print(f"DEBUG: Raw IFSC Code extracted: {ifsc_code}")

        # Normalize OCR misreads in the first 4 positions (should be letters)
        normalized_ifsc = list(ifsc_code)
        for i in range(4):  # Only first 4 positions
            if normalized_ifsc[i] == '8':
                normalized_ifsc[i] = 'B'
            elif normalized_ifsc[i] == '1':
                normalized_ifsc[i] = 'I'
            elif normalized_ifsc[i] == '0':
                normalized_ifsc[i] = 'O'
            elif normalized_ifsc[i] == '5':
                normalized_ifsc[i] = 'S'
            elif normalized_ifsc[i] == '3':
                normalized_ifsc[i] = 'E'
            elif normalized_ifsc[i] == '2':
                normalized_ifsc[i] = 'Z'
            elif normalized_ifsc[i] == '7':
                normalized_ifsc[i] = 'T'
            elif normalized_ifsc[i] == '4':
                normalized_ifsc[i] = 'A'
            elif normalized_ifsc[i] == '6':
                normalized_ifsc[i] = 'G'
            # Add more corrections as needed for other common OCR misreads

        ifsc_code = ''.join(normalized_ifsc)
        print(f"DEBUG: Normalized IFSC Code: {ifsc_code}")
        return ifsc_code

    print("DEBUG: No IFSC Code found")
    return None

def extract_mobile_number(text):
    """Extract Mobile Number from text using regex patterns"""
    print(f"DEBUG: Searching for Mobile Number in text (first 500 chars): {text[:500]}")

    mobile_pattern = re.compile(
        r'(?i)((?:'
        r'mobile\s*no\.?'                    # Mobile No / Mobile No.
        r'|mobile\s*number'                  # Mobile Number
        r'|phone\s*no\.?'                    # Phone No / Phone No.
        r'|phone\s*number'                   # Phone Number
        r'|contact\s*no\.?'                  # Contact No / Contact No.
        r'|contact\s*number'                 # Contact Number
        r'|registered\s*mobile\s*no\.?'      # Registered Mobile No
        r'|registered\s*mobile\s*number'     # Registered Mobile Number
        r'|registered\s*phone\s*no\.?'       # Registered Phone No
        r'|registered\s*phone\s*number'      # Registered Phone Number
        r'|registered\s*contact\s*no\.?'     # Registered Contact No
        r'|registered\s*contact\s*number'    # Registered Contact Number
        r'|tel\s*no\.?'                      # Tel No
        r'|tel\s*number'                     # Tel Number
        r'|cell\s*no\.?'                     # Cell No
        r'|cell\s*number'                    # Cell Number
        r'|sms\s*no\.?'                      # SMS No
        r'|sms\s*number'                     # SMS Number
        r'))\s*[:\-=\s/]*\s*([0-9xX*]+(?:[/,][0-9xX*]+)*)'    # Followed by digits, x, or *, possibly multiple separated by / or ,
    )

    match = mobile_pattern.search(text)
    if match:
        mobile_raw = match.group(2)
        # Remove separators and clean to digits, x, *
        cleaned = re.sub(r'[/,]', '', mobile_raw).upper()
        # Extract only valid characters: digits, X, *
        valid_chars = re.findall(r'[0-9X*]', cleaned)
        if valid_chars:
            mobile_number = ''.join(valid_chars)
            print(f"DEBUG: Found Mobile Number: {mobile_number}")
            return mobile_number

    # Fallback: extract numbers after "phone number" until non-alphanumeric or end
    fallback_pattern = re.compile(r'(?i)phone\s*number\s*[:\-]?\s*([0-9xX*/,\s]+?)(?=\W|$)')
    fallback_match = fallback_pattern.search(text)
    if fallback_match:
        fallback_raw = fallback_match.group(1).strip()
        # Clean and extract valid characters
        cleaned = re.sub(r'[/,]', '', fallback_raw).upper()
        valid_chars = re.findall(r'[0-9X*]', cleaned)
        if valid_chars:
            mobile_number = ''.join(valid_chars)
            print(f"DEBUG: Found Mobile Number (fallback): {mobile_number}")
            return mobile_number

    print("DEBUG: No Mobile Number found")
    return None

def extract_account_number(text):
    """Extract Account Number from text using regex patterns"""
    print(f"DEBUG: Searching for Account Number in text (first 500 chars): {text[:500]}")

    account_pattern = re.compile(
        r'(?i)((?:'
        r'account\s*no\.?'                   # Account No / Account No.
        r'|account\s*number'                 # Account Number
        r'|acc\s*no\.?'                      # Acc No / Acc No.
        r'|acc\s*number'                     # Acc Number
        r'|account\s*id'                     # Account ID
        r'|acc\s*id'                         # Acc ID
        r'|bank\s*account\s*no\.?'           # Bank Account No
        r'|bank\s*account\s*number'          # Bank Account Number
        r'|saving\s*account\s*no\.?'         # Saving Account No
        r'|saving\s*account\s*number'        # Saving Account Number
        r'|current\s*account\s*no\.?'        # Current Account No
        r'|current\s*account\s*number'       # Current Account Number
        r'|a/c\s*no\.?'                      # A/C No
        r'|a/c\s*number'                     # A/C Number
        r'))\s*[:\-=\s/]*\s*([0-9\s\-/]+)'
    )

    match = account_pattern.search(text)
    if match:
        account_raw = match.group(2).strip()
        # Clean up the account number: remove spaces, dashes, slashes
        account_number = re.sub(r'[\s\-/]', '', account_raw)
        # Ensure it's numeric and reasonable length (8-18 digits for bank accounts)
        if account_number.isdigit() and 8 <= len(account_number) <= 18:
            print(f"DEBUG: Found Account Number: {account_number}")
            return account_number

    # Fallback: look for sequences of 8-18 digits that might be account numbers
    fallback_pattern = re.compile(r'\b(\d{8,18})\b')
    fallback_matches = fallback_pattern.findall(text)
    if fallback_matches:
        # Take the first reasonable match
        for match in fallback_matches:
            if len(match) >= 8:
                print(f"DEBUG: Found Account Number (fallback): {match}")
                return match

    print("DEBUG: No Account Number found")
    return None

def extract_email_ids(text):
    """Extract all Email IDs from text using regex patterns, including labeled and plain emails"""
    print(f"DEBUG: Searching for Email IDs in text (first 500 chars): {text[:500]}")

    email_ids = []
    seen_emails = set()  # Track unique emails

    # Pattern 1: Extract all plain email addresses first (most reliable)
    plain_email_pattern = re.compile(
        r'\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b',
        re.IGNORECASE
    )

    plain_matches = plain_email_pattern.findall(text)
    for email_raw in plain_matches:
        email_clean = email_raw.strip().lower()
        if email_clean not in seen_emails:
            seen_emails.add(email_clean)
            email_ids.append(email_clean)
            print(f"DEBUG: Found plain Email ID: {email_clean}")

    # Pattern 2: Extract labeled emails with potential masking/truncation
    labeled_email_pattern = re.compile(
        r'(?i)(?:'
        r'email\s*(?:id|address)?'            # Email / Email ID / Email Address
        r'|e-?mail\s*(?:id|address)?'         # E-mail / E-mail ID
        r'|registered\s+e-?mail\s*(?:id|address)?'  # Registered Email
        r'|contact\s+e-?mail'                 # Contact Email
        r'|mail\s*(?:id|address)?'            # Mail / Mail ID
        r')\s*[:\-=\s/]*\s*'
        r'([a-zA-Z0-9._%+\-*]+@[a-zA-Z0-9.*\-]+(?:\.[a-zA-Z]{1,})?)',  # Allow partial domains
        re.IGNORECASE
    )

    labeled_matches = labeled_email_pattern.findall(text)
    for email_raw in labeled_matches:
        email_raw = email_raw.strip()
        print(f"DEBUG: Raw labeled email extracted: {email_raw}")

        # Remove all spaces from email
        email_raw = re.sub(r'\s+', '', email_raw)

        # Check if @ symbol exists
        if '@' not in email_raw:
            continue

        # Split by @
        parts = email_raw.split('@')
        local_part = parts[0]
        domain_part = parts[1] if len(parts) > 1 else ''

        # Clean domain - remove asterisks for processing
        domain_clean = domain_part.replace('*', '').upper()

        # Handle truncated domains
        if domain_clean and not domain_clean.endswith(('.COM', '.NET', '.ORG', '.IN', '.CO')):
            # Try to infer common domains
            if 'GMAIL' in domain_clean or domain_clean.startswith('G'):
                domain_clean = 'GMAIL.COM'
            elif 'YAHOO' in domain_clean or domain_clean.startswith('Y'):
                domain_clean = 'YAHOO.COM'
            elif 'HOTMAIL' in domain_clean or 'OUTLOOK' in domain_clean:
                domain_clean = 'OUTLOOK.COM'
            else:
                # Extract domain name before '.' or 'C' (for truncated .COM)
                if '.' in domain_clean:
                    domain_name = domain_clean.split('.')[0]
                elif 'C' in domain_clean:
                    domain_name = domain_clean.split('C')[0].rstrip('.')
                else:
                    domain_name = domain_clean
                domain_clean = f"{domain_name}.COM"

        # Reconstruct email
        email_id = f"{local_part}@{domain_clean}".lower()
        
        # Add to results if not already present
        if email_id not in seen_emails and '@' in email_id:
            seen_emails.add(email_id)
            email_ids.append(email_id)
            print(f"DEBUG: Found labeled Email ID: {email_id}")

    # Pattern 3: Look for masked emails (with asterisks)
    # Example: "abc***@gmail.com" or "a***b@domain.com"
    masked_email_pattern = re.compile(
        r'\b[a-zA-Z0-9._%+\-*]+@[a-zA-Z0-9.*\-]+\.[a-zA-Z]{2,}\b',
        re.IGNORECASE
    )

    masked_matches = masked_email_pattern.findall(text)
    for email_raw in masked_matches:
        email_clean = email_raw.strip().lower()
        if email_clean not in seen_emails and '@' in email_clean:
            seen_emails.add(email_clean)
            email_ids.append(email_clean)
            print(f"DEBUG: Found masked Email ID: {email_clean}")

    # Pattern 4: Search for email-like patterns with spaces that need cleanup
    # Example: "user @ domain . com"
    spaced_email_pattern = re.compile(
        r'\b([a-zA-Z0-9._%+\-]+)\s*@\s*([a-zA-Z0-9.\-]+)\s*\.\s*([a-zA-Z]{2,})\b',
        re.IGNORECASE
    )

    spaced_matches = spaced_email_pattern.findall(text)
    for match in spaced_matches:
        local, domain, tld = match
        email_clean = f"{local}@{domain}.{tld}".lower()
        if email_clean not in seen_emails:
            seen_emails.add(email_clean)
            email_ids.append(email_clean)
            print(f"DEBUG: Found spaced Email ID: {email_clean}")

    if email_ids:
        print(f"DEBUG: Total Email IDs found: {len(email_ids)}")
        print(f"DEBUG: All emails: {email_ids}")
        return email_ids
    else:
        print("DEBUG: No Email IDs found")
        return []

def extract_ckyc(text):
    """Extract CKYC from text using regex patterns"""
    print(f"DEBUG: Searching for CKYC in text (first 500 chars): {text[:500]}")

    # Pattern 1: CKYC with label (most common)
    # Handles various formats: "CKYC: 12345", "CKYC ID: 12345", etc.
    labeled_ckyc_pattern = re.compile(
        r'(?i)\b(?:'
        r'ckyc\s*(?:id|no\.?|number|identifier)?'  # CKYC, CKYC ID, CKYC No, etc.
        r')\s*[:,\-=]\s*'  # ← CHANGED: Require at least one separator (colon, comma, dash, equals)
        r'([A-Z0-9][A-Z0-9*\-/\s]{8,20})',  # Capture alphanumeric with *, -, /, spaces
        re.IGNORECASE
    )

    match = labeled_ckyc_pattern.search(text)
    if match:
        ckyc_raw = match.group(1).strip()
        # Clean up: remove spaces, dashes, slashes but keep asterisks (for masked data)
        ckyc = re.sub(r'[\s\-/]', '', ckyc_raw)
        print(f"DEBUG: Found CKYC (labeled): {ckyc}")
        return ckyc

    # Pattern 2: Look for 14-digit number after "CKYC" (common format)
    digit_pattern = re.compile(
        r'(?i)\bckyc\b[:\s\-]+([0-9*]{14})',  # ← CHANGED: Require at least one separator
        re.IGNORECASE
    )

    match = digit_pattern.search(text)
    if match:
        ckyc = match.group(1).strip()
        print(f"DEBUG: Found CKYC (14-digit): {ckyc}")
        return ckyc

    # Pattern 3: Generic alphanumeric pattern near "CKYC"
    # Look for sequences that might be CKYC (typically 10-20 characters)
    generic_pattern = re.compile(
        r'(?i)ckyc[:\-=]+([A-Z0-9*\-/]{10,20})',  # ← CHANGED: Require at least one separator
        re.IGNORECASE
    )

    match = generic_pattern.search(text)
    if match:
        ckyc_raw = match.group(1).strip()
        ckyc = re.sub(r'[\s\-/]', '', ckyc_raw)
        print(f"DEBUG: Found CKYC (generic): {ckyc}")
        return ckyc

    # Pattern 4: Standalone 14-digit number (fallback - use cautiously)
    # Only if you're sure CKYC is always 14 digits
    standalone_pattern = re.compile(r'\b([0-9*]{14})\b')
    matches = standalone_pattern.findall(text)
    if matches:
        # Return the first 14-digit number found
        ckyc = matches[0]
        print(f"DEBUG: Found CKYC (standalone 14-digit): {ckyc}")
        return ckyc

    print("DEBUG: No CKYC found")
    return None

def extract_account_type(text):
    """Extract Account Type from text using regex patterns"""
    print(f"DEBUG: Searching for Account Type in text (first 500 chars): {text[:500]}")

    # Account Type regex pattern - captures label in group 1, value in group 2
    account_type_pattern = re.compile(
        r'(?i)((?:'
        r'account\s*type'                    # Account Type
        r'|a/c\s*type'                       # A/c Type
        r'|a\.c\.?\s*type'                   # A.C. Type / A.C Type
        r'|type\s*of\s*account'              # Type of Account
        r'|ac\s*type'                        # Ac Type
        r'|account\s*category'               # Account Category
        r'|a/c\s*category'                   # A/c Category
        r'|acct\s*type'                      # Acct Type
        r'|scheme\s*type'                    # Scheme Type
        r'|scheme\s*code'                    # Scheme Code
        r'|scheme'                           # Scheme
        r'|product\s*type'                   # Product Type
        r'|product\s*code'                   # Product Code
        r'|relationship\s*type'              # Relationship Type
        r'|relation\s*type'                  # Relation Type
        r'|customer\s*relationship'          # Customer Relationship
        r'|customer\s*relation\s*type'       # Customer Relation Type
        r'|mode\s*of\s*operation'            # Mode of Operation
        r'|operating\s*type'                 # Operating Type
        r'|operative\s*type'                 # Operative Type
        r'|a/c\s*operation'                  # A/c Operation
        r'|account\s*operation\s*mode'       # Account Operation Mode
        r'|operation\s*mode'                 # Operation Mode
        r'))\s*[:\-=\s/]*\s*([A-Za-z0-9\s\-/]+)(?=\s|$)'
    )

    # Find all matches
    matches = account_type_pattern.findall(text)

    # Prioritize matches where the value contains "account", "a/c", or "a.c"
    prioritized_matches = [m for m in matches if re.search(r'(?i)account|a/c|a\.c', m[1])]

    # If prioritized matches exist, use the first one; otherwise, use the first match
    if prioritized_matches:
        selected_match = prioritized_matches[0]
    elif matches:
        selected_match = matches[0]
    else:
        print("DEBUG: No Account Type found")
        return None

    label = selected_match[0].strip()
    account_type_raw = selected_match[1].strip()

    # Process the value: find the word containing "account"/"a/c"/"a.c", take previous word and that word
    words = re.split(r'\s+', account_type_raw)
    account_word_index = None
    for i, word in enumerate(words):
        if re.search(r'(?i)account|a/c|a\.c', word):
            account_word_index = i
            break

    if account_word_index is not None:
        if account_word_index > 0:
            account_type = words[account_word_index - 1] + '  ' + words[account_word_index]
        else:
            account_type = words[account_word_index]
    else:
        # Fallback: take first 3 words
        account_type = '  '.join(words[:3])

    account_type = account_type.upper()
    print(f"DEBUG: Found Account Type - Label: '{label}', Value: '{account_type}'")
    return {
        'label': label,
        'account_type': account_type
    }

def extract_statement_period(pdf_file):
    """Extract statement period from the first page of a PDF using regex"""
    try:
        # Extract text from the first page
        text = extract_text_from_pdf_first_page(pdf_file)
        if not text:
            return None

        print(f"DEBUG: Extracted text for statement period (first 500 chars): {text[:500]}")

        # First, fix dates that are split across lines by removing spaces between date components
        # This handles cases like "30/06 /2025" -> "30/06/2025"
        text = re.sub(r'(\d{1,2}[-/.]\d{1,2})\s+([-/.])\s*(\d{2,4})', r'\1\2\3', text)
        text = re.sub(r'(\d{4}[-/.]\d{1,2})\s+([-/.])\s*(\d{1,2})', r'\1\2\3', text)
        
        print(f"DEBUG: Text after date fixing (first 500 chars): {text[:500]}")

        # Date pattern: 
        # - dd-mm-yyyy, dd-mm-yy, dd/mm/yyyy, dd/mm/yy, dd.mm.yy, dd.mm.yyyy
        # - yyyy-mm-dd, yy-mm-dd, yyyy/mm/dd, yy/mm/dd (ISO format)
        # - dd month yyyy, dd mon yyyy
        # - mon dd, yyyy (e.g., JUL 01, 2025)
        date_pattern = r'\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b|\b\d{2}[-/.]\d{1,2}[-/.]\d{1,2}\b|\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b|\b\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}\b|\b(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{4}\b'

        # Period pattern: from: date to: date or date to date (case-insensitive, handles optional asterisks)
        period_pattern = r'(?i)(?:statement\s+)?period[:\s*]+(' + date_pattern + r')[:\s*]+to[:\s*]+(' + date_pattern + r')|(?:period\s+)?from[:\s*]*(' + date_pattern + r')[:\s*]+to[:\s*]+(' + date_pattern + r')|(' + date_pattern + r')\s+to\s+(' + date_pattern + r')'

        match = re.search(period_pattern, text, re.IGNORECASE)
        if match:
            # Extract the matched groups
            groups = match.groups()
            from_date = None
            to_date = None
            
            # Find which pair of groups has values
            for i in range(0, len(groups), 2):
                if groups[i] and groups[i+1]:
                    from_date = groups[i].strip()
                    to_date = groups[i+1].strip()
                    break
            
            if from_date and to_date:
                print(f"DEBUG: Found Statement Period - From: {from_date}, To: {to_date}")
                return {
                    'from_date': from_date,
                    'to_date': to_date
                }

        print("DEBUG: No Statement Period found")
        return None

    except Exception as e:
        print(f"DEBUG: Error extracting statement period: {str(e)}")
        return None
    
@app.route('/extract-text', methods=['POST'])
def extract_text():
    """Endpoint to extract text from uploaded file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        extracted_text = ""
        
        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            extracted_text = extract_text_from_image(file)
        elif file_ext == '.pdf':
            extracted_text = extract_text_from_pdf(file)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400
        
        return jsonify({
            'extracted_text': extracted_text,
            'filename': file.filename,
            'file_type': file_ext
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/extract-tables', methods=['POST'])
def extract_tables():
    """Endpoint to extract tables from uploaded PDF file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext != '.pdf':
            return jsonify({'error': 'Table extraction is only supported for PDF files'}), 400

        tables_data = extract_tables_from_pdf(file)

        return jsonify({
            'tables': tables_data,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/extract-text-first-page', methods=['POST'])
def extract_text_first_page():
    """Endpoint to extract text from first page of uploaded PDF file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext != '.pdf':
            return jsonify({'error': 'First page extraction is only supported for PDF files'}), 400

        extracted_text = extract_text_from_pdf_first_page(file)

        return jsonify({
            'extracted_text': extracted_text,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/extract-pan', methods=['POST'])
def extract_pan():
    """Endpoint to extract PAN number from uploaded file using improved regex"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        extracted_text = ""

        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            extracted_text = extract_text_from_image_aadhar_pan(file)
        elif file_ext == '.pdf':
            extracted_text = extract_text_from_pdf_first_page(file)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        print(f"\n{'='*60}")
        print(f"Processing file: {file.filename}")
        print(f"{'='*60}")

        # Use improved PAN extraction function
        pan_number = extract_pan_number(extracted_text)

        if pan_number:
            print(f"✅ PAN FOUND: {pan_number}")
        else:
            print("❌ PAN NOT FOUND")
        print(f"{'='*60}\n")

        return jsonify({
            'pan_number': pan_number,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        print(f"❌ Error in extract_pan: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/extract-customer-id', methods=['POST'])
def extract_customer_id_endpoint():
    """Endpoint to extract Customer ID from uploaded file using regex"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        extracted_text = ""

        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            extracted_text = extract_text_from_image(file)
        elif file_ext == '.pdf':
            extracted_text = extract_text_from_pdf_first_page(file)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        print(f"\n{'='*60}")
        print(f"Processing file: {file.filename}")
        print(f"{'='*60}")

        # Use customer ID extraction function
        customer_id = extract_customer_id(extracted_text)

        if customer_id:
            print(f"✅ CUSTOMER ID FOUND: {customer_id}")
        else:
            print("❌ CUSTOMER ID NOT FOUND")
        print(f"{'='*60}\n")

        return jsonify({
            'customer_id': customer_id,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        print(f"❌ Error in extract_customer_id: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/extract-mobile-number', methods=['POST'])
def extract_mobile_number_endpoint():
    """Endpoint to extract Mobile Number from uploaded file using regex"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        extracted_text = ""

        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            extracted_text = extract_text_from_image(file)
        elif file_ext == '.pdf':
            extracted_text = extract_text_from_pdf_first_page(file)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        print(f"\n{'='*60}")
        print(f"Processing file: {file.filename}")
        print(f"{'='*60}")

        # Use mobile number extraction function
        mobile_number = extract_mobile_number(extracted_text)

        if mobile_number:
            print(f"✅ MOBILE NUMBER FOUND: {mobile_number}")
        else:
            print("❌ MOBILE NUMBER NOT FOUND")
        print(f"{'='*60}\n")

        return jsonify({
            'mobile_number': mobile_number,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        print(f"❌ Error in extract_mobile_number: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/extract-account-number', methods=['POST'])
def extract_account_number_endpoint():
    """Endpoint to extract Account Number from uploaded file using regex"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        extracted_text = ""

        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            extracted_text = extract_text_from_image(file)
        elif file_ext == '.pdf':
            extracted_text = extract_text_from_pdf_first_page(file)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        print(f"\n{'='*60}")
        print(f"Processing file: {file.filename}")
        print(f"{'='*60}")

        # Use account number extraction function
        account_number = extract_account_number(extracted_text)

        if account_number:
            print(f"✅ ACCOUNT NUMBER FOUND: {account_number}")
        else:
            print("❌ ACCOUNT NUMBER NOT FOUND")
        print(f"{'='*60}\n")

        return jsonify({
            'account_number': account_number,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        print(f"❌ Error in extract_account_number: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/extract-ifsc', methods=['POST'])
def extract_ifsc_endpoint():
    """Endpoint to extract IFSC Code from uploaded file using regex"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        extracted_text = ""

        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            extracted_text = extract_text_from_image(file)
        elif file_ext == '.pdf':
            extracted_text = extract_text_from_pdf_first_page(file)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        print(f"\n{'='*60}")
        print(f"Processing file: {file.filename}")
        print(f"{'='*60}")

        # Use IFSC extraction function
        ifsc_code = extract_ifsc_code(extracted_text)

        if ifsc_code:
            print(f"✅ IFSC CODE FOUND: {ifsc_code}")
        else:
            print("❌ IFSC CODE NOT FOUND")
        print(f"{'='*60}\n")

        return jsonify({
            'ifsc_code': ifsc_code,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        print(f"❌ Error in extract_ifsc: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/extract-email', methods=['POST'])
def extract_email_endpoint():
    """Endpoint to extract Email IDs from uploaded file using regex"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        extracted_text = ""

        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            extracted_text = extract_text_from_image(file)
        elif file_ext == '.pdf':
            extracted_text = extract_text_from_pdf_first_page(file)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        print(f"\n{'='*60}")
        print(f"Processing file: {file.filename}")
        print(f"{'='*60}")

        # Use email extraction function
        email_ids = extract_email_ids(extracted_text)

        if email_ids:
            print(f"✅ EMAIL IDs FOUND: {email_ids}")
        else:
            print("❌ EMAIL IDs NOT FOUND")
        print(f"{'='*60}\n")

        return jsonify({
            'email_ids': email_ids,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        print(f"❌ Error in extract_email: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/extract-ckyc', methods=['POST'])
def extract_ckyc_endpoint():
    """Endpoint to extract CKYC from uploaded file using regex"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        extracted_text = ""

        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            extracted_text = extract_text_from_image(file)
        elif file_ext == '.pdf':
            extracted_text = extract_text_from_pdf_first_page(file)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        print(f"\n{'='*60}")
        print(f"Processing file: {file.filename}")
        print(f"{'='*60}")

        # Use CKYC extraction function
        ckyc = extract_ckyc(extracted_text)

        if ckyc:
            print(f"✅ CKYC FOUND: {ckyc}")
        else:
            print("❌ CKYC NOT FOUND")
        print(f"{'='*60}\n")

        return jsonify({
            'ckyc': ckyc,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        print(f"❌ Error in extract_ckyc: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/extract-account-type', methods=['POST'])
def extract_account_type_endpoint():
    """Endpoint to extract Account Type from uploaded file using regex"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        extracted_text = ""

        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            extracted_text = extract_text_from_image(file)
        elif file_ext == '.pdf':
            extracted_text = extract_text_from_pdf_first_page(file)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        print(f"\n{'='*60}")
        print(f"Processing file: {file.filename}")
        print(f"{'='*60}")

        # Use account type extraction function
        account_type_data = extract_account_type(extracted_text)

        if account_type_data:
            print(f"✅ ACCOUNT TYPE FOUND: {account_type_data}")
        else:
            print("❌ ACCOUNT TYPE NOT FOUND")
        print(f"{'='*60}\n")

        return jsonify({
            'account_type': account_type_data,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        print(f"❌ Error in extract_account_type: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/extract-opening-balance', methods=['POST'])
def extract_opening_balance_endpoint():
    """Endpoint to extract Opening Balance from uploaded file using regex"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        extracted_text = ""

        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            extracted_text = extract_text_from_image(file)
        elif file_ext == '.pdf':
            extracted_text = extract_text_first_and_last_page(file)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        print(f"\n{'='*60}")
        print(f"Processing file: {file.filename}")
        print(f"{'='*60}")

        # Use opening balance extraction function
        opening_balance_data = extract_opening_balance(extracted_text)

        if opening_balance_data:
            print(f"✅ OPENING BALANCE FOUND: {opening_balance_data}")
        else:
            print("❌ OPENING BALANCE NOT FOUND")
        print(f"{'='*60}\n")

        return jsonify({
            'opening_balance': opening_balance_data,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        print(f"❌ Error in extract_opening_balance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/extract-closing-balance', methods=['POST'])
def extract_closing_balance_endpoint():
    """Endpoint to extract Closing Balance from uploaded file using regex"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        extracted_text = ""

        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            extracted_text = extract_text_from_image(file)
        elif file_ext == '.pdf':
            extracted_text = extract_text_first_and_last_page(file)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        print(f"\n{'='*60}")
        print(f"Processing file: {file.filename}")
        print(f"{'='*60}")

        # Use closing balance extraction function
        closing_balance_data = extract_closing_balance(extracted_text)

        if closing_balance_data:
            print(f"✅ CLOSING BALANCE FOUND: {closing_balance_data}")
        else:
            print("❌ CLOSING BALANCE NOT FOUND")
        print(f"{'='*60}\n")

        return jsonify({
            'closing_balance': closing_balance_data,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        print(f"❌ Error in extract_closing_balance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/extract-statement-period', methods=['POST'])
def extract_statement_period_endpoint():
    """Endpoint to extract Statement Period from uploaded PDF file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext != '.pdf':
            return jsonify({'error': 'Statement period extraction is only supported for PDF files'}), 400

        print(f"\n{'='*60}")
        print(f"Processing file: {file.filename}")
        print(f"{'='*60}")

        # Use statement period extraction function
        statement_period_data = extract_statement_period(file)

        if statement_period_data:
            print(f"✅ STATEMENT PERIOD FOUND: {statement_period_data}")
        else:
            print("❌ STATEMENT PERIOD NOT FOUND")
        print(f"{'='*60}\n")

        return jsonify({
            'statement_period': statement_period_data,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        print(f"❌ Error in extract_statement_period: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/extract-dob', methods=['POST'])
def extract_dob_endpoint():
    """Endpoint to extract DOB from uploaded file using regex"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.pdf']:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        print(f"\n{'='*60}")
        print(f"Processing file: {file.filename}")
        print(f"{'='*60}")

        # Determine file type for extract_dob function
        file_type = 'pdf' if file_ext == '.pdf' else 'image'

        # Use extract_dob function
        dob_data = extract_dob(file, file_type)

        if dob_data:
            print(f"✅ DOB FOUND: {dob_data}")
        else:
            print("❌ DOB NOT FOUND")
        print(f"{'='*60}\n")

        return jsonify({
            'dob': dob_data,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        print(f"❌ Error in extract_dob: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/extract-formatted-text', methods=['POST'])
def extract_formatted_text():
    """Endpoint to extract formatted text from uploaded file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        extracted_text = ""

        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            extracted_text = extract_formatted_text_from_image(file)
        elif file_ext == '.pdf':
            extracted_text = extract_formatted_text_from_pdf(file)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        return jsonify({
            'extracted_text': extracted_text,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

@app.route('/extract-aadhar', methods=['POST'])
def extract_aadhar():
    """Endpoint to extract Aadhaar number from uploaded file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            file_type = 'image'
        elif file_ext == '.pdf':
            file_type = 'pdf'
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

        print(f"\n{'='*60}")
        print(f"Processing file: {file.filename}")
        print(f"{'='*60}")

        aadhar_number = extract_aadhar_number(file, file_type)

        if aadhar_number:
            print(f"✅ AADHAAR NUMBER FOUND: {aadhar_number}")
        else:
            print("❌ AADHAAR NUMBER NOT FOUND")
        print(f"{'='*60}\n")

        return jsonify({
            'aadhar_number': aadhar_number,
            'filename': file.filename,
            'file_type': file_ext
        }), 200

    except Exception as e:
        print(f"❌ Error in extract_aadhar: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = 5001
    print("Starting OCR Flask Server...")
    print(f"Tesseract path: {TESSERACT_PATH}")
    print(f"Server running on http://localhost:{port}")
    print("\n⚠️  IMPORTANT: Keep this terminal window open while using the app!\n")

    try:
        app.run(debug=True, host='127.0.0.1', port=port)
    except OSError as e:
        if "address already in use" in str(e).lower():
            print(f"\n❌ Port {port} is already in use!")
            print("Try changing to a different port (5002, 5003, etc.)")
        else:
            raise
