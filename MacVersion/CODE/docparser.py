import os
import sys, traceback
import re
import abc
import pandas as pd
from os import listdir
from pathlib import Path

"""
    .. module:: NLPProgram
    :platform: any
    :synopsis: superclass for parsing .txt documents

    .. moduleauthor:: Gillian Petro <gillian.s.petro@gmail.com>

    The DocParser class contains implementations of methods common to both msds and certification parsing. 
    It is not functional on its own (similar to an abstract class). 

"""
class DocParser:
    # constructor 
    # self == 'this' in Java but is also passed as an argument to the class's methods
    def __init__(self):
        self.get_locations()
        self.header = {'Unique_Key': [], 'Heading': [], 'Content': [], 'SRM_Title': [], 'Details_Hyperlink' : [], 'Hyperlink' : []}
    
    # This method allows the user to indicate where the data is coming from and where to save the output
    # try/except is like try/catch in Java
    def get_locations(self):
        self.set_folder()
        self.set_destination()
    
    # Setter method for folder_path field
    def set_folder(self):
        try: 
            self.folder_path = input('Please enter the full path of the FOLDER where the data files are located: \n') + '/'
            while (not os.path.isdir(self.folder_path)):
                print('ERROR. You did not enter a file FOLDER/directory. ')
                self.folder_path = input('Please reenter the full path of the FOLDER where the data files are located: \n') + '/'
        except: 
            #prints stacktrace
            print('ERROR: ', traceback.print_exc(file=sys.stdout))
            sys.exit()
    
    # Setter method for destination field
    def set_destination(self):
        self.destination = input('Please indicate the full path of the CSV FILE where the data should be saved: \n')
        while (not self.destination.endswith('.csv')):
            self.destination = input('ERROR. The full path must end with ".csv" \n')
    
    # This method gets the paragraph (abstract) corresponding to each heading in the original document 
    # @param text - document text in string form 
    # @param file - file name
    # @param df - DataFrame (table) containing information on Unique_Key, Heading, line-by-line content, SRM name/number, and srm order link
    # @return result - the full data table including abstracts
    def getAbstract(self, text, file, df): 
        abstract_data = {'Unique_Key': [], 'Heading_Key': [], 'Abstract': []}
        srm = file[:file.find('-')]

        # Add content under a given heading to list of abstracts
        abstracts = dict()
        for num in range(len(df['Unique_Key'])):
            # Get current row
            current = df.iloc[int(num)]
            heading = current['Heading']
            key = current['Unique_Key']
            srm = key[:key.find('-')]
            heading_key = srm + '_' + heading
            # Check whether the heading_key is in abstracts and whether the content is null or not
            if (heading_key not in abstracts) and current['Content']:
                abstracts[heading_key] = [[key], str(current['Content'])]
            # If current['Content'] exists/is not null, add it to the abstracts dictionary
            elif current['Content']:
                # Use heading_key as primary key column
                # Append all Unique_Keys with the same heading to a list
                abstracts[heading_key][0].append(key)
                # Add the content from the line. If it is too long, get only the first 3800 characters
                abstracts[heading_key][1] += (' ' + (str(current['Content']))[:3800])

        # Create a dictionary/map with key columns 'Unique_Key', 'Heading_Key', and 'Abstract'
        # for each heading key in abstracts...
        for hkey in abstracts:
            #... go through each unique key in the list for that heading
            for uk in abstracts[hkey][0]:
                try: 
                    # In each row, add the Unique_Key, its corresponding heading_key, and the full abstract
                    # Note that many Unique_Keys may share a heading key or abstract, since the unique key refers to the line of the document
                    if uk and hkey and abstracts[hkey][1]:
                        abstract_data['Unique_Key'].append(uk)
                        abstract_data['Heading_Key'].append(hkey)
                        abstract_data['Abstract'].append(abstracts[hkey][1])
                except:
                    print(traceback.print_exc(file=sys.stdout) + '\n')
                    continue
        
        # Create dataframe/table with columns 'Unique_Key', 'Heading_Key', and 'Abstract' using the dictionary above
        abstract_data = pd.DataFrame(abstract_data)
        # Join the original table (df) with the abstract data on the Unique_Key column
        result = pd.merge(df, abstract_data, how='left', on=['Unique_Key', 'Unique_Key'])
        return result

    # Create a .csv file to export
    # @param df - the dataframe (i.e. data table) to convert to spreadsheet form
    # @param destination - full file path where spreadsheet will be saved
    def create_files(self, df, destination): 
        try: 
            data = pd.DataFrame(df)
            data.to_csv(destination, encoding='utf-8-sig') 
        except:
            try: 
                self.destination = input('ERROR. Make sure the file is closed and the FULL file path was entered. Reenter the file path: ') + '/'
                data = pd.DataFrame(df)
                data.to_csv(destination, encoding='utf-8-sig') # CHANGE
            except: 
                print('ERROR: ', traceback.print_exc(file=sys.stdout))
                sys.exit()
