from importlib import resources

import incentivedkutils as utils
import requests
from dateutil import parser

from . import parms_ICE


class ICE():
    @staticmethod
    def commodity_prices(product):
        indata_list = ICE._get_product_prices(product)
        return indata_list

    @classmethod
    def _get_product_prices(cls, product):
        product_dict = cls._product_data()
        product = product_dict[product]
        contracts = requests.get(product['contracts_url']).json()
        for c in contracts:
            c['contract_date'] = parser.parse(c['endDate'].replace('EDT', 'UTC').replace('EST', 'UTC'))
        if product['name'] == 'CO2 price':
            next_contract = min([c['contract_date'] for c in contracts if c['contract_date'].month == 12])
        else:
            next_contract = min([c['contract_date'] for c in contracts])
        market_id = [c['marketId'] for c in contracts if c['contract_date'] == next_contract][0]
        data_url = f'https://www.theice.com/marketdata/DelayedMarkets.shtml?' \
                   f'getHistoricalChartDataAsJson=&marketId={market_id}&historicalSpan=3'
        data_list = [{'product': product['name'], 'date': parser.parse(x[0]), 'value': x[1]} for x in
                     requests.get(data_url).json()['bars']]
        return data_list

    @classmethod
    def _product_data(cls):
        csv_file = utils.load_csv((resources.files(parms_ICE) / 'commodities.csv'))
        _parms_dict = {obs['product']: obs for obs in csv_file}
        return _parms_dict
