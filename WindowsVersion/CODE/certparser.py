import re
import csv
import pandas as pd
import os, sys, traceback
import copy
import datetime
from os import listdir
# from filename import class
from docparser import DocParser

"""
    .. module:: NLPProgram
    :platform: any
    :synopsis: abstract subclass for parsing SRM certification documents in .txt form

    .. moduleauthor:: Gillian Petro <gillian.s.petro@gmail.com>

"""
# ParseCert extends DocParser
class ParseCert(DocParser):
    # constructor 
    # self == 'this' in Java but is also passed as an argument to the class's methods
    def __init__(self):
        super().__init__()

    # A method to extract content line by line from the file and create a spreadsheet with heading, content, SRM name/number, and link to srmors
    # @param text - text of the file in string form
    # @param table - table containing processed data from preceding files
    # @param file_name - name of the file
    # @param title - SRM name & number
    # @return table
    def process_text(self, text, header, file_name, title):
        table = copy.deepcopy(header)
        DETAILS_HYPERLINK = 'https://www-s.nist.gov/srmors/view_detail.cfm?srm='
        HYPERLINK = 'https://www-s.nist.gov/srmors/view_cert.cfm?srm='
        line_count = 1
        current_heading = 'INTRODUCTION'
        name = file_name[:file_name.find('-')]
        for line in text:
            if not line or line.isspace():
                line_count += 1
            # Gets headings that are all caps --> specifically headings with at least 8 capital letters within the first 15 characters
            # This allows for spaces in the first 15 characters but prevents NIST or SRM from registering as headings
            elif re.search('[A-Z]{8,}', line[:15]):
                current_heading = line
                line_count += 1
            # Finds the "Reference" heading, where citations begin
            elif line.find('REFERENCE') != -1:
                # Set heading as references
                current_heading = 'REFERENCES'
                line_count += 1
            else:
                try:
                    # If the heading is 'REFERENCES,' break out of loop. File processing ends for this file. 
                    if (current_heading.find('REFERENCES') != -1):
                        break
                    # If the line contains a colon follow by some whitespace and then WORDS, include the words in 'Content'
                    #elif re.search(r':\s+\S+', line):
                    # If the line contains at least one capital letter and a colon, include words in 'content'
                    elif re.search(r'[A-Z][a-z]+.+:', line):
                        # exclude PHONE, FAX, and NOTE as headings
                        if 'phone:' not in line.lower() and 'fax:' not in line.lower() and 'note.*:' not in line.lower() \
                            and 'issue\s+date' not in line.lower() and 'were:' not in line.lower() and 'serial\s+no:' not in line.lower():
                            index = line.find(': ')
                            if index != -1 and index < 70:
                                current_heading = line[:index].strip()
                                line = line[(index + 1):]
                    #key = name + '_cert_' + str(line_count)
                    table['Unique_Key'].append(name + '-cert_' + str(line_count))
                    table['Heading'].append(current_heading)
                    table['Content'].append(line.strip())
                    table['SRM_Title'].append(title)
                    table['Details_Hyperlink'].append(DETAILS_HYPERLINK + name)
                    table['Hyperlink'].append(HYPERLINK + name)
                    line_count += 1

                except:
                    traceback.print_exc(file=sys.stdout)
        return table
    
    # A method to get the name of the SRM
    def getName(self, fileName, fileContents):
        if fileName.find("(") != -1:
            index = fileName.find("(")
        else:
            index = fileName.find("-")
        number = fileName[: index].lower()
        fileContents = fileContents.splitlines()
        name = 'NOT FOUND'
        # Use single flag to locate SRM name when data is contained in one line
        found = False
        # Use double flag to locate SRM name when data is split over multiple lines
        srmFound = False
        numFound = False
        
        for line in fileContents:
            if found == True and not line.isspace() and line:
                name = line.strip()
                break
            elif numFound == True and not line.isspace() and line:
                name = line.strip()
                break
            # If any of the following patterns are matched AND SRM # is in the line, we have found the location of the name
            elif ((re.search(r'standard\s+reference\s+', line.lower())) or (re.search(r'standard\s+sample', line.lower())) or (re.search(r'reference\s+material', line.lower())) or (re.search(r'standard\s+.*.*material', line.lower())) or (re.search(r'research\s+material', line.lower()))) and (line.lower().find(number.lower()) != -1):
                found = True
            # If 'Standard Reference' (or similar) AND number have been found, we have found the location of the name
            elif srmFound == True and (line.lower().find(number.lower()) != -1):
                numFound = True
            # If any of the following patterns are matched, set srmFound to True and look for SRM #
            elif ((re.search(r'standard\s+reference\s+', line.lower())) or (re.search(r'standard\s+sample', line.lower())) or (re.search(r'reference\s+material', line.lower())) or (re.search(r'standard\s+.*.*material', line.lower())) or (re.search(r'research\s+material', line.lower()))):
                srmFound = True
        # If none of the conditions above are met, attempt one more search: 
        if found == False and numFound == False: 
            for line in fileContents:
                if found == True and not line.isspace() and line:
                    name = line.strip()
                    break
                elif (re.search(r'certificate', line.lower())):
                    found = True
        return str(number) + '_' + name

    def process_files(self, folder, df):
        data = list()
        for file in listdir(self.folder_path):
            print(file)
            if (file.endswith('.txt')):
                with open(folder + file, 'r', encoding='utf-8') as f:
                    # Read in text from file in string form
                    text = f.read()
                    # Get SRM number & name
                    srm_title = self.getName(file, text)
                    text = text.splitlines()
                    # Create dataframe for SRM in file
                    new_data = pd.DataFrame(self.process_text(text, self.header, file, srm_title))
                    # Get/add abstract for SRM 
                    results = self.getAbstract(text, file, new_data)
                    # Create a list of dataframes to concatenate later
                    data.append(results)
        final = pd.concat(data, ignore_index = True)
        return final
    