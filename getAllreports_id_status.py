import sqlite3 as sqlite
con = sqlite.connect('report_data.db')
cursor = con.cursor()
cursor.execute("select * from report_data")
print(*list(cursor), sep='\n')
