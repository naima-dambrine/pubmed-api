#!/usr/local/bin/python3.6
# -*- coding: utf-8 -*-

"""
PubMed-API Unofficial API
[Search|Export|Download] research papers from [pubmed] and export results in csv file.
@author Naïma Dambrine

USAGE:

pubmed.py [-h] [-a AUTHOR] [-k [KEYWORDS]] [-o {AND,OR,NOT}]
                 [-ko {AND,OR,NOT}] [-d DATE] [-f FREESYNTAXE]

PubMed - Search and Download papers for you. Don't waste your time ;-)

optional arguments:
  -h, --help            show this help message and exit
  -a AUTHOR, --author AUTHOR
                        tries to find and download papers by author. Exemple :
                        "Firstname J"
  -k [KEYWORDS], --keywords [KEYWORDS]
                        tries to find and download papers by terms. Exemple :
                        "nipah bats"
  -o {AND,OR,NOT}, --operator {AND,OR,NOT}
                        general operator. choose from : "OR", "AND", "NOT"
  -ko {AND,OR,NOT}, --keywordsoperator {AND,OR,NOT}
                        keywords operator. choose from : "OR", "AND", "NOT"
  -d DATE, --date DATE  tries to find and download papers by date. YYYY/MM/DD
  -f FREESYNTAXE, --freesyntaxe FREESYNTAXE
                        Free Syntax. Exclusive argument

EXAMPLES :
search by author
./pubmed.py -a "Firstname, Lastname"
>>(Firstname, Lastname[Author])

search by date
./pubmed.py -d "2017"
./pubmed.py -d "2017/01"
>>(2017/01[Date - Publication])

search by keywords
./pubmed.py -k "nipah bats"
>>( (nipah bats) )

search by keywords and  specifie keyword operator
./pubmed.py -k "nipah bats" -k "other" -k "another" -ko OR
>>( (nipah bats)    OR    (other) OR (another) )

search by free syntax if familiar
./pubmed.py -f "(Firstname, Lastname[Author])  AND  (2017[Date - Publication])"
>> search by author AND date fixed to 2017

./pubmed.py  -k "nipah bats" -k "dffddfdf"  -k "dssdds" -a "Firstname,Lastname" -ko OR -a "Firstname, Lastname" -o NOT
>> search by multiple keywords and fix keyword operator to OR (AND is default) , results is :
>>( ( (nipah bats) OR (dffddfdf) OR (dssdds) ) ) NOT ( (Firstname, Lastname[Author]) )
"""
import sys

if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.x \n")
    sys.exit(1)

import os
import csv
import argparse
import re

from Bio import Entrez, Medline
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from urllib.error import URLError

#CONSTANTS
CSV_FILE_NAME = "pubmed.csv"
UPLOAD_DIRECTORY="PDF"
PUBMED_URL="https://www.ncbi.nlm.nih.gov/pubmed/"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

