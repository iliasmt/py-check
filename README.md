# py-check
manual tool to check for content in a website

Instructions for install:
* create a virtualenv
* pip install -r requirements.txt


Instructions for the software:
* python py-check.py --help


# Example usage:

in successful execution there is no output.


`python py-check.py "http://google.com" 'title' 'Google'`


in erroneous execution there is an error message.


`python py-check.py "http://google.com" 'title' 'blah'`

`FAILURE to find blah in http://google.com into html element title`