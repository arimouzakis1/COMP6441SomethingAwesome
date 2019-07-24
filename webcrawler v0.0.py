from urllib.request import urlopen
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


for link in linkList:
    fullUrlUsed = True
    urlLoaded = True
    if count < 25:
        # Opens a python handler and gets the HTML of the webpage being loaded
        try:
            pageHandler = urlopen(link)
            html = BeautifulSoup(pageHandler, "html.parser")
            count += 1
        except:
            # print("invalid URL - retrying with base URL")
            fullUrlUsed = False
            count += 1
            try:
                pageHandler = urlopen(baseURL + link)
            except:
                count -= 1
                print("URL cannot be loaded")
                urlLoaded = False



    #print(html.prettify())

    # for item in html.find_all('a'):
    #     item.get('href')
    #     emailsOnPage.add(re.findall("\S+@\S+", str(item)))
        if urlLoaded:
            emails = re.findall('"mailto:([\S]+@[\S]+)"', str(html))
            for email in emails:
                emailSet.add(email)
            links = re.findall('href="([\S]+)"', str(html))
            for currentLink in links:
                if currentLink not in linkList:
                    linkList.append(currentLink)
            if fullUrlUsed:
                print(str(count) + " " + link)
            else:
                print(str(count) + " " + baseURL + link)

# print(linkList)
# print("hello world")
print(emailSet)
