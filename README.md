# netkeiba_collector

[netkeiba](http://www.netkeiba.com/)からデータを取得しJSONで保存します．  

## 事前準備
```
$ pip install configparser beautifulsoup4 urllib3
```

## 使い方

### 設定ファイルの記述
`nc.conf`に以下の形式で取得範囲と対象年を記述します．  
```
[settings]
PageIdFrom = 100000
PageIdTo   = 100001
Years      = [2013, 2014, 2015, 2016]

```
この例では，2013〜2016年の100000番，100001番ページの情報が取得できます．

### 実行
pythonコマンドで以下のように実行します．
```
$ python netkeiba_collector.py
```

## 出力
`data/netkeiba_<year>.json`の形式で，年ごとに各ファイルが出力されます．
