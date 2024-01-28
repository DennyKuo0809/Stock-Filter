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
    print(df)

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
def fetchPrice(code, period=12): 
    year = datetime.date.today().year
    month = datetime.date.today().month
    data = []
    # columns= ['日期', '成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數']

    for i in range(1, period+1):
        y = year
        m = month - period + i
        if m <= 0:
            y -= 1
            m += 12

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

        ### Calculate MACD
        self.prices['day']['fastEMA'], self.prices['day']['slowEMA'], self.prices['day']['DIF'], self.price['day']['MACD'] = self.calculate(
            self.prices['day']['close']
        )
        self.prices['week']['fastEMA'], self.prices['week']['slowEMA'], self.prices['week']['DIF'], self.price['week']['MACD'] = self.calculate(
            self.prices['week']['close']
        )
        self.prices['month']['fastEMA'], self.prices['month']['slowEMA'], self.prices['month']['DIF'], self.price['month']['MACD'] = self.calculate(
            self.prices['month']['close']
        )

        ### Check the conditions
        if int(condition['MACD_zero']):
            if int(condition['MACD_zero_day']):
                if not len(self.prices['day']['DIF']):
                    return 0
                if int(condition['MACD_zero_upper']) and (self.prices['day']['DIF'][-1] < 0 or self.prices['day']['MACD'][-1] < 0 ):
                    return 0
                if int(condition['MACD_zero_lower']) and (self.prices['day']['DIF'][-1] >= 0 or self.prices['day']['MACD'][-1] >= 0 ):
                    return 0
            if int(condition['MACD_zero_week']):
                if not len(self.prices['week']['DIF']):
                    return 0
                if int(condition['MACD_zero_upper']) and (self.prices['week']['DIF'][-1] < 0 or self.prices['week']['MACD'][-1] < 0 ):
                    return 0
                if int(condition['MACD_zero_lower']) and (self.prices['week']['DIF'][-1] >= 0 or self.prices['week']['MACD'][-1] >= 0 ):
                    return 0
            if int(condition['MACD_zero_month']):
                if not len(self.prices['month']['DIF']):
                    return 0
                if int(condition['MACD_zero_upper']) and (self.prices['month']['DIF'][-1] < 0 or self.prices['month']['MACD'][-1] < 0 ):
                    return 0
                if int(condition['MACD_zero_lower']) and (self.prices['month']['DIF'][-1] >= 0 or self.prices['month']['MACD'][-1] >= 0 ):
                    return 0

        if int(condition['MACD_cross']):
            if int(condition['MACD_cross_day']):
                if int(condition['MACD_golden_cross']) and self.cross(interval='day') != 1:
                        return 0
                if int(condition['MACD_d_cross']) and self.cross(interval='day') != -1:
                        return 0
            
            if int(condition['MACD_cross_week']):
                if int(condition['MACD_golden_cross']) and self.cross(interval='week') != 1:
                        return 0
                if int(condition['MACD_d_cross']) and self.cross(interval='week') != -1:
                        return 0
            
            if int(condition['MACD_cross_month']):
                if int(condition['MACD_golden_cross']) and self.cross(interval='month') != 1:
                        return 0
                if int(condition['MACD_d_cross']) and self.cross(interval='month') != -1:
                        return 0

        if int(condition['MACD_osc_shorten']):
            if int(condition['MACD_osc_shorten_day']):
                if int(condition['MACD_osc_shorten_red']) and self.SOC_shorten(interval='day') != 1:
                        return 0
                if int(condition['MACD_osc_shorten_green']) and self.SOC_shorten(interval='day') != -1:
                        return 0
            
            if int(condition['MACD_osc_shorten_week']):
                if int(condition['MACD_osc_shorten_red']) and self.SOC_shorten(interval='week') != 1:
                        return 0
                if int(condition['MACD_osc_shorten_green']) and self.SOC_shorten(interval='week') != -1:
                        return 0
            
            if int(condition['MACD_osc_shorten_month']):
                if int(condition['MACD_osc_shorten_red']) and self.SOC_shorten(interval='month') != 1:
                        return 0
                if int(condition['MACD_osc_shorten_green']) and self.SOC_shorten(interval='month') != -1:
                        return 0

        if int(condition['MACD_cross_predict']):
            if int(condition['MACD_cross_predict_day']):
                if int(condition['MACD_golden_cross_predict']) and self.cross(interval='day') != 1:
                        return 0
                if int(condition['MACD_d_cross_predict']) and self.cross(interval='day') != -1:
                        return 0
            
            if int(condition['MACD_cross_predict_week']):
                if int(condition['MACD_golden_cross_predict']) and self.cross_predict(interval='week') != 1:
                        return 0
                if int(condition['MACD_d_cross_predict']) and self.cross_predict(interval='week') != -1:
                        return 0
            
            if int(condition['MACD_cross_predict_month']):
                if int(condition['MACD_golden_cross_predict']) and self.cross_predict(interval='month') != 1:
                        return 0
                if int(condition['MACD_d_cross_predict']) and self.cross_predict(interval='month') != -1:
                        return 0
        return 1

    
    def cross(self, interval='day'):
        ### Return
        ### 1:  Golden Cross (DIF > MACD)
        ### -1: Death Corss (MACD < DIF)
        ### 0:  Neither

        info = self.prices[interval]

        if len(info['DIF']) <= 1 or len(info['MACD']) <= 1:
            return 0
        
        # for i in reversed(range(1, delay+2)): # [-1, -2, -3, ...]
        if info['DIF'][-2] < info['MACD'][-2] and info['DIF'][-1] > info['MACD'][-1]: # Golden Cross
            return 1
        if info['DIF'][-2] > info['MACD'][-2] and info['DIF'][-1] < info['MACD'][-1]: # Death Cross
            return -1
        return 0

    def SOC_shorten(self, interval='day'):
        ### Return
        ### 1:  green
        ### -1: red
        ### 0:  Neither

        info = self.prices[interval]

        if len(info['DIF']) <= 1 or len(info['MACD']) <= 1:
            return 0
        
        previous, last = (info['DIF'][-2] - info['MACD'][-2]), (info['DIF'][-1] - info['MACD'][-1])
        if previous < 0 and last < 0 and previous < last: # Golden Cross
            return 1
        if previous > 0 and last > 0 and previous > last: # Death Cross
            return -1
        return 0

    def cross_predict(self, interval='day', soc=2.5):
        ### Return
        ### 1:  Golden Cross (DIF > MACD)
        ### -1: Death Corss (MACD < DIF)
        ### 0:  Neither

        info = self.prices[interval]

        if len(info['DIF']) <= 1 or len(info['MACD']) <= 1:
            return 0
        
        SOC = info['DIF'][-1] - info['MACD'][-1]
        if SOC < 0 and SOC > soc * (-1) : # Golden Cross
            return 1
        if SOC >= 0 and SOC < soc: # Death Cross
            return -1
        return 0

    def calculate(self, close, date, fast=12, slow=26, x=9):
        fastEMA, slowEMA, macd = sum(close[:(fast-1)])/(fast-1), sum(close[:(slow-1)])/(slow-1), 0
        F, S, DIF, MACD = [], [], [], []
        for i in range(slow, len(close)):
            fastEMA = (fastEMA * (fast-1) + close[i] * 2) / (fast+1)
            slowEMA = (slowEMA * (slow-1) + close[i] * 2) / (slow+1)
            macd = (macd * (x-1) + (fastEMA - slowEMA) * 2) / (x+1)
            F.append(fastEMA)
            S.append(slowEMA)
            DIF.append(fastEMA-slowEMA)
            MACD.append(macd)
            print(f'({i}-{date[i]}) price: {close[i]:.3f}\t|\tfast: {fastEMA:.3f}\t|\tslow: {slowEMA:.3f}\t|\tdif: {DIF[-1]:.2f}\t|\tMACD: {macd:.2f}')
        return F, S, DIF, MACD


if __name__ == "__main__":
    d = fetchPrice(2412)
    date = [i['日期'] for i in d['data']]
    p = [float(i['收盤價']) for i in d['data']]
    m = MACD_Filter()
    m.calculate(p, date)