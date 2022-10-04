import re
import time
import requests
from info import rent_type, city_info
import pymysql
import random
header={
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
}
class Rent(object):
    """
    初始化函数，获取租房类型（整租、合租）、要爬取的城市分区信息以及连接mongodb数据库
    """
    def __init__(self):
        self.rent_type = rent_type
        self.city_info = city_info
        self.headr=header

    def get_data(self):
        """
        爬取不同租房类型、不同城市各区域的租房信息
        :return: None
        """
        db = pymysql.connect(host='localhost', user='root', password='809349289xc', database='lianjia')
        cursor = db.cursor()
        for ty, type_code in self.rent_type.items():  # 整租、合租
            for city, info in self.city_info.items():  # 城市、城市各区的信息
                for dist, dist_py in info[2].items():  # 各区及其拼音
                    url='https://m.lianjia.com/chuzu/{}/zufang/{}/'.format(info[1], dist_py)
                    res_bc = requests.get(url,headers=self.headr)
                    # print(res_bc.text)
                    pa_bc = r"data-type=\"bizcircle\" data-key=\"(.*)\" class=\"oneline \">"
                    bc_list = re.findall(pa_bc, res_bc.text)
                    self._write_bc(bc_list)
                    bc_list = self._read_bc()  # 先爬取各区的商圈，最终以各区商圈来爬数据，如果按区爬，每区最多只能获得2000条数据

                    if len(bc_list) > 0:
                        for bc_name in bc_list:
                            idx = 0
                            has_more = 1
                            while has_more:
                                try:
                                    url = 'https://app.api.lianjia.com/Rentplat/v1/house/list?city_id={}&condition={}' \
                                          '/rt{}&limit=30&offset={}&request_ts={}&scene=list'.format(info[0],
                                                                                                     bc_name,
                                                                                                     type_code,
                                                                                                     idx*30,
                                                                                                     int(time.time()))
                                    res = requests.get(url=url, timeout=10,headers=self.headr)
                                    print('成功爬取{}市{}-{}的{}第{}页数据！'.format(city, dist, bc_name, ty, idx+1))
                                    json=res.json()
                                    datas = json['data']['list']
                                    for item in datas:
                                        code = item['house_code']
                                        # district_name=item['district_name']
                                        bizcircle_name = item['bizcircle_name']

                                        sql=f"insert into codes values ('{code}','{city}','{dist}','{bizcircle_name}')"
                                        try:
                                            cursor.execute(sql)
                                            db.commit()
                                        except:
                                            print("error")
                                    total = res.json()['data']['total']
                                    idx += 1
                                    if total/30 <= idx:
                                        has_more = 0
                                    time.sleep(2*random.random()+3)
                                except:
                                    print('链接访问不成功，正在重试！')
                time.sleep(8)

    @staticmethod
    def _write_bc(bc_list):
        """
        把爬取的商圈写入txt，为了整个爬取过程更加可控
        :param bc_list: 商圈list
        :return: None
        """
        with open('bc_list.txt', 'w') as f:
            for bc in bc_list:
                f.write(bc+'\n')

    @staticmethod
    def _read_bc():
        """
        读入商圈
        :return: None
        """
        with open('bc_list.txt', 'r') as f:
            return [bc.strip() for bc in f.readlines()]


if __name__ == '__main__':
    rent = Rent()
    rent.get_data()