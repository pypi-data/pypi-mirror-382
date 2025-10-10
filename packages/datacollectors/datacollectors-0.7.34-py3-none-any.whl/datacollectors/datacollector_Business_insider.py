import requests
from dateutil import parser
from importlib import resources
import incentivedkutils as utils

from . import parms_business_insider


class Business_insider():
    @staticmethod
    def metals_prices(commodity, start_date, end_date):
        _data = Business_insider._data_loader(commodity, start_date, end_date)
        _data = [{'date': parser.parse(obs['Date']), 'value': obs['Close'], 'metal': commodity} for obs in _data]
        return _data

    @staticmethod
    def show_metals():
        csv_file = utils.load_csv((resources.files(parms_business_insider) / 'metal_codes.csv'))
        list_of_metals = sorted([obs['metal']  for obs in csv_file])
        return list_of_metals


    @classmethod
    def _data_loader(cls, commodity, start_date, end_date):
        product_dict = cls._parms()
        url_base = f'https://markets.businessinsider.com/Ajax/Chart_GetChartData?instrumentType=Commodity'
        url_commodity = f'&tkData=300002,{product_dict[commodity]},0,333'
        url_date = f'&from={start_date.strftime("%Y%m%d")}&to={end_date.strftime("%Y%m%d")}'
        url = f'{url_base}{url_commodity}{url_date}'
        _indata = requests.get(url).json()
        return _indata

    @classmethod
    def _parms(cls):
        csv_file = utils.load_csv((resources.files(parms_business_insider) / 'metal_codes.csv'))
        _parms_dict = {obs['metal']: int(obs['code']) for obs in csv_file}
        return _parms_dict
