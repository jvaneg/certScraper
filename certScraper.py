import requests as rq
from bs4 import BeautifulSoup
import re
import sys
import subprocess
import os
from OpenSSL import crypto


def main(argv):
    if(len(argv) != 3):
        print("Invalid args!\ncertScraper.py [alexa category] [number of links]")
        exit(-1)

    category = argv[1]
    numLinks = int(argv[2])

    if(numLinks < 1):
        print("Invalid number of links, must be > 1")
        exit(-1)
    if(numLinks > MAX_LINKS):
        print("Too many links! More links than " + str(MAX_LINKS) + " not supported (because I don't have alexa premium)")
        exit(-1)

    # gets the html
    rawHtml = rq.get('https://www.alexa.com/topsites/category/Top/' + category)

    # parse the html in pairs: root - subdomain
    # phil made me use this line im sorry its like this lmao
    links = [list((str((((line.split('/'))[2]).split('"'))[0]).lower(),str((((line.split('>'))[1]).split('<'))[0]).lower())) for line in rawHtml.text.split('\n') if "/siteinfo/" in line]

    # puts the www. back for sites that dont have subdomains
    # this is because i was having some weirdness with www.nih.gov and nih.gov having different certs,
    # but www.docs.google.com didnt have a cert and docs.google.com did have one
    # probably not optimal but works for my purposes
    for link in links:
        if link[1].count('.') <= 1:
            link[1] = "www." + str(link[1])

    if(len(links) == 0):
        print("No links in this category! (Note: Category is case-sensitive, and should have underscores instead of spaces")
        exit(-1)

    # reduces the link count to the specified number
    links = links[:numLinks]


    # create folders for the certs and indexes about to be downloaded
    subprocess.call(["mkdir","-p", INDEX_PATH])
    subprocess.call(["mkdir","-p", CERTS_PATH])

    # attempt to download the index of a site and get its cert for each set
    for link in links:
        print(link[1])
        subprocess.call(["bash", CERT_DOWNLOADER, link[1]])
        

    indexes = os.listdir(INDEX_PATH)
    numIndexes = len(indexes)
    certs = os.listdir(CERTS_PATH)
    numCerts = len(certs)

    # print out the sites for human readability
    print("Root --- Site")
    for link in links:
        print(link[0] + " --- " + link[1])

    percentLinksWork = (numIndexes/len(links))*100
    percentLinksTLS = (numCerts/len(links))*100

    print("Percent of links that work: " + str(percentLinksWork) + "% (" + str(numIndexes) + "/" + str(len(links)) + ")")
    print("Percent of links that support TLS: " + str(percentLinksTLS) + "% (" + str(numCerts) + "/" + str(len(links)) + ")")

    # gets the CA and expiration for each cert
    for certFile in os.listdir(CERTS_PATH):
        print(certFile)
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(CERTS_PATH + certFile).read())
        issuer = cert.get_issuer()
        issuerName = issuer.CN
        expirationDate = cert.get_notAfter()    #format: YYYYMMDDhhmmssZ
        print(issuerName)
        print(expirationDate)


    

# keeping this for some reason
# old version before phil wanted to show off his one-line abomination
def old_main(argv):
    if(len(argv) != 3):
        print("Invalid args!\ncertScraper.py [alexa category] [number of links]")
        exit(-1)

    category = argv[1]
    numLinks = int(argv[2])

    if(numLinks < 1):
        print("Invalid number of links, must be > 1")
        exit(-1)
    if(numLinks > MAX_LINKS):
        print("Too many links! More links than " + str(MAX_LINKS) + " not supported (because I don't have alexa premium)")
        exit(-1)

    # gets the html
    rawHtml = rq.get('https://www.alexa.com/topsites/category/Top/' + category)

    html = BeautifulSoup(rawHtml.text, 'html.parser')

    # gets the /siteinfo/ links
    links = html.find_all(href=hasLink) 

    # formats the links
    links = map(formatLink, links)

    if(len(links) == 0):
        print("No links in this category! (Note: Category is case-sensitive, and should have underscores instead of spaces")
        exit(-1)

    # reduces the link count to the specified number
    links = links[:numLinks]

    for link in links:
        print(link)



# finds links that start with "/siteinfo/"
def hasLink(href):
    return href and re.compile("/siteinfo/").search(href)

# formats the /siteinfo/website.com links to be regular www.website.com links
def formatLink(linkToFormat):
    link = linkToFormat.get('href')
    remove = '/siteinfo/'
    link = "www." + link[len(remove):]
    return link



# Constants
ALEXA_CATEGORY_ROOT = "https://www.alexa.com/topsites/category/Top/"        # file containing list of password "words"
MAX_LINKS = 50
CERT_DOWNLOADER = "getCerts.sh"
INDEX_PATH = "./tmp/indexes/"
CERTS_PATH = "./tmp/certs/"

if __name__ == "__main__":
    main(sys.argv)

