import sqlite3
conn = sqlite3.connect('test.sqlite')
c = conn.cursor()
print(c.execute('select * from test').fetchall())
print([colname for colname, *_ in c.description])
conn.close()
