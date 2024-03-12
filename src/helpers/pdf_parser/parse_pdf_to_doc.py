import os
import pdf2docx

pabulib_dir = os.path.join(os.getcwd(), "src", "pabulib")

path_to_pdf_files = os.path.join(
    pabulib_dir, "data", "Czestochowa", "edycja_6_2020")
pdf_name = "Ogólnomiejskie2020.pdf"
output_doc_name = "sample.docx"

path_to_pdf = os.path.join(path_to_pdf_files, pdf_name).replace("\\", "/")
path_to_sample_doc = os.path.join(
    path_to_pdf_files, output_doc_name).replace("\\", "/")
pdf2docx.parse(path_to_pdf, path_to_sample_doc)
