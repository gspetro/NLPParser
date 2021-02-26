import os
import sys, traceback
import re
import abc
import pandas as pd
from os import listdir
from pathlib import Path
from docparser import DocParser
from certparser import ParseCert
from msdsparser import ParseMSDS
from fileconverter import FileConverter

# Ensures that the correct process is selected
def validation(char, message, function): 
    char = char[0].lower()
    while char[0] != 'y' and char[0] != 'n' and char[0] != 'q':
        char = input('ERROR. ' + message)[0].lower()
    return char

# Determines whether the files are MSDS or certs 
def type_validation(): 
    response = input('\nAre these MSDS files (m) or certifications (c)? (m/c): \n')
    while response[0].lower() != 'm' and response[0] != 'c':
        print('ERROR. ')
        response = input('\nAre these MSDS files (m) or certifications (c)? (m/c): \n')
    return response[0].lower()

# Converts .pdf or .docx files to .txt form
def convert():
    # y = yes, n = no, q = quit
    message = '\nDo you need to convert pdf or Word files to .txt form? (y/n/q): \n'
    response = input(message)
    response = validation(response, message, 'convert')
    if response == 'q':
        print('Goodbye!')
        sys.exit()
    elif response == 'y':
        filetype = type_validation()
        if filetype == 'm':
            conv_obj = FileConverter('msds')
        elif filetype == 'c':
            conv_obj = FileConverter('cert')
        print(conv_obj.folder_path)
        conv_obj.convert_files(conv_obj.folder_path, conv_obj.destination)
        print('Done converting files!')

# Takes in a .txt file and outputs a spreadsheet with the data from the file
def parse():
    # y = yes, n = no, q = quit
    message = '\nDo you need to parse .txt data into a spreadsheet? (y/n/q): \n'
    response = input(message)
    response = validation(response, message, 'parse')
    if response == 'q':
        print('Goodbye!')
        sys.exit()
    elif response == 'y':
        filetype = type_validation()
        if filetype == 'm':
            parse_obj = ParseMSDS()
        elif filetype == 'c':
            parse_obj = ParseCert()
        print('Processing...')
        # Create a dictionary/spreadsheet header with empy lists for data values
        #header = {'Unique_Key': [], 'Heading': [], 'Content': [], 'SRM_Title': [], 'Hyperlink' : []}
        # Convert to dataframe/table form
        data = pd.DataFrame(parse_obj.header, columns = ['Unique_Key', 'Heading', 'Content', 'SRM_Title', 'Hyperlink'])
        data = parse_obj.process_files(parse_obj.folder_path, data)
        print('Saving file...')
        parse_obj.create_files(data, parse_obj.destination)
        print('Done processing files!')

def main():
    convert()
    parse()
    print('Goodbye! \n')
    
if __name__ == "__main__":
    main()