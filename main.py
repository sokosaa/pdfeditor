import streamlit as st
import PyPDF2
from reportlab.pdfgen import canvas
import io
from datetime import datetime
import os

# Configuration: Hardcoded coordinates for three text entries
TEXT_CONFIG = [
    {'label': "Igra", "placeholder": "HNK Hajduk - PFC Zire", "x": 410, "y": 593},
    {'label': "Igra Drugi Red", "placeholder": "", "x": 410, "y": 569.5},
    {'label': "Datum", "placeholder": "31.07.2025.", "x": 410, "y": 616.5},
    {'label': "Plate", "placeholder": "ŠI  988 JK .", "x": 125, "y": 616.5}
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
            text_width = c.stringWidth(text, "Helvetica-Bold", 20)
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

# Radio button to select PDF file
pdf_options = ["propusnica.pdf", "b2.pdf", "c.pdf"]
selected_pdf = st.radio("Odaberi PDF predložak:", pdf_options, index=0)
pdf_path = selected_pdf

# Check if the selected PDF exists
if not os.path.exists(pdf_path):
    st.error(f"{pdf_path} not found in the app directory. Please ensure it’s included in the repository.")
else:
    # Get text values for each entry
    all_text_entered = True
    for config in TEXT_CONFIG:
        placeholder = config["placeholder"]
        label = config['label']
        config["text"] = st.text_input(f"Stavi text za red {label}", placeholder, key=label)
        if not config["text"] and label != "Igra Drugi Red":
            all_text_entered = False

    if all_text_entered and st.button("Napravi PDF"):
        modified_pdf = add_text_at_coordinates(pdf_path, TEXT_CONFIG)
        # Generate filename including PDF type, game, date, and license plate
        if selected_pdf == "propusnica.pdf":
            pdf_type = "PROP"
        elif selected_pdf == "b2.pdf":
            pdf_type = "B2"
        else:  # c.pdf
            pdf_type = "PROP"  # Using same values as propusnica
        game_text = TEXT_CONFIG[0]["text"].replace(" ", "_")
        date_text = TEXT_CONFIG[2]["text"].replace(".", "_")
        plate_text = TEXT_CONFIG[3]["text"].replace(" ", "_")
        filename = f"PARKING_{pdf_type}_{game_text}_{date_text}_{plate_text}.pdf"
        st.success("Napravljeno PDF!")
        st.download_button(
            label="Preuzmi PDF",
            data=modified_pdf,
            file_name=filename,
            mime="application/pdf"
        )