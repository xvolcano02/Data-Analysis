import time
import requests
import re
from bs4 import BeautifulSoup
import pymysql
import pandas as pd
header={
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36',
}
home_url="https://m.lianjia.com/chuzu/bj/zufang/"
def get_codes(file):
    df=pd.read_csv(file,header=None,names=['house_code','city','area','bizcircle'])
    codes=df['house_code'].values
    citys=df['city'].values
    areas=df['area'].values
    bizcircles=df['bizcircle'].values
    return codes,citys,areas,bizcircles
def get_data(url,session):
    codes=[]
    resp2 = session.get(url, headers=header)
    html = resp2.content.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    for item in soup.find_all('div', class_='content__item'):
        code = str(item.get("data-housecode"))      #获取房屋唯一标识符
        codes.append(code)
    return codes
def ask_url(url,session):
    resp3=session.get(url,headers=header)
    html=resp3.content.decode("utf-8")
    return html
def parase_html(html):
    pattern1=re.compile(r'<span>(\s*.*?)</span>')
    pattern2=re.compile(r'<i.*>(.*?)</i>')
    pattern3=re.compile(r'<span>(.*?)</span>')
    pattern4=re.compile(r'<a class="map--container" href=(.*?)>')
    pattern5 = re.compile(r'<span class="fr">(.*?)</span>')
    soup = BeautifulSoup(html, 'html.parser')
    title = str(soup.find_all("h2", class_="page-title-h2")[0].text).lstrip().rstrip()
    title=title.split("·")
    try:
        rent_type=title[0]                #整租/合租？
        region=title[1].split(" ")[0]     #小区名称
    except:
        rent_type=""
        region=""
    #------------------------------------------------------------------------  获取租金、户型、房屋面积
    info1=soup.find_all("div",class_="box content__detail--info")[0]
    info1=pattern1.findall(str(info1))
    rent_price=info1[1]
    type=info1[3].split("\n")[1].lstrip().rstrip()
    size=info1[5]
    #------------------------------------------------------------------------  获取房屋描述
    des=soup.find_all('p',class_="content__item__tag--wrapper")[0]
    des=pattern2.findall(str(des))
    des=" ".join(des)
    #------------------------------------------------------------------------  获取楼层、电梯信息
    info2=soup.find_all("ul",class_="page-house-info-list")[0]
    info2=pattern3.findall(str(info2))
    direc=info2[1]
    level=info2[4]
    have_lift=info2[5]
    #------------------------------------------------------------------------  获取经、纬度
    loc = pattern4.findall(str(html))[0]
    loc = loc.split("?coord=")[1].split(",")
    longitude=loc[0]
    latitude=loc[1].split("\"")[0]
    #------------------------------------------------------------------------  地铁距离
    try:
        text = soup.find_all('ul', class_="box page-map-list")[0]
        dis=pattern5.findall(str(text))[0]
    except:
        dis=""
    return rent_type,region,rent_price,type,size,des,direc,level,have_lift,longitude,latitude,dis
if __name__ == '__main__':
    session = requests.session()
    resp1 = session.get(home_url, headers=header)
    t1=time.time()
    db = pymysql.connect(host='localhost', user='root', password='809349289xc', database='lianjia')
    cursor = db.cursor()
    codes,citys,areas,bizcircles=get_codes('codes.csv')
    # for i in range(1,50):
    #     print(i)
    #     item_url = f"https://m.lianjia.com/chuzu/bj/zufang/yanqing/pg{i}/?ajax=1"
    #     codes=get_data(item_url,session)
    with open("process.txt","r") as f:
        last=int(f.read())
    f.close()
    for i in range(last,len(codes)):
        code=codes[i]
        city=citys[i]
        area=areas[i]
        bizcircle=bizcircles[i]
        detail_url=home_url+code+".html"
        html=ask_url(detail_url,session)
        rent_type,region,rent_price,house_type,house_size,des,direc,level,have_lift,longitude,latitude,dis=parase_html(html)
        print(code,city,area,bizcircle,rent_type,region,rent_price,house_type,house_size,des,direc,level,have_lift,longitude,latitude,dis,detail_url)
        # sql=f"insert into infos values ('{code}','{city}','{area}','{bizcircle}','{rent_type}','{region}','{rent_price}','{house_type}','{house_size}','{des}','{direc}','{level}','{have_lift}','{longitude}','{latitude}','{dis}','{detail_url}')"
        # try:
        #     cursor.execute(sql)
        #     db.commit()
        # except:
        #     print("error")
        if (i+1)%200==0:
            with open("process.txt","w") as f:
                f.write(str(i+1))
            f.close()
            t2 = time.time()
            print(f"已爬取{i+1}条房源 用时：{t2-t1}s")
        # cursor.execute(sql)
        # db.commit()

            # print(code)

    t2=time.time()