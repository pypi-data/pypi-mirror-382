import fitz  # PyMuPDF

# Takes units in PT (Therefore must be converted correctly)
def overlay_pdfs(base_pdf_path, pdf_data, output_pdf_path):
    base_pdf = fitz.open(base_pdf_path)

    for pdf_info in pdf_data:
        page_num = pdf_info['page']-1
        overlay_pdf = fitz.open(pdf_info['pdf_path'])
        base_page = base_pdf[page_num]

        x = (pdf_info['x']) # X coordinate of the bottom-left corner of the overlay
        y = (pdf_info['y']) # Y coordinate of the bottom-left corner of the overlay
        width = (pdf_info['width'])  # Width of the overlay
        height = (pdf_info['height'])  # Height of the overlay

        # Define the position rectangle for the overlay
        position = fitz.Rect(x, y, x + width, y + height)

        # Draw a rectangle for visual debugging
        # red_color = (1, 0, 0)
        # base_page.draw_rect(position, color=red_color, width=1.5, fill=None)

        # Place the overlay PDF
        base_page.show_pdf_page(position, overlay_pdf, 0)
        overlay_pdf.close()

    base_pdf.save(output_pdf_path)
    print(f"Overlay PDF saved: {output_pdf_path}")