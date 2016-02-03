import time
import pymongo
import requests
from bs4 import BeautifulSoup

url_sample = 'http://bj.xiaozhu.com/fangzi/844400738.html'

client = pymongo.MongoClient('localhost',27017)
xiaozhu_bj = client['xiaozhu_bj']
sheet_houseInfo = xiaozhu_bj['sheet_houseInfo']


def get_link_list(pages_upper_limit):
    link_list = []
    page = 1
    while page <= pages_upper_limit:
        url = 'http://bj.xiaozhu.com/search-duanzufang-p{}-0/'.format(str(page))
        wb_data = requests.get(url)
        soup = BeautifulSoup(wb_data.text,'lxml')
        links = soup.select('div#page_list > ul > li > a')
        for link in links:
            link_list.append(link.get('href'))
        page += 1
    return link_list


def get_house_info(url):
    # house_info = []
    time.sleep(1) 
    wb_data = requests.get(url)
    soup = BeautifulSoup(wb_data.text,'lxml')
    titles = soup.select('div.pho_info > h4 > em')
    addresses = soup.select('div.pho_info > p')
    imgs = soup.select('img#curBigImage')
    prices = soup.select('div.day_l > span')

    host_names = soup.select('a.lorder_name')
    host_genders = soup.select('div.w_240 > h6 > span')
    host_avatars = soup.select('div.member_pic > a > img')

    # print(titles,addresses,imgs,prices,host_names,host_genders,host_avatars,sep='\n------------------------------------\n')
    for title,address,img,price,host_name,host_gender,host_avatar in zip(titles,addresses,imgs,prices,host_names,host_genders,host_avatars):
        data = {
            '标题':title.get_text(),
            '地址':address.get('title'),
            '图片':img.get('src'),
            '每晚':float(price.get_text()),
            '房主姓名':host_name.get('title'),
            '房主头像':host_avatar.get('src'),
            '房主性别':str(host_gender.get('class'))
        }
        if data['房主性别'] == "['member_girl_ico']":
            data['房主性别']='女'
        else:
            data['房主性别']='男'
        sheet_houseInfo.insert_one(data)
    #     house_info.append(data)
    # print(house_info)


def insert_info(pages_upper_limit):
    for url in get_link_list(pages_upper_limit):
        get_house_info(url)


insert_info(3)

for item in sheet_houseInfo.find({'每晚':{'$gt':300}}):
    print(item)

