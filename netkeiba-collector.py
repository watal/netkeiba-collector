#!/usr/bin/env python
# -*- coding:utf-8 -*-

import collections as cl
import configparser
import json
import time
import multiprocessing as mp
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen

# 4プロセスで実行
__PROC__ = 4

# 設定ファイル読み込み
config = configparser.ConfigParser()
config.read('nc.conf')


def scraping_netkeiba(year):
    # netkeibaのURL
    url = 'http://db.netkeiba.com/horse/' + str(year) + '{0}/'

    # 開始ページと終了ページIDを指定
    page_id_from = config.getint('settings', 'PageIdFrom')
    page_id_to = config.getint('settings', 'PageIdTo')

    netkeiba_list = []

    for i in range(page_id_from, page_id_to+1):
        # ページ情報を取得
        page = bs(urlopen(url.format(i)), 'lxml')
        result_tr_arr = page.select('table.db_h_race_results > tbody > tr')

        # 1秒に1回実行
        time.sleep(1)
        div = page.find('div', class_='horse_title')
        table = page.find('table', class_='db_prof_table')
        dl = page.find('dl', class_='fc')

        # コンテンツがあった場合，配列に追加
        if div != None:
            result_list = []
            horse_name = div.h1.text
            if horse_name != None:
                # 各要素の抜き出し
                birthday = table.find_all('td')[0].text.strip('\n')
                money = table.find_all('td')[6].text.strip('\n')
                fathor = dl.find_all('td', class_='b_ml')[0].text.strip('\n')
                mother = dl.find_all('td', class_='b_fml')[1].text.strip('\n')
                b_sire = dl.find_all('td', class_='b_ml')[2].text.strip('\n')

                for tr in result_tr_arr:
                    tds = tr.find_all('td')
                    if len(tds) != 0:
                        race_ymd = tds[0].a.text
                        race_place = tds[1].a.text
                        race_name = tds[4].a.text
                        race_result = tds[11].text
                        race_jockey = tds[12].text.strip('\n')
                        race_conditions = tds[14].text
                        result_list.append(
                            {"race_ymd": race_ymd.strip()})         # レース日付
                        result_list.append(
                            {"race_place": race_place.strip()})     # 開催場所
                        result_list.append(
                            {"race_name": race_name.strip()})       # レース名
                        result_list.append(
                            {"race_result": race_result})           # レース結果
                        result_list.append(
                            {"race_jockey": race_jockey})           # 騎手
                        result_list.append(
                            {"race_conditions": race_conditions})   # レース条件

                tmp_list = [{"page_id": str(year) + str(i)}]        # ページID
                tmp_list.append({"name": horse_name.strip()})       # 馬名
                tmp_list.append({"birthday": birthday.strip()})     # 生年月日
                tmp_list.append({"money": money.strip()})           # 獲得賞金
                tmp_list.append({"father": fathor.strip()})         # 父
                tmp_list.append({"mother": mother.strip()})         # 母
                tmp_list.append({"b_sire": b_sire.strip()})         # 母父
                tmp_list.append(result_list)                        # 戦績
                netkeiba_list.append(tmp_list)

    # ファイル出力
    with open('data/netkeiba_' + str(year) + '.json', 'w') as rslt_file:
        json.dump(netkeiba_list, rslt_file, ensure_ascii=False, indent=2)


def main():

    # 対象年を指定
    years = json.loads(config['settings']['Years'])
    pool = mp.Pool(__PROC__)
    pool.map(scraping_netkeiba, years)


if __name__ == '__main__':
    main()
