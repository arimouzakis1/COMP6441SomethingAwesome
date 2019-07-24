from urllib.request import urlopen
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re

from fake_useragent import UserAgent

# Creating the Sets that will store the links that need to be investigated AND the resultant email addresses found
linkList = list()
titleSet = set()

# Organisational URL to analyse
url = "https://www.smh.com.au/"

URLParts = url.split("/")
baseURL = URLParts[0] + "//" + URLParts[2]

linkList.append(url)
count = 0;
ua = UserAgent()
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
headers = {"User-Agent": '"' + ua.chrome + '"'}


for link in linkList:
    html = None
    fullUrlUsed = True
    if count < 1:
        # Opens a python handler and gets the HTML of the webpage being loaded
        try:
            req = urllib.request.Request(link, None, headers)
            pageHandler = urlopen(req)
            html = BeautifulSoup(pageHandler, "html.parser")
            count += 1
        except:
            fullUrlUsed = False
            dashRequired = False
            if link[0] != '/':
                dashRequired = True
            if dashRequired:
                req = urllib.request.Request(baseURL + "/" + link, None, headers)
            else:
                req = urllib.request.Request(baseURL + link, None, headers)
            try:
                pageHandler = urlopen(req)
                html = BeautifulSoup(pageHandler, "html.parser")
                count += 1
            except:
                count -= 1
                print("URL cannot be loaded - " + link + " - " + baseURL + link)
                continue

print(str(html))

#         titles = re.findall('>(.)</a>', str(html))
#         for title in titles:
#             titleSet.add(title)
#         # TODO: Stop this from finding emails too!!
#         links = re.findall('href="([\S]+)"', str(html))
#         for currentLink in links:
#             if currentLink not in linkList:
#                 linkList.append(currentLink)
#         if fullUrlUsed:
#             print(str(count) + " " + link)
#         else:
#             print(str(count) + " " + baseURL + link)
#
# print(titleSet)
