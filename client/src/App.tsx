import React, { useRef, useState } from "react";
import ocrhunterLogo from "/ocrhunterlogo.png";

function App() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [hovered, setHovered] = useState<{ [key: string]: boolean }>({});
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentUrl, setDocumentUrl] = useState<string | null>(null);
  const [extractedText, setExtractedText] = useState<string>("");
  const [extractedTables, setExtractedTables] = useState<Array<Array<any>>>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isLoadingDOB, setIsLoadingDOB] = useState<boolean>(false);
    const [isLoadingText, setIsLoadingText] = useState<boolean>(false);
    const [isLoadingTables, setIsLoadingTables] = useState<boolean>(false);
    const [isLoadingAadhar, setIsLoadingAadhar] = useState<boolean>(false);
    const [error, setError] = useState<string>("");
  const [gallery, setGallery] = useState<Array<{ file: File; url: string }>>(
    []
  );
  const [selectedGalleryIndex, setSelectedGalleryIndex] = useState<
    number | null
  >(null);
  const [selectedDocumentType, setSelectedDocumentType] = useState<string>("");
  const [accountNumber, setAccountNumber] = useState<string>("");
  const [ifscCode, setIfscCode] = useState<string>("");
  const [panNumber, setPanNumber] = useState<string>("");
  const [bankPanNumber, setBankPanNumber] = useState<string>("");
  const [customerId, setCustomerId] = useState<string>("");
  const [mobileNumber, setMobileNumber] = useState<string>("");
  const [emailIds, setEmailIds] = useState<string[]>([]);
  const [emailExtracted, setEmailExtracted] = useState<boolean>(false);
  const [ckyc, setCkyc] = useState<string>("");
  const [accountType, setAccountType] = useState<string>("");
  const [openingBalance, setOpeningBalance] = useState<string>("");
  const [statementPeriod, setStatementPeriod] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [highlightedText, setHighlightedText] = useState<string>("");
  const [FetchDOB, setFetchDOB] = useState<string>("");
  const [aadharNumber, setAadharNumber] = useState<string>("");
  const textDisplayRef = useRef<HTMLDivElement>(null);

  const handleExtractAadhar = async () => {
    if (!selectedFile) {
      setAadharNumber("No file selected");
      alert("No file selected");
      return;
    }

      setIsLoadingAadhar(true);
    setError("");
    setAadharNumber("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    console.log("Attempting to extract Aadhar number from:", selectedFile.name);

    try {
      const response = await fetch("http://localhost:5001/extract-aadhar", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok && data.aadhar_number) {
        setAadharNumber(data.aadhar_number);
        alert("Aadhar number extracted successfully!");
      } else {
        setAadharNumber("Aadhar Number not found");
        alert("Aadhar Number not found");
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      console.error("Aadhar extract error:", error);
      setAadharNumber("Error extracting Aadhar number");
      alert("Error extracting Aadhar number: " + errorMsg);
    } finally {
        setIsLoadingAadhar(false);
    }
  };

  const handleExtractDOB = async () => {
    if (!selectedFile) {
      setFetchDOB("No file selected");
      alert("No file selected");
      return;
    }

    setIsLoadingDOB(true);
    setError("");
    setFetchDOB("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    console.log("Extracting DOB from:", selectedFile.name);

    try {
      const response = await fetch("http://localhost:5001/extract-dob", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      console.log("DOB extract response status:", response.status);
      console.log("DOB extract response data:", data);

      if (response.ok && data.dob) {
        const dobData = data.dob;
        if (typeof dobData === "object" && dobData.dob) {
          setFetchDOB(dobData.dob);
        } else {
          setFetchDOB(dobData);
        }
        console.log("✅ DOB extracted successfully:", dobData);
      } else {
        setFetchDOB("DOB not found");
        console.log("❌ DOB not found in document");
      }
    } catch (error) {
      console.error("❌ DOB extract error:", error);
      setFetchDOB("Error extracting DOB");
    } finally {
      setIsLoadingDOB(false);
    }
  };

  const handleSearch = () => {
    if (!extractedText) {
      alert("No text to search");
      return;
    }
    if (!searchQuery.trim()) {
      setHighlightedText(extractedText);
      return;
    }
    const regex = new RegExp(searchQuery, "gi");
    const highlighted = extractedText.replace(regex, "<mark>$&</mark>");
    setHighlightedText(highlighted);
    if (extractedText.toLowerCase().includes(searchQuery.toLowerCase())) {
      alert(`Found "${searchQuery}" in the text`);
    } else {
      alert(`"${searchQuery}" not found`);
    }
  };

  const handleCloseDocument = () => {
    if (documentUrl) {
      URL.revokeObjectURL(documentUrl);
    }
    setSelectedFile(null);
    setDocumentUrl(null);
    setExtractedText("");
    setError("");
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      if (documentUrl) {
        URL.revokeObjectURL(documentUrl);
      }
      const newFile = files[0];
      setSelectedFile(newFile);
      const newUrl = URL.createObjectURL(newFile);
      setDocumentUrl(newUrl);
      setExtractedText("");
      setError("");
      setEmailIds([]);
      setEmailExtracted(false);
    }
  };

  const handleSelectDocumentClick = () => {
    fileInputRef.current?.click();
  };

  const handleExtractText = async () => {
    if (!selectedFile) {
      setError("No file selected");
      alert("No file selected");
      return;
    }

    // Clear the extracted text immediately when extraction starts
    setExtractedText("");
    setHighlightedText("");
      setIsLoadingText(true);
    setError("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    console.log("Attempting to extract text from:", selectedFile.name);
    console.log("File type:", selectedFile.type);
    console.log("File size:", selectedFile.size, "bytes");

    try {
      console.log("Sending request to http://localhost:5001/extract-text");

      const response = await fetch("http://localhost:5001/extract-text", {
        method: "POST",
        body: formData,
      });

      console.log("Response status:", response.status);
      console.log("Response ok:", response.ok);

      const data = await response.json();
      console.log("Response data:", data);

      if (response.ok) {
        if (data.extracted_text) {
          setExtractedText(data.extracted_text);
          setHighlightedText(data.extracted_text);
          console.log("✅ Text extracted successfully");
          alert("Text extracted successfully!");
        } else {
          setError("No text found in document");
          alert("No text found in document");
        }
      } else {
        const errorMsg = data.error || "Unknown error occurred";
        setError(errorMsg);
        console.error("❌ Server error:", errorMsg);
        alert("Error: " + errorMsg);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      console.error("❌ Network error:", error);

      if (errorMsg.includes("Failed to fetch")) {
        const msg =
          "Cannot connect to server. Please ensure:\n1. Flask server is running (python main.py)\n2. Server is on http://localhost:5001\n3. Check terminal for server errors";
        setError(msg);
        alert(msg);
      } else {
        setError("Error: " + errorMsg);
        alert("Error: " + errorMsg);
      }
    } finally {
        setIsLoadingText(false);
    }
  };

  const handleCopyText = async () => {
    try {
      await navigator.clipboard.writeText(extractedText);
      alert("Text copied to clipboard!");
    } catch (err) {
      console.error("Failed to copy text: ", err);
      alert("Failed to copy text");
    }
  };

  const handleClearText = () => {
    setExtractedText("");
    setHighlightedText("");
    setSearchQuery("");
  };

  const handleClearTables = () => {
    setExtractedTables([]);
  };

  const handlePasteScreenshot = async (
    event: React.ClipboardEvent<HTMLDivElement>
  ) => {
    event.preventDefault();
    const items = event.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.type.indexOf("image") !== -1) {
        const blob = item.getAsFile();
        if (blob) {
          const file = new File([blob], `pasted-screenshot-${Date.now()}.png`, {
            type: blob.type,
          });
          const url = URL.createObjectURL(file);
          setGallery((prev) => [...prev, { file, url }]);
          alert("Screenshot added to gallery!");
          break;
        }
      }
    }
  };

  const handleSelectFromGallery = (item: { file: File; url: string }) => {
    if (documentUrl) {
      URL.revokeObjectURL(documentUrl);
    }
    setSelectedFile(item.file);
    setDocumentUrl(item.url);
    setExtractedText("");
    setError("");
  };

  const handleExtractFromGallery = async () => {
    if (selectedGalleryIndex === null) return;

    const item = gallery[selectedGalleryIndex];
    if (!item) return;

    // Clear the extracted text immediately when extraction starts
    setExtractedText("");
    setHighlightedText("");
    setIsLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", item.file);

    console.log(
      "Attempting to extract text from gallery item:",
      item.file.name
    );
    console.log("File type:", item.file.type);
    console.log("File size:", item.file.size, "bytes");

    try {
      console.log("Sending request to http://localhost:5001/extract-text");

      const response = await fetch("http://localhost:5001/extract-text", {
        method: "POST",
        body: formData,
      });

      console.log("Response status:", response.status);
      console.log("Response ok:", response.ok);

      const data = await response.json();
      console.log("Response data:", data);

      if (response.ok) {
        if (data.extracted_text) {
          setExtractedText(data.extracted_text);
          setHighlightedText(data.extracted_text);
          console.log("✅ Text extracted successfully from gallery");
          alert("Text extracted successfully from gallery!");
        } else {
          setError("No text found in gallery item");
          alert("No text found in gallery item");
        }
      } else {
        const errorMsg = data.error || "Unknown error occurred";
        setError(errorMsg);
        console.error("❌ Server error:", errorMsg);
        alert("Error: " + errorMsg);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      console.error("❌ Network error:", error);

      if (errorMsg.includes("Failed to fetch")) {
        const msg =
          "Cannot connect to server. Please ensure:\n1. Flask server is running (python main.py)\n2. Server is on http://localhost:5001\n3. Check terminal for server errors";
        setError(msg);
        alert(msg);
      } else {
        setError("Error: " + errorMsg);
        alert("Error: " + errorMsg);
      }
    } finally {
      setIsLoading(false);
    }
  };
  const handleExtractTables = async () => {
    if (!selectedFile) {
      setError("No file selected");
      alert("No file selected");
      return;
    }

    if (selectedFile.type !== "application/pdf") {
      setError("Table extraction is only supported for PDF files");
      alert("Table extraction is only supported for PDF files");
      return;
    }

      setIsLoadingTables(true);
    setError("");
    setExtractedTables([]);

    const formData = new FormData();
    formData.append("file", selectedFile);

    console.log("Attempting to extract tables from:", selectedFile.name);
    console.log("File type:", selectedFile.type);
    console.log("File size:", selectedFile.size, "bytes");

    try {
      console.log("Sending request to http://localhost:5001/extract-tables");

      const response = await fetch("http://localhost:5001/extract-tables", {
        method: "POST",
        body: formData,
      });

      console.log("Response status:", response.status);
      console.log("Response ok:", response.ok);

      const data = await response.json();
      console.log("Response data:", data);

      if (response.ok) {
        if (data.tables && data.tables.length > 0) {
          setExtractedTables(data.tables);
          console.log("✅ Tables extracted successfully");
          alert("Tables extracted successfully!");
        } else {
          setError("No tables found in this PDF");
          alert("No tables found in this PDF");
        }
      } else {
        const errorMsg = data.error || "Unknown error occurred";
        setError(errorMsg);
        console.error("❌ Server error:", errorMsg);
        alert("Error: " + errorMsg);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      console.error("❌ Network error:", error);

      if (errorMsg.includes("Failed to fetch")) {
        const msg =
          "Cannot connect to server. Please ensure:\n1. Flask server is running (python main.py)\n2. Server is on http://localhost:5001\n3. Check terminal for server errors";
        setError(msg);
        alert(msg);
      } else {
        setError("Error: " + errorMsg);
        alert("Error: " + errorMsg);
      }
    } finally {
        setIsLoadingTables(false);
    }
  };

  const handleDownloadCSV = () => {
    if (extractedTables.length === 0) return;

    const csvContent = extractedTables
      .map((row) => row.map((cell) => `"${cell}"`).join(","))
      .join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", "extracted_tables.csv");
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Helper: find debit/credit header columns (scan top-down) and return top-5 values
  const parseTopAmounts = (tables: Array<Array<any>>) => {
    const amountRegex = /-?\(?\d{1,3}(?:[,\d]*)(?:\.\d+)?\)?/g;

    let debitCol: number | null = null;
    let creditCol: number | null = null;

    // Find first occurrence of debit/credit words scanning from top rows
    for (let r = 0; r < tables.length; r++) {
      const row = tables[r] || [];
      for (let c = 0; c < row.length; c++) {
        const cell = (row[c] ?? "").toString().toLowerCase();
        if (debitCol === null && /\bdebit\b|\bdr\b/.test(cell)) {
          debitCol = c;
        }
        if (creditCol === null && /\bcredit\b|\bcr\b/.test(cell)) {
          creditCol = c;
        }
        if (debitCol !== null && creditCol !== null) break;
      }
      if (debitCol !== null && creditCol !== null) break;
    }

    // date detection for left-most column
    const dateRegex = new RegExp(
      "(\\b\\d{1,2}[-\\/.]\\d{1,2}[-\\/.]\\d{2,4}\\b)|(\\b\\d{4}[-\\/.]\\d{1,2}[-\\/.]\\d{1,2}\\b)|(" +
        "\\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\\s+\\d{1,2},?\\s+\\d{4}\\b)",
      "i"
    );

    const isDateCell = (cell: any) => {
      if (cell == null) return false;
      const s = cell.toString().trim();
      if (!s) return false;
      return dateRegex.test(s);
    };

    const parseNumber = (raw: string) => {
      if (!raw) return NaN;
      let s = raw.toString().trim();
      const isParen = /^\(.*\)$/.test(s);
      s = s.replace(/[()]/g, "");
      s = s.replace(/[^0-9.\-_,]/g, "");
      s = s.replace(/,/g, "");
      const n = parseFloat(s);
      if (isNaN(n)) return NaN;
      return n;
    };

    const collectColumnValues = (colIndex: number | null) => {
      const items: Array<any> = [];
      if (colIndex === null) return items;
      for (let r = 0; r < tables.length; r++) {
        const row = tables[r] || [];
        // require left-most column to be a date-like cell
        if (!isDateCell(row[0])) continue;
        if (colIndex >= row.length) continue;
        const cell = row[colIndex];
        if (cell == null) continue;
        const text = cell.toString();
        const matches = text.match(amountRegex);
        if (!matches) continue;
        matches.forEach((m: string) => {
          const num = parseNumber(m);
          if (!isNaN(num)) {
            items.push({ value: Math.abs(num), rowIndex: r, colIndex, raw: text });
          }
        });
      }
      return items;
    };

    let debits = collectColumnValues(debitCol);
    let credits = collectColumnValues(creditCol);

    // If none found for either, fallback to scanning cells heuristics (legacy)
    if ((debits.length === 0 && debitCol === null) || (credits.length === 0 && creditCol === null)) {
      const legacyDebits: Array<any> = [];
      const legacyCredits: Array<any> = [];
      for (let r = 0; r < tables.length; r++) {
        const row = tables[r] || [];
        // only consider rows where left-most column looks like a date
        if (!isDateCell(row[0])) continue;
        const rowText = row.map((c) => (c ?? "")).join(" ").toString().toLowerCase();
        for (let colIndex = 0; colIndex < row.length; colIndex++) {
          const cell = row[colIndex];
          const text = (cell ?? "").toString();
          const lc = text.toLowerCase();
          const matches = text.match(/([0-9]{1,3}(?:[0-9,]*)(?:\.\d+)?)/g);
          if (!matches) continue;
          matches.forEach((m: string) => {
            const num = parseFloat(m.replace(/,/g, ""));
            if (isNaN(num)) return;
            if (/\bcr\b|credit/.test(lc) || /\(cr\)/.test(lc)) {
              legacyCredits.push({ value: num, rowIndex: r, colIndex, raw: text });
            } else if (/\bdr\b|debit|withdrawal/.test(lc) || /-\d/.test(text)) {
              legacyDebits.push({ value: num, rowIndex: r, colIndex, raw: text });
            } else {
              if (/credit|\bcr\b/.test(rowText)) {
                legacyCredits.push({ value: num, rowIndex: r, colIndex, raw: text });
              } else if (/debit|\bdr\b|withdrawal/.test(rowText)) {
                legacyDebits.push({ value: num, rowIndex: r, colIndex, raw: text });
              }
            }
          });
        }
      }
      if (debits.length === 0) debits = legacyDebits;
      if (credits.length === 0) credits = legacyCredits;
    }

    // sort descending
    debits.sort((a, b) => b.value - a.value);
    credits.sort((a, b) => b.value - a.value);

    return { debits: debits.slice(0, 5), credits: credits.slice(0, 5) };
  };

  const exportTopDebitCreditCSV = (debits: Array<any>, credits: Array<any>) => {
    const hasDebits = debits && debits.length > 0;
    const hasCredits = credits && credits.length > 0;
    if (!hasDebits && !hasCredits) {
      alert("No debit or credit entries found to export");
      return;
    }

    const quote = (s: any) => `"${String(s ?? "").replace(/"/g, '""')}"`;
    const maxRows = Math.max(debits?.length || 0, credits?.length || 0);
    const rows: string[] = [];
    rows.push("debit,credit");
    for (let i = 0; i < maxRows; i++) {
      const dRaw = debits && debits[i] ? debits[i].raw : "";
      const cRaw = credits && credits[i] ? credits[i].raw : "";
      rows.push(`${quote(dRaw)},${quote(cRaw)}`);
    }

    const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `top5_debit_credit.csv`;
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportTopDebitCredit = () => {
    const { debits, credits } = parseTopAmounts(extractedTables as Array<Array<any>>);
    exportTopDebitCreditCSV(debits, credits);
  };

  const handleClearGallery = () => {
    gallery.forEach((item) => URL.revokeObjectURL(item.url));
    setGallery([]);
    setSelectedGalleryIndex(null);
  };

  return (
    <div style={{ paddingBottom: "80px", marginBottom: "80px" }}>
      {/* Loading Bar */}
      {(isLoading || isLoadingDOB || isLoadingText || isLoadingTables || isLoadingAadhar) && (
        <div
          style={{
            position: "fixed",
            top: "0",
            left: "0",
            right: "0",
            height: "4px",
            backgroundColor: "#636fe9",
            animation: "progress 1s ease-in-out infinite",
            zIndex: "10000",
          }}
        >
          <style>{`
            @keyframes progress {
              0% {
                width: 0%;
              }
              50% {
                width: 80%;
              }
              100% {
                width: 100%;
              }
            }
          `}</style>
        </div>
      )}
      
      {/* Logo */}
      <div
        style={{
          position: "absolute",
          top: "15%",
          left: "50%",
          transform: "translate(-50%, -50%)",
        }}
      >
        <img
          src={ocrhunterLogo}
          alt="OCRHunter logo"
          style={{ width: "230px", height: "auto" }}
        />
      </div>

      {/* Buttons below logo */}
      <div
        style={{
          position: "absolute",
          top: "30%",
          left: "0",
          right: "0",
          padding: "0 50px",
          display: "flex",
          gap: "20px",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        {["Select Document ", "Select Document type"].map((label) =>
          label === "Select Document type" ? (
            <select
              key={label}
              value={selectedDocumentType}
              onChange={(e) => setSelectedDocumentType(e.target.value)}
              style={{
                backgroundColor: "#636fe9",
                color: "white",
                border: "1px solid #ccc",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "18px",
                cursor: "pointer",
                fontWeight: "500",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flex: "1",
                margin: "0 10px",
                transition: "background-color 0.3s ease",
              }}
            >
              <option value="">Select Document Type</option>
              <option value="pan card">Pan Card</option>
              <option value="aadhar card">Aadhar Card</option>
              <option value="bank statement">Bank Statement</option>
            </select>
          ) : (
            <button
              key={label}
              onClick={handleSelectDocumentClick}
              onMouseEnter={() =>
                setHovered((prev) => ({ ...prev, [label]: true }))
              }
              onMouseLeave={() =>
                setHovered((prev) => ({ ...prev, [label]: false }))
              }
              style={{
                backgroundColor: hovered[label] ? "#4a5bd1" : "#636fe9",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "18px",
                cursor: "pointer",
                fontWeight: "500",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flex: "1",
                margin: "0 10px",
                transition: "background-color 0.3s ease",
              }}
            >
              {label}
            </button>
          )
        )}
      </div>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/*,.pdf"
        style={{ display: "none" }}
      />

      {/* Document name */}
      {selectedFile && (
        <div
          style={{
            position: "absolute",
            top: "40%",
            left: "50px",
            fontSize: "18px",
            fontWeight: "500",
            color: "#333",
          }}
        >
          {selectedFile.name}
        </div>
      )}

      {/* Two-column layout */}
      <div
        style={{
          position: "absolute",
          top: "45%",
          left: "0",
          right: "0",
          padding: "0 50px",
          display: "flex",
          gap: "20px",
          height: "100%",
        }}
      >
        {/* Left column - Document preview */}
         <div
          style={{
            flex: "0.9",
            borderRadius: "8px",
            padding: "10px",
            display: "flex",
            flexDirection: "column",
            position: "relative",
            // Removed maxHeight constraint that was preventing the box from growing
          }}
        >
          <div
            style={{
              height: "600px", // CHANGE THIS VALUE: Increase/decrease to change preview box height
              maxHeight: "600px", // CHANGE THIS VALUE: Must match height above
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              position: "relative",
              border: selectedFile ? "1px solid #ddd" : "none",
              borderRadius: "8px",
              overflow: "auto", // Added: Enable scrolling for tall images
              backgroundColor: "#f5f5f5", // Added: Background to visualize container size
            }}
          >
            {selectedFile ? (
              selectedFile.type.startsWith("image/") ? (
                <img
                  src={documentUrl || ""}
                  alt="Selected Document"
                  style={{
                    maxWidth: "100%",
                    maxHeight: "100%",
                    objectFit: "contain",
                  }}
                />
              ) : selectedFile.type === "application/pdf" ? (
                <iframe
                  src={documentUrl || ""}
                  style={{ width: "100%", height: "100%", border: "none" }}
                  title="Selected PDF Document"
                />
              ) : (
                <p>{selectedFile.name}</p>
              )
            ) : (
              <p style={{ color: "#999" }}>No document selected</p>
            )}
            {selectedFile && (
              <button
                onClick={handleCloseDocument}
                style={{
                  position: "absolute",
                  top: "10px",
                  right: "10px",
                  width: "30px",
                  height: "30px",
                  backgroundColor: "#ff4444",
                  color: "white",
                  border: "none",
                  borderRadius: "50%",
                  cursor: "pointer",
                  fontSize: "18px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: "bold",
                }}
              >
                ×
              </button>
            )}
          </div>

          {selectedFile && (
            <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
              <button
                onClick={handleExtractText}
                  disabled={isLoadingText}
                style={{
                    backgroundColor: isLoadingText ? "#ccc" : "#636fe9",
                  color: "white",
                  border: "none",
                  borderRadius: "8px",
                  padding: "12px 20px",
                  fontSize: "16px",
                    cursor: isLoadingText ? "not-allowed" : "pointer",
                  fontWeight: "500",
                  transition: "background-color 0.3s ease",
                }}
                onMouseEnter={(e) => {
                    if (!isLoadingText)
                    e.currentTarget.style.backgroundColor = "#4a5bd1";
                }}
                onMouseLeave={(e) => {
                    if (!isLoadingText)
                    e.currentTarget.style.backgroundColor = "#636fe9";
                }}
              >
                  {isLoadingText ? "Extracting..." : "Extract All Text"}
              </button>
              {selectedFile.type === "application/pdf" && (
                <button
                  onClick={handleExtractTables}
                    disabled={isLoadingTables}
                  style={{
                      backgroundColor: isLoadingTables ? "#ccc" : "#28a745",
                    color: "white",
                    border: "none",
                    borderRadius: "8px",
                    padding: "12px 20px",
                    fontSize: "16px",
                      cursor: isLoadingTables ? "not-allowed" : "pointer",
                    fontWeight: "500",
                    transition: "background-color 0.3s ease",
                  }}
                  onMouseEnter={(e) => {
                      if (!isLoadingTables)
                      e.currentTarget.style.backgroundColor = "#218838";
                  }}
                  onMouseLeave={(e) => {
                      if (!isLoadingTables)
                      e.currentTarget.style.backgroundColor = "#28a745";
                  }}
                >
                    {isLoadingTables ? "Extracting..." : "Extract Tables"}
                </button>
              )}
            </div>
          )}

          {/* Paste Screenshot Box */}
          <div
            style={{
              marginTop: "20px",
              padding: "20px",
              border: "2px dashed #ccc",
              borderRadius: "8px",
              textAlign: "center",
              color: "#666",
              fontSize: "16px",
              cursor: "pointer",
              backgroundColor: "#f9f9f9",
              minHeight: "8px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            onPaste={handlePasteScreenshot}
            tabIndex={0}
            onClick={() =>
              alert("Click here and press Ctrl+V to paste a screenshot")
            }
          >
            📸 Paste screenshot here
          </div>

          {error && (
            <div
              style={{
                marginTop: "10px",
                padding: "10px",
                backgroundColor: "#ffebee",
                border: "1px solid #f44336",
                borderRadius: "8px",
                color: "#c62828",
                fontSize: "14px",
                whiteSpace: "pre-wrap",
              }}
            >
              {error}
            </div>
          )}
        </div>

        {/* Right column - Extracted text */}
        <div
          style={{
            flex: "1.0",
            maxWidth: "600px", // Add this to limit the maximum width
            minWidth: "600px", // Add this to maintain constant width
            height: "100%",
            borderRadius: "8px",
            padding: "1px",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <h3 style={{ margin: "0 0 10px 0" }}>Extracted Text 📖</h3>

          <div
            style={{
              height: "500px",
              width: "100%", // This will now respect the parent's fixed width
              borderRadius: "8px",
              padding: "10px",
              fontSize: "14px",
              border: "1px solid #ccc",
              overflow: "auto",
              fontFamily: "monospace",
              backgroundColor: "#fff",
            }}
            dangerouslySetInnerHTML={{
              __html:
                highlightedText ||
                extractedText ||
                "Extracted text will appear here...",
            }}
          />

          {extractedText && (
            <div style={{ marginTop: "10px", display: "flex", gap: "10px" }}>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter search query"
                style={{
                  flex: "1",
                  borderRadius: "8px",
                  padding: "8px 12px",
                  fontSize: "14px",
                  border: "1px solid #ccc",
                  fontFamily: "monospace",
                }}
              />
              <button
                onClick={handleSearch}
                style={{
                  backgroundColor: "#636fe9",
                  color: "white",
                  border: "none",
                  borderRadius: "8px",
                  padding: "8px 16px",
                  fontSize: "14px",
                  cursor: "pointer",
                  fontWeight: "500",
                  transition: "background-color 0.3s ease",
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.backgroundColor = "#4a5bd1")
                }
                onMouseLeave={(e) =>
                  (e.currentTarget.style.backgroundColor = "#636fe9")
                }
              >
                Search
              </button>
            </div>
          )}

          {extractedText && (
            <div style={{ position: "relative", marginTop: "10px" }}>
              <button
                onClick={handleCopyText}
                style={{
                  position: "absolute",
                  left: "0",
                  backgroundColor: "#636fe9",
                  color: "white",
                  border: "none",
                  borderRadius: "8px",
                  padding: "8px 16px",
                  fontSize: "14px",
                  cursor: "pointer",
                  fontWeight: "500",
                  transition: "background-color 0.3s ease",
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.backgroundColor = "#4a5bd1")
                }
                onMouseLeave={(e) =>
                  (e.currentTarget.style.backgroundColor = "#636fe9")
                }
              >
                Copy Text
              </button>
              <button
                onClick={handleClearText}
                style={{
                  position: "absolute",
                  right: "0",
                  backgroundColor: "#ff4444",
                  color: "white",
                  border: "none",
                  borderRadius: "8px",
                  padding: "8px 16px",
                  fontSize: "14px",
                  cursor: "pointer",
                  fontWeight: "500",
                  transition: "background-color 0.3s ease",
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.backgroundColor = "#cc0000")
                }
                onMouseLeave={(e) =>
                  (e.currentTarget.style.backgroundColor = "#ff4444")
                }
              >
                Clear
              </button>
            </div>
          )}

          {/* Gallery Section */}
          <div
            style={{
              marginTop: "40px",
              border: "1px solid #ddd",
              borderRadius: "8px",
              padding: "10px",
              backgroundColor: "#f9f9f9",
              position: "relative",
            }}
          >
            <h3 style={{ margin: "0 0 10px 0" }}>🖼️ Gallery</h3>
            <div
              style={{
                height: "200px",
                display: "flex",
                flexWrap: "wrap",
                gap: "10px",
                overflowY: "auto",
                border: gallery.length === 0 ? "1px dashed #ccc" : "none",
                borderRadius: "8px",
                padding: gallery.length === 0 ? "20px" : "0",
                alignItems: gallery.length === 0 ? "center" : "flex-start",
                justifyContent: gallery.length === 0 ? "center" : "flex-start",
                color: "#666",
                fontSize: "16px",
              }}
            >
              {gallery.length === 0
                ? "Gallery content will appear here"
                : gallery.map((item, index) => (
                    <div
                      key={index}
                      style={{ position: "relative", display: "inline-block" }}
                    >
                      <img
                        src={item.url}
                        alt={`Gallery item ${index + 1}`}
                        style={{
                          width: "80px",
                          height: "80px",
                          objectFit: "cover",
                          borderRadius: "4px",
                          cursor: "pointer",
                          border:
                            selectedGalleryIndex === index
                              ? "2px solid #636fe9"
                              : "1px solid #ddd",
                        }}
                        onClick={() => setSelectedGalleryIndex(index)}
                      />
                      {selectedGalleryIndex === index && (
                        <button
                          onClick={handleExtractFromGallery}
                          disabled={isLoading}
                          style={{
                            position: "absolute",
                            top: "50%",
                            left: "50%",
                            transform: "translate(-50%, -50%)",
                            backgroundColor: isLoading ? "#ccc" : "#636fe9",
                            color: "white",
                            border: "none",
                            borderRadius: "4px",
                            padding: "4px 8px",
                            fontSize: "12px",
                            cursor: isLoading ? "not-allowed" : "pointer",
                            fontWeight: "300",
                            boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
                          }}
                        >
                          {isLoading ? "..." : "Extract"}
                        </button>
                      )}
                    </div>
                  ))}
            </div>
            {gallery.length > 0 && (
              <button
                onClick={handleClearGallery}
                style={{
                  position: "absolute",
                  bottom: "10px",
                  left: "10px",
                  backgroundColor: "#ff4444",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  padding: "6px 12px",
                  fontSize: "12px",
                  cursor: "pointer",
                  fontWeight: "500",
                  transition: "background-color 0.3s ease",
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.backgroundColor = "#cc0000")
                }
                onMouseLeave={(e) =>
                  (e.currentTarget.style.backgroundColor = "#ff4444")
                }
              >
                Clear Gallery
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Extracted Tables Section */}
      <div
        style={{
          position: "absolute",
          top: "150%",
          left: "0",
          right: "0",
          padding: "20px 50px",
          border: "1px solid #ddd",
          borderRadius: "8px",
          backgroundColor: "#f9f9f9",
        }}
      >
        <div
          style={{
            marginBottom: "10px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <h3 style={{ margin: 0 }}>Extracted Tables 📊</h3>
            {extractedTables.length > 0 && (
              <button
                onClick={handleClearTables}
                style={{
                  width: "30px",
                  height: "30px",
                  backgroundColor: "#ff4444",
                  color: "white",
                  border: "none",
                  borderRadius: "50%",
                  cursor: "pointer",
                  fontSize: "18px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: "bold",
                  transition: "background-color 0.3s ease",
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.backgroundColor = "#cc0000")
                }
                onMouseLeave={(e) =>
                  (e.currentTarget.style.backgroundColor = "#ff4444")
                }
              >
                ×
              </button>
            )}
          </div>
  {extractedTables.length > 0 && (
    <button
      onClick={handleDownloadCSV}
      style={{
        backgroundColor: "#28a745",
        color: "white",
        border: "none",
        borderRadius: "8px",
        padding: "8px 16px",
        fontSize: "14px",
        cursor: "pointer",
        fontWeight: "500",
        transition: "background-color 0.3s ease",
        marginLeft: "20px",
      }}
      onMouseEnter={(e) =>
        (e.currentTarget.style.backgroundColor = "#218838")
      }
      onMouseLeave={(e) =>
        (e.currentTarget.style.backgroundColor = "#28a745")
      }
    >
      📥 Download CSV
    </button>
  )}
          {extractedTables.length > 0 && (
            <div style={{ display: "inline-flex", gap: "8px", marginLeft: "10px" }}>
              <button
                onClick={handleExportTopDebitCredit}
                style={{
                  backgroundColor: "#6a5acd",
                  color: "white",
                  border: "none",
                  borderRadius: "8px",
                  padding: "8px 12px",
                  fontSize: "13px",
                  cursor: "pointer",
                  fontWeight: "500",
                }}
                title="Export top 5 highest debits and credits"
              >
                📥 Export Top 5 Debit & Credit
              </button>
            </div>
          )}
        </div>

        {extractedTables.length > 0 ? (
          <div
            style={{
              height: "300px",
              width: "100%",
              borderRadius: "8px",
              // border: '1px solid #ccc',
              overflow: "auto",
              // backgroundColor: '#fff',
              paddingLeft: "0px",
              paddingRight: "0px",
            }}
          >
            <table
              style={{
                width: "auto",
                borderCollapse: "collapse",
                fontSize: "14px",
                fontFamily: "monospace",
                margin: "0 auto",
              }}
            >
              <tbody>
                {extractedTables.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {row.map((cell, cellIndex) => (
                      <td
                        key={cellIndex}
                        style={{
                          border: "1px solid #ddd",
                          padding: "8px 40px",
                          backgroundColor: rowIndex === 0 ? "#e9ecef" : "white",
                        }}
                      >
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div
            style={{
              height: "100px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#666",
              fontSize: "16px",
              border: "1px dashed #ccc",
              borderRadius: "8px",
              backgroundColor: "#f9f9f9",
            }}
          >
            Extracted tables will appear here
          </div>
        )}
      </div>

      {/* Prompt Gallery Section */}
      <div
        style={{
          position: "absolute",
          top: "210%",
          left: "0",
          right: "0",
          padding: "20px 50px",
        }}
      >
        <h3>Prompt Gallery 💡</h3>
        {selectedDocumentType === "pan card" ? (
          <div>
            <h4>Preset Prompts for Pan Card:</h4>
            <button
              onClick={async () => {
                if (!selectedFile) {
                  setPanNumber("No file selected");
                  return;
                }

                setIsLoading(true);
                setError("");
                const formData = new FormData();
                formData.append("file", selectedFile);

                console.log("Extracting PAN from:", selectedFile.name);

                try {
                  const response = await fetch(
                    "http://localhost:5001/extract-pan",
                    {
                      method: "POST",
                      body: formData,
                    }
                  );

                  console.log("PAN extract response status:", response.status);
                  const data = await response.json();
                  console.log("PAN extract response data:", data);

                  if (response.ok && data.pan_number) {
                    setPanNumber(data.pan_number);
                  } else {
                    setPanNumber("PAN Number not found");
                  }
                } catch (error) {
                  console.error("PAN extract error:", error);
                  setPanNumber("Error extracting PAN number");
                } finally {
                  setIsLoading(false);
                }
              }}
              disabled={!selectedFile || isLoading}
              style={{
                backgroundColor:
                  selectedFile && !isLoading ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                cursor: selectedFile && !isLoading ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {isLoading ? "Extracting..." : "Extract PAN Number"}
            </button>
            <button
              onClick={async () => {
                if (!selectedFile) {
                  setFetchDOB("No file selected");
                  return;
                }

                setIsLoading(true);
                setError("");
                const formData = new FormData();
                formData.append("file", selectedFile);

                console.log("Extracting DOB from:", selectedFile.name);

                try {
                  const response = await fetch(
                    "http://localhost:5001/extract-dob",
                    {
                      method: "POST",
                      body: formData,
                    }
                  );

                  console.log("DOB extract response status:", response.status);
                  const data = await response.json();
                  console.log("DOB extract response data:", data);

                  if (response.ok && data.dob) {
                    const dobData = data.dob;
                    if (typeof dobData === "object" && dobData.dob) {
                      // Just display the DOB, no format or confidence
                      setFetchDOB(dobData.dob);
                    } else {
                      setFetchDOB(dobData);
                    }
                    console.log("✅ DOB extracted successfully:", dobData);
                  } else {
                    setFetchDOB("DOB not found");
                    console.log("❌ DOB not found in document");
                  }
                } catch (error) {
                  console.error("❌ DOB extract error:", error);
                  setFetchDOB("Error extracting DOB");
                } finally {
                  setIsLoading(false);
                }
              }}
              disabled={!selectedFile || isLoading}
              style={{
                backgroundColor:
                  selectedFile && !isLoading ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                cursor: selectedFile && !isLoading ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {isLoading
                ? "Extracting..."
                : selectedFile
                ? "Fetch DOB"
                : "No doc selected"}
            </button>
            {/* Display extracted PAN number */}
            {panNumber && (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>PAN Number:</strong> {panNumber}
              </div>
            )}
            {/* Display extracted DOB */}
            {FetchDOB && (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>Date of Birth:</strong> {FetchDOB}
              </div>
            )}
            {/* Add more buttons as needed */}
          </div>
        ) : selectedDocumentType === "aadhar card" ? (
          <div>
            <h4>Preset Prompts for Aadhar Card:</h4>
            <p>
              Selected Document:{" "}
              {selectedFile ? selectedFile.name : "No document selected"}
            </p>
            <button
              onClick={handleExtractAadhar}
              disabled={!selectedFile || isLoadingAadhar}
              style={{
                backgroundColor:
                  selectedFile && !isLoadingAadhar ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                  cursor: selectedFile && !isLoadingAadhar ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                  if (selectedFile && !isLoadingAadhar)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                  if (selectedFile && !isLoadingAadhar)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {selectedFile
                  ? isLoadingAadhar
                  ? "Extracting..."
                  : "Extract Aadhar Number"
                : "No doc selected"}
            </button>

            <button
              onClick={handleExtractDOB}
              disabled={!selectedFile || isLoadingDOB}
              style={{
                backgroundColor:
                  selectedFile && !isLoadingDOB ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                cursor:
                  selectedFile && !isLoadingDOB ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (selectedFile && !isLoadingDOB)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                if (selectedFile && !isLoadingDOB)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {isLoadingDOB
                ? "Extracting..."
                : selectedFile
                ? "fetch DOB"
                : "No doc selected"}
            </button>

            {aadharNumber && (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>Aadhar Number:</strong> {aadharNumber}
              </div>
            )}

            {FetchDOB && (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>Date of birth:</strong> {FetchDOB}
              </div>
            )}

            {/* Add more buttons as needed */}
          </div>
        ) : selectedDocumentType === "bank statement" ? (
          <div>
            <h4>Preset Prompts for Bank Statement:</h4>
            <p>
              Selected Document:{" "}
              {selectedFile ? selectedFile.name : "No document selected"}
            </p>
            <button
              onClick={async () => {
                if (!selectedFile) {
                  setBankPanNumber("No file selected");
                  return;
                }

                setIsLoading(true);
                setError("");
                const formData = new FormData();
                formData.append("file", selectedFile);

                console.log(
                  "Attempting to extract PAN from:",
                  selectedFile.name
                );
                console.log("File type:", selectedFile.type);
                console.log("File size:", selectedFile.size, "bytes");

                try {
                  console.log(
                    "Sending request to http://localhost:5001/extract-pan"
                  );

                  const response = await fetch(
                    "http://localhost:5001/extract-pan",
                    {
                      method: "POST",
                      body: formData,
                    }
                  );

                  console.log("Response status:", response.status);
                  console.log("Response ok:", response.ok);

                  const data = await response.json();
                  console.log("Response data:", data);

                  if (response.ok && data.pan_number) {
                    setBankPanNumber(data.pan_number);
                    console.log(
                      "✅ PAN extracted successfully:",
                      data.pan_number
                    );
                  } else {
                    setBankPanNumber("PAN Number not found");
                    console.log("❌ PAN not found in document");
                  }
                } catch (error) {
                  console.error("❌ Network error:", error);
                  setBankPanNumber("Error extracting PAN number");
                } finally {
                  setIsLoading(false);
                }
              }}
              disabled={!selectedFile || isLoading}
              style={{
                backgroundColor:
                  selectedFile && !isLoading ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                cursor: selectedFile && !isLoading ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {isLoading ? "Extracting..." : "Extract PAN Number"}
            </button>
            <button
              onClick={async () => {
                if (!selectedFile) {
                  setAccountNumber("No file selected");
                  return;
                }

                setIsLoading(true);
                setError("");
                const formData = new FormData();
                formData.append("file", selectedFile);

                try {
                  // Extract text from first page only
                  const response = await fetch(
                    "http://localhost:5001/extract-text-first-page",
                    {
                      method: "POST",
                      body: formData,
                    }
                  );

                  const data = await response.json();
                  if (response.ok && data.extracted_text) {
                    const textToSearch = data.extracted_text;
                    // Now search for account number
                    const accPattern = new RegExp(
                      "\\b(?:account\\s*number|account\\s*no\\.?|accountno|a\\/c(?:\\s*no?)?|ac(?:c?t)?\\s*no?|acct\\s*#?|acc#|account\\s*id|accountid|account)\\s*[:\\-#]?\\s*(\\d{9,18})\\b",
                      "i"
                    );
                    const match = textToSearch.match(accPattern);
                    if (match) {
                      setAccountNumber(match[1]);
                    } else {
                      setAccountNumber("Account Number not found");
                    }
                  } else {
                    setAccountNumber("Failed to extract text from first page");
                  }
                } catch (error) {
                  setAccountNumber("Error extracting text from first page");
                } finally {
                  setIsLoading(false);
                }
              }}
              disabled={!selectedFile || isLoading}
              style={{
                backgroundColor:
                  selectedFile && !isLoading ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                cursor: selectedFile && !isLoading ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {isLoading ? "Extracting..." : "Fetch Account number"}
            </button>
            <button
              onClick={async () => {
                if (!selectedFile) {
                  setIfscCode("No file selected");
                  return;
                }

                setIsLoading(true);
                setError("");
                const formData = new FormData();
                formData.append("file", selectedFile);

                console.log("Extracting IFSC Code from:", selectedFile.name);

                try {
                  const response = await fetch(
                    "http://localhost:5001/extract-ifsc",
                    {
                      method: "POST",
                      body: formData,
                    }
                  );

                  console.log("IFSC extract response status:", response.status);
                  const data = await response.json();
                  console.log("IFSC extract response data:", data);

                  if (response.ok && data.ifsc_code) {
                    setIfscCode(data.ifsc_code);
                  } else {
                    setIfscCode("IFSC Code not found");
                  }
                } catch (error) {
                  console.error("IFSC extract error:", error);
                  setIfscCode("Error extracting IFSC Code");
                } finally {
                  setIsLoading(false);
                }
              }}
              disabled={!selectedFile || isLoading}
              style={{
                backgroundColor:
                  selectedFile && !isLoading ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                cursor: selectedFile && !isLoading ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {isLoading
                ? "Extracting..."
                : selectedFile
                ? "Fetch IFSC code"
                : "No doc selected"}
            </button>
            <button
              onClick={async () => {
                if (!selectedFile) {
                  setCustomerId("No file selected");
                  return;
                }

                setIsLoading(true);
                setError("");
                const formData = new FormData();
                formData.append("file", selectedFile);

                console.log("Extracting Customer ID from:", selectedFile.name);

                try {
                  const response = await fetch(
                    "http://localhost:5001/extract-customer-id",
                    {
                      method: "POST",
                      body: formData,
                    }
                  );

                  console.log(
                    "Customer ID extract response status:",
                    response.status
                  );
                  const data = await response.json();
                  console.log("Customer ID extract response data:", data);

                  if (response.ok && data.customer_id) {
                    setCustomerId(data.customer_id);
                  } else {
                    setCustomerId("Customer ID not found");
                  }
                } catch (error) {
                  console.error("Customer ID extract error:", error);
                  setCustomerId("Error extracting Customer ID");
                } finally {
                  setIsLoading(false);
                }
              }}
              disabled={!selectedFile || isLoading}
              style={{
                backgroundColor:
                  selectedFile && !isLoading ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                cursor: selectedFile && !isLoading ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {isLoading ? "Extracting..." : "Fetch Customer ID"}
            </button>
            <button
              onClick={async () => {
                if (!selectedFile) {
                  setMobileNumber("No file selected");
                  return;
                }

                setIsLoading(true);
                setError("");
                const formData = new FormData();
                formData.append("file", selectedFile);

                console.log(
                  "Extracting Mobile Number from:",
                  selectedFile.name
                );

                try {
                  const response = await fetch(
                    "http://localhost:5001/extract-mobile-number",
                    {
                      method: "POST",
                      body: formData,
                    }
                  );

                  console.log(
                    "Mobile Number extract response status:",
                    response.status
                  );
                  const data = await response.json();
                  console.log("Mobile Number extract response data:", data);

                  if (response.ok && data.mobile_number) {
                    setMobileNumber(data.mobile_number);
                  } else {
                    setMobileNumber("Mobile Number not found");
                  }
                } catch (error) {
                  console.error("Mobile Number extract error:", error);
                  setMobileNumber("Error extracting Mobile Number");
                } finally {
                  setIsLoading(false);
                }
              }}
              disabled={!selectedFile || isLoading}
              style={{
                backgroundColor:
                  selectedFile && !isLoading ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                cursor: selectedFile && !isLoading ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {isLoading ? "Extracting..." : "Fetch Mobile Number"}
            </button>
            <button
              onClick={async () => {
                if (!selectedFile) {
                  setCkyc("No file selected");
                  return;
                }

                setIsLoading(true);
                setError("");
                const formData = new FormData();
                formData.append("file", selectedFile);

                console.log("Extracting CKYC from:", selectedFile.name);

                try {
                  const response = await fetch(
                    "http://localhost:5001/extract-ckyc",
                    {
                      method: "POST",
                      body: formData,
                    }
                  );

                  console.log("CKYC extract response status:", response.status);
                  const data = await response.json();
                  console.log("CKYC extract response data:", data);

                  if (response.ok && data.ckyc) {
                    setCkyc(data.ckyc);
                  } else {
                    setCkyc("CKYC not found");
                  }
                } catch (error) {
                  console.error("CKYC extract error:", error);
                  setCkyc("Error extracting CKYC");
                } finally {
                  setIsLoading(false);
                }
              }}
              disabled={!selectedFile || isLoading}
              style={{
                backgroundColor:
                  selectedFile && !isLoading ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                cursor: selectedFile && !isLoading ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {isLoading ? "Extracting..." : "Fetch CKYC"}
            </button>
            <button
              onClick={async () => {
                if (!selectedFile) {
                  setEmailIds([]);
                  return;
                }

                setIsLoading(true);
                setError("");
                const formData = new FormData();
                formData.append("file", selectedFile);

                console.log("Extracting Email from:", selectedFile.name);

                try {
                  const response = await fetch(
                    "http://localhost:5001/extract-email",
                    {
                      method: "POST",
                      body: formData,
                    }
                  );

                  console.log(
                    "Email extract response status:",
                    response.status
                  );
                  const data = await response.json();
                  console.log("Email extract response data:", data);

                  if (
                    response.ok &&
                    data.email_ids &&
                    data.email_ids.length > 0
                  ) {
                    setEmailIds(data.email_ids);
                    setEmailExtracted(true);
                    console.log(
                      "✅ Emails extracted successfully:",
                      data.email_ids
                    );
                  } else {
                    setEmailIds([]);
                    setEmailExtracted(true);
                    console.log("❌ Emails not found in document");
                  }
                } catch (error) {
                  console.error("❌ Email extract error:", error);
                  setEmailIds([]);
                  setEmailExtracted(true);
                } finally {
                  setIsLoading(false);
                }
              }}
              disabled={!selectedFile || isLoading}
              style={{
                backgroundColor:
                  selectedFile && !isLoading ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                cursor: selectedFile && !isLoading ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {isLoading ? "Extracting..." : "Fetch Email"}
            </button>
            <button
              onClick={async () => {
                if (!selectedFile) {
                  setAccountType("No file selected");
                  return;
                }

                setIsLoading(true);
                setError("");
                const formData = new FormData();
                formData.append("file", selectedFile);

                console.log("Extracting Account Type from:", selectedFile.name);

                try {
                  const response = await fetch(
                    "http://localhost:5001/extract-account-type",
                    {
                      method: "POST",
                      body: formData,
                    }
                  );

                  console.log(
                    "Account Type extract response status:",
                    response.status
                  );
                  const data = await response.json();
                  console.log("Account Type extract response data:", data);

                  if (response.ok && data.account_type) {
                    const accountTypeData = data.account_type;
                    if (
                      typeof accountTypeData === "object" &&
                      accountTypeData.account_type
                    ) {
                      setAccountType(
                        `${accountTypeData.label}: ${accountTypeData.account_type}`
                      );
                    } else {
                      setAccountType(accountTypeData);
                    }
                  } else {
                    setAccountType("Account Type not found");
                  }
                } catch (error) {
                  console.error("Account Type extract error:", error);
                  setAccountType("Error extracting Account Type");
                } finally {
                  setIsLoading(false);
                }
              }}
              disabled={!selectedFile || isLoading}
              style={{
                backgroundColor:
                  selectedFile && !isLoading ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                cursor: selectedFile && !isLoading ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {isLoading ? "Extracting..." : "Fetch Account Type"}
            </button>
            <button
              onClick={async () => {
                if (!selectedFile) {
                  setOpeningBalance("No file selected");
                  return;
                }

                setIsLoading(true);
                setError("");
                const formData = new FormData();
                formData.append("file", selectedFile);

                console.log(
                  "Extracting Opening Balance from:",
                  selectedFile.name
                );

                try {
                  const response = await fetch(
                    "http://localhost:5001/extract-opening-balance",
                    {
                      method: "POST",
                      body: formData,
                    }
                  );

                  console.log(
                    "Opening Balance extract response status:",
                    response.status
                  );
                  const data = await response.json();
                  console.log("Opening Balance extract response data:", data);

                  if (response.ok && data.opening_balance) {
                    const balance = data.opening_balance;
                    const balanceTypeDisplay =
                      balance.type && (balance.type.toUpperCase() === "CR" || balance.type.toUpperCase() === "DR")
                        ? ` (${balance.type})`
                        : "";
                    setOpeningBalance(`${balance.amount}${balanceTypeDisplay}`);
                    console.log(
                      "✅ Opening Balance extracted successfully:",
                      `${balance.amount} (${balance.type})`
                    );
                  } else {
                    setOpeningBalance("Opening Balance not found");
                    console.log("❌ Opening Balance not found in document");
                  }
                } catch (error) {
                  console.error("Opening Balance extract error:", error);
                  setOpeningBalance("Error extracting Opening Balance");
                } finally {
                  setIsLoading(false);
                }
              }}
              disabled={!selectedFile || isLoading}
              style={{
                backgroundColor:
                  selectedFile && !isLoading ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                cursor: selectedFile && !isLoading ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {isLoading ? "Extracting..." : "Fetch Opening Balance"}
            </button>
            <button
              onClick={async () => {
                if (!selectedFile) {
                  setStatementPeriod("No file selected");
                  return;
                }

                setIsLoading(true);
                setError("");
                const formData = new FormData();
                formData.append("file", selectedFile);

                console.log(
                  "Extracting Statement Period from:",
                  selectedFile.name
                );

                try {
                  const response = await fetch(
                    "http://localhost:5001/extract-statement-period",
                    {
                      method: "POST",
                      body: formData,
                    }
                  );

                  console.log(
                    "Statement Period extract response status:",
                    response.status
                  );
                  const data = await response.json();
                  console.log("Statement Period extract response data:", data);

                  if (response.ok && data.statement_period) {
                    const period = data.statement_period;
                    setStatementPeriod(
                      `From: ${period.from_date} To: ${period.to_date}`
                    );
                    console.log(
                      "✅ Statement Period extracted successfully:",
                      period
                    );
                  } else {
                    setStatementPeriod("Statement Period not found");
                    console.log("❌ Statement Period not found in document");
                  }
                } catch (error) {
                  console.error("Statement Period extract error:", error);
                  setStatementPeriod("Error extracting Statement Period");
                } finally {
                  setIsLoading(false);
                }
              }}
              disabled={!selectedFile || isLoading}
              style={{
                backgroundColor:
                  selectedFile && !isLoading ? "#636fe9" : "#ccc",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "16px",
                cursor: selectedFile && !isLoading ? "pointer" : "not-allowed",
                fontWeight: "500",
                margin: "5px",
                transition: "background-color 0.3s ease",
              }}
              onMouseEnter={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#4a5bd1";
              }}
              onMouseLeave={(e) => {
                if (selectedFile && !isLoading)
                  e.currentTarget.style.backgroundColor = "#636fe9";
              }}
            >
              {isLoading
                ? "Extracting..."
                : selectedFile
                ? "Fetch Statement Period"
                : "No doc selected"}
            </button>

            {/* Display extracted data */}
            {bankPanNumber && (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>PAN Number:</strong> {bankPanNumber}
              </div>
            )}
            {accountNumber && (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>Account Number:</strong> {accountNumber}
              </div>
            )}
            {ifscCode && (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>IFSC Code:</strong> {ifscCode}
              </div>
            )}
            {statementPeriod && (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>Statement Period:</strong> {statementPeriod}
              </div>
            )}
            {customerId && (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>Customer ID:</strong> {customerId}
              </div>
            )}
            {mobileNumber && (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>Mobile Number:</strong> {mobileNumber}
              </div>
            )}
            {emailExtracted && emailIds.length === 0 ? (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>Email IDs not found</strong>
              </div>
            ) : (
              emailIds.length > 0 && (
                <div
                  style={{
                    marginTop: "10px",
                    padding: "10px",
                    backgroundColor: "#f0f8ff",
                    border: "1px solid #636fe9",
                    borderRadius: "8px",
                    fontSize: "16px",
                    fontWeight: "500",
                  }}
                >
                  <strong>Email IDs:</strong> {emailIds.join(", ")}
                </div>
              )
            )}
            {ckyc && (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>CKYC:</strong> {ckyc}
              </div>
            )}
            {accountType && (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>Account Type:</strong> {accountType}
              </div>
            )}
            {openingBalance && (
              <div
                style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#f0f8ff",
                  border: "1px solid #636fe9",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "500",
                }}
              >
                <strong>Opening Balance:</strong> {openingBalance}
              </div>
            )}

            {/* Add more buttons as needed */}
          </div>
        ) : (
          <p>Please select a document type to view preset prompts.</p>
        )}
      </div>

      {/* <div style={{ position: "absolute", top: "270%", left: "0", right: "0", padding: "20px 50px" }}>
        <textarea
          style={{
            width: "100%",
            height: "200px",
            border: "1px solid #ccc",
            borderRadius: "8px",
            padding: "10px",
            fontFamily: "monospace",
            fontSize: "14px",
            backgroundColor: "#fff",
            resize: "vertical"
          }}
          placeholder="Formatted text box"
        />
      </div> */}

      {/* Footer Watermark */}
      <div
        style={{
          position: "fixed",
          bottom: "0",
          left: "0",
          right: "0",
          padding: "8px 30px",
          paddingBottom: "2px",
          backgroundColor: "#f8f9fa",
          borderTop: "1px solid #e0e0e0",
          textAlign: "center",
          fontSize: "12px",
          color: "#666",
          fontFamily: "Arial, sans-serif",
          width: "100%",
          boxSizing: "border-box",
          zIndex: "9999",
        }}
      >
        OCR Hunter v1.0 © 2025 AIBI Technologies. All rights reserved.
      </div>
    </div>
  );
}

export default App;
