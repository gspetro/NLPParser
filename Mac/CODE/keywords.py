
import os, sys, traceback
import pandas as pd
import csv
import re

# Method to delete elements of search term that are random characters or short terms like "mm" or "mg"
def delete_short_words(search_term):
    word_list = search_term.split()
    search_term = ''
    for word in word_list:
        word = word.strip()
        if len(word) < 3: 
            continue
        else:
            search_term += word + ' '
    return search_term

# A method that assembles a dictionary of all search terms and the files/SRM's in which they occur
def terms_in_file(file_name, dictionary): 
    with open(file_name, encoding='utf-8-sig', newline='') as fh:
        print(file_name)
        contents = csv.reader(fh, delimiter=',', quoting=csv.QUOTE_ALL)
        for line in contents:
            # potential is search term from column 1
            potential = line[0].strip()
            potential = delete_short_words(potential)
            # source is the start of the Unique_Key from column 4
            source = line[3][:line[3].find('_')].strip()
            if potential not in dictionary:
                dictionary[potential] = [source]
            elif potential in dictionary and source not in dictionary[potential]:
                dictionary[potential].append(source)
    return dictionary

# A method that narrows down valid search terms by excluding overly frequent terms or search terms greater than 4 words long
def get_best_terms(search_term_dict, SIZE):
    PERCENT = 0.02
    best_terms = dict()
    for term in search_term_dict: 
        length = len(term.strip().split())
        # get all search terms of 1-4 words that appear in documents with a frequency of 2% or less than the number of documents
        if length > 0 and length < 5 and len(search_term_dict[term]) <= SIZE*PERCENT:
            best_terms[term] = search_term_dict[term]
    return best_terms

def get_search_terms(best_terms, folder):
    terms_by_srm = dict()
    # Goes through each term in best_terms
    for term in best_terms:
        # Iterates through the list of SRM's containing that particular term
        for srm in best_terms[term]:
            # If the SRM is NOT in terms_by_srm, add the SRM as a key and the search term as a value
            if srm not in terms_by_srm:
                terms_by_srm[srm] = [term]
            # If the SRM IS in terms_by_srm, add the search term to the value list for that SRM
            else:
                terms_by_srm[srm].append(term)
    create_file(terms_by_srm, folder)

def create_file(dictionary, folder):
    for srm in dictionary:
        with open(folder + '/' + srm + '-keywords.txt', 'w', encoding='utf-8-sig') as fh:
            for keyword in dictionary[srm]:
                fh.write(keyword + '\n')

# Verify that a CSV file is entered
def get_file():
    try:
        file = input('Enter the full file path of the RandR program\'s CSV output: \n')
        while not file.endswith('.csv'):
            file = input('ERROR. Enter the full file path of the RandR program\'s CSV output: \n')
        return file
    except FileNotFoundError:
        print('File not found.')
        get_file()
    except:
        print(traceback.print_exc(file=sys.stdout))
        sys.exit()

# Verify that a list directory/folder is entered
def get_folder():
    folder = input('Enter the full file path of the FOLDER where keyword results should be saved: \n')
    while not os.path.isdir(folder):
        folder = input('ERROR. Enter the full file path of the FOLDER where keyword results should be saved: \n')
    return folder

def main(): 
    TOTAL_SRMS = 1600
    search_terms = dict()
    #file_name = r'C:\Users\gsp3.NIST\Documents\NLP\MSDS_rr_db_input.csv'
    #file_name = r'C:\Users\gsp3.NIST\Documents\NLP\NLPParser\Test\MSDS_rr_excerpt.csv'
    #file_name = r'C:\Users\gsp3.NIST\Documents\NLP\NLPParser\spreadsheets\certs_rr_db_input.csv'
    #folder = r'C:\Users\gsp3.NIST\Documents\NLP\NLPParser\Test\KWFiles'
    file_name = get_file()
    folder = get_folder()
    print('Processing...')
    search_terms = terms_in_file(file_name, search_terms)
    """
    large_count = 0
    small_count = 0
    for term in search_terms:
        try:
            if len(search_terms[term]) < 32 and len(search_terms[term]) > 16:
                #print(term, '\t' + str(len(search_terms[term])), '\t' + str(search_terms[term]))
                large_count += 1
            elif len(search_terms[term]) < 16:
                small_count += 1
        except:
            print(traceback.print_exc(file=sys.stdout))
            continue
    print('Large Count:', large_count, 'Small Count: ', small_count)
    """
    search_terms = get_best_terms(search_terms, TOTAL_SRMS)
    get_search_terms(search_terms, folder)
    print('Done!')
    
if __name__ == '__main__':
    main()

