import sys
import requests
from lxml import html
from loguru import logger
from bs4 import BeautifulSoup, Comment
from init import *

logger.add("../../log/expireddomains.log", rotation="1 MB", retention="1 day")

def get_total_pages_count(facr_min,facr_max,fminhost,fmaxhost):
    try:
        params = (
            ('start', '0'),
            ('flast24', '1'),
            ('ftlds/[/]', '2'),
            ('flimit', '200'),
            ('facr', str(facr_min)),
            ('facrm', str(facr_max)),
            ('fminhost',str(fminhost)),
            ('fmaxhost',str(fmaxhost)),
            ('q', '.com'),
            ('fwhois', '22'),
        )

        response = requests.get('https://member.expireddomains.net/domain-name-search/', headers=headers, params=params)
        soup = BeautifulSoup(response.content.decode(),"lxml")

        total_pages = soup.find("div", class_="pageinfo")
        total_pages = int(total_pages.text.replace("Page 1 of ","").replace(",","").replace("\n","").replace("\t","").replace("|","").strip())

        logger.debug("total pages : " + str(total_pages) + "  " + str(facr_min) + " - " + str(facr_max) + " - / - " + str(fminhost) + " - " + str(fmaxhost))
    except Exception as ex:
        logger.error(ex)
        total_pages = get_total_pages_count(facr_min,facr_max,fminhost,fmaxhost)

    return total_pages

def get_domains(page_number,facr_min,facr_max,fminhost,fmaxhost):
    try:
        time.sleep(3)
        params = (
            ('start', str(page_number*200)),
            ('flast24', '1'),
            ('ftlds/[/]', '2'),
            ('flimit', '200'),
            ('facr', str(facr_min)),
            ('facrm', str(facr_max)),
            ('fminhost',str(fminhost)),
            ('fmaxhost',str(fmaxhost)),
            ('q', '.com'),
            ('fwhois', '22'),
        )

        response = requests.get('https://member.expireddomains.net/domain-name-search/', headers=headers, params=params)
        soup = BeautifulSoup(response.content.decode(),"lxml")

        page = soup.find("div", class_="pageinfo")
        logger.info(page.text.replace("\n","").replace("\t","").strip() + "  " + str(facr_min) + " - " + str(facr_max) + " -/ " + str(fminhost) + " - " + str(fmaxhost))

        domain_list = []
        td_data = soup.find_all("td",class_="field_domain")
        for td in td_data:
            domain_name = td.find("a").text
            domain_list.append(domain_name)
            # logger.info(domain_name)
    except Exception as ex:
        logger.error(ex)
        time.sleep(30)
        domain_list = get_domains(page_number,facr_min,facr_max,fminhost,fmaxhost)
    return domain_list

def login(username,password,ExpiredDomainssessid):
    headers = {
        'authority': 'member.expireddomains.net',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'origin': 'null',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en;q=0.9',
        'cookie': 'ExpiredDomainssessid='+ExpiredDomainssessid,
    }

    data = {
        'login': username,
        'password': password,
        'rememberme': '0',
        'redirect_to_url': '/begin'
    }

    response = requests.post('https://member.expireddomains.net/login/', headers=headers, data=data)
    logger.info(response.headers)

login(USERNAME,PASSWORD,ExpiredDomainssessid)

if MAIN_ACCOUNT:
    logger.info("Main Account : " + str(ACCOUNT_NO))
else:
    logger.info("Account : " + str(ACCOUNT_NO))

headers = {
    'authority': 'member.expireddomains.net',
    'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://member.expireddomains.net/domain-name-search/?q=.com',
    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6,gu;q=0.5,fr;q=0.4',
    'cookie': 'ExpiredDomainssessid='+ExpiredDomainssessid,
}

response = requests.get('https://member.expireddomains.net/domains/combinedexpired/', headers=headers)
soup = BeautifulSoup(response.content.decode(),"lxml")
title = soup.find("title").text.strip()
if title == "Login":
    logger.info("Login required")
    headers = { 'Content-Type': 'application/json' }
    data = '{"chat_id": "474359564", "text": "Expired - '+expireddomains_accounts['username']+'", "disable_notification": false}'
    response = requests.post('https://api.telegram.org/bot1514790648:AAGEav8ADxAGbHK1ozVAkMBQsd6qPfSKSq0/sendMessage', headers=headers, data=data)
