import json, sys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from pprint import pprint 
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1, PDFObjRef


def load_form(filename):
    """Load pdf form contents into a nested list of name/value tuples"""
    with open(filename, 'rb') as file:
        parser = PDFParser(file)
        doc = PDFDocument(parser)
        return [load_fields(resolve1(f)) for f in
                   resolve1(doc.catalog['AcroForm'])['Fields']]


def load_fields(field):
    """Recursively load form fields"""
    form = field.get('Kids', None)
    if form:
        return [load_fields(resolve1(f)) for f in form]
    elif field.get('T'):
        pprint(field)
        try:
            # Some field types, like signatures, need extra resolving
            return (field.get('T').decode('utf-16'), resolve1(field.get('V')))
        except UnicodeDecodeError:
            return (field.get('T'), resolve1(field.get('V')))
    else:
        return None
def pdf_as_html(file_name):
    url = "http://127.0.0.1:8080/js/pdfjs/web/viewer.html?file=/forms/"+file_name
    print(url)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(url)
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.annotationLayer")))

    return driver


def main(forms_json = '../forms/forms.json'):
    print('Validating form PIDs')
    with open(forms_json) as f: 
        forms_data = json.load(f)

    for form_data in forms_data['Forms']:
        print(form_data["file_name"])
        form = pdf_as_html(form_data["file_name"])
        # form = load_form("../forms/"+form_data["file_name"])
        print(len(form.find_elements(By.CSS_SELECTOR, 'input')))
        # inputs = form.html.find('input')
        # pprint([(i.attrs.get("id"), i.attrs.get('data-name'), i.attrs.get('role')) for i in inputs])
        


if __name__ == '__main__':
    main()