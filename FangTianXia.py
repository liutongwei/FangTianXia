#coding: utf-8
"""
Created on Thu Mar 23 23:45:36 2017

@author: Tongwei
"""

import requests
from lxml import etree
import sys
import BaiduAPI
import xlwings as xw
import pandas as pd

stdi,stdo,stde = sys.stdin,sys.stdout,sys.stderr
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdin,sys.stdout,sys.stderr = stdi,stdo,stde

class FangTianXia: 
    def __init__(self, target_city, target_district, target_county, target_location, target_category):
        self.target_city = target_city
        self.target_district = target_district
        self.target_county = target_county
        self.target_location = target_location
        self.target_category = target_category
        self.category = ['不限', '住宅用地', '商业/办公用地', '工业用地', '其它用地']
        self.loginUrl = 'https://passport.fang.com/login.api'        
        self.postdata = {
            'Uid' : 'XYZ',
            'Pwd' : 'XYZ',
            'Service' : 'soufun-passport-web',
            'AutoLogin' : '1'
         }
        self.loginHeaders =  {
            'Host' : 'passport.fang.com',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
            'Referer' : 'https://passport.fang.com/Default/Login',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection' : 'Keep-Alive'
        }
        self.Headers =  {
            'Host' : 'land.fang.com',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
            'Connection' : 'Keep-Alive'
        }
 
    def login(self):
        url_check = 'http://land.fang.com/market/110100________1_0_1.html'        
        try:
            result = requests.get(url_check, headers = self.Headers, timeout = 10).text
            a = etree.HTML(result).xpath(r'//*[@id="divUser"]/a[2]/text()')
            if a[0] == u'退出':
                print u'已登录'
            else:
#                request = urllib2.Request(url = self.loginUrl, data = self.postdata, headers = self.loginHeaders)
#                result = self.opener.open(request)
#                self.cookies.save(ignore_discard = True, ignore_expires = True)
                result = requests.Session()
                result.post(self.loginUrl, data = self.postdata, headers = self.loginHeaders)
                result.get(url_check, headers = self.Headers, timeout = 10)                
