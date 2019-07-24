from urllib.request import urlopen
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re

# Creating the Sets that will store the links that need to be investigated AND the resultant email addresses found
linkList = list()
emailSet = set()

# Organisational URL to analyse
url = "https://www.business.unsw.edu.au/about/contact"

URLParts = url.split("/")
baseURL = URLParts[0] + "//" + URLParts[2]
# print(baseURL)

linkList.append(url)
count = 0;
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
headers = {"User-Agent": userAgent}
# values = {'name' : 'Michael Foord',
#           'location' : 'Northampton',
#           'language' : 'Python' }


for link in linkList:
    fullUrlUsed = True
    if count < 100:
        # Opens a python handler and gets the HTML of the webpage being loaded
        try:
            # data = urllib.parse.urlencode(values).encode("ascii")
            req = urllib.request.Request(link, None, headers)
        except:
            continue
        try:
            pageHandler = urlopen(req)
            html = BeautifulSoup(pageHandler, "html.parser")
            # print(html.preetify())
            count += 1
        except:
            # print("invalid URL - retrying with base URL")
            fullUrlUsed = False
            count += 1
            try:
                req = urllib.request.Request(baseURL + link, None, headers)
                pageHandler = urlopen(req)
            except:
                count -= 1
                print("URL cannot be loaded - " + link + " - " + baseURL + link)
                continue




    # for item in html.find_all('a'):
    #     item.get('href')
    #     emailsOnPage.add(re.findall("\S+@\S+", str(item)))
        # print(html.prettify())
        emails = re.findall('"mailto:([\S]+@[\S]+)"', str(html))
        for email in emails:
            emailSet.add(email)
        # TODO: Stop this from finding emails too!!
        links = re.findall('href="([\S]+)"', str(html))
        for currentLink in links:
            if currentLink not in linkList:
                linkList.append(currentLink)
        if fullUrlUsed:
            print(str(count) + " " + link)
        else:
            print(str(count) + " " + baseURL + link)

print(linkList)
# print("hello world")
print(emailSet)
