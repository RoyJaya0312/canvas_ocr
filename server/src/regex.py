import os
import re
import pdfplumber

# 📂 Folder with your PDFs
input_folder = r"C:\Users\Jayasmita\Desktop\pytesseract\bank_statements_both"

# ✅ Account type regex (improved pattern for various labels)
account_type_pattern = re.compile(
    r'(?i)((?:'
    r'account\s*type'                    # Account Type
    r'|accounttype'                      # AccountType
    r'|a/c\s*type'                       # A/c Type
    r'|a\.c\.?\s*type'                   # A.C. Type / A.C Type
    r'|type\s*of\s*account'              # Type of Account
    r'|ac\s*type'                        # Ac Type
    r'|account\s*category'               # Account Category
    r'|a/c\s*category'                   # A/c Category
    r'|acct\s*type'                      # Acct Type
    r'|scheme\s*type'                    # Scheme Type
    r'|scheme\s*code'                    # Scheme Code
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

# 🆔 Customer ID regex - ENHANCED for OCR robustness
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
    r'))\s*[:\-=\s/]*\s*([A-Za-z0-9\-/]+)(?=\s|$)'
)

# 🧾 PAN detection patterns
# 1️⃣ Labeled PAN (looks for "PAN", "PAN No", "PAN Number")
labeled_pan_pattern = re.compile(
    r'(?i)\b(?:pan(?:\s*(?:no\.?|number)?)?)\b[:\-\s]*'      # pan / pan no / pan number
    r'([A-Z]{3}[ABCFGHLJPTK][A-Z]\s*[0-9]{4}\s*[A-Z])',       # Strict PAN format
    re.IGNORECASE
)

# 2️⃣ Fallback pattern (general PAN match with stricter rules)
generic_pan_pattern = re.compile(
    r'\b(?<![A-Za-z])'                          # Word boundary, not preceded by letter
    r'[A-Z]{3}'                                 # First 3 letters (AAA to ZZZ)
    r'[ABCFGHLJPTK]'                            # 4th char must be valid PAN type
    r'[A-Z]'                                    # 5th letter
    r'\s*'
    r'[0-9]{4}'                                 # Exactly 4 digits (no OCR substitutes here)
    r'\s*'
    r'[A-Z]'                                    # Last letter
    r'(?![A-Za-z0-9])\b',                       # Not followed by alphanumeric
    re.IGNORECASE
)

# 🏦 IFSC Code regex
ifsc_pattern = re.compile(
    r'(?i)(?:ifsc(?:\s*code)?)\s*[:\-]?\s*([A-Z]{4}0[A-Z0-9]{6})',
    re.IGNORECASE
)

# 🔁 Iterate over PDF files
for file_name in os.listdir(input_folder):
    if file_name.lower().endswith(".pdf"):
        pdf_path = os.path.join(input_folder, file_name)
        print(f"\n📄 Processing: {file_name}")

        account_type = "Not Found"
        pan_number = "Not Found"
        customer_id = "Not Found"

        try:
            with pdfplumber.open(pdf_path) as pdf:
                first_page = pdf.pages[0]
                text = first_page.extract_text() or ""

                # DEBUG: Print first 500 chars to see what we're working with
                print(f"   First 500 chars of text: {text[:500]}")

                # ✅ Extract account type
                account_type = "Not Found"
                match = account_type_pattern.search(text)
                if match:
                    label = match.group(1).strip()
                    account_type_raw = match.group(2).strip()
                    # Clean up the account type: remove extra spaces, normalize, take first 3 words, join with 2 spaces
                    words = re.sub(r'\s+', ' ', account_type_raw).split()
                    account_type = '  '.join(words[:3]).upper()
                    print(f"   DEBUG: Found Account Type - Label: '{label}', Value: '{account_type}'")

                # 🆔 Extract customer ID
                cust_match = customer_id_pattern.search(text)
                if cust_match:
                    customer_id = cust_match.group(2).strip().replace(" ", "").replace("-", "").replace("/", "")
                    print(f"   DEBUG: Matched Customer ID pattern: {cust_match.group(0)}")
                    print(f"   DEBUG: Label: {cust_match.group(1)}")
                    print(f"   DEBUG: Extracted Customer ID: {customer_id}")
                else:
                    print(f"   DEBUG: No Customer ID match found in text.")

                # ✅ Extract PAN (label first, fallback next)
                lbl_match = labeled_pan_pattern.search(text)
                if lbl_match:
                    raw_pan = lbl_match.group(1).replace(" ", "").upper()
                else:
                    pan_match = generic_pan_pattern.search(text)
                    raw_pan = pan_match.group(0).replace(" ", "").upper() if pan_match else ""

                if raw_pan:
                    # Normalize OCR misreads in digits only (positions 5–8)
                    if len(raw_pan) == 10:
                        letters_first3 = raw_pan[:3]
                        fourth_char = raw_pan[3]
                        fifth_char = raw_pan[4]
                        digits = list(raw_pan[5:9])
                        last = raw_pan[9]
                        
                        # Clean up digit misreads
                        for i, ch in enumerate(digits):
                            if ch == 'O': digits[i] = '0'
                            if ch in ('I', 'L'): digits[i] = '1'
                        
                        pan_number = letters_first3 + fourth_char + fifth_char + ''.join(digits) + last
                    else:
                        pan_number = raw_pan

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

        print(f"   Account: {account_type}")
        print(f"   PAN Number: {pan_number}")
        print(f"   Customer ID: {customer_id}")