class PubMed():
	"""
	PubMed class can search for papers on PubMed
	export results in csv file and download papers from PubMedCentral (PMC)
	"""
	term=''

	def __init__(self):
		pass

	def directory(self, UPLOAD_DIRECTORY):
		"""
		@brief      Creates directory if not exists .
		@param      UPLOAD_DIRECTORY   directory name to create
		@return     { Creates a directory to store PDF}
		"""
		if not os.path.exists(UPLOAD_DIRECTORY):
			os.mkdir(UPLOAD_DIRECTORY)
		return UPLOAD_DIRECTORY

	def _get_total_review(self, term):
		"""
		@brief      Returns total result .
		@param      self   The object
		@param      term   Search criteria
		@return     { Returns total of papers matching the search criteria}
		"""
		Entrez.email = "me@wonderful.wordl.fr"
		try:
			handle = Entrez.esearch(db="pubmed", term=term)
			record = Entrez.read(handle)
		except URLError as e:
			if hasattr(e, 'reason'):
				print('We failed to reach a server.')
				print('Reason: ', e.reason)
				sys.exit(1)
			elif hasattr(e, 'code'):
				print('The server couldn\'t fulfill the request.')
				print('Error code: ', e.code)
				sys.exit(1)
		except:
			print('Empty term and query_key - nothing todo')
			sys.exit(1)
		else:
			count = int(record['Count'])
			print("Found reviews :" + str(count))
			return count

	def _get_pmid_from_previous(self):
		"""
		@brief      Get list of PMID from csv file if exists
		@param      self   The object
		@param      data   List of all PMID
		@return     { Return list of PMID so as not to reprocess them afterwards}
		"""
		previous=[]
		if os.path.exists(CSV_FILE_NAME):
			with open(CSV_FILE_NAME) as f:
				for row in f:
					previous.append(re.sub("[^A-Z\d]","",row.split(';',1)[0]))
		return previous

	def _get_all_pmid(self, term):
		"""
		@brief      Gets all PMID matching the search criteria
		@param      self   The object
		@param      term   Search criteria
		@return     { Returns all PMID from PubMed and returns results in list}
		"""
		ids=[]
		retmax = self._get_total_review(term)
		if retmax == 0:
			exit()
		try:
			handle = Entrez.esearch(db="pubmed", term=term,  retmax=retmax)
			record = Entrez.read(handle)
			handle.close()
		except URLError as e:
			if hasattr(e, 'reason'):
				print('We failed to reach a server.')
				print('Reason: ', e.reason)
				sys.exit(1)
			elif hasattr(e, 'code'):
				print('The server couldn\'t fulfill the request.')
				print('Error code: ', e.code)
				sys.exit(1)
		else:
			ids = record["IdList"]

		return ids

	def _merge_result(self, newList):
		"""
		@brief      Merge results between current and previous search
		@param      self   The object
		@param      newList   List of PMID
		@return     { Returns PMID merged list }
		"""
		previous = self._get_pmid_from_previous()
		current = newList
		if len(previous) > 0:
			ids = list(set(current) - set(previous))
		else:
			ids = current
		return ids

	def request_safely(self, req):
		"""
        	@brief      Performs a request .
		@param      self   The object
		@return     { Performs request on pubmed throw exceptions}
        	"""
		try:
			page = urlopen(req).read()
		except URLError as e:
			if hasattr(e, 'reason'):
				print('We failed to reach a server.')
				print('Reason: ', e.reason)
				sys.exit(1)
			elif hasattr(e, 'code'):
				print('The server couldn\'t fulfill the request.')
				print('Error code: ', e.code)
				sys.exit(1)
			else:
				print('Everything is fine')
		return page

	def download(self, url,pmid):
		"""
		@brief      Download article PDF .
		@param      self   The object
		@param      pmid  The items are list of results search by term
		@return     { Performs a query on pubmed and download PDF }
		"""
		rq = Request(url, headers=HEADERS)
		res = self.request_safely(rq)
		if res:
			res = urlopen(rq)
			pdf_dir = self.directory(UPLOAD_DIRECTORY)
			if not os.path.isfile(pdf_dir+'/'+pmid+'.pdf'):
				pdf = open(pdf_dir+'/'+pmid+'.pdf', 'wb')
				pdf.write(res.read())
				pdf.close()

	def search(self,idlist):
		"""
		@brief      Search articles in PubMed according to given list .
		@param      self   The object
		@param      idlist List of PMID
		@return     { Performs a query on pubmed, stores results in list }
		"""

		records=""

		try:
			handle = Entrez.efetch(db="pubmed", id=idlist, rettype="medline",retmode="text")
		except URLError as e:
			if hasattr(e, 'reason'):
				print('We failed to reach a server.')
				print('Reason: ', e.reason)
				sys.exit(1)
			elif hasattr(e, 'code'):
				print('The server couldn\'t fulfill the request.')
				print('Error code: ', e.code)
				sys.exit(1)
		else:
			records = Medline.parse(handle)
			records = list(records)
		return records

	def export(self, items):
		"""
		@brief      Export in csv file.
		@param      self   The object
		@param      items  The items are list of results search by term
		@return     { Exports results in csv file }
		"""
		if os.path.exists(CSV_FILE_NAME):
			csvfile = open(CSV_FILE_NAME, 'a', newline='')
			csvwriter = csv.writer(csvfile, delimiter=';',quoting=csv.QUOTE_MINIMAL, escapechar='\\', quotechar='"')
		else:
			csvfile = open(CSV_FILE_NAME, 'w', newline='')
			csvwriter = csv.writer(csvfile, delimiter=';',quoting=csv.QUOTE_MINIMAL, escapechar='\\', quotechar='"')
			csvwriter.writerow(['PMID','Title','Date publication','First author', 'Authors', 'Publication Type', 'Journal Title', 'Source', 'Volume','Pagination', 'Abstract','DOI'])

		for record in items:
			FA=record.get("FAU","")[:1] # first author and  remove brackets
			DP=re.findall('\d{4}', record.get("DP")) # extract yyyy
			csvwriter.writerow([record.get("PMID", "?"),record.get("TI", "?"),DP, FA, record.get("FAU","?"),record.get("PT","?"),record.get("JT","?"), record.get("SO", "?"), record.get("VI","?"), record.get("PG","?"), record.get("AB", "?"),record.get("LID", "?")])

		csvfile.close()

	def downloadAll(self, items):
		"""
		@brief      Downloads all.
		@param      self   The object
		@param      items  The items are list of results search by term
		@return     { Downloads PDF if PMC link finded }
		"""
		for record in items:
			pmid = record.get("PMID", "?")
			print("PMID:", pmid)
			req = Request(PUBMED_URL+'?term='+pmid, headers=HEADERS)
			page = self.request_safely(req)
			if page:
				base_url = urlparse(PUBMED_URL + '?term='+pmid).netloc
				soup = BeautifulSoup(page, "lxml")
				#CHECK IF PMC LINK
				if soup.find('a', {'class' : 'status_icon'}):
					if 'PMC' in soup.find('a', {'class' : 'status_icon'}).text:
						#FETCH FOR PDF LINKS
						if soup.find('div',{'class' : 'icons portlet'}):
							links = soup.find('div',{'class' : 'icons portlet'}).findAll('a')
							for l in links:
								if 'pmc' in str(l):
									print('PMC link finded ... Trying to get PDF')
									pmc_url = l.get('href')
									req = Request(pmc_url,  headers={'User-Agent': 'Mozilla/5.0'} )
									page = self.request_safely(req)
									if page:
										page = urlopen(req).read()
										soup = BeautifulSoup(page, "lxml")
										links = soup.find('div',{'class' : 'format-menu'}).select('a')
										for link in links:
											if '.pdf' in str(link):
											    if 'http' in str(link):
											    	url = link.get('href')
											    else:
											    	url = req.type + '://' + req.host + link.get('href')
											    print('Downloading: ' + url)
											    self.download(url,pmid)

	def surround(self, word, tag1, tag2):
		"""
		@brief      Surround a word by tag1 and tag2.
		@param      self   The object
		@param      tag1  Begin tag
		@param      tag2  End tag
		@return     { Returns string }
		"""
		return " " + tag1 + str(word) + tag2 + " "

