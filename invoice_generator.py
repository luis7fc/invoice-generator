import streamlit as st
import fitz  # PyMuPDF
import re
from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import os

# ─── Helper to Extract PO Info ─────────────────────────────────────────────
def extract_po_details(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "\n".join([page.get_text() for page in doc])

    details = {
        "po_number": re.search(r"Purchase Order[^\n:]*[:\s]*([A-Z0-9\-]+)", text, re.IGNORECASE),
        "job_info": re.search(r"Project:\s*(.*?)\nLot:\s*(.*?)\n", text),
        "description": re.search(r"Craft:\s*4440\s*-\s*(.*?)\n", text),
        "amount": re.search(r"Total:\s*\$?([0-9,.]+)", text),
        "customer": re.search(r"Granville Homes Inc\.", text),
    }

    result = {}
    if details["po_number"]:
        result["po_number"] = details["po_number"].group(1)
    if details["job_info"]:
        result["job"] = details["job_info"].group(1).strip()
        result["lot"] = details["job_info"].group(2).strip()
    if details["description"]:
        result["description"] = details["description"].group(1).strip()
    if details["amount"]:
        result["amount"] = details["amount"].group(1).strip()
    if details["customer"]:
        result["customer"] = "Granville Homes"

    return result, doc

# ─── Invoice Number Generator ──────────────────────────────────────────────
def get_next_invoice_number():
    counter_file = "invoice_counter.txt"
    if not os.path.exists(counter_file):
        with open(counter_file, "w") as f:
            f.write("1001")
    with open(counter_file, "r+") as f:
        current = int(f.read().strip())
        next_number = current + 1
        f.seek(0)
        f.write(str(next_number))
        f.truncate()
    return f"INV-{current}"

# ─── PDF Invoice Generator ─────────────────────────────────────────────────
def generate_invoice(data, original_po, invoice_number):
    invoice_pdf = FPDF()
    invoice_pdf.add_page()
    invoice_pdf.set_font("Arial", size=12)

    invoice_pdf.cell(200, 10, txt="INVOICE", ln=1, align="C")
    invoice_pdf.cell(100, 10, txt=f"Invoice #: {invoice_number}", ln=1)
    invoice_pdf.cell(100, 10, txt=f"Invoice Date: {datetime.today().strftime('%m/%d/%Y')}", ln=1)
    invoice_pdf.cell(100, 10, txt="Terms: NET30", ln=1)

    invoice_pdf.cell(100, 10, txt="\nVendor: I'll Klean It", ln=1)
    invoice_pdf.cell(100, 10, txt=f"PO#: {data.get('po_number', 'N/A')}", ln=1)
    invoice_pdf.cell(100, 10, txt=f"Description: {data.get('description', 'Interior Cleaning')}", ln=1)
    invoice_pdf.cell(100, 10, txt=f"Amount: ${data.get('amount', '0.00')}", ln=1)

    invoice_pdf.ln(10)
    invoice_pdf.cell(200, 10, txt="THANK YOU FOR YOUR BUSINESS!", ln=1, align="C")

    output_str = invoice_pdf.output(dest='S').encode('latin1')
    buffer = BytesIO(output_str)

    # Append original PO pages
    result_pdf = fitz.open()
    result_pdf.insert_pdf(fitz.open(stream=buffer.getvalue(), filetype="pdf"))
    result_pdf.insert_pdf(original_po)

    final_buffer = BytesIO()
    result_pdf.save(final_buffer)
    return final_buffer

# ─── Streamlit UI ──────────────────────────────────────────────────────────
st.title("📄 Invoice Generator Prototype")

uploaded_files = st.file_uploader("Upload Client PO(s) (PDF)", type="pdf", accept_multiple_files=True)
combined_invoice = fitz.open()

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            extracted, original_po = extract_po_details(uploaded_file)

        st.subheader(f"Extracted Info from {uploaded_file.name}")
        st.json(extracted)

        st.subheader("Manual Edits (Optional)")
        po_number = st.text_input(f"PO Number for {uploaded_file.name}", value=extracted.get("po_number", ""), key=f"po_{uploaded_file.name}")
        description = st.text_input(f"Description for {uploaded_file.name}", value=extracted.get("description", ""), key=f"desc_{uploaded_file.name}")
        amount = st.text_input(f"Amount ($) for {uploaded_file.name}", value=extracted.get("amount", ""), key=f"amt_{uploaded_file.name}")

        if st.button(f"Generate Invoice for {uploaded_file.name}"):
            manual_data = {
                "po_number": po_number,
                "description": description,
                "amount": amount
            }
            invoice_number = get_next_invoice_number()
            invoice_pdf = generate_invoice(manual_data, original_po, invoice_number)
            st.download_button("Download Invoice PDF", data=invoice_pdf, file_name=f"{invoice_number}.pdf")

        # Always add to combined output
        manual_data = {
            "po_number": po_number,
            "description": description,
            "amount": amount
        }
        invoice_number = get_next_invoice_number()
        pdf = generate_invoice(manual_data, original_po, invoice_number)
        combined_invoice.insert_pdf(fitz.open(stream=pdf.getvalue(), filetype="pdf"))

    final_batch = BytesIO()
    combined_invoice.save(final_batch)
    st.download_button("Download Combined Invoice Batch PDF", data=final_batch, file_name="Combined_Invoices.pdf")