#            with open('E:/ErnstYoung/Fangtianxia_Content.txt', 'w') as f:
#                f.write(result.text)
        except requests.exceptions.RequestException as e:
            raise e('Failed due to: {0}'.format(e))          
        return result
    
    def get_sumurl(self):
        url_search = 'http://land.fang.com/market/110100________1_0_1.html'
        try:
            request = self.login()
            result = request.get(url_search, headers = self.Headers, timeout = 10).text
            city_url = etree.HTML(result).xpath(r'//*[@id="landlb_B04_04"]/span[2]/a')
            city_corr = dict([[each_city.text, each_city.attrib.values()[0]] for each_city in city_url])
            if city_corr.has_key(self.target_city):
                url_need = 'http://land.fang.com' + city_corr.get(self.target_city)
        except requests.exceptions.RequestException:
            print 'Search City Failed.'
        try:
            result = request.get(url_need, headers = self.Headers, timeout = 10).text
            district_url = etree.HTML(result).xpath(r'//*[@id="landlb_B04_04"]/span/a')
            district_corr = dict([[each_district.text, each_district.attrib.values()[0]] for each_district in district_url])
            if district_corr.has_key(self.target_district):
                url_need = 'http://land.fang.com' + district_corr.get(self.target_district)
        except requests.exceptions.RequestException:
            print 'Search District Failed.'
        if self.target_county != '':
            try:
                result = request.get(url_need, headers = self.Headers, timeout = 10).text
                county_url = etree.HTML(result).xpath(r'//*[@id="landlb_B04_04"]/span/a')
                county_corr = dict([[each_county.text, each_county.attrib.values()[0]] for each_county in county_url])
                if county_corr.has_key(self.target_county):
                    url_need = 'http://land.fang.com' + county_corr.get(self.target_county)
            except requests.exceptions.RequestException:
                print 'Search County Failed.'
        if self.target_category in self.category:
            i = self.category.index(self.target_category) + 1
            try:
                result = request.get(url_need, headers = self.Headers, timeout = 10).text
                category_url = etree.HTML(result).xpath(r'//*[@id="landlb_B04_06"]/a[' + str(i) + ']')[0].attrib.values()[0]
                url_need = 'http://land.fang.com' + category_url
            except requests.exceptions.RequestException:
                print 'Search Caetgory Failed.'        
        result = request.get(url_need, headers = self.Headers, timeout = 10).text
        page_url = etree.HTML(result).xpath(r'//*[@id="divAspNetPager"]/a')
        for i in range(len(page_url) - 1, 0, -1):
            if page_url[i].text == u'尾页':
                max_pagenum = page_url[i-1].text        
        url_need = ['http://land.fang.com' + page_url[0].attrib.values()[0].split('.')[0][:-1] + str(page_num) + '.html' for page_num in range(1, int(max_pagenum)+1)]
        corr_url = []
        try:
            for i in range(len(url_need)):
                result = request.get(url_need[i], headers = self.Headers, timeout = 10).text
                location_url = etree.HTML(result).xpath(r'//*[@id="landlb_B04_22"]/dd/div[1]/h3/a')
                location_corr = ['http://land.fang.com' + each_location.attrib.values()[2] for each_location in location_url]
                corr_url.extend(location_corr)
            return corr_url
        except etree.XMLSyntaxError as e:
            print 'Sorry.' + str(e)
            return corr_url
    
    def getPage(self, url_list):
        request = self.login()
        data = []
        for i in range(len(url_list)):
            url_search = url_list[i]
            result = request.get(url_search, headers = self.Headers, timeout = 10).text            
            Name = etree.HTML(result).xpath(r'//*[@id="printData1"]/div[1]/text()')[0]
            Area = etree.HTML(result).xpath(r'//*[@id="printData1"]/div[5]/table/tbody/tr[2]/td[1]/em')[0].text
            Deal_Status = etree.HTML(result).xpath(r'//*[@id="printData1"]/div[5]/div[3]/table/tbody/tr[1]/td[1]/text()')[0]
            Deal_date = etree.HTML(result).xpath(r'//*[@id="printData1"]/div[5]/div[3]/table/tbody/tr[3]/td[1]/text()')[0]
            Deal_amount = etree.HTML(result).xpath(r'//*[@id="printData1"]/div[5]/div[3]/table/tbody/tr[4]/td[2]/text()')[0]
            Deal_amount = Deal_amount[:-2]
            Distance = 0
            data.append([Name, Distance, Area, Deal_Status, Deal_date, Deal_amount, url_search])
        return data
        
    def main(self):
        all_url = self.get_sumurl()
        all_data = self.getPage(all_url[:7])
        return all_data

def write_toexcel(data):
    app = xw.App(visible = False, add_book = False)
    wb = app.books.add()
    df = pd.DataFrame(data, columns=['Name', 'Distance/km', 'Area/m2', 'Deal_Status', 'Deal_date', 'Deal_amount/万元', 'url_search'])
    wb.sheets['sheet1'].range('A1').value = df
    wb.sheets['sheet1'].range('A1').options(pd.DataFrame, expand='table').value
    wb.save(r'comp_data.xlsx')
    wb.close()
    app.quit()

if __name__ == '__main__':
    target_city = u'江苏'
    target_district = u'无锡'
    target_county = u'宜兴市'
    target_location = u'徐舍镇'
    target_category = '商业/办公用地'
    target_search = target_city + target_district + target_county + target_location
    fangtianxia = FangTianXia(target_city, target_district, target_county, target_location, target_category)
    a = fangtianxia.main()
    for each in a:
        each[1] = BaiduAPI.Distance(target_search, each[0], target_city).main()
        write_toexcel(a)