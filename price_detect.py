import json
import os
import sys
from datetime import datetime as dt2
import datetime as dt
import finlab_crypto
sys.path.append("..")
from public.web3_utils import Web3Utils
web3Utils = Web3Utils("https://bsc-dataseed.binance.org/", 5, 56,0)


now_path = os.getcwd()
contract_path = now_path+'/bsc/contract'

with open(contract_path+'/contract.json') as f:
    contract_data = json.load(f)

with open(contract_path+'/pair.json') as f:
    pair_data = json.load(f)
    

#  swap method
def Biswap_factory_method(tokenA_address,tokenB_address):
    '''
    tokenA_address [str] : Token Address
    tokenB_address [str] : Token Address
    '''
    factory_contract = web3Utils.w3.eth.contract(address=web3Utils.w3.toChecksumAddress(contract_data['Biswap_factory']['address']), abi=contract_data['Biswap_factory']['ABI'])
    pair_address = factory_contract.functions.getPair(tokenA_address,tokenB_address).call()
    pair_contract = web3Utils.w3.eth.contract(address=web3Utils.w3.toChecksumAddress(pair_address), abi=contract_data['Biswap_pair']['ABI'])
    temp_token0 = pair_contract.functions.token0().call()
    temp_token1 = pair_contract.functions.token1().call()
    pair_rate = pair_contract.functions.getReserves().call()
    return temp_token0,temp_token1 ,pair_rate

def get_binance_price(Symbol):
    '''
    get binance symbol data
        args:
            symbol (str) 
            timesetup (str) : '1m' , '5m' , '1h' , '4h' , '1d'
        return:
            data_dict (dict) :{'time':{'close':close , 'low':low , 'open':open , 'high':high } ....}
    '''

    data = finlab_crypto.crawler.get_single_binance(Symbol,'1m',1)  
    data = float(data['close'])
    return data
def get_biswap_price(pair_item):
    token0_name,token1_name = pair_item.split('-')
    token0 = contract_data[token0_name]
    token1 = contract_data[token1_name]
    temp_token0,temp_token1,[token0_pool_balance,token1_pool_balance,temp_timestamp] = Biswap_factory_method(token0['address'],token1['address'])
    # temp_time = dt2.fromtimestamp(temp_timestamp)
    if token0['address'] == temp_token0:
        biswap_price = token1_pool_balance/token0_pool_balance
    else:
        biswap_price = token0_pool_balance/token1_pool_balance
    return biswap_price
 

for pair_item in pair_data:
    biswaptoken = pair_data[pair_item]['biswap']
    binancetoken = pair_data[pair_item]['binance']
    biswap_price = get_biswap_price(biswaptoken)
    binance_price = get_binance_price(binancetoken)
    pair_rate = str(round(abs(((binance_price-biswap_price)/binance_price)*100),2))+'%'
    print(pair_item,'Biswap:',biswap_price,'Binance:',binance_price,pair_rate)