from datetime import datetime, timedelta
from importlib import resources
from urllib.parse import unquote

import incentivedkutils as utils
import requests
from dateutil.relativedelta import relativedelta

from . import parms_barchart


class Barchart:
    commodity_codes = utils.load_csv((resources.files(parms_barchart) / 'commodity_codes.csv'))
    month_codes = utils.load_csv((resources.files(parms_barchart) / 'month_codes.csv'))

    @staticmethod
    def show_commodities():
        commodities = sorted([c['commodity'] for c in Barchart.commodity_codes])
        print(commodities)

    @staticmethod
    def commodity_prices(commodity, start_date):
        Barchart.commodity = commodity
        contracts = lib.build_contracts_list(commodity, start_date)
        indata = lib.get_data(contracts)
        indata_dicts = lib.read_data(indata)
        timeseries = lib.create_timeseries(indata_dicts)
        return timeseries


class lib(Barchart):
    @classmethod
    def create_timeseries(cls, indata_dicts):
        dates = sorted(list(set([obs['date'] for obs in indata_dicts])))
        out_list = []
        for date in dates:
            date_obs = [obs for obs in indata_dicts if obs['date'] == date]
            price = [obs['close'] for obs in date_obs if
                     obs['contract_start'] == min([obs['contract_start'] for obs in date_obs])][0]
            out_list.append({'date': date, 'value': price, 'commodity': Barchart.commodity})
        return out_list

    @classmethod
    def read_data(cls, in_list):
        out_list = []
        keys = ['contract', 'date', 'open', 'high', 'low', 'close', 'volume', 'interest']
        for c in in_list:
            c_list = [tuple(x.split(',')) for x in c[1].split('\n')]
            obs_dicts = [dict(zip(keys, x)) for x in c_list]
            obs_dicts = [{k: v for k, v in obs.items() if k in ['contract', 'date', 'close']} for obs in obs_dicts]
            obs_list = []
            for obs in obs_dicts:
                if obs['contract'] and int(obs['date'][:4]) >= (c[0]['year']) - 1:
                    obs['date'] = datetime.strptime(obs['date'], '%Y-%m-%d')
                    obs['contract_start'] = datetime(c[0]['year'], c[0]['month'], 1)
                    for k in [k for k in obs.keys() if
                              k not in ['contract', 'date', 'contract_year', 'contract_month', 'contract_start']]:
                        obs[k] = float(obs[k])
                    obs_list.append(obs)
            out_list.append(obs_list)
        out_list = utils.flatten_list(out_list)
        return out_list

    @classmethod
    def get_data(cls, contracts):
        headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"}
        url_site = 'https://www.barchart.com/futures/quotes/TGH16/overview'
        url_base = f'https://www.barchart.com/proxies/timeseries/queryeod.ashx?data=daily&maxrecords=60&volume=total&order=asc&dividends=false&backadjust=false&daystoexpiration=1&contractroll=expiration&symbol='
        out_list = []
        with requests.Session() as s:
            s.get(url_site, headers=headers)
            headers["X-XSRF-TOKEN"] = unquote(s.cookies["XSRF-TOKEN"])
            for contract in contracts[:]:
                indata = s.get(f"{url_base}{contract['contract']}", headers=headers).text
                out_list.append((contract, indata))
        return out_list

    @classmethod
    def build_contracts_list(cls, commodity, start_date):
        months = (datetime.today() - start_date) // timedelta(days=30) + 2
        c_months = {int(x['month_no']): x['contract_month'] for x in Barchart.month_codes}
        commodity_code = [c['symbol'] for c in Barchart.commodity_codes if c['commodity'] == commodity][0]
        contracts_list = [{'contract': f'{commodity_code}{c_months[m.month].upper()}{str(m.year)[-2:]}', 'year': m.year,
                           'month': m.month} for m in [start_date + relativedelta(months=m) for m in range(months)]]
        return contracts_list
