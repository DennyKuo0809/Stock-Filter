import re
import copy

class KDJ_Filter:
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
                    # print('non bool')
                    return -1
        # print('in KDJ match pass check')

        ### Fetch prices by code
        self.prices = copy.deepcopy(info)

        ### Calculate KDJ
        self.prices['day']['K'], self.prices['day']['D'], self.prices['day']['J'] = self.calculate(
            self.prices['day']['high'], self.prices['day']['low'], self.prices['day']['close']
        )
        self.prices['week']['K'], self.prices['week']['D'], self.prices['week']['J'] = self.calculate(
            self.prices['week']['high'], self.prices['week']['low'], self.prices['week']['close']
        )
        self.prices['month']['K'], self.prices['month']['D'], self.prices['month']['J'] = self.calculate(
            self.prices['month']['high'], self.prices['month']['low'], self.prices['month']['close']
        )
        ### Check the conditions
        if int(condition['K_value']):
            if int(condition['K_value_day']):
                if not len(self.prices['day']['K']):
                    return 0
                if int(condition['K_greater']) and self.prices['day']['K'][-1] < float(condition['K_greater_than']):
                    return 0
                if int(condition['K_less']) and self.prices['day']['K'][-1] > float(condition['K_less_than']):
                    return 0
            if int(condition['K_value_week']):
                if not len(self.prices['week']['K']):
                    return 0
                if int(condition['K_greater']) and self.prices['week']['K'][-1] < float(condition['K_greater_than']):
                    return 0
                if int(condition['K_less']) and self.prices['week']['K'][-1] > float(condition['K_less_than']):
                    return 0
            if int(condition['K_value_month']):
                if not len(self.prices['month']['K']):
                    return 0
                if int(condition['K_greater']) and self.prices['month']['K'][-1] < float(condition['K_greater_than']):
                    return 0
                if int(condition['K_less']) and self.prices['month']['K'][-1] > float(condition['K_less_than']):
                    return 0

        if int(condition['D_value']):
            if int(condition['D_value_day']):
                if not len(self.prices['day']['D']):
                    return 0
                if int(condition['D_greater']) and self.prices['day']['D'][-1] < float(condition['D_greater_than']):
                    return 0
                if int(condition['D_less']) and self.prices['day']['D'][-1] > float(condition['D_less_than']):
                    return 0
            if int(condition['D_value_week']):
                if not len(self.prices['week']['D']):
                    return 0
                if int(condition['D_greater']) and self.prices['week']['D'][-1] < float(condition['D_greater_than']):
                    return 0
                if int(condition['D_less']) and self.prices['week']['D'][-1] > float(condition['D_less_than']):
                    return 0
            if int(condition['D_value_month']):
                if not len(self.prices['month']['D']):
                    return 0
                if int(condition['D_greater']) and self.prices['month']['D'][-1] < float(condition['D_greater_than']):
                    return 0
                if int(condition['D_less']) and self.prices['month']['D'][-1] > float(condition['D_less_than']):
                    return 0

        if int(condition['J_value']):
            if int(condition['J_value_day']):
                if not len(self.prices['day']['J']):
                    return 0
                if int(condition['J_greater']) and self.prices['day']['J'][-1] < float(condition['J_greater_than']):
                    return 0
                if int(condition['J_less']) and self.prices['day']['J'][-1] > float(condition['J_less_than']):
                    return 0
            if int(condition['J_value_week']):
                if not len(self.prices['week']['J']):
                    return 0
                if int(condition['J_greater']) and self.prices['week']['J'][-1] < float(condition['J_greater_than']):
                    return 0
                if int(condition['J_less']) and self.prices['week']['J'][-1] > float(condition['J_less_than']):
                    return 0
            if int(condition['J_value_month']):
                if not len(self.prices['month']['J']):
                    return 0
                if int(condition['J_greater']) and self.prices['month']['J'][-1] < float(condition['J_greater_than']):
                    return 0
                if int(condition['J_less']) and self.prices['month']['J'][-1] > float(condition['J_less_than']):
                    return 0

        if int(condition['KDJ_cross']):
            if int(condition['KDJ_cross_day']):
                if int(condition['KDJ_golden_cross']) and self.cross(interval='day') != 1:
                        return 0
                if int(condition['KDJ_d_cross']) and self.cross(interval='day') != -1:
                        return 0
            
            if int(condition['KDJ_cross_week']):
                if int(condition['KDJ_golden_cross']) and self.cross(interval='week') != 1:
                        return 0
                if int(condition['KDJ_d_cross']) and self.cross(interval='week') != -1:
                        return 0
            
            if int(condition['KDJ_cross_month']):
                if int(condition['KDJ_golden_cross']) and self.cross(interval='month') != 1:
                        return 0
                if int(condition['KDJ_d_cross']) and self.cross(interval='month') != -1:
                        return 0
        return 1

    def calculate(self, high, low, close):
        K, D, J = [], [], []
        k, d, j = 50, 50, 50
        for i in range(8, len(high)):
            if (max(high[(i-8):(i+1)]) - min(low[(i-8):(i+1)])) != 0:
                rsv = 100 * (close[i] - min(low[(i-8):(i+1)])) / (max(high[(i-8):(i+1)]) - min(low[(i-8):(i+1)]))
                k = k * 2 / 3 + rsv / 3
                d = d * 2 / 3 + k / 3
                j = d * 3 - 2 * k
                K.append(k)
                D.append(d)
                J.append(j)
                # print(f'{k}\t\t{d}\t\t{j}')
        return K, D, J
    
    def cross(self, delay=0, interval='day'):
        ### Return
        ### 1:  Golden Cross (K > D)
        ### -1: Death Corss (K < D)
        ### 0:  Neither

        info = self.prices[interval]

        if len(info['K']) <= 1 or len(info['D']) <= 1:
            return 0
        
        # for i in reversed(range(1, delay+2)): # [-1, -2, -3, ...]
        if info['K'][-2] < info['D'][-2] and info['K'][-1] > info['D'][-1]: # Golden Cross
            return 1
        if info['K'][-2] > info['D'][-2] and info['K'][-1] < info['D'][-1]: # Death Cross
            return -1
        return 0
    