def main():
	pm = PubMed()

	parser = argparse.ArgumentParser(description='PubMed - Search and Download papers for you. Don\'t waste your time ;-)')
	parser.add_argument('-a', '--author', help='tries to find and download papers by author', type=str)
	parser.add_argument('-k', '--keywords', help='tries to find and download papers by terms', nargs='?', action='append', type=str)
	parser.add_argument('-o', '--operator', help='general operator. applies between all arguments', choices=['AND','OR','NOT'], default=' AND ', type=str)
	parser.add_argument('-ko', '--keywordsoperator', help='keywords operator. applies between keywords only', choices=['AND','OR','NOT'], default=' AND ', type=str)
	parser.add_argument('-d', '--date', help='tries to find and download papers by date (YYYY/MM/DD)', type=str)
	parser.add_argument('-f', '--freesyntaxe', help='free Syntax. Exclusive argument', type=str)

	if len(sys.argv)==1:
		parser.print_help()
		sys.exit(1)

	args = parser.parse_args()

	if args.author:
		author = args.author+"[Author]"
		author = pm.surround(author, "(",")")

	if args.keywords:
		keywords = args.keywords
		st = args.keywordsoperator.join(str(pm.surround(item,"(",")")) for item in keywords)
		st = st.replace('[','(')
		st = st.replace(']',')')
		st = st.replace('\'','')
		st = pm.surround(st,"(",")")
		keywords=st

	if args.date:
		dp = args.date
		dp = (dp+'[Date - Publication]')
		dp = pm.surround(dp, "(",")")


	if args.freesyntaxe:
		criteria = args.freesyntaxe

	orderedArguments = sys.argv
	argumentList = ['-a','-k','-d']
	tmp=[]
	for t in orderedArguments:
		if t in argumentList:
			if t not in tmp:
				tmp.append(t)
	liste=[]
	for c in tmp:
		if c == '-k':
			liste.append(keywords)
		if c == '-d':
			liste.append(dp)
		if c == '-a':
			liste.append(author)

	criteria=args.operator.join(str(pm.surround(item,"(",")")) for item in liste)

	print("Search criteria in use: " + criteria)

	currentList = pm._get_all_pmid(criteria)
	mergedList = pm._merge_result(currentList)
	if len(mergedList) == 0:
		print("Already in database")
	else:
		records = pm.search(mergedList)
		pm.export(records)
		pm.downloadAll(records)

if __name__ == '__main__':
	main()
