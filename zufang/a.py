import time
import requests
import re
from bs4 import BeautifulSoup
import pymysql
header={
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
}

home_url="https://app.api.lianjia.com/Rentplat/v1/house/list?city_id=110000&condition=huairou&limit=30&offset="
def get_info(html):
    pass
def get_data(url,session):
    pass
def ask_url(url,session):
    codes=[]
    bizcircles=[]
    resp=session.get(url,headers=header)
    json=resp.json()
    datas=json['data']['list']
    for item in datas:
        code=item['house_code']
        bizcircle_name=item['bizcircle_name']
        codes.append(code)
        bizcircles.append(bizcircle_name)
    return codes,bizcircles


if __name__ == '__main__':
    session = requests.session()
    db = pymysql.connect(host='localhost', user='root', password='809349289xc', database='lianjia')
    cursor = db.cursor()
    for k in range(1,5):
        url=f"https://app.api.lianjia.com/Rentplat/v1/house/list?city_id=110000&condition=huairou&limit=30&offset={91}&request_ts={int(time.time())}&scene=list"
        print(url)
        codes,bizcircles=ask_url(url,session)
        for i in range(len(codes)):
            code=codes[i]
            bizcircle_name=bizcircles[i]
            sql=f"insert into codes values ('{code}','怀柔','{bizcircle_name}')"
            try:
                cursor.execute(sql)
                db.commit()
            except:
                print("error")
        time.sleep(30)

    # for i in range()
    #     codes=get_data(item_url,session)
        # sql = f"insert into codes values ("","")"
        # try:
        #     cursor.execute(sql)
        #     db.commit()
        # except:
        #     pass

    t2=time.time()