else:
    if MAIN_ACCOUNT:
        filter_data = [
            {"facr_min":1,"facr_max":1,"fminhost":1,"fmaxhost":100},
            {"facr_min":2,"facr_max":2,"fminhost":1,"fmaxhost":100},
            {"facr_min":3,"facr_max":3,"fminhost":1,"fmaxhost":100},
            {"facr_min":4,"facr_max":4,"fminhost":1,"fmaxhost":100},
            {"facr_min":5,"facr_max":7,"fminhost":1,"fmaxhost":100},
            {"facr_min":8,"facr_max":10,"fminhost":1,"fmaxhost":100},
            {"facr_min":11,"facr_max":13,"fminhost":1,"fmaxhost":100},
            {"facr_min":14,"facr_max":15,"fminhost":1,"fmaxhost":100},
            {"facr_min":16,"facr_max":18,"fminhost":1,"fmaxhost":100},
            {"facr_min":19,"facr_max":20,"fminhost":1,"fmaxhost":100},
            {"facr_min":21,"facr_max":25,"fminhost":1,"fmaxhost":100},
            {"facr_min":26,"facr_max":40,"fminhost":1,"fmaxhost":100},
            {"facr_min":41,"facr_max":70,"fminhost":1,"fmaxhost":100},
            {"facr_min":71,"facr_max":100,"fminhost":1,"fmaxhost":100},
            {"facr_min":100,"facr_max":100000,"fminhost":1,"fmaxhost":100},
            {"facr_min":0,"facr_max":0,"fminhost":1,"fmaxhost":5},                
            {"facr_min":0,"facr_max":0,"fminhost":6,"fmaxhost":7},
            {"facr_min":0,"facr_max":0,"fminhost":8,"fmaxhost":9},
            {"facr_min":0,"facr_max":0,"fminhost":10,"fmaxhost":11},
            {"facr_min":0,"facr_max":0,"fminhost":12,"fmaxhost":13},
            {"facr_min":0,"facr_max":0,"fminhost":14,"fmaxhost":15},
            {"facr_min":0,"facr_max":0,"fminhost":16,"fmaxhost":17},
            {"facr_min":0,"facr_max":0,"fminhost":18,"fmaxhost":20},
            {"facr_min":0,"facr_max":0,"fminhost":20,"fmaxhost":1000}
        ]
    else:
        if ACCOUNT_NO == 1:
            filter_data = [
                {"facr_min":1,"facr_max":1,"fminhost":1,"fmaxhost":100},
                {"facr_min":2,"facr_max":2,"fminhost":1,"fmaxhost":100},
                {"facr_min":3,"facr_max":3,"fminhost":1,"fmaxhost":100},
                {"facr_min":4,"facr_max":4,"fminhost":1,"fmaxhost":100},
                {"facr_min":5,"facr_max":7,"fminhost":1,"fmaxhost":100},
                {"facr_min":8,"facr_max":10,"fminhost":1,"fmaxhost":100},
                {"facr_min":11,"facr_max":13,"fminhost":1,"fmaxhost":100},
                {"facr_min":14,"facr_max":15,"fminhost":1,"fmaxhost":100}
            ]
        elif ACCOUNT_NO == 2:
            filter_data = [
                {"facr_min":16,"facr_max":18,"fminhost":1,"fmaxhost":100},
                {"facr_min":19,"facr_max":20,"fminhost":1,"fmaxhost":100},
                {"facr_min":21,"facr_max":25,"fminhost":1,"fmaxhost":100},
                {"facr_min":26,"facr_max":40,"fminhost":1,"fmaxhost":100},
                {"facr_min":41,"facr_max":70,"fminhost":1,"fmaxhost":100},
                {"facr_min":71,"facr_max":100,"fminhost":1,"fmaxhost":100},
                {"facr_min":100,"facr_max":100000,"fminhost":1,"fmaxhost":100},
                {"facr_min":0,"facr_max":0,"fminhost":1,"fmaxhost":5}
            ]        
        elif ACCOUNT_NO == 3:
            filter_data = [
                {"facr_min":0,"facr_max":0,"fminhost":6,"fmaxhost":7},
                {"facr_min":0,"facr_max":0,"fminhost":8,"fmaxhost":9},
                {"facr_min":0,"facr_max":0,"fminhost":10,"fmaxhost":11},
                {"facr_min":0,"facr_max":0,"fminhost":12,"fmaxhost":13},
                {"facr_min":0,"facr_max":0,"fminhost":14,"fmaxhost":15},
                {"facr_min":0,"facr_max":0,"fminhost":16,"fmaxhost":17},
                {"facr_min":0,"facr_max":0,"fminhost":18,"fmaxhost":20},
                {"facr_min":0,"facr_max":0,"fminhost":20,"fmaxhost":1000}
            ]
        else:
            filter_data = []

    for data in filter_data:
        total_pages = get_total_pages_count(data['facr_min'],data['facr_max'],data['fminhost'],data['fmaxhost'])
        for page_number in range(0,total_pages):
            domain_list = get_domains(page_number,data['facr_min'],data['facr_max'],data['fminhost'],data['fmaxhost'])
            domain_list = ",".join(domain_list)
            data_domain = {"domain_list":domain_list}
            response = requests.post(DOMAIN+"project/expireddomains_net_data",data=data_domain)
            # logger.info(domain_list)
