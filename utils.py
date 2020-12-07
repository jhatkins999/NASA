from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfdevice import PDFDevice

from io import StringIO
import glob
from tqdm import tqdm

import os
# Contains some random functions imported from Irina's code. It is not currently relevant

def convert_pdf2txt(input_path : str, output_path : str) -> None:
    for file in tqdm(glob.glob(input_path+'*.pdf'), ascii=True,desc='pdf->txt'):
      try:
        fp = open(file, 'rb')
        parser = PDFParser(fp)
        document = PDFDocument(parser)
        if not document.is_extractable:
          raise PDFTextExtractionNotAllowed

        rsrcmgr = PDFResourceManager()
        device = PDFDevice(rsrcmgr)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        retstr = StringIO()


        # Process each page contained in the document.
        for page in PDFPage.create_pages(document):
          interpreter.process_page(page)
          result = device.get_result()
        data = retstr.getvalue()
        print("RESULT:", result)
        print("DATA:",data)
        txt_file = output_path + file.split("/")[-1] + '.txt'
        if txt_file not in os.listdir(output_path):
          txt_out = open(txt_file, "w")
          txt_out.write(data)
      except Exception as e:
        print(e)
        print("Text document could not be created from %s" %(file))