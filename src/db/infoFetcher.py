from .db import *
from tqdm import tqdm
import datetime
import requests
from pyquery import PyQuery as pq

### For fetching price
root = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json'

### For fetching codes
TWSE_URL = 'http://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
TPEX_URL = 'http://isin.twse.com.tw/isin/C_public.jsp?strMode=4'

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

def getCodes():
    columns = ['dtype', 'code', 'name', '國際證券辨識號碼', '上市日', '市場別', '產業別', 'CFI']
    list = []
    for url in [TWSE_URL, TPEX_URL]:
        html = requests.get(url).text
        response_dom = pq(html)
        for tr in response_dom('.h4 tr:eq(0)').next_all().items():
            if tr('b'):
                dtype = tr.text()
            else:
                row = [td.text() for td in tr('td').items()]
                code, name = row[0].split('\u3000')
                list.append(dict(zip(columns, [dtype, code, name, *row[1: -1]])))
    return list

class InfoFetcher:
    def __init__(self, dbInterface):
        self.db = dbInterface
        pass

    def preCheck(self,):
        pass

    def updateCode(self, ):
        codeList = getCodes()
        print(f"[INFO] Got meta for {len(codeList)} stocks.")

        code_col = self.db.create_collection('code', drop_when_copy=True)
        self.db.insert_data(self.db.code_col, codeList)

    def updatePrice(self, key=[], val=[]):
        ### Chcek
        if len(key) != len(val):
            print("[ERROR] The length of key and value do not match.")
            return
        
        ### Get the list of code
        stock_list = []
        if len(key) != 0:
            for d in self.db.code_col.find():
                match = True
                for k, v in zip(key, val):
                    if d[k] != v:
                        match = False
                        break
                if match:
                    stock_list.append(d['code'])
        else:
            stock_list = [s['code'] for s in self.db.code_col.find()]
        # print(code_list)
                    
        ### Fetch the price and update to db
        exist_stock = {}
        for s in self.db.price_col.find():
            # print(s['code'])
            exist_stock[s['code']] = s['data'][-1]['日期'] if len(s['data']) else 'empty'

        price_data = []

        date_now = datetime.date.fromisoformat(
            f'{datetime.date.today().year}-{datetime.date.today().month:02}-{datetime.date.today().day:02}'
        )
        month_now = datetime.date.today().month
        year_now = datetime.date.today().year

        for stock in tqdm(stock_list):
        # for stock in exist_stock:
            # print(stock)
            if stock not in exist_stock:
                # print('newly add')
                d = fetchPrice(stock)
                self.db.insert_data(self.db.price_col, d)
            elif exist_stock[stock] == 'empty':
                self.db.price_col.delete_one({'code' : stock})
                price_data = fetchPrice(stock)
                self.db.insert_data(self.db.price_col, price_data)
            else:
                # print('exist')
                luy, lum, lud = exist_stock[stock].split('/')
                last_update = datetime.date.fromisoformat(f'{int(luy)+1911}-{lum}-{lud}')
                day_without_update = (date_now - last_update).days
                # print(date_now, ' ', last_update, ' ', day_without_update)

                current_data = self.db.price_col.find({'code' : stock}, {'_id': 0, 'data' : 1})[0]['data']
                # print(len(current_data))

                if day_without_update > 1800: # Over a year
                    self.db.price_col.delete_one({'code' : stock})
                    price_data = fetchPrice(stock)
                    self.db.insert_data(self.db.price_col, price_data)
                elif day_without_update > 0:
                    period = (month_now-int(lum)+1) if month_now >= int(lum) else (month_now-int(lum)+13)
                    price_data = fetchPrice(stock, period = period)
                    current_data = self.db.price_col.find({'code' : stock}, {'_id': 0, 'data' : 1})[0]['data']
                    new_data = []
                    for cd in current_data:
                        y, m, _ = cd['日期'].split('/')
                        if (int(y) < year_now - 1911 and int(m) <= month_now) \
                            or (int(y) == year_now - 1911 and int(m) == month_now):
                            continue
                        new_data.append(cd)
                    new_data += price_data['data']
                    self.db.price_col.update_one({'code': stock}, {"$set": {'data': new_data}})

if __name__ == "__main__":
    ### Init a db interface
    dbi = DB_Interface()

    IF = InfoFetcher(dbi)
    # IF.updateCode()
    IF.updatePrice(key=['code'], val=['1102'])
