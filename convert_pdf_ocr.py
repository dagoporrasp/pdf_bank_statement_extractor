import ocrmypdf
import pandas as pd
from pathlib import Path
import pdfplumber
import tempfile

# get pdf files
# file_list = [f for f in os.listdir(path=PATH) if f.endswith('.pdf') or f.endswith('.PDF')]

"""
main ocr code, which create new pdf file with OCR_ ahead its origin filename, 
and error messege can be find in error_log
"""
# error_log = {}
# for file in file_list:
#     try:
#         result = ocrmypdf.ocr(file, 'OCR_'+file,output_type='pdf',skip_text=True,deskew=True)
#     except Exception as e:
#         if hasattr(e,'message'):
#             error_log[file] = e.message
#         else:
#             error_log[file] = e
#         continue


# result = ocrmypdf.ocr(
#     pdf_file, "OCR_" + pdf_file.name, output_type="pdf", skip_text=True, deskew=True
# )
# with tempfile.TemporaryDirectory(dir="./temp") as temp_dir:
def ocr_pdf(pdf_file, out_dir):
    result = ocrmypdf.ocr(
        pdf_file,
        out_dir + "/OCR_" + pdf_file.name,
        output_type="pdf",
        skip_text=True,
        deskew=True,
    )
    return result


pdf_file = Path("data", "finca", "2022", "12- DICIEMBRE ALLPA GROUP SAS.pdf")
ocr_pdf(pdf_file, "temp")


# with pdfplumber.open(temp_dir + "/OCR_" + pdf_file.name) as pdf:
#     print(pdf.pages)
#     print(type(pdf.pages[0]))
#     print(dir(pdf.pages[0]))
#     txt = pdf.pages[0].extract_text().split("\n")
