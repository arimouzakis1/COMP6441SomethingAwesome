from urllib.request import urlopen
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re
import sqlite3

def keyboardCancelRequest():
    c.close()
    conn.close()
    print("Finished execution")

# Creating the Sets that will store the links that need to be investigated AND the resultant email addresses found
emailsToWrite = [("example@unsw.edu.au", "example", "@unsw.edu.au")]

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

# Get data already collected (if any)
firstCrawl = False
c.execute("SELECT url FROM LINK_TABLE WHERE html IS NULL OR html = 'None' OR html = '';")
unsearchedLinks = [item[0] for item in c.fetchall()]

# Hardcoded base URL - This will be overwritten if this is the first time you're running a scan
baseURL = "https://www.business.unsw.edu.au"
if len(unsearchedLinks) == 0:
    # Organisational URL to analyse for the first crawl
    url = "https://www.business.unsw.edu.au/about/contact"

    URLParts = url.split("/")
    baseURL = URLParts[0] + "//" + URLParts[2]

    unsearchedLinks.append(url)
    firstCrawl = True

count = 0
maxCount = 0

# HTML Headers added to the program to get better compatibility with websites that have simple measures in place to stop crawling
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
headers = {"User-Agent": userAgent}

if firstCrawl:
    maxCount = 25
else:
    maxCount = 200

try:
    for link in unsearchedLinks:
        html = None
        fullUrlUsed = True
        if count < maxCount:
            # Opens a python handler and gets the HTML of the webpage being loaded
            try:
                req = urllib.request.Request(link, None, headers)
                pageHandler = urlopen(req)
                html = BeautifulSoup(pageHandler, "html.parser")
                count += 1
            except KeyboardInterrupt:
                keyboardCancelRequest()
            except ValueError:
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
                except KeyboardInterrupt:
                    keyboardCancelRequest()
                except ValueError:
                    count -= 1
                    print("URL cannot be loaded - " + link)
                    c.execute("DELETE FROM LINK_TABLE WHERE url = '" + link + "'")
                    continue


            emails = re.findall('"mailto:([a-zA-Z0-9.]+@[a-zA-Z0-9.]+)"', str(html))
            for email in emails:
                emailParts = email.split("@")
                emailsToWrite.append((email, emailParts[0], "@" + emailParts[1]))
            links = re.findall('href="([\S]+)"', str(html))
            for currentLink in links:
                if "mailto" not in currentLink and "javascript" not in currentLink:
                    if currentLink not in unsearchedLinks:
                        unsearchedLinks.append(currentLink)
            if fullUrlUsed:
                if firstCrawl:
                    updateCurrentUrl = (str(html), link)
                    c.execute("INSERT OR REPLACE INTO LINK_TABLE(html, url) VALUES(?, ?)", updateCurrentUrl)
                else:
                    updateCurrentUrl = (str(html), link)
                    c.execute("UPDATE OR REPLACE LINK_TABLE SET html = ? WHERE url = ?", updateCurrentUrl)
                conn.commit()
                print(str(count) + " " + link)
            else:
                if firstCrawl:
                    updateCurrentUrl = (str(html), link)
                    c.execute("INSERT OR REPLACE INTO LINK_TABLE(html, url) VALUES(?, ?)", updateCurrentUrl)
                else:
                    updateCurrentUrl = (baseURL + link, str(html), link)
                    c.execute("UPDATE OR IGNORE LINK_TABLE SET url = ?, html = ? WHERE url = ?", updateCurrentUrl)
                conn.commit()
                print(str(count) + " " + baseURL + link)



            # Every 25 iterations, commit this data to the database and clear the lists
            if count % 25 == 0:
                c.executemany("INSERT OR IGNORE INTO EMAIL_TABLE(email, host, domain) VALUES(?, ?, ?)", emailsToWrite)
                for linkToWrite in unsearchedLinks:
                    try:
                        c.execute("INSERT OR IGNORE INTO LINK_TABLE(url) VALUES('" + linkToWrite + "');")
                    except :
                        print("link failed to write - " + linkToWrite)
                        unsearchedLinks.remove(linkToWrite)
                conn.commit()

except KeyboardInterrupt:
    keyboardCancelRequest()

keyboardCancelRequest()
