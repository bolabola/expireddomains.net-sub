#!/usr/local/bin/python3
import re
import csv
import sys
import json
import requests
from lxml import html
from loguru import logger
from bs4 import BeautifulSoup
# from headings import Headings

class Ahrefs:
    def __init__(self,XSRF_TOKEN,BSSESSID,USERAGENT):
        self.XSRF_TOKEN = XSRF_TOKEN
        self.BSSESSID = BSSESSID
        self.USERAGENT = USERAGENT

    def check_cookie(self):
        headers = {
            'authority': 'ahrefs.com',
            'user-agent': self.USERAGENT,
            'content-type': 'application/json',
            'cookie': 'BSSESSID='+self.BSSESSID+';',
        }

        data = '{"select":"cost","mode":"subdomains","url":"fitnessbfdeals.com"}'
        response = requests.post('https://ahrefs.com/v3/api-adaptor/seGetOrganicChartDataPhpCompat?pretty=1', headers=headers, data=data)
        flag = False
        try:
            response_data = json.loads(response.content.decode())
            response_data = response_data[0]
            if response_data != "Error":
                flag = True
        except Exception as ex:
            flag = False

        return flag    

    def get_highest_traffic(self,domain_name):
        headers = {
            'authority': 'ahrefs.com',
            'user-agent': self.USERAGENT,
            'content-type': 'application/json',
            'cookie': 'BSSESSID='+self.BSSESSID+';',
        }

        data = '{"select":"traffic","mode":"subdomains","url":"'+domain_name+'"}'
        response = requests.post('https://ahrefs.com/v3/api-adaptor/seGetOrganicChartDataPhpCompat?pretty=1', headers=headers, data=data)
        highest_traffic = 0
        highest_traffic_date = "-"
        latest_traffic = 0
        latest_traffic_date = "-"
        try:
            response_data = json.loads(response.content.decode())
            response_data = response_data[1][1]
            for metrics in response_data :
                if(metrics['traffic'] > highest_traffic):
                    highest_traffic = metrics['traffic']
                    highest_traffic_date = metrics['date']
                latest_traffic = metrics['traffic']
                latest_traffic_date = metrics['date']
        except Exception as ex:
            highest_traffic = -1
            latest_traffic = -1
            logger.error(ex)

        highest_traffic = round(highest_traffic)
        latest_traffic = round(latest_traffic)
        return highest_traffic,highest_traffic_date,latest_traffic,latest_traffic_date

    def get_highest_keywords(self,domain_name):
        headers = {
            'authority': 'ahrefs.com',
            'user-agent': self.USERAGENT,
            'content-type': 'application/json',
            'cookie': 'BSSESSID='+self.BSSESSID+';',
        }

        data = '{"select":"position","mode":"subdomains","url":"'+domain_name+'"}'
        response = requests.post('https://ahrefs.com/v3/api-adaptor/seGetOrganicChartDataPhpCompat?pretty=1', headers=headers, data=data)
        highest_keywords = 0
        highest_keywords_date = "-"
        latest_keywords = 0
        latest_keywords_date = "-"
        try:
            response_data = json.loads(response.content.decode())
            response_data = response_data[1][1]
            for metrics in response_data :
                if(metrics['position'] > highest_keywords):
                    highest_keywords = metrics['position']
                    highest_keywords_date = metrics['date']
                latest_keywords = metrics['position']
                latest_keywords_date = metrics['date']
        except Exception as ex:
            highest_keywords = -1
            latest_keywords = -1
            logger.error(ex)

        highest_keywords = round(highest_keywords)
        latest_keywords = round(latest_keywords)
        return highest_keywords,highest_keywords_date,latest_keywords,latest_keywords_date

    def get_highest_cost(self,domain_name):
        headers = {
            'authority': 'ahrefs.com',
            'user-agent': self.USERAGENT,
            'content-type': 'application/json',
            'cookie': 'BSSESSID='+self.BSSESSID+';',
        }

        data = '{"select":"cost","mode":"subdomains","url":"'+domain_name+'"}'
        response = requests.post('https://ahrefs.com/v3/api-adaptor/seGetOrganicChartDataPhpCompat?pretty=1', headers=headers, data=data)
        highest_cost = 0
        highest_cost_date = "-"
        latest_cost = 0
        latest_cost_date = "-"
        try:
            response_data = json.loads(response.content.decode())
            response_data = response_data[1][1]
            for metrics in response_data :
                if(metrics['cost'] > highest_cost):
                    highest_cost = metrics['cost']
                    highest_cost_date = metrics['date']
                latest_cost = metrics['cost']
                latest_cost_date = metrics['date']
        except Exception as ex:
            highest_cost = -1
            latest_cost = -1
            logger.error(ex)

        highest_cost = round(highest_cost)
        latest_cost = round(latest_cost)
        return highest_cost,highest_cost_date,latest_cost,latest_cost_date

    def get_domain_compare_metrics(self,domain_id,domain_name):
        try:
            headers = {
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': self.USERAGENT,
                'cookie': 'BSSESSID='+self.BSSESSID+';',
            }

            response = requests.get('https://ahrefs.com/domain-comparison?targets[]='+domain_name.strip(), headers=headers)
            soup = BeautifulSoup(response.content.decode(), 'html.parser')
            title = soup.find("title").text
            if "Domain Comparison  - Ahrefs" != title:
                logger.error("Cookie Expired")
                sys.exit()

            [x.extract() for x in soup.findAll('p')]
            tbody = soup.find("tbody")
            tr = tbody.find_all("tr")
            nonBreakSpace = u'\xa0'
            domain_data = {}
            domain_data.update({"domain_id":domain_id})
            domain_data.update({"domain_name":domain_name})
            for _tr in tr:
                td_all = _tr.find_all("td")
                heading = (td_all[0].text).replace(nonBreakSpace, ' ').strip()
                value = (td_all[1].text).replace(nonBreakSpace, ' ').strip()
                if heading == "Form":
                    break

                value = value.replace("-","")
                value = value.replace(",","")
                if len(value.strip()) == 0:
                    value = 0

                heading = heading.lower()
                heading = heading.replace(" ","_")
                heading = heading.replace(".","")
                domain_data.update({heading:value})

            highest_traffic,highest_traffic_date,latest_traffic,latest_traffic_date = self.get_highest_traffic(domain_name)
            domain_data.update({"highest_traffic":highest_traffic})
            domain_data.update({"highest_traffic_date":highest_traffic_date})
            domain_data.update({"latest_traffic":latest_traffic})
            domain_data.update({"latest_traffic_date":latest_traffic_date})

            highest_keywords,highest_keywords_date,latest_keywords,latest_keywords_date = self.get_highest_keywords(domain_name)
            domain_data.update({"highest_keywords":highest_keywords})
            domain_data.update({"highest_keywords_date":highest_keywords_date})
            domain_data.update({"latest_keywords":latest_keywords})
            domain_data.update({"latest_keywords_date":latest_keywords_date})

            highest_cost,highest_cost_date,latest_cost,latest_cost_date = self.get_highest_cost(domain_name)
            domain_data.update({"highest_cost":highest_cost})
            domain_data.update({"highest_cost_date":highest_cost_date})
            domain_data.update({"latest_cost":latest_cost})
            domain_data.update({"latest_cost_date":latest_cost_date})

            logger.debug("ahrefs done - " + domain_name)
            return domain_data
        except Exception as ex:
            logger.error(ex)
            logger.error("Cookie Error")
            return False
            