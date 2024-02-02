from tqdm import tqdm
import datetime
import requests
from pyquery import PyQuery as pq
import yfinance

### For fetching price
root = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json'

### For fetching codes
TWSE_URL = 'http://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
TPEX_URL = 'http://isin.twse.com.tw/isin/C_public.jsp?strMode=4'


### Fetch Price from yahoo
def fetchPrice_yahoo(code, days=1800, expansion='TW'):
    period = 1800 if days > 1800 else days
    end = datetime.date.today()+datetime.timedelta(days=1)
    start = datetime.date.today()+datetime.timedelta(days=(-1)*period)
    df = yfinance.download(
        f'{code}.{expansion}', 
        start=f'{start.year}-{start.month:02}-{start.day:02}', 
        end=f'{end.year}-{end.month:02}-{end.day:02}', 
    )
    # print(df)

    data = [] # columns= ['日期', '開盤價', '最高價', '最低價', '收盤價']
    for i in range(df.shape[0]):
        d = {}
        date = df.index[i]
        d['日期'] = f'{date.year-1911}/{date.month}/{date.day}'
        d['開盤價'] = f"{df.iloc[i]['Open']}"
        d['最高價'] = f"{df.iloc[i]['High']}"
        d['最低價'] = f"{df.iloc[i]['Low']}"
        d['收盤價'] = f"{df.iloc[i]['Adj Close']}"
        data.append(d)
    return {'code': code, 'data': data }

### Fetch daily price for the past (period) months
def fetchPrice(code, period=120): 
    year = datetime.date.today().year
    month = datetime.date.today().month
    data = []
    # columns= ['日期', '成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數']

    for i in reversed(range(period)):
        m =  (month - i%12) if (month - i%12 > 0) else (month - i%12 + 12) 
        y = year
        if i >= month:
            y -= ((i-month)//12 + 1)

        url = f'{root}&date={y}{m:02}01&stockNo={code}'
        # print(url)
        json_data = requests.get(url).json()
        if 'data' in json_data:
            for info in json_data['data']:
                d = {}
                for k, v in zip(json_data['fields'], info):
                    d[k] = v
                data.append(d)
    return {'code': code, 'data': data }

import re
import copy
class MACD_Filter():
    def __init__(self, ):
        self.prices = {}

    def match(self, info: dict, condition: dict):
        ### Validation
        for k, v in condition.items():
            if 'than' in k:
                if re.match(r'^-?\d+(?:\.\d+)$', v) is None and re.match(r'^[-+]?[0-9]+$', v) is None:
                    # print(v)
                    return -1
            else:
                if v != '0' and v != '1':
                    return -1

        ### Fetch prices by code
        self.prices = copy.deepcopy(info)

        ### Check the conditions
        if int(condition['TREND_high_price']):
            intervalLen = int(condition['TREND_high_price_interval'])
            if int(condition['TREND_high_price_day']):
                if not len(self.prices['day']['close']):
                    return 0
                if self.highPrice(length=intervalLen, interval='day') == 0:
                    return 0

            if int(condition['TREND_high_price_week']):
                if not len(self.prices['day']['close']):
                    return 0
                if self.highPrice(length=intervalLen, interval='week') == 0:
                    return 0

            if int(condition['TREND_high_price_month']):
                if not len(self.prices['day']['close']):
                    return 0
                if self.highPrice(length=intervalLen, interval='month') == 0:
                    return 0

        return 1

    
    def highPrice(self, length=18, interval='day'):
        ### Return
        ### 1:  High Price
        ### 0:  None

        info = self.prices[interval]['close']

        historyLen = min(len(info)-1, length)
        for i in range(historyLen):
            if info[-1] <= info[-(i+2)]:
                return 0
        return 1


if __name__ == "__main__":
    from interval import Interval_Applier
    IA = Interval_Applier()
    m = MACD_Filter()

    d = fetchPrice(2330)['data']
    # print(d)
    # day
    # p = [float(i['收盤價']) for i in d]
    # dates = [i['日期'] for i in d]
    # print(dates)
    # print('(DAY)', end=' ')
    # m.calculate(p, dates, fast=10, slow=20)

    # # week
    week_d = IA.apply_interval(d, interval='week')
    p = [float(i['收盤價']) for i in week_d]
    dates = [i['日期'] for i in week_d]
    print('(WEEK)', end='\n')
    m.calculate(p, dates, fast=12, slow=26)

    # month
    # month_d = IA.apply_interval(d, interval='month')
    # p = [float(i['收盤價']) for i in month_d]
    # dates = [i['日期'] for i in month_d]
    # print('(MONTH)', end=' ')
    # m.calculate(p, dates, fast=12, slow=26)
