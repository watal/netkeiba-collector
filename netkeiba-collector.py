#!/usr/bin/env python
# -*- coding:utf-8 -*-

import multiprocessing as mp
import time

import collections as cl
import configparser
import csv
import datetime
import json

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen

# 4プロセスで実行
__PROC__ = 8

# 設定ファイル読み込み
config = configparser.ConfigParser()
config.read('nc.conf')


def is_float(s):
  try:
    float(s)
  except:
    return False
  return True


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
                sex = div.find('p', class_='txt_01').text.strip('\n')
                if '牡'in sex:
                    sex = '牡'
                elif '牝' in sex:
                    sex = '牝'
                elif 'セン' in sex:
                    sex = 'セン'
                else:
                    sex = None

                for j in range(len(table.find_all('th'))):
                    th = table.find_all('th')[j].text.strip('\n')
                    if th == '生年月日':
                        birthday = table.find_all('td')[j].text.strip('\n')
                    elif th == '調教師':
                        trainer = table.find_all('td')[j].text.strip('\n')
                    elif th == '馬主':
                        owner = table.find_all('td')[j].text.strip('\n')
                    elif th == '生産者':
                        maker = table.find_all('td')[j].text.strip('\n')
                    elif th == '獲得賞金':
                        prize_money = table.find_all('td')[j].text.strip('\n')

                fathor = dl.find_all('td', class_='b_ml')[0].text.strip('\n')
                mother = dl.find_all('td', class_='b_fml')[1].text.strip('\n')
                b_sire = dl.find_all('td', class_='b_ml')[2].text.strip('\n')
                # ページID
                tmp_list = {'page_id': str(year) + str(i)}
                tmp_list['name'] = horse_name.strip()                 # 馬名
                tmp_list['sex'] = sex                                 # 性別
                tmp_list['birthday'] = birthday.strip()               # 生年月日
                tmp_list['birthday_y'] = datetime.datetime.strptime(
                    birthday.strip(), '%Y年%m月%d日').strftime('%Y')  # 生まれ年
                tmp_list['birthday_m'] = datetime.datetime.strptime(
                    birthday.strip(), '%Y年%m月%d日').strftime('%m')  # 生まれ月
                tmp_list['trainer'] = trainer.strip()                 # 獲得賞金
                tmp_list['owner'] = owner.strip()                     # 馬主
                tmp_list['maker'] = maker.strip()                     # 生産者
                tmp_list['prize_money'] = prize_money.strip()         # 獲得賞金
                tmp_list['father'] = fathor.strip()                   # 父
                tmp_list['mother'] = mother.strip()                   # 母
                tmp_list['b_sire'] = b_sire.strip()                   # 母父

                pog_prize = 0.0
                for tr in result_tr_arr:
                    tds = tr.find_all('td')
                    if len(tds) != 0:
                        race_ymd = datetime.datetime.strptime(
                            tds[0].a.text, '%Y/%m/%d')
                        start_pog = datetime.datetime.strptime(
                            '%d-05-01' % (year+2), '%Y-%m-%d')
                        end_pog = datetime.datetime.strptime(
                            '%d-06-01' % (year+3), '%Y-%m-%d')
                        if race_ymd >= start_pog and race_ymd <= end_pog:
                            if is_float(tds[27].text.replace(',', '')):
                                pog_prize += float(tds[27].text.replace(',', ''))

                        if False:
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
                                        {'race_ymd': race_ymd.strip()})        # レース日付
                                    result_list.append(
                                        {'race_place': race_place.strip()})    # 開催場所
                                    result_list.append(
                                        {'race_name': race_name.strip()})      # レース名
                                    result_list.append(
                                        {'race_result': race_result})          # レース結果
                                    result_list.append(
                                        {'race_jockey': race_jockey})          # 騎手
                                    result_list.append(
                                        {'race_conditions': race_conditions})  # レース条件
                            tmp_list['race_result'] = result_list  # 戦績

                tmp_list['pog_prize'] = '{:.1f}'.format(pog_prize)     # 母父
                netkeiba_list.append(tmp_list)
                print('{}: {} ({}/{})'.format(year,
                                              horse_name.strip(), i, page_id_to))

    # ファイル出力
    # json
    with open('data/netkeiba_' + str(year) + '.json', 'w') as rslt_file:
        json.dump(netkeiba_list, rslt_file, ensure_ascii=False, indent=2)

    # csv
    with open('data/netkeiba_' + str(year) + '.csv', 'w', newline='') as rslt_file:
        fieldnames = netkeiba_list[0].keys()
        fieldnames = sorted(fieldnames)
        writer = csv.DictWriter(rslt_file, fieldnames=fieldnames)
        writer.writeheader()
        for w in netkeiba_list:
            writer.writerow(w)


def main():

    # 対象年を指定
    years = json.loads(config['settings']['Years'])
    pool = mp.Pool(__PROC__)
    pool.map(scraping_netkeiba, years)


if __name__ == '__main__':
    main()
