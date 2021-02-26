import os
import sys, traceback
import re
import copy
import pandas as pd
from os import listdir
from pathlib import Path
# from filename import class
from docparser import DocParser

"""
    .. module:: NLPProgram
    :platform: any
    :synopsis: subclass for parsing SRM MSDS documents in .txt form

    .. moduleauthor:: Gillian Petro <gillian.s.petro@gmail.com>

"""
# ParseMSDS extends DocParser
class ParseMSDS(DocParser):

    # constructor
    # self == 'this' in Java but is also passed as an argument to the class's methods
    def __init__(self):
        super().__init__()

    # A method to get the name and number of the SRM
    # @param fileName - name of the file (NOT the full path)
    # @fileContents - a string containing the text of the file 
    # @return (key, number, name) - a tuple containing the Unique_Key (minus the line number), the SRM number, and the SRM name
    def getName(self, fileName, fileContents):
        if fileName.startswith("tika") or fileName.startswith("wdoc"):
            index = 4
        else: 
            index = 0
        eola = fileName.find("-")
        eolb = fileName.find(".")
        number = fileName[index : eola]
        key = fileName[index : eolb]
        if (fileContents.find("SRM Name:") != -1):
            index = fileContents.find("SRM Name:")
            eol = fileContents.find("\n", index + 9)
            name = fileContents[index + 9 : eol].strip()
        elif (fileContents.find("Name:") != -1):
            index = fileContents.find("Name:")
            eol = fileContents.find("\n", index + 5)
            name = fileContents[index + 5 : eol].strip()
        elif (fileContents.find("(SRM") != -1):
            index = fileContents.find("(SRM")
            index = fileContents.find(str(number), index)
            length = len(number) + 1
            eol = fileContents.find("\n", index + length)
            name = fileContents[index + length : eol].strip()
        else: 
            name = "NOT FOUND"
        return (key, number, name)
    
    # A method to handle exceptions when adding rows to the DataFrame
    # Appends a dummy row 
    # @param df - a dataframe with msds data up to this point
    # @param line_count
    # @return line_count + 1 - ensures that the line count remains accurate in the calling method
    def handleException(self, df, line_count):
        print('problem appending row')
        print(traceback.print_exc(file=sys.stdout) + '\n')
        # append dummy row
        df['Unique_Key'].append('problem_0')
        df['Heading'].append('problem_1')
        df['Content'].append('problem_2')
        df['SRM_Title'].append('problem_3')
        df['Details_Hyperlink'].append('problem_4')
        df['Hyperlink'].append('problem_5')
        return (line_count + 1)

    # A method to parse standard MSDS's with the required 15 headings
    # @param df - dataframe containing the parsed data up to this point
    # @param lines - a list where each entry is one line of the document
    # @param srm_dict - a dictionary with data on srm # and name
    # @param key - Unique_Key prefix
    # @DETAILS_HYPERLINK - link to the srmors.org page pertaining to the srm
    # @HYPERLINK - link to the pdf of the msds
    # @return df - dataframe with additions
    def standardParsing(self, df, lines, srm_dict, key, DETAILS_HYPERLINK, HYPERLINK):
        msds_sections_a = ['INTRODUCTION', 'SUBSTANCE AND SOURCE IDENTIFICATION', 'HAZARDS IDENTIFICATION', \
            'COMPOSITION AND INFORMATION ON HAZARDOUS INGREDIENTS', 'FIRST AID MEASURES', 'FIRE FIGHTING MEASURES', 'ACCIDENTAL RELEASE MEASURES', \
            'HANDLING AND STORAGE', 'EXPOSURE CONTROLS AND PERSONAL PROTECTION', 'PHYSICAL AND CHEMICAL PROPERTIES', 'STABILITY AND REACTIVITY', \
            'TOXICOLOGICAL INFORMATION', 'ECOLOGICAL INFORMATION', 'DISPOSAL CONSIDERATIONS', 'TRANSPORTATION INFORMATION', \
            'REGULATORY INFORMATION', 'OTHER INFORMATION']
        msds_sections_b = ['INTRODUCTION', 'SUBSTANCE AND SOURCE IDENTIFICATION', 'COMPOSITION AND INFORMATION ON HAZARDOUS INGREDIENTS', \
            'HAZARDS IDENTIFICATION', 'FIRST AID MEASURES', 'FIRE FIGHTING MEASURES', 'ACCIDENTAL RELEASE MEASURES', \
            'HANDLING AND STORAGE', 'EXPOSURE CONTROLS AND PERSONAL PROTECTION', 'PHYSICAL AND CHEMICAL PROPERTIES', 'STABILITY AND REACTIVITY', \
            'TOXICOLOGICAL INFORMATION', 'ECOLOGICAL INFORMATION', 'DISPOSAL CONSIDERATIONS', 'TRANSPORTATION INFORMATION', \
            'REGULATORY INFORMATION', 'OTHER INFORMATION']
        line_count = 1
        heading = msds_sections_a[0] # 'INTRODUCTION'
        next_section_idx = 1
        for line in lines:
            try: 
                new_row = dict() 
                # Check for empty string or spaces
                if (line.isspace() or not line): 
                    # Skip adding row but up line count
                    line_count += 1 
                elif (msds_sections_a[next_section_idx].lower() in line.lower()) and ((str(next_section_idx) + '.') in line.lower()): 
                    # if the line contains a standard headings, assign the new heading
                    heading = msds_sections_a[next_section_idx]
                    if (next_section_idx != 16): 
                        # if the line has one of the standard headings, increase next section index unless on last index
                        next_section_idx += 1
                    line_count += 1
                elif (msds_sections_b[next_section_idx].lower() in line.lower()) and ((str(next_section_idx) + '.') in line.lower()): 
                    # if the line contains a standard headings, assign the new heading
                    heading = msds_sections_b[next_section_idx]
                    if (next_section_idx != 16): 
                        # if the line has one of the standard headings, increase next section index unless on last index
                        next_section_idx += 1
                    line_count += 1
                elif(line.find('Date of Issue') != -1 or line.find('Issue Date') != -1):
                    data_start = line.find(':') + 1
                    data = line[data_start:]
                    df['Unique_Key'].append((key + '_' + str(line_count)))
                    df['Heading'].append('DATE')
                    df['Content'].append(data.strip())
                    df['SRM_Title'].append(srm_dict[key][0] + ': ' + srm_dict[key][1])
                    df['Details_Hyperlink'].append(DETAILS_HYPERLINK + srm_dict[key][0])
                    df['Hyperlink'].append(HYPERLINK + srm_dict[key][0])
                    line_count += 1
                else:
                    df['Unique_Key'].append((key + '_' + str(line_count)))
                    df['Heading'].append(heading)
                    df['Content'].append(line.strip())
                    df['SRM_Title'].append(srm_dict[key][0] + ': ' + srm_dict[key][1])
                    df['Details_Hyperlink'].append(DETAILS_HYPERLINK + srm_dict[key][0])
                    df['Hyperlink'].append(HYPERLINK + srm_dict[key][0])
                    line_count += 1
            except:
                line_count = self.handleException(df, line_count)
                continue
        return df

    # A method to parse non-standard MSDS's and exemption letters using regular expressions
    # @param df - dataframe containing the parsed data up to this point
    # @param lines - a list where each entry is one line of the document
    # @param srm_dict - a dictionary with data on srm # and name
    # @param key - Unique_Key prefix
    # @DETAILS_HYPERLINK - link to the srmors.org page pertaining to the srm
    # @HYPERLINK - link to the pdf of the msds
    # @return df - dataframe with additions
    def regexParsing(self, df, lines, srm_dict, key, DETAILS_HYPERLINK, HYPERLINK):
        #print('REGEX parsing\n')
        heading = 'INTRODUCTION'
        line_count = 1
        for line in lines:
            try: 
                # Check for empty string or spaces
                if (line.isspace() or not line): 
                    # Skip adding row but up line count
                    line_count += 1 
                elif (re.search(r'SECTION\s+[IVX]+', line)): 
                    # if the line contains a SECTION regex headings, assign the line as the new heading
                    heading = line
                    line_count += 1
                elif(line.find('Date of Issue') != -1):
                    data_start = line.find(':') + 1
                    data = line[data_start:]
                    df['Unique_Key'].append((key + '_' + str(line_count)))
                    df['Heading'].append('DATE')
                    df['Content'].append(data.strip())
                    df['SRM_Title'].append(srm_dict[key][0] + ': ' + srm_dict[key][1])
                    df['Details_Hyperlink'].append(DETAILS_HYPERLINK + srm_dict[key][0])
                    df['Hyperlink'].append(HYPERLINK + srm_dict[key][0])
                    line_count += 1
                else:
                    df['Unique_Key'].append((key + '_' + str(line_count)))
                    df['Heading'].append(heading)
                    df['Content'].append(line.strip())
                    df['SRM_Title'].append(srm_dict[key][0] + ': ' + srm_dict[key][1])
                    df['Details_Hyperlink'].append(DETAILS_HYPERLINK + srm_dict[key][0])
                    df['Hyperlink'].append(HYPERLINK + srm_dict[key][0])
                    line_count += 1
            except:
                line_count = self.handleException(df, line_count)
                continue
        return df

    # A method to parse non-standard MSDS's and exemption letters
    # @param df - dataframe containing the parsed data up to this point
    # @param lines - a list where each entry is one line of the document
    # @param srm_dict - a dictionary with data on srm # and name
    # @param key - Unique_Key prefix
    # @DETAILS_HYPERLINK - link to the srmors.org page pertaining to the srm
    # @HYPERLINK - link to the pdf of the msds
    # @return df - dataframe with additions
    def generalParsing(self, df, lines, srm_dict, key, fileContents, DETAILS_HYPERLINK, HYPERLINK):
        #print('GENERAL parsing\n')
        heading = 'GENERAL'
        sections = ['Exemption:', 'Description:', 'Disposal:', 'Transport Information:', 'Disclaimer:']
        if (sections[0] not in fileContents):
            next_section_idx = 1
        else: 
            next_section_idx = 0
        line_count = 1
        for line in lines:
            try: 
                new_row = dict()
                # Check for empty string or spaces
                if (line.isspace() or not line): 
                    # Skip adding row but up line count
                    line_count += 1 
                elif(line.find('DATE:') != -1):
                    data_start = line.find(':') + 1
                    data = line[data_start:]
                    df['Unique_Key'].append((key + '_' + str(line_count)))
                    df['Heading'].append('DATE')
                    df['Content'].append(data.strip())
                    df['SRM_Title'].append(srm_dict[key][0] + ': ' + srm_dict[key][1])
                    df['Details_Hyperlink'].append(DETAILS_HYPERLINK + srm_dict[key][0])
                    df['Hyperlink'].append(HYPERLINK + srm_dict[key][0])
                    line_count += 1
                elif (line.find(sections[next_section_idx]) != -1): 
                    # if the line contains a value from sections list, assign new heading & add rest of line as data
                    heading = line[:(len(sections[next_section_idx]) - 1)].upper()
                    if (next_section_idx != 4):
                        next_section_idx += 1
                    data_start = line.find(':') + 1
                    data = line[data_start:]
                    df['Unique_Key'].append((key + '_' + str(line_count)))
                    df['Heading'].append(heading)
                    df['Content'].append(data.strip())
                    df['SRM_Title'].append(srm_dict[key][0] + ': ' + srm_dict[key][1])
                    df['Details_Hyperlink'].append(DETAILS_HYPERLINK + srm_dict[key][0])
                    df['Hyperlink'].append(HYPERLINK + srm_dict[key][0])
                    line_count += 1
                else:
                    df['Unique_Key'].append((key + '_' + str(line_count)))
                    df['Heading'].append(heading)
                    df['Content'].append(line.strip())
                    df['SRM_Title'].append(srm_dict[key][0] + ': ' + srm_dict[key][1])
                    df['Details_Hyperlink'].append(DETAILS_HYPERLINK + srm_dict[key][0])
                    df['Hyperlink'].append(HYPERLINK + srm_dict[key][0])
                    line_count += 1
            except: 
                line_count = self.handleException(df, line_count)
                continue
        return df

    # A method to parse exemption letters
    # @param df - dataframe containing the parsed data up to this point
    # @param lines - a list where each entry is one line of the document
    # @param srm_dict - a dictionary with data on srm # and name
    # @param key - Unique_Key prefix
    # @DETAILS_HYPERLINK - link to the srmors.org page pertaining to the srm
    # @HYPERLINK - link to the pdf of the msds
    # @return df - dataframe with additions
    def exemptionParsing(self, df, lines, srm_dict, key, DETAILS_HYPERLINK, HYPERLINK):
        #print('EXEMPTION LETTER parsing\n')
        heading = 'INTRODUCTION'
        section_count = 0
        line_count = 1
        for line in lines:
            try: 
                new_row = dict()
                # Check for empty string or spaces
                if (line.isspace()) or not line: 
                    # Skip adding row but up line count
                    line_count += 1 
                #elif not line:
                    #continue
                elif (line[0].isdigit() and (int(line[0]) == (section_count + 1)) and (line[1].isspace() or line[2].isspace())): 
                    # if the line contains a standard headings, assign the new heading
                    ##if (int(line[0]) == (section_count + 1)):
                    section_count += 1
                    heading = 'SECTION ' + str(section_count)
                    data = line[1:].strip()
                    new_row = {'Unique_Key': (key + '_' + str(line_count)), 'Heading': heading, 'Content': data.strip(), \
                        'SRM_Title': srm_dict[key][0] + ': ' + srm_dict[key][1], 'Details_Hyperlink': DETAILS_HYPERLINK + srm_dict[key][0], \
                            'Hyperlink': HYPERLINK + srm_dict[key][0]}
                    df = df.append(new_row, ignore_index = True)
                    line_count += 1
                elif(line.find('DATE:') != -1):
                    data_start = line.find(':') + 1
                    data = line[data_start:]
                    df['Unique_Key'].append((key + '_' + str(line_count)))
                    df['Heading'].append('DATE')
                    df['Content'].append(data.strip())
                    df['SRM_Title'].append(srm_dict[key][0] + ': ' + srm_dict[key][1])
                    df['Details_Hyperlink'].append(DETAILS_HYPERLINK + srm_dict[key][0])
                    df['Hyperlink'].append(HYPERLINK + srm_dict[key][0])
                    line_count += 1
                else:
                    df['Unique_Key'].append((key + '_' + str(line_count)))
                    df['Heading'].append(heading)
                    df['Content'].append(line.strip())
                    df['SRM_Title'].append(srm_dict[key][0] + ': ' + srm_dict[key][1])
                    df['Details_Hyperlink'].append(DETAILS_HYPERLINK + srm_dict[key][0])
                    df['Hyperlink'].append(HYPERLINK + srm_dict[key][0])
                    line_count += 1
            except:
                line_count = self.handleException(df, line_count)
                continue
        return df

    # A method to parse MSDS's and exemption letters when other methods are not applicable
    # @param df - dataframe containing the parsed data up to this point
    # @param lines - a list where each entry is one line of the document
    # @param srm_dict - a dictionary with data on srm # and name
    # @param key - Unique_Key prefix
    # @DETAILS_HYPERLINK - link to the srmors.org page pertaining to the srm
    # @HYPERLINK - link to the pdf of the msds
    # @return df - dataframe with additions
    def miscParsing(self, df, lines, srm_dict, key, DETAILS_HYPERLINK, HYPERLINK):
        #print('MISCELLANEOUS parsing\n')
        heading = 'MISCELLANEOUS'
        line_count = 1
        for line in lines:
            try: 
                # Check for empty string or spaces
                if (line.isspace() or not line): 
                    # Skip adding row but up line count
                    line_count += 1 
                elif(line.find('DATE:') != -1):
                    data_start = line.find(':') + 1
                    data = line[data_start:]
                    df['Unique_Key'].append((key + '_' + str(line_count)))
                    df['Heading'].append('DATE')
                    df['Content'].append(data.strip())
                    df['SRM_Title'].append(srm_dict[key][0] + ': ' + srm_dict[key][1])
                    df['Details_Hyperlink'].append(DETAILS_HYPERLINK + srm_dict[key][0])
                    df['Hyperlink'].append(HYPERLINK + srm_dict[key][0])
                    line_count += 1
                else:
                    df['Unique_Key'].append((key + '_' + str(line_count)))
                    df['Heading'].append(heading)
                    df['Content'].append(line.strip())
                    df['SRM_Title'].append(srm_dict[key][0] + ': ' + srm_dict[key][1])
                    df['Details_Hyperlink'].append(DETAILS_HYPERLINK + srm_dict[key][0])
                    df['Hyperlink'].append(HYPERLINK + srm_dict[key][0])
                    line_count += 1
            except:
                line_count = self.handleException(df, line_count)
                continue
        return df

    # A method to determine which type of parsing to use
    # @param df - dataframe containing the parsed data up to this point
    # @param srm_dict - a dictionary with data on srm # and name
    # @param key - Unique_Key prefix
    # @param fileContents - a string containing all text in the document
    # @return df - dataframe with additions
    def get_subject_data_linenum(self, header, srm_dict, key, fileContents):
        df = copy.deepcopy(header)
        try: 
            DETAILS_HYPERLINK = 'https://www-s.nist.gov/srmors/view_detail.cfm?srm='
            HYPERLINK = 'https://www-s.nist.gov/srmors/view_msds.cfm?srm='
            lines = fileContents.splitlines() # list containing one file line per index
            if (fileContents.lower().find("SUBSTANCE AND SOURCE IDENTIFICATION".lower()) != -1):
                df = self.standardParsing(df, lines, srm_dict, key, DETAILS_HYPERLINK, HYPERLINK)
            # Regex Docs: https://docs.python.org/3/howto/regex.html
            elif (re.search(r'SECTION\s+[IVX]+', fileContents)): 
                df = self.regexParsing(df, lines, srm_dict, key, DETAILS_HYPERLINK, HYPERLINK)
            elif('Description:' in fileContents and 'Disposal:' in fileContents and 'Transport Information:' in fileContents):
                df = self.generalParsing(df, lines, srm_dict, key, fileContents, DETAILS_HYPERLINK, HYPERLINK)
            elif('ExemptionLetter' in fileContents):
                df = self.exemptionParsing(df, lines, srm_dict, key, DETAILS_HYPERLINK, HYPERLINK)
            else:
                df = self.miscParsing(df, lines, srm_dict, key, DETAILS_HYPERLINK, HYPERLINK)
        except: 
            #print('YEKSEPTIONAL!!!')
            df['Unique_Key'].append('problem_0')
            df['Heading'].append('problem_1')
            df['Content'].append('problem_2')
            df['SRM_Title'].append('problem_3')
            df['Details_Hyperlink'].append('problem_4')
            df['Hyperlink'].append('problem_5')
            print(traceback.print_exc(file=sys.stdout) + '\n')
        return df

    # A method that loops through all the MSDS .txt files in a directory and parses them 
    # @param df - dataframe containing the parsed data up to this point
    # @param file_folder - the folder containing all the .txt files to parse
    # @return results - dataframe with Abstract merged in
    def process_files(self, file_folder, df):
        SRMdict = dict()
        data = list()
        try:
            for item in listdir(file_folder):
                if item.endswith(".txt"):
                    path_name = file_folder + item
                    with open(path_name, "r", encoding="utf-8") as fh:
                        try: 
                            # Read in file contents
                            contents = fh.read()
                            # Assign Unique_Key prefix, SRM number, and name
                            key, number, name = self.getName(item, contents)
                            SRMdict[key] = [number, name]
                            print("SRM " + number)
                            new_data = pd.DataFrame(self.get_subject_data_linenum(self.header, SRMdict, key, contents))
                            results = self.getAbstract(contents, item, new_data)
                            data.append(results)
                        except: 
                            print(traceback.print_exc(file = sys.stdout))
                            print(number, " - PROBLEM PROCESSING FILE\n")
                            SRMdict[key] = [number, "PROBLEM PROCESSING FILE"]
                            continue
            final = pd.concat(data, ignore_index = True)
            return final
        except NotADirectoryError:
            print('ERROR. You did not enter a file FOLDER/directory. ')
            super().set_folder()
            print('Thank you! ')
