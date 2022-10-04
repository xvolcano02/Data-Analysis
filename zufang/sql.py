import pymysql
db = pymysql.connect(host='localhost', user='root', password='xxxx', database='lianjia')
cursor = db.cursor()
# sql1="select * from customer"
sql2='insert into test value ("整租","1200")'
try:
    cursor.execute(sql2)
    db.commit()
except:
    print("error")
# db.commit()
# results = cursor.fetchall()
# for row in results:
#     print(row)