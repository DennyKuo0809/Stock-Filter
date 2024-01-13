from .interval import Interval_Applier
import pymongo
import re

from .KDJ import KDJ_Filter

class Filter:
    def __init__(self,):
        self.info = {}
        self.condition = {}
        self.IA = Interval_Applier()
        self.KDJ_F = KDJ_Filter()
        pass
    
    def makeInfo(self, data):
        info = {
            'day': {
                'open': [],
                'close': [],
                'high': [],
                'low': []
            },
            'week': {
                'open': [],
                'close': [],
                'high': [],
                'low': []
            },
            'month': {
                'open': [],
                'close': [],
                'high': [],
                'low': []
            }
                
        }
        week_data = self.IA.apply_interval(data, interval='week')
        month_data = self.IA.apply_interval(data, interval='month')
        for d in data:
            if re.match(r'^-?\d+(?:\.\d+)$', d['開盤價'].replace(',', '')) is not None: # Check if it's float
                info['day']['open'].append(float(d['開盤價'].replace(',', '')))
                info['day']['close'].append(float(d['收盤價'].replace(',', '')))
                info['day']['high'].append(float(d['最高價'].replace(',', '')))
                info['day']['low'].append(float(d['最低價'].replace(',', '')))
        
        for d in week_data:
            if re.match(r'^-?\d+(?:\.\d+)$', d['開盤價'].replace(',', '')) is not None: # Check if it's float
                info['week']['open'].append(float(d['開盤價'].replace(',', '')))
                info['week']['close'].append(float(d['收盤價'].replace(',', '')))
                info['week']['high'].append(float(d['最高價'].replace(',', '')))
                info['week']['low'].append(float(d['最低價'].replace(',', '')))
        
        for d in month_data:
            if re.match(r'^-?\d+(?:\.\d+)$', d['開盤價'].replace(',', '')) is not None: # Check if it's float
                info['month']['open'].append(float(d['開盤價'].replace(',', '')))
                info['month']['close'].append(float(d['收盤價'].replace(',', '')))
                info['month']['high'].append(float(d['最高價'].replace(',', '')))
                info['month']['low'].append(float(d['最低價'].replace(',', '')))
        return info
    
    
    def filter(self, info: dict, condition: dict) -> bool:
        self.info = info
        self.condition = condition
        match =  (self.KDJ_F.match(info, condition) == 1)
        return match
    
    # def matchKDJ(self,):
    #     k, d, j = self.TI.KDJ(self.info['high'], self.info['low'], self.info['close'])
    #     # print(f'k: {k:.3f}\t\td: {d:.3f}\t\tj: {j:.3f}', end='')
    #     if int(self.condition['K_value']):
    #         if int(self.condition['K_greater']) and k <= float(self.condition['K_greater_than']):
    #             return False
    #         if int(self.condition['K_less']) and k >= float(self.condition['K_less_than']):
    #             return False
    #     if int(self.condition['D_value']):
    #         if int(self.condition['D_greater']) and d <= float(self.condition['D_greater_than']):
    #             return False
    #         if int(self.condition['D_less']) and d >= float(self.condition['D_less_than']):
    #             return False
    #     if int(self.condition['J_value']):
    #         if int(self.condition['J_greater']) and j <= float(self.condition['J_greater_than']):
    #             return False
    #         if int(self.condition['J_less']) and j >= float(self.condition['J_less_than']):
    #             return False
    #     return True
    
if __name__ == "__main__":
    f = Filter()
    ### Create database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['finance']
    price_col = db['price']
    code_col = db['code']

    condition = {
        'K-value': 'no',
        'K>': 'no',
        'K=': 'no',
        'K<': 'no',
        'K-lower': 50,
        'K-upper': 20,
        'K-equal': 20,
        'D-value': 'no',
        'D>': 'no',
        'D=': 'no',
        'D<': 'no',
        'D-lower': 80,
        'D-upper': 20,
        'D-equal': 20,
        'J-value': 'no',
        'J>': 'no',
        'J=': 'no',
        'J<': 'no',
        'J-lower': 80,
        'J-upper': 20,
        'J-equal': 20,
    }

    ### Asking for conditions
    print('[篩選條件]')
    kdj = input('[KDJ值](yes/no) ')
    if kdj:
        k = input('****[K值](yes/no) ')
        if k == 'yes':
            condition['K-value'] = 'yes'
            lower = input('********[大於](0~100, enter 跳過) ')
            equal = ''
            if lower == '':
                equal = input('********[等於](0~100, enter 跳過) ')
            upper = input('********[小於](0~100, enter 跳過) ')

            condition['K>'] = 'yes' if (lower != '') else 'no'
            condition['K-lower'] = float(lower) if (lower != '') else 'no'
            condition['K='] = 'yes' if (equal != '') else 'no'
            condition['K-equal'] = float(equal) if (equal != '') else 'no'
            condition['K<'] = 'yes' if (upper != '') else 'no'
            condition['K-upper'] = float(upper) if (upper != '') else 'no'
        d = input('****[D值](yes/no) ')
        if d == 'yes':
            condition['D-value'] = 'yes'
            lower = input('********[大於](0~100, enter 跳過) ')
            equal = ''
            if lower == '':
                equal = input('********[等於](0~100, enter 跳過) ')
            upper = input('********[小於](0~100, enter 跳過) ')

            condition['D>'] = 'yes' if (lower != '') else 'no'
            condition['D-lower'] = float(lower) if (lower != '') else 'no'
            condition['D='] = 'yes' if (equal != '') else 'no'
            condition['D-equal'] = float(equal) if (equal != '') else 'no'
            condition['D<'] = 'yes' if (upper != '') else 'no'
            condition['D-upper'] = float(upper) if (upper != '') else 'no'
        j = input('****[J值](yes/no) ')
        if j == 'yes':
            condition['J-value'] = 'yes'
            lower = input('********[大於](0~100, enter 跳過) ')
            equal = ''
            if lower == '':
                equal = input('********[等於](0~100, enter 跳過) ')
            upper = input('********[小於](0~100, enter 跳過) ')

            condition['J>'] = 'yes' if (lower != '') else 'no'
            condition['J-lower'] = float(lower) if (lower != '') else 'no'
            condition['J='] = 'yes' if (equal != '') else 'no'
            condition['J-equal'] = float(equal) if (equal != '') else 'no'
            condition['J<'] = 'yes' if (upper != '') else 'no'
            condition['J-upper'] = float(upper) if (upper != '') else 'no'

    stock = {}
    for s in code_col.find():
        stock[s['code']] = s
    
    for s in price_col.find():
        info = {
            'open': [],
            'close': [],
            'high': [],
            'low': []
        }
        for d in s['data']:
            if re.match(r'^-?\d+(?:\.\d+)$', d['開盤價'].replace(',', '')) is not None: # Check if it's float
                info['open'].append(float(d['開盤價'].replace(',', '')))
                info['close'].append(float(d['收盤價'].replace(',', '')))
                info['high'].append(float(d['最高價'].replace(',', '')))
                info['low'].append(float(d['最低價'].replace(',', '')))
        print(f'[Checking]{stock[s["code"]]["code"]}\t{stock[s["code"]]["name"]}', end='')
        match = f.filter(info, condition)
        if match:
            print('\t\t[MATCH]')
        else:
            print()

### Structure
### 1. info
###     'open': list
###     'close': list
###     'high': list
###     'low': list
###
### 2. condition
###     "index name": {
###         'care': bool,
###         'operator': single value in {-1 0 1},
###         'operand': single value
###     }
