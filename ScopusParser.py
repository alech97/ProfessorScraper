import bs4, requests, sys, pprint

DOMAIN = 'https://www.scopus.com'
END_TAIL = '/search/submit/authorFreeLookup.uri'

#Parses html response from scopus for an author search
def search_author(firstname, lastname, org, pp=False):
    text_response = search_author_request(firstname, lastname, org).text
    bs = bs4.BeautifulSoup(text_response, 'html.parser')
    authors = []
    for row in bs.find_all('tr', class_='searchArea'):
        author = {}
        names = []
        author['names'] = names
        #Get names and url from name_col
        name_col = row.find('td', class_='authorResultsNamesCol')
        a_first = name_col.find('a')
        if a_first:
            author['url'] = a_first.get('href')
            names.append(a_first.text.strip())
            author['scopus_auth_id'] = author['url'].split('authorID=')[1].split('&')[0]
        for div in name_col.find_all('div'):
            names.append(div.text.strip())
        if len(names) == 0:
            names.append(name_col.text.strip())
        #Get number of documents
        author['documents'] = int(
            row.find(
                'td',
                id=lambda x: x and x.startswith('resultsDocumentsCol')
            ).find('a').text
        )
        #Get Affiliation
        a_aff = row.find('td', class_='dataCol5').find('a')
        author['affiliation_url'] = a_aff.get('href')
        author['affiliation'] = a_aff.text.strip()
        #Add author
        authors.append(author)
    if pp:
        print_author_results(authors)
    return authors

#Sends a post request to scopus based on three search fields, returns response
def search_author_request(firstname, lastname, org):
    form_data = {
        'origin': 'searchauthorfreelookup',
        'freeSearch': True,
        'src': '',
        'edit': '',
        'poppUp': '',
        'exactSearch': 'on',
        'searchterm1': lastname,
        'searchterm2': firstname,
        'institute': org,
        'submitButtonName': 'Search',
        'orcidId': '',
        'authSubject': 'LFSC',
        '_authSubject': 'on',
        'authSubject': 'HLSC',
        '_authSubject': 'on',
        'authSubject': 'PHSC',
        '_authSubject': 'on',
        'authSubject': 'SOSC',
        '_authSubject': 'on'
    }
    s = requests.Session()
    s.get('https://www.scopus.com/freelookup/form/author.uri?zone=&origin=AuthorProfile')
    r = s.post(DOMAIN + END_TAIL, data=form_data)
    return r

#Pretty prints the return of a search_author call
def print_author_results(authors):
    for i in range(len(authors)):
        print(i, '\t', authors[i]['names'][0])
        for j in range(1, len(authors[i]['names'])):
            print('\t', authors[i]['names'][j])
        print('Affiliation:', authors[i]['affiliation'])
        print('Documents:', authors[i]['documents'])
        print('')

def main():
    pp = pprint.PrettyPrinter(indent=4)
    if len(sys.argv) != 4:
        print('Incorrect formatting.  Should be: "fname" "lname" "org"')
    else:
        authors = search_author(*sys.argv[1:], pp=True)
        ind = 0
        if len(authors) > 1:
            ind = int(input('Select the author using the number above.\n'))
            print('Selected', ind)
        pp.pprint(authors[ind])

if __name__ == "__main__":
    main()
