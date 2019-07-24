import sqlite3

conn = sqlite3.connect("email.db")
c = conn.cursor()

c.execute("SELECT COUNT(email) FROM EMAIL_TABLE")
count = c.fetchone()

print("The number of distinct emails found from the analysis was: " + str(count[0]))

for row in c.execute("SELECT DISTINCT domain FROM EMAIL_TABLE"):
    print(row[0])

# for row in c.execute("SELECT DISTINCT email FROM EMAIL_TABLE"):
#     print(row[0])
#
# for row in c.execute("SELECT DISTINCT url FROM LINK_TABLE"):
#     print(row[0])
