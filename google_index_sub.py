from init import *

logger.add("../../log/google_index.log", rotation="1 MB", retention="1 day")

while True:
    try:
        facebook_test_accounts = requests.get(DOMAIN+"project/facebook_test_accounts")
        facebook_test_accounts = facebook_test_accounts.content.decode()
        facebook_test_accounts = json.loads(facebook_test_accounts)

        fb_obj = Facebook()
        fb_obj.set_cookie(facebook_test_accounts['c_user'],facebook_test_accounts['xs'])

        response = requests.get(DOMAIN+"DomainData/get_domains_by_google_index_status")
        response = response.content.decode()
        response = json.loads(response)
        if response:
            pool = ThreadPool(40)
            results = []
            for domain_data in response:
                domain_id = domain_data['domain_id']
                domain_name = domain_data['domain_name']
                results.append(pool.apply_async(fb_obj.check_google_index, args=(domain_id,domain_name,)))
            pool.close()
            pool.join()
            results = [r.get() for r in results]

            logger.info(results)
            ts = time.time() 
            file_name = str(round(ts))

            result_final = ""
            for result in results:
                if result != False:
                    result_final += json.dumps(result) + ","

            result_final = result_final.strip(",")
            result_final = "["+result_final+"]"

            f = open("google_index/"+file_name+".json", "a")
            f.write(result_final)
            f.close()

            for i in range(0,3):
                files = {'google_index_file': open("google_index/"+file_name+".json",'rb')}
                response = requests.post(DOMAIN+"Project/upload_google_index_file", files=files)
                logger.info(response.content.decode())
                
                if response.status_code == 200:
                    break
                time.sleep(5)
        else:
            logger.info("wait 1 min")
            time.sleep(60)

    except Exception as ex:
        logger.error(ex)


