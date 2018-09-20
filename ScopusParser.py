import bs4, requests, sys, pprint, codecs

DOMAIN = 'https://www.scopus.com'
END_TAIL = '/search/submit/authorFreeLookup.uri'
s = requests.Session()

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

#Scrapes documents found on author's scopus profile
def scrape_scopus_author(scopus_auth_id, download_resp=False):
    doc_resp = author_documents_request(scopus_auth_id)
    bs = bs4.BeautifulSoup(doc_resp, 'html.parser')
    if download_resp:
        f = codecs.open('author_page.html', 'w', encoding='utf-8')
        f.write(doc_resp)
        f.close()
    tbody = bs.find('table', id='srchResultsList').find('tbody')
    documents = []
    for row in tbody.find_all('tr', class_='searchArea'):
        document = {}
        cols = row.find_all('td')
        document['title'] = cols[0].text.strip().replace('\n', '')
        document['authors'] = [x.text.strip().replace('\n', '') for x in
            cols[1].find_all('span', class_='previewTxt')]
        document['year'] = int(cols[2].text.strip().replace('\n', ''))
        document['source'] = cols[3].text.strip().replace('\n', '')
        document['cited_by'] = cols[4].text.strip().replace('\n', '')
        documents.append(document)
    return documents

def main():
    pp = pprint.PrettyPrinter(indent=4)
    if len(sys.argv) != 4:
        print('Incorrect formatting.  Should be: "fname" "lname" "org"')
    else:
        authors = search_author(*sys.argv[1:], pp=True)
        ind = 0
        if len(authors) > 1:
            ind = int(input('Select the author using the number above.\n'))
        print_map(authors[ind], title=authors[ind]['names'][0])
        print_documents(scrape_scopus_author(authors[ind]['scopus_auth_id']))



#Printing--------------------------------------------------------------
#Pretty prints the return of a search_author call
def print_author_results(authors):
    for i in range(len(authors)):
        print(i, '\t', authors[i]['names'][0])
        for j in range(1, len(authors[i]['names'])):
            print('\t', authors[i]['names'][j])
        print('Affiliation:', authors[i]['affiliation'])
        print('Documents:', authors[i]['documents'])
        print('')

#Pretty prints a list of documents owned by an author
def print_documents(documents):
    print(''.join(100 * '-'))
    print("Documents -", len(documents))
    for i in range(len(documents)):
        print(i, '\t', documents[i]['title'])
        print('Authors:', ';'.join(documents[i]['authors']))
        print('Source:', documents[i]['source'])
        print('Year:', documents[i]['year'])
        print('Cited by:', documents[i]['cited_by'], '\n')

#Pretty prints a generic map
def print_map(m, index=None, title=None):
    if title:
        if index:
            print(index, '\t', title)
        else:
            print(title)
    for key in m:
        key_str = key
        if len(key_str) < 19:
            key_str = key_str + (19 - len(key_str)) * ' '
        else:
            key_str = key_str[0:19]
        val_str = str(m[key])
        if len(val_str) > 90:
            val_str = val_str[0:90]
        print(key_str.capitalize() + ':', '\t', val_str)

#Requests--------------------------------------------------------------
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
    s.get('https://www.scopus.com/freelookup/form/author.uri?zone=&origin=AuthorProfile')
    r = s.post(DOMAIN + END_TAIL, data=form_data)
    return r

#Sends a get request to scopus for documents
def author_documents_request(scopus_auth_id):
    resp = s.get('https://www.scopus.com/author/document/retrieval.uri?authorId='\
        + scopus_auth_id \
        + '&tabSelected=docLi&sortType=plf-f')
    if resp.status_code != requests.codes.ok:
        print("Response was", resp.status)
        return
    return resp.text

if __name__ == "__main__":
    main()
