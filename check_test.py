import sqlite3
conn = sqlite3.connect('test.sqlite')
c = conn.cursor()
print(c.execute('select * from test').fetchall())
conn.close()
