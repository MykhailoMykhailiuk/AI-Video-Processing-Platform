import unicodedata

from docx import Document
from fpdf import FPDF

def generate_doc_file(text, output_type, upload_id):
    doc = Document()
    doc.add_paragraph(text)
    file_path = f'{output_type}_{upload_id}.docx'
    doc.save(file_path)
    return file_path


def generate_pdf_file(text, output_type, upload_id):
    
    cleaned_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

    pdf = FPDF(format='A4', unit='mm')
    pdf.add_page()
    pdf.set_font('Arial', size=11)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.multi_cell(0, 5, cleaned_text)
    file_path = f'{output_type}_{upload_id}.pdf'
    pdf.output(file_path)
    return file_path

def generate_txt_file(text, output_type, upload_id):
    file_path = f'{output_type}_{upload_id}.txt'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    return file_path

extentions = {
    '.txt': generate_txt_file,
    '.pdf': generate_pdf_file,
    '.docx': generate_doc_file
}

def document_generation(text, output_type, upload_id, file_type):
    if file_type in extentions:
        return extentions[file_type](text, output_type, upload_id)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")