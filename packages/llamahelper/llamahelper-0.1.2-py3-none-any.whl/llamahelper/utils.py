from utils_tool import *

import yaml
import PyPDF2

def get_data_from_md(text):
    """_summary_

    Args:
        text (_type_): _description_

    Returns:
        _type_: _description_
    """
    _,infos,content = text.split("---",2)
    data = yaml.safe_load(infos)
    return data, content

def extract_text_from_pdf(file_path):
    """
    Extracts the full text from a single PDF file.
    Args:
        file_path (str): The absolute path to the PDF file.
    Returns:
        str: The extracted text from the PDF, or an empty string if extraction fails.
    """
    full_text = ""
    try:
        with open(file_path, 'rb') as file_object:
            pdf_reader = PyPDF2.PdfReader(file_object)
            num_pages = len(pdf_reader.pages)
            for page_num in range(num_pages):
                page_obj = pdf_reader.pages[page_num]
                page_text = page_obj.extract_text()
                if page_text:
                    full_text += page_text + "\n" # Add a newline between pages
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        # You might want to log this error or handle it differently
        return "" # Return empty string on failure
    return full_text.strip() # Remove leading/trailing whitespace

