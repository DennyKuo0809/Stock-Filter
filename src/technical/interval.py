import datetime
import re

class Interval_Applier:
    def __init__(self):
        pass
    
    def apply_week(self, dates):
        intervals = []
        last_weekday = 1
        for i, date_ in enumerate(dates):
            y_, m_, d_ = date_.split('/')
            y_ = 1911 + int(y_)
            week_day = datetime.datetime.strptime(f"{y_}-{m_}-{d_[:2]}", '%Y-%m-%d').weekday()
            # print(f"{y_}-{m_}-{d_}", ' ', week_day)
            if week_day < last_weekday:
                if len(intervals):
                    intervals[-1][1] = i-1
                intervals.append([i, None])
            last_weekday = week_day

        if len(intervals) and intervals[-1][1] is None:
            intervals[-1][1] = len(dates)-1
        return intervals

    def apply_month(self, dates):
        intervals = []
        last_month = -1
        for i, date_ in enumerate(dates):
            _, month, _ = date_.split('/')
            month = int(month)
            if month != last_month:
                if len(intervals):
                    intervals[-1][1] = i-1
                intervals.append([i, None])
            last_month = month

        if len(intervals) and intervals[-1][1] is None:
            intervals[-1][1] = len(dates)-1
            intervals = intervals[1:]
        return intervals

    def apply_interval(self, datas: list, interval='day'):
        if interval == 'day':
            return datas
        dates = [d['日期'] for d in datas]

        if interval == 'week':
            intervals = self.apply_week(dates)
            # print(intervals)
            # for i in intervals:
            #     print(f"{dates[i[0]]} ~ {dates[i[1]]}")

        if interval == 'month':
            intervals = self.apply_month(dates)
            # print(intervals)
            # for i in intervals:
            #     print(f"{dates[i[0]]} ~ {dates[i[1]]}")
            
        new_datas = []
        for i in intervals:
            d = { 
                '日期': f"{dates[i[0]]} ~ {dates[i[1]]}",
                '成交股數': 0,
                '成交金額': 0,
                '開盤價': 0,
                '最高價': 0,
                '最低價': 2147483647,
                '收盤價': 0,
                '漲跌價差': 0,
                '成交筆數': 0
            }

            for index in range(i[0], i[1]+1):
                # if re.match(r'^-?\d+(?:\.\d+)$', datas[index]['成交股數'].replace(',', '')) is not None: # Check if it's float
                #     d['成交股數'] += float(datas[index]['成交股數'].replace(',', ''))
                # if re.match(r'^-?\d+(?:\.\d+)$', datas[index]['成交金額'].replace(',', '')) is not None: # Check if it's float
                #     d['成交金額'] += float(datas[index]['成交金額'].replace(',', ''))
                # if re.match(r'^-?\d+(?:\.\d+)$', datas[index]['成交筆數'].replace(',', '')) is not None: # Check if it's float
                #     d['成交筆數'] += float(datas[index]['成交筆數'].replace(',', ''))
                if re.match(r'^-?\d+(?:\.\d+)$', datas[index]['最高價'].replace(',', '')) is not None: # Check if it's float
                    d['最高價'] = max(d['最高價'], float(datas[index]['最高價'].replace(',', '')))
                if re.match(r'^-?\d+(?:\.\d+)$', datas[index]['最低價'].replace(',', '')) is not None: # Check if it's float
                    d['最低價'] = min(d['最低價'], float(datas[index]['最低價'].replace(',', '')))
            
            for index in range(i[0], i[1]+1):
                if re.match(r'^-?\d+(?:\.\d+)$', datas[index]['開盤價'].replace(',', '')) is not None: # Check if it's float
                    d['開盤價'] = datas[index]['開盤價'].replace(',', '')
                    break
            
            for index in reversed(range(i[0], i[1]+1)):
                if re.match(r'^-?\d+(?:\.\d+)$', datas[index]['收盤價'].replace(',', '')) is not None: # Check if it's float
                    d['收盤價'] = datas[index]['收盤價'].replace(',', '')
                    break
            
            for k in d:
                if not isinstance(d[k], str):
                    d[k] = str(d[k])
            new_datas.append(d)

        return new_datas
                

        # applied_df = None
        # date_list = list(df['日期'])
        # if interval == 'week':
        #     ### Find the first Monday
        #     first = 0
        #     while True:
        #         week_day = datetime.datetime.strptime(date_list[first], '%Y-%m-%d').weekday()
        #         if week_day != 1:
        #             first += 1
        #         else:
        #             break
            
        #     ### Construct new dataframe
        #     last_close_price = 
        #     for index in range(first, len(date_list), 5):
        #         df_interval = df.iloc[index:(index+5)]
        #         date = date_list[index]
        #         trading_volumne = sum([int(v.replace(',', '')) for v in df_interval['成交股數']])
        #         business_volumne = sum([int(v.replace(',', '')) for v in df_interval['成交金額']])
        #         open_price = df_interval['開盤價'][0]
        #         high_price = max([float(v.replace(',', '')) for v in df_interval['最高價']])
        #         low_price = min([float(v.replace(',', '')) for v in df_interval['最低價']])
        #         close_prince = df_interval['收盤價'][-1]
        #         change = df_interval['收盤價'][-1]
        #         transaction = sum([int(v.replace(',', '')) for v in df_interval['成交筆數']])
                
        # elif interval == 'month':
        #     pass
        
        # return applied_df

if __name__ == "__main__":
    IA = Interval_Applier()
    import pymongo
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['finance']
    price_col = db['price']
    code_col = db['code']
    print(price_col.find()[0]['code'])
    new_datas = IA.apply_interval(price_col.find()[0]['data'], 'month')
    # print(new_datas)
    from index import Technical_Index
    ti = Technical_Index()
    high = [float(d['最高價']) for d in new_datas]
    low = [float(d['最低價']) for d in new_datas]
    close = [float(d['收盤價']) for d in new_datas]
    k, d, j = ti.KDJ(high, low, close)
    print(f'{k}\t\t{d}\t\t{j}')
### input format = list[d]
    ### d = {
    ###     '日期': 'yyy-mm-dd',
    ###     '開盤價': '',
    ###     '收盤價': '',
    ###     '最高價': '',
    ###     '最低價': '',
    ### }

### output format = list[d]
    ### d = {
    ###     '日期': 'yyy-mm-dd~yyy-mm-dd',
    ###     '開盤價': '',
    ###     '收盤價': '',
    ###     '最高價': '',
    ###     '最低價': '',
    ### }
