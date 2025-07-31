import streamlit as st
import PyPDF2
from reportlab.pdfgen import canvas
import io
from datetime import datetime
import os

# Configuration: Hardcoded coordinates for three text entries
TEXT_CONFIG = [
    {'label': "Igra", "placeholder": "HNK Hajduk - PFC Zire", "x": 373.5, "y": 593},
    {'label': "Datum", "placeholder": "31.07.2025.", "x": 396, "y": 616.5},
    {'label': "Plate", "placeholder": "ŠI  988 JK .", "x": 113, "y": 616.5}
]

# Streamlit app title
st.title("PDF Generator")

def add_text_at_coordinates(pdf_path, text_configs):
    """Add multiple text entries to the first page of the PDF at specified coordinates."""
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        pdf_writer = PyPDF2.PdfWriter()

        # Create a temporary PDF with the text, using page size 8.26 x 11.69 inches
        text_buffer = io.BytesIO()
        c = canvas.Canvas(text_buffer, pagesize=(594.72, 840.88))  # 8.26 * 72, 11.69 * 72
        c.setFont("Helvetica-Bold", 20)
        c.setFillColorRGB(0, 0, 0)  # Black text

        # Add each text entry at its specified coordinates
        for config in text_configs:
            text = config["text"]
            x = config["x"]
            y = config["y"]
            # Calculate text width to center it
            text_width = c.stringWidth(text, "Helvetica-Bold", 12)
            centered_x = x - (text_width / 2)
            c.drawString(centered_x, y, text)

        c.save()
        text_buffer.seek(0)
        text_pdf = PyPDF2.PdfReader(text_buffer)

        # Merge text with the first page
        first_page = pdf_reader.pages[0]
        first_page.merge_page(text_pdf.pages[0])
        pdf_writer.add_page(first_page)

        # Add remaining pages as-is
        for page in pdf_reader.pages[1:]:
            pdf_writer.add_page(page)

        output = io.BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        return output

# Path to the static PDF
pdf_path = "main-blank.pdf"

# Check if the PDF exists
if not os.path.exists(pdf_path):
    st.error("main-blank.pdf not found in the app directory. Please ensure it’s included in the repository.")
else:
    # Get text values for each entry
    # st.subheader("Enter Text Values")
    all_text_entered = True
    for config in TEXT_CONFIG:
        placeholder = config["placeholder"]
        label = config['label']
        config["text"] = st.text_input(f"Stavi text za red {label}", placeholder, key=label)
        if not config["text"]:
            all_text_entered = False

    if all_text_entered and st.button("Napravi PDF"):
        modified_pdf = add_text_at_coordinates(pdf_path, TEXT_CONFIG)
        # Generate filename from the third text input (plate)
        plate_text = TEXT_CONFIG[2]["text"]
        plate_parts = plate_text.split()
        prefix = " ".join(plate_parts[:3])
        filename = f"PARKING_PROPUSNICE_CROATEL-{prefix}.pdf"
        st.success("Napravljeno PDF!")
        st.download_button(
            label="Preuzmi PDF",
            data=modified_pdf,
            file_name=filename,
            mime="application/pdf"
        )