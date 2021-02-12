import os
import re
import sys
import json
import time
import random
import requests
from loguru import logger
try:
    from urllib.parse import quote_plus as url_encode
except ImportError:
    from urllib import quote_plus as url_encode

class Facebook:
    def __init__(self):
        self.COOKIE_FB = ""
        self.TRY = 4

    def set_cookie(self,c_user,xs):
        self.COOKIE_FB = "c_user="+str(c_user)+";xs="+str(xs)+";"

    def decode_html(self,fb_response):
        decoded = ['>', '<', '"', '&', '\'']
        encoded = ['&gt;', '&lt;', '&quot;', '&amp;', '&#039;']
        for e, d in zip(encoded, decoded):
            fb_response = fb_response.replace(e, d)
        for e, d in zip(encoded[::-1], decoded[::-1]):
            fb_response = fb_response.replace(e, d)
        return fb_response

    def crawler_data(self,link):
        self.get_cookie()
        ## Special Case ignore single quote in url##
        link = re.sub("""'([^']*)""","",link)

        ### Append https:// if link is started from //
        pattern_append_https = '^//([^"]*)'
        if re.search(pattern_append_https,link):
            link = "https:" + link

        self.TRY = self.TRY - 1
        if self.TRY < 0:
            return ""

        ####################################
        self.internal = []
        self.external = []
        try:
            encoded_link = url_encode(link)

            headers = {
                    'Host': 'developers.facebook.com',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'deflate',
                    'Connection': 'keep-alive',
                    'Cookie': self.COOKIE_FB,
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0',
                    'TE': 'Trailers'
            }
            fb_response = requests.get('https://developers.facebook.com/tools/debug/echo/?q=%s' % encoded_link, headers=headers)
            cleaned_response = self.decode_html(fb_response.text)
            if int(fb_response.status_code) != 200:
                logger.error(link)
                return self.crawler_data(link)
            if "<title>" in fb_response.text:
                logger.error(str(self.TRY) + " -- "+link)
                return self.crawler_data(link)

            return cleaned_response

        except Exception as ex:
            logger.error("Error : " + str(ex))
            return self.crawler_data(link)

    def check_google_index(self,domain_id,domain_name):
        try:
            url = "https://www.google.com/search?q=site:"+domain_name.strip()
            escaped = url_encode(url)
            headers = {
                'Host': 'developers.facebook.com',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'deflate',
                'Connection': 'keep-alive',
                'Cookie': self.COOKIE_FB,
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
                'TE': 'Trailers'
            }
            response = requests.get('https://developers.facebook.com/tools/debug/echo/?q=%s' % escaped, headers=headers)
            cleaned_response = self.decode_html(response.text)
            cleaned_response = cleaned_response.replace("\n","")

            status = -1
            if "Google Search" in cleaned_response:
                if "<h3" in cleaned_response:
                    status = 1
                else :
                    status = -1
            elif "Sorry, the link you followed may be broken, or the page may have been removed." in cleaned_response:
                status = 0
            elif "Our systems have detected unusual traffic from your computer network" in cleaned_response:
                status = 0
            elif "The document returned no data." in cleaned_response:
                status = 0
            else: 
                print("Error")
                f = open("temp.html", "w")
                f.write(cleaned_response)
                f.close()
                sys.exit()

            domain_data = {}
            domain_data.update({"domain_id":domain_id})
            domain_data.update({"domain_name":domain_name})
            domain_data.update({"google_index":status})
        except Exception as ex:
            return None
        return domain_data