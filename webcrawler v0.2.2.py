from urllib.request import urlopen
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re
import sqlite3


# Creating the Sets that will store the links that need to be investigated AND the resultant email addresses found
linkList = list()
emailsToWrite = [("example@unsw.edu.au", "example", "@unsw.edu.au")]
linksToWrite = [("www.example.com.example", "<p>this is an example</p>")]

# Setting up SQLite Database
conn = sqlite3.connect("email.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS EMAIL_TABLE(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    domain TEXT NOT NULL,
    host TEXT NOT NULL
);
""")

c.execute("""CREATE TABLE IF NOT EXISTS LINK_TABLE(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    html TEXT
);
""")

# Organisational URL to analyse
url = "https://www.business.unsw.edu.au/about/contact"

URLParts = url.split("/")
baseURL = URLParts[0] + "//" + URLParts[2]

linkList.append(url)
count = 0;
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
headers = {"User-Agent": userAgent}


for link in linkList:
    html = None
    fullUrlUsed = True
    if count < 500:
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


        emails = re.findall('"mailto:([a-zA-Z0-9.]+@[a-zA-Z0-9.]+)"', str(html))
        for email in emails:
            emailParts = email.split("@")
            emailsToWrite.append((email, emailParts[0], "@" + emailParts[1]))
        # TODO: Stop this from finding emails too!!
        links = re.findall('href="([\S]+)"', str(html))
        for currentLink in links:
            if "mailto" not in currentLink:
                if currentLink not in linkList:
                    linkList.append(currentLink)
        if fullUrlUsed:
            linksToWrite.append((link,  str(html)))
        else:
            linksToWrite.append((baseURL + link, str(html)))
        if fullUrlUsed:
            print(str(count) + " " + link)
        else:
            print(str(count) + " " + baseURL + link)

        # Every 10 iterations, commit this data to the database and clear the lists
        if count % 25 == 0:
            c.executemany("INSERT OR IGNORE INTO EMAIL_TABLE(email, host, domain) VALUES(?, ?, ?)", emailsToWrite)
            c.executemany("INSERT OR IGNORE INTO LINK_TABLE(url, html) VALUES(?, ?)", linksToWrite)
            conn.commit()
            emailsToWrite.clear()
            linksToWrite.clear()

print("Finished execution")
