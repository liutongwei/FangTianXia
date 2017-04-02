# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 23:12:06 2017

@author: Tongwei
"""

import json  
import urllib2 
import math 
  
class Distance:
    def __init__(self, target_, comp_, region_content_):
        self.target = target_
        self.comp = comp_
        self.region_content = region_content_
    
    def cal_distances(self, target, comparable):        
        distance = math.sqrt((target['lat'] - comparable['lat']) ** 2 + (target['lng'] - comparable['lng']) ** 2) * 100
        return distance
    
    def get_coordinates(self, query_content, region_content): 
        url_pri = 'http://api.map.baidu.com/place/v2/suggestion?query='
        region ='&region='
        city_limit ='&city_limit=false'
        output = '&output=json&&ak='    
        ak = 'XXX' #token for Baidu Map API 
        url = url_pri + query_content + region + region_content + city_limit + output + ak 
        temp = urllib2.urlopen(url) 
        hjson = json.loads(temp.read())
        if hjson['result']:
            temp = hjson['result'][0]['location']
            loc_sum = eval(json.dumps(temp))
        elif '(' in query_content:
            url = url_pri + query_content.split('(')[0] + region + region_content + city_limit + output + ak
            temp = urllib2.urlopen(url) 
            hjson = json.loads(temp.read())
            if hjson['result']:
                temp = hjson['result'][0]['location']
                loc_sum = eval(json.dumps(temp))
            else: loc_sum = 'string'
        else: loc_sum = 'string'
        return loc_sum
    
    def main(self):
        target_coor = self.get_coordinates(self.target, self.region_content)
        comp_coor = self.get_coordinates(self.comp, self.region_content)
        if comp_coor != 'string':            
            distance = self.cal_distances(target_coor, comp_coor)
        else: distance = 'Sorry, the place could not be found.'
        return distance

#if __name__ == "__main__":
#    target = '宜兴市徐舍镇'
#    comp = '宜兴市新建镇路庄村(新宜金公路东侧)'
#    region_content = '江苏'
#    distance = Distance(target, comp, region_content).main()
#    print distance