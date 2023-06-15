import requests
import random
import datetime
import multiprocessing
import os

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
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
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
        self.folder     = "./iplist"
        self.filepath   = f"{self.folder}/{year}_{month}_{day}_{hour}_{minute}_{second}_geoNodeProxyIPList.txt"

    # single workload
    def get_data(self, page, return_dict, proxy_number, run):
        print(f"[INF] Getting page {page}")
        request_url  = f"https://proxylist.geonode.com/api/proxy-list?limit=500&page={page}&sort_by=lastChecked&sort_type=desc&filterLastChecked=30&filterUpTime=90&speed=fast"
        headers      = { "User-Agent" : random.choice(UA_string.UA_string_list) }
        response     = requests.get(request_url, headers = headers)
        ip_list = []

        if response.status_code == 200:
            proxy_server_list_json = response.json()["data"]
            if proxy_server_list_json != []:
                for _server in proxy_server_list_json:
                    ip_address = _server["ip"]
                    ip_list.append(ip_address)
                    proxy_number.value += 1
                    print(f"[INF] (Gathered : {proxy_number.value}) address {ip_address} gathered")
            else:
                print(f"[WRN] (Gathered : {proxy_number.value}) There is no more available proxy server.")
                run.clear()
                return
        else:
            print(f"[WRN] Failed to fetch data page {page}, status code was {response.status_code}")

        return_dict[page] = ip_list

    # parallize scrapping by multiprocessing tool
    def get_data_multiprocessing(self):
        target_page   = int(self.qty / 500)
        work_load     = [x for x in range(1, target_page + 1)]
        jobs          = []

        manager       = multiprocessing.Manager()
        proxy_list    = manager.dict()
        proxy_number  = manager.Value("int", 0)
        run           = manager.Event()

        # Run subprocesses
        for _target in work_load:
            proxy_scrapper = multiprocessing.Process(target = self.get_data, args = (_target, proxy_list, proxy_number, run))
            jobs.append(proxy_scrapper)
            proxy_scrapper.start()

        # Finish subproceses
        for process in jobs:
            process.join()

        # Export extracted IP address to the given file
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

        with open(self.filepath, 'w') as file:
            for _chunk in proxy_list.values():
                for _ip in _chunk:
                    file.write(f"{_ip}\n")

        print(f"IP list exported : {self.filepath}")

    
if __name__ == "__main__":
    gnproxy = geo_node_proxy_scrapper(500)
    gnproxy.get_data_multiprocessing()
