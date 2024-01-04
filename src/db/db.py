import pymongo
import logging


class DB_Interface:
    def __init__(self, host='localhost', port=27017):
        self.client = pymongo.MongoClient(f"mongodb://{host}:{port}/")
        self.db = None
        self.code_col = None
        self.price_col = None
        self.startup()
    
    # Create Database and Collections
    def startup(self):
        self.db = self.create_database('finance')
        self.code_col = self.create_collection('code')
        self.price_col = self.create_collection('price')
        return


    # create data base
    def create_database(self, name: str):
        # dblist = self.client.list_database_names()
        db = self.client[name]
        return db

    # create collection
    def create_collection(self, name: str, drop_when_copy=False):
        collist = self.db.list_collection_names()
        if name in collist and drop_when_copy:
            col = self.db[name]
            col.drop()
        col = self.db[name]
        return col

    # insert data
    def insert_data(self, col, data):
        if isinstance(data, list):
            res = col.insert_many(data)
        else:
            res = col.insert_one(data)
        return res

    # Search code of stocks by condition list
    def search_code(self, key=[], val=[]):
        ### Chcek
        if len(key) != len(val):
            logging.error("The length of key and value in condition do not match.")
            return []
        
        ### Get the list of code
        stock_list = []
        if len(key) != 0:
            for d in self.code_col.find():
                match = True
                for k, v in zip(key, val):
                    if d[k] != v:
                        match = False
                        break
                if match:
                    stock_list.append(d['code'])
        else:
            stock_list = [s['code'] for s in self.code_col.find()]

        return stock_list
