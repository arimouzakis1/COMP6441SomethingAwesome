from urllib.request import urlopen
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re
import sqlite3


def loadHtml(req):
    pageHandler = urlopen(req)
    return BeautifulSoup(pageHandler, "html.parser")

# Creating the Sets that will store the links that need to be investigated AND the resultant email addresses found
# linkList = list()
emailsToWrite = [("example@unsw.edu.au", "example", "@unsw.edu.au")]
# linksToWrite = list()

# Setting up SQLite Database
conn = sqlite3.connect("UNSWBusinessSchool.db")
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

c.execute("SELECT url FROM LINK_TABLE WHERE html IS NULL OR html = 'None' OR html = '';")
unsearchedLinks = [item[0] for item in c.fetchall()]

baseURL = "https://www.business.unsw.edu.au"
if len(unsearchedLinks) == 0:
    # Organisational URL to analyse
    url = "https://www.business.unsw.edu.au/about/contact"

    URLParts = url.split("/")
    baseURL = URLParts[0] + "//" + URLParts[2]

    unsearchedLinks.append(url)

count = 0;
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
headers = {"User-Agent": userAgent}


for link in unsearchedLinks:
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
            count += 1
            fullUrlUsed = False
            dashRequired = False
            if link[0] != '/':
                dashRequired = True
            try:
                if dashRequired:
                    req = urllib.request.Request(baseURL + "/" + link, None, headers)
                else:
                    req = urllib.request.Request(baseURL + link, None, headers)
                pageHandler = urlopen(req)
                html = BeautifulSoup(pageHandler, "html.parser")
            except:
                count -= 1
                print("URL cannot be loaded - " + link + " - " + baseURL + link)
                continue


        emails = re.findall('"mailto:([a-zA-Z0-9.]+@[a-zA-Z0-9.]+)"', str(html))
        for email in emails:
            emailParts = email.split("@")
            emailsToWrite.append((email, emailParts[0], "@" + emailParts[1]))
        links = re.findall('href="([\S]+)"', str(html))
        for currentLink in links:
            if "mailto" and "javascript" not in currentLink:
                if currentLink not in unsearchedLinks:
                    unsearchedLinks.append(currentLink)
        if fullUrlUsed:
            # unsearchedLinks.append(link)
            print(str(count) + " " + link)
            # updateCurrentUrl = (str(html), link)
            updateCurrentUrl = (baseURL + link, str(html), link)
            c.execute("UPDATE OR REPLACE LINK_TABLE SET url = ? AND html = ? WHERE url = ?", updateCurrentUrl)
            # c.execute("INSERT OR REPLACE INTO LINK_TABLE(html, url) VALUES(?, ?)", updateCurrentUrl)
            conn.commit()
        else:
            # unsearchedLinks.append(baseURL + link)
            print(str(count) + " " + baseURL + link)
            updateCurrentUrl = (baseURL + link, str(html), link)
            c.execute("UPDATE OR REPLACE LINK_TABLE SET url = ? AND html = ? WHERE url = ?", updateCurrentUrl)
            # updateCurrentUrl = (str(html), link)
            # c.execute("INSERT OR REPLACE INTO LINK_TABLE(html, url) VALUES(?, ?)", updateCurrentUrl)
            conn.commit()



        # Every 10 iterations, commit this data to the database and clear the lists
        if count % 10 == 0:
            c.executemany("INSERT OR IGNORE INTO EMAIL_TABLE(email, host, domain) VALUES(?, ?, ?)", emailsToWrite)
            for linkToWrite in unsearchedLinks:
                try:
                    c.execute("INSERT OR IGNORE INTO LINK_TABLE(url) VALUES('" + linkToWrite + "');")
                except :
                    print("link failed to write - " + linkToWrite)
                    unsearchedLinks.remove(linkToWrite)
                    # c.execute("DELETE FROM LINK_TABLE WHERE url = " + linkToWrite)
            conn.commit()
            # emailsToWrite.clear()
            # linksToWrite.clear()

c.close()
conn.close()
print("Finished execution")
