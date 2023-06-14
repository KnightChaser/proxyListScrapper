import requests
import random
import datetime
import multiprocessing
import asyncio

class UA_string:

    UA_string_list =  [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.41",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.37",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15"
        ]


class geo_node_proxy_scrapper:

    def __init__(self, qty):

        now     = datetime.datetime.now()
        year    = now.year
        month   = now.month
        day     = now.day
        hour    = now.hour
        minute  = now.minute
        second  = now.second

        self.qty        = qty
        self.filepath   = f"{year}_{month}_{day}_{hour}_{minute}_{second}_geoNodeProxyIPList.txt"
    # def register_ip_bunch(self, data):
    #     self.all_ip.append(data)
    #     print("hit")
    #     print(self.all_ip)

    # single workload
    def get_data(self, page, return_dict):
        print(f"[INF] Getting page {page}")
        request_url  = f"https://proxylist.geonode.com/api/proxy-list?limit=100&page={page}&sort_by=lastChecked&sort_type=desc&filterLastChecked=30&filterUpTime=90&speed=fast"
        headers      = { "User-Agent" : random.choice(UA_string.UA_string_list) }
        response     = requests.get(request_url, headers = headers)
        ip_list = []

        if response.status_code == 200:
            proxy_server_list_json = response.json()["data"]
            for _server in proxy_server_list_json:
                ip_address = _server["ip"]
                ip_list.append(ip_address)
                print(f"[INF] address {ip_address} gathered")
        else:
            print(f"[WRN] Failed to fetch data page {page}")

        return_dict[page] = ip_list

    # parallize scrapping by multiprocessing tool
    def get_data_multiprocessing(self):
        target_page   = int(self.qty / 100)
        work_load     = [x for x in range(1, target_page + 1)]
        jobs          = []

        manager       = multiprocessing.Manager()
        proxy_list    = manager.dict()

        # Run
        for _target in work_load:
            proxy_scrapper = multiprocessing.Process(target = self.get_data, args = (_target, proxy_list))
            jobs.append(proxy_scrapper)
            proxy_scrapper.start()

        # Finish
        for process in jobs:
            process.join()

        print(proxy_list.values())
        



    
if __name__ == "__main__":
    gnproxy = geo_node_proxy_scrapper(200)
    gnproxy.get_data_multiprocessing()
