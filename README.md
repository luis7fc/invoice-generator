# invoice-generator# 🧾 Invoice Generator for Client POs

This Streamlit app helps subcontractors like **I'll Klean It** generate professional invoices from **uploaded PDF purchase orders (POs)**. Designed for speed and accuracy, it supports both single and batch processing.

---

## 🚀 Features

- 📄 **Auto-extract PO data** from client PDFs
- ✏️ **Optional manual edits** (description, PO#, amount)
- 🔢 **Auto-generates invoice numbers** (`INV-1001`, `INV-1002`, ...)
- 🧷 **Appends original PO** to each invoice PDF
- 📦 **Batch mode**: Upload multiple POs and generate a **combined PDF**
- 📥 One-click download for **individual invoices** or a **master file**

---

## 📂 Folder Structure

```bash
invoice-generator/
├── invoice_generator.py      # Main Streamlit app
├── requirements.txt          # Dependency list
├── invoice_counter.txt       # (Optional) Tracks next invoice number
