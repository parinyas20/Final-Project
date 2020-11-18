import urllib.request
from bs4 import BeautifulSoup
import os
import pandas as pd
import numpy as np
import time
from multiprocessing.pool import ThreadPool

def extract_reports(argument_list):
    city_name, path, report_count, page_count = argument_list
#for city_name in city_list:
    location_mapping = {}
    print(f'\nExtracting reports of the city {city_name}')
    url_list = []
    page_num = 0
    root_path = path
    city_reports_path = os.path.join(root_path)
    if not os.path.exists(city_reports_path):
        os.makedirs(city_reports_path)

    while len(url_list) < report_count and page_num < page_count:
        page_num +=1
        url=f'https://timesofindia.indiatimes.com/citizen-reporter/{city_name.lower()}/crstories/query-{city_name},curpg-{page_num}.cms'
        try:
            page = urllib.request.urlopen(url,timeout=6)
        except:
            print('page timeout error')
            page_num +=1
            continue
        soup = BeautifulSoup(page, "lxml")
        
        temp_url_list = soup.find_all('li',{'class':"article"})
#         print('list lenth :',len(url_list))
        for i,tag in enumerate(temp_url_list):
            print(city_name,' : ',len(url_list)+i,flush=True,end = '\t\t\t\r')
            report_url = 'https://timesofindia.indiatimes.com' + tag.div.a['href']
            try:
                report_page = urllib.request.urlopen(report_url,timeout=3)
            except:
                print('report timeout error')
                continue
                
            report_soup = BeautifulSoup(report_page, "lxml")
            txt = report_soup.find(class_="section1").get_text()
            location = report_soup.find(class_="time_cptn").get_text()
            try:
                if len(location.split('| '))==3:
                    a,loc,date_time = location.split('| ')
                elif len(location.split('| '))==2:
                    loc,date_time = location.split('| ')
            except:
                print(f"error here {location.split('| ')}")
                continue
            fname = f'{city_name}_report_{len(url_list)+i}.txt'
            with open(os.path.join(city_reports_path,fname), "w", encoding='utf-8') as f:
                location_mapping[fname] = loc
                f.write('%-1s' % (txt))
                f.write(" Report timestamp : " + date_time)
        url_list.extend(soup.find_all('li',{'class':"article"}))
        
#         print(f'Reports processed: {len(os.listdir(root_path))}',end='\r')
    return location_mapping

def extract_reports_mp(city_list, process_count=12,path='./reports', report_count=50, page_count=1, mapping_csv = 'location_mapping.csv' ):
    '''
    Extracts reports for specified cities from newspaper website.

    city_list : List of city str.  A list of cities, for which reports are to be extracted.
                Available city name ('Delhi','Mumbai','Bangalore',Kolkata')
    process_count : Int.  Number of parallel threads on which the scraping will happen.
    path : Valid path to directory (str). Path to the folder, where extracted reports will be writtern on disk.
    report_count : Int. Number of reports to be extracted.
    page_count : Int. Number of report pages to be scraped(Each page contains ~30 reports.)
    mapping_csv : Valid path to csv file (str). Path to the csv file, where report and its location mapping will be preserved.
    '''
    p = ThreadPool(process_count)
    argument_list = list(zip(city_list,[path]*len(city_list),[report_count]*len(city_list),[page_count]*len(city_list)))
    result = p.map_async(extract_reports,argument_list)
    master_location_mapping = {}

    for mapping in result.get():
        master_location_mapping.update(mapping)

    result_df = pd.DataFrame(master_location_mapping.items(), columns=['filename','location'])

    result_df.to_csv(mapping_csv, index=False)
    print(f''' Reports location : {path}
location mapping : {mapping_csv}''')