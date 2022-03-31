"""
Before executing this script make sure that all packages are installed properly
purpose:
-------
This script can be used independently to scrape the latest RC OVA build and
downloads OVA and place it in local system. 

"""

import requests
from bs4 import BeautifulSoup
import urllib
import os
from pathlib import Path

URL = 'http://ci-artifacts04.vse.rdlabs.hpecorp.net/omni/master/OVA/DCS-CP-synergy/'
r = requests.get(URL)
#print(r.content)

def find_td_entries(original):
    soup = BeautifulSoup(r.content, 'html5lib')
    body = soup.find('body')
    string = str(body).replace('<body>define([],"', '').replace('");</body>', '')
    #print(body)

    #to get content for table tag
    soup = BeautifulSoup(string, 'html5lib')

    # to retrieve all rows in table
    if original:
        tr = soup.findAll('tr')[-9:-8]
    else:
        tr = soup.findAll('tr')[-14:-13]
    # print(tr)

    td_entries = []
    for each_tr in tr:
        td = each_tr.find_all('td')
        # In each tr rown find each td cell
        for each_td in td:
            td_entries.append(each_td)
    ova_rc_build = str(td_entries[1]).replace("<td>","").replace("</a>","").replace("</td>","").replace(">","!").split("!")[1]
    return ova_rc_build
    
# execution starts here ...

ova_rc_build = find_td_entries(True)
if ova_rc_build.find('FAILED') == '-1':
    ova_rc_build = find_td_entries(False)    
file_name =  "latestbuildfile.ova"
while(True):
    url1 = URL + ova_rc_build
    urllib.request.urlretrieve(url1, file_name)
    if (os.path.getsize(file_name) >= 2693642240):
        print("Download Successful")
        break
    else:
        continue
