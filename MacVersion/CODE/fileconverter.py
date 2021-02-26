import docx2txt
import tika
import os
from os import listdir
from os.path import isfile, join, splitext
from tika import parser
from pathlib import Path
import ocrmypdf
import PIL
import sys, traceback
import re
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from io import StringIO

"""
    .. module:: NLPProgram
    :platform: any
    :synopsis: abstract superclass for converting .pdf and .docx document to .txt form

    .. moduleauthor:: Gillian Petro <gillian.s.petro@gmail.com>

    The FileConverter class contains implementations of methods common to both msds and certification file conversion

"""

class FileConverter:
    def __init__(self, ftype):
        self.folder_path = self.get_folder('Please enter the full path of the FOLDER where the data files are located: \n')
        self.destination = self.get_folder('Please enter the full path of the FOLDER where the text files should be SAVED: \n')
        self.ftype = ftype
    
    def get_folder(self, message):
        try: 
            #folder_path = "/Users/gillianpetro/Desktop/CodeProjects/NLPParser/Mac/"
            folder_path = input(message) + '/'
            while (not os.path.isdir(folder_path)):
                print('ERROR. You did not enter a file FOLDER/directory. ')
                folder_path = input(message) + '/'
            return folder_path
        except: 
            print('ERROR: ', traceback.print_exc(file=sys.stdout))
            sys.exit()

    def convert_doc2txt(self, doc_folder, file, srm_num, destination):
        try:
            #index = file.find("_")
            # filename without .docx or full path
            name = srm_num + '-' + self.ftype
            # full path name
            filename = doc_folder + file 
            text = docx2txt.process(filename)
            new_file = destination + name + '.txt'
            print(str(name) + '.txt', '\n')
            with open(new_file, 'w', encoding='utf-8-sig') as fh:
                fh.write(text)
        except: 
            print('problem with doc conversion')
            print('File: ', file)
            print(traceback.print_exc(file=sys.stdout))

    def try_various_pdf_programs(self, pdf_folder, file, srm_num, destination):
        try: 
            #index = file.find(".pdf")
            name = srm_num + '-' + self.ftype
            onlyfile = join(pdf_folder,file)
            output_string = StringIO()
            with open(onlyfile, 'rb') as in_file:
                parser = PDFParser(in_file)
                doc = PDFDocument(parser)
                rsrcmgr = PDFResourceManager()
                device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                for page in PDFPage.create_pages(doc):
                    interpreter.process_page(page)
                outfile = (destination + name + '.txt')
                print(name + '.txt', '\n')
                with open(outfile, 'w', encoding='utf-8-sig') as output:
                    output.write(output_string.getvalue())
                with open(outfile, 'r', encoding='utf-8-sig') as check:
                    text = check.read()
                    if re.search(r'(cid:[0-9]+)', text):
                        raise Exception('File contains cid values')
        except: 
            # Any file for which an exception occurs should be checked manually to determine whether data was lost in tika conversion
            print(file + ': converting file using tika')
            os.remove(outfile)
            # get full pathname to PDF
            onlyfile = join(pdf_folder,file)
            # use tika Parser for parsing PDF
            parsedPDF = tika.parser.from_file(onlyfile)
            # get only the content from the PDF file
            fulltext = parsedPDF['content']
            try: 
                # filename for tika processed files
                outfile = (destination + name + '.txt')
                with open(outfile, 'w', encoding='utf-8') as output:
                    #write PDF text to .txt file
                    output.write(fulltext.lstrip())
            except Exception:
                print('problem with conversion to .txt\nConvert file manually.')
                print('File: ', file)
                print(traceback.print_exc(file=sys.stdout))

    def convert_files(self, folder, destination):
        # loop over files in the folder
        for file in listdir(folder):
            # False means no match with a .docx file of the same srm num
            flag = False
            # (file.find('-')) gives ending index
            if file.find('_') != -1:
                srm_num = file[:(file.find('_'))]
            elif file.find('-') != -1:
                srm_num = file[:(file.find('-'))]
            else:
                srm_num = file[:(file.find('.'))]
            try:
                if file.endswith('.docx'): 
                    self.convert_doc2txt(folder, file, srm_num, destination)
                elif file.endswith('.pdf'):
                    for item in listdir(folder):
                        if item.startswith(srm_num) and item.endswith('.docx'): 
                            # There is a .docx file; don't process the pdf
                            flag = True 

                    # no match; process pdf
                    if flag == False: 
                        self.try_various_pdf_programs(folder, file, srm_num, destination)
            except:
                print('File: ', file)
                traceback.print_exc(file=sys.stdout)