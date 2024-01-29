from fastapi import FastAPI, Form, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import pymongo
import re

from src.db.db import DB_Interface
from src.db.infoFetcher import InfoFetcher
from src.technical.filter import *

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
DB = DB_Interface()
infoFetcher = InfoFetcher(DB)

# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client['finance']
# price_col = db['price']
# code_col = db['code']


@app.get("/")
async def root():
    return {"message": "Hello World"}

# @app.get("/price/{code}")
# async def root(code):
#     prices =  pf.fetchPrice(code)
#     res = {
#         'Open': [s[3] for s in prices],
#         'Close': [s[6] for s in prices],
#     }
#     return res

@app.get("/refresh/code/")
async def refreshCode():
    infoFetcher.updateCode()

@app.get("/refresh/price/")
async def refreshPrice():
    # infoFetcher.updatePrice_yahoo(key=['dtype'], val=['股票'])
    infoFetcher.updatePrice(key=['市場別', 'dtype'], val=['上市', '股票'])


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     error_messages = []
#     for error in exc.errors():
#         error_messages.append({"field": error["loc"], "error": error["msg"]})
#     return JSONResponse(status_code=422, content={"detail": error_messages})

@app.post("/filter/")
async def filter(request: Request):
    condition = await request.json()
    condition = dict(condition)
    print(condition)
    ### Check input
    non_numeral = False
    for k in condition:
        if len(condition[k]) == 0:
            condition[k] = '0'
        elif re.match(r'^-?\d+(?:\.\d+)$', condition[k]) is not None: # Check if it's float
            non_numeral = True
            break
    if non_numeral:
        return [
            {
                'code': 'Error',
                'name': '請勿輸入非數值'
            }
        ]
    
    f = Filter()
    stock = {}
    res = []
    for s in DB.code_col.find():
        stock[s['code']] = s
    # href = 'https://tw.stock.yahoo.com/quote/${element.code}.TW/technical-analysis'
    for s in DB.price_col.find():
        # print(f'API_SERVER: code: {s["code"]}')
        info = f.makeInfo(s['data'])
        match = f.filter(info, condition)
        if match:
            res.append(
                {
                    'code': s['code'],
                    'name': stock[s['code']]['name'],
                    'category': stock[s['code']]['市場別'],
                    'src': f'https://tw.stock.yahoo.com/quote/{s["code"]}.TW/technical-analysis' \
                            if stock[s['code']]['市場別'] == '上市' \
                            else f'https://tw.stock.yahoo.com/quote/{s["code"]}.TWO/technical-analysis'
                }
            )

    return res

if __name__ == "__main__":
    port = 8555
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
    
