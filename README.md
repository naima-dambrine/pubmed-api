pubmed.py
=========

pubmed.py is an unofficial API for pubmed. 
pubmed.py can search for papers on PUBMED and download PDF papers if exist in PMC (PubMed Central). 
Use from the command-line.

Features
--------
* Multi-criteria search
* Download articles from PubMed Central (free version)
* Export results in csv file (in a separate folder named PDF)

**Note**: Use python 3

![](images/screenshot.png)

Setup
-----
```
pip3 install -r requirements.txt
```

Usage
-----
pubmed.py [-h] [-a AUTHOR] [-k [KEYWORDS]] [-o {AND,OR,NOT}]
[-ko {AND,OR,NOT}] [-d DATE] [-f FREESYNTAXE]

PubMed - Search and Download papers for you. Don't waste your time ;-)

optional arguments:

-h, --help            
>>show this help message and exit

-a AUTHOR, --author AUTHOR
>>tries to find and download papers by author. Exemple :
"Firstname J"

-k [KEYWORDS], --keywords [KEYWORDS]
>>tries to find and download papers by terms. Exemple :
"nipah bats"

-o {AND,OR,NOT}, --operator {AND,OR,NOT}
>>general operator. choose from : "OR", "AND", "NOT"

-ko {AND,OR,NOT}, --keywordsoperator {AND,OR,NOT}
>>keywords operator. choose from : "OR", "AND", "NOT"

-d DATE, --date DATE  
>>tries to find and download papers by date. YYYY/MM/DD

-f FREESYNTAXE, --freesyntaxe FREESYNTAXE
>>Free Syntax. Exclusive argument

Examples
--------
search by author
./pubmed.py -a "Firstname, Lastname"
>>(Firstname, Lastname[Author])

search by date
./pubmed.py -d "2017"
./pubmed.py -d "2017/01"
>>(2017/01[Date - Publication] : "3000"[Date - Publication])
>>From 2017/01 to Present

search by keywords
./pubmed.py -k "nipah bats"
>>( (nipah bats) )

search by keywords and  specifie keyword operator
./pubmed.py -k "nipah bats" -k "other" -k "another" -ko OR
>>( (nipah bats)    OR    (other) OR (another) )

search by free syntax if familiar
./pubmed.py -f "(Firstname, Lastname[Author])  AND  (2017[Date - Publication] : "3000"[Date - Publication])"
>> search by author AND date fixed from 2017 to present

./pubmed.py  -k "nipah bats" -k "dffddfdf"  -k "dssdds" -a "Firstname,Lastname" -ko OR -a "Firstname, Lastname" -o NOT
>> search by multiple keywords , fix keyword operator to OR (AND is default) , fix general operator to NOT :
>>( ( (nipah bats) OR (dffddfdf) OR (dssdds) ) ) NOT ( (Firstname, Lastname[Author]) ) 


## Authors

* **Naïma Dambrine** 

## License

This project is licensed under the MIT License 
