search_term = input('Enter your search term')
terms = search_term.split()
hyperlink = 'enter_hyperlink_here'
for term in terms: 
    addition = '&' + term
    hyperlink = hyperlink + addition