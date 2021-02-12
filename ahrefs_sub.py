from init import *
logger.add("../../log/ahrefs.log", rotation="1 MB", retention="1 day")

while True:
    try:
        ahrefs_response = requests.get(DOMAIN+"Ahrefs/get_cookie_json")
        ahrefs_response = ahrefs_response.content.decode()
        ahrefs_response = json.loads(ahrefs_response)

        ahrefs_obj = Ahrefs(ahrefs_response['xsrf_token'],ahrefs_response['bssessid'],ahrefs_response['useragent'])
        cookie_check = ahrefs_obj.check_cookie()
        if not cookie_check:
            logger.error("Cookie Expired")
            ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
            headers = { 'Content-Type': 'application/json' }
            data = '{"chat_id": "474359564", "text": "Cookie Expired - '+str(ip)+'", "disable_notification": false}'
            response = requests.post('https://api.telegram.org/bot1669164397:AAFlF2QuW5ng7OlTNvKVGRDYPIpFrkTpMW0/sendMessage', headers=headers, data=data)
            sys.exit()

        response = requests.get(DOMAIN+"DomainData/get_domains_by_ahrefs_highest_status")
        response = response.content.decode()
        response = json.loads(response)
        if response:
            pool = ThreadPool(40)
            results = []
            for domain_data in response:
                domain_id = domain_data['domain_id']
                domain_name = domain_data['domain_name']
                results.append(pool.apply_async(ahrefs_obj.get_domain_compare_metrics, args=(domain_id,domain_name,)))
            pool.close()
            pool.join()
            results = [r.get() for r in results]

            ts = time.time() 
            file_name = str(round(ts))

            result_final = ""
            for result in results:
                if result != False:
                    result_final += json.dumps(result) + ","

            result_final = result_final.strip(",")
            result_final = "["+result_final+"]"

            f = open("ahrefs/"+file_name+".json", "a")
            f.write(result_final)
            f.close()

            for i in range(0,3):
                files = {'ahrefs_file': open("ahrefs/"+file_name+".json",'rb')}
                response = requests.post(DOMAIN+"Ahrefs/upload_file", files=files)
                logger.info(response.content.decode())
                
                if response.status_code == 200:
                    break
                time.sleep(5)
        else:
            logger.info("wait 1 min")
            time.sleep(60)

    except Exception as ex:
        logger.error(ex)
    


