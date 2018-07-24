# -*- coding:utf-8 -*-

import json
import time
import collections as cl
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen

def scraping_netkeiba(year):
    url = 'http://db.netkeiba.com/horse/' + str(year) + '{0}/'
    page_id_from = 100000
    page_id_to = 100004
    pedigree_list = []

    for i in range(page_id_from, page_id_to+1):
        # ページ情報を取得
        page = bs(urlopen(url.format(i)), 'lxml')

        # 1秒に1回実行
        time.sleep(1)
        div = page.find('div', class_='horse_title')
        table = page.find('table', class_='db_prof_table')
        dl = page.find('dl', class_='fc')

        # コンテンツがあった場合，配列に追加
        if div != None:
            horse_name = div.h1.text
            if horse_name != None:

                birthday = table.find_all('td')[0].text.strip('\n')
                fathor = dl.find_all('td', class_='b_ml')[0].text.strip('\n')
                mother = dl.find_all('td', class_='b_fml')[1].text.strip('\n')
                b_sire = dl.find_all('td', class_='b_ml')[2].text.strip('\n')

                tmp_list = [{"page_id":i}]                          # ページID
                tmp_list.append({"name":horse_name.strip()})        # 馬名
                tmp_list.append({"birthday":birthday.strip()})      # 生年月日
                tmp_list.append({"father":fathor.strip()})          # 父
                tmp_list.append({"mother":mother.strip()})          # 母
                tmp_list.append({"b_sire":b_sire.strip()})          # 母父
                pedigree_list.append(tmp_list)
            else:
                continue
        else:
            continue
    rslt_file = open('data/pedigree_' + str(year) + '.txt', 'w')
    json.dump(pedigree_list, rslt_file, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    year = 2016
    scraping_netkeiba(year)
