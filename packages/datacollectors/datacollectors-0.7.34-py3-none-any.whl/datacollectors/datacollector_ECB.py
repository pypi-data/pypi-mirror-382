import csv
from datetime import datetime, timedelta

import requests
from dateutil import parser


class ECB():
    @staticmethod
    def exrates(currency, denominator, start_date, end_date, decimals=4):
        weekday_no = start_date.isoweekday()
        if weekday_no > 5:
            start_date = start_date - timedelta(days=weekday_no - 5)
        if denominator == 'EUR':
            _exrates = ECB._exrate_loader(currency, start_date, end_date, decimals)
        elif currency == 'EUR':
            _exrates = ECB._exrate_loader(denominator, start_date, end_date, decimals)
            _exrates = {dte: round(1 / _exrates[dte], decimals) for dte in _exrates}
        else:
            _exrates_currency = ECB._exrate_loader(currency, start_date, end_date, 10)
            _exrates_denominator = ECB._exrate_loader(denominator, start_date, end_date, 10)
            _exrates = {dte: round(_exrates_currency[dte] / _exrates_denominator[dte], decimals) for dte in
                        _exrates_denominator}
        _exrates = [{'date': obs, 'exrate':f'{currency} per {denominator}',
                     'denominator': denominator,
                     'currency': currency,
                     'value': _exrates[obs]} for obs in _exrates]
        return _exrates

    @classmethod
    def _exrate_loader(cls, currency, start_date, end_date, decimals):
        baseurl = 'https://sdw-wsrest.ecb.europa.eu/service/data/EXR'
        url = f'{baseurl}/D.{currency}.EUR.SP00.A'
        _parameters = {'startPeriod': start_date.strftime('%Y-%m-%d'), 'endPeriod': end_date.strftime('%Y-%m-%d')}
        _response = requests.get(url, params=_parameters, headers={'Accept': 'text/csv'})
        _decoded_content = _response.content.decode('utf-8')
        _in_list = list(csv.reader(_decoded_content.splitlines(), delimiter=','))
        _exrates = {parser.parse(l[6]): round(float(l[7]), decimals) for l in _in_list[1:]}
        # for _date_index in range((end_date - start_date).days):
        #     _start_date = datetime(start_date.year, start_date.month, start_date.day)
        #     _date_test = _start_date + timedelta(days=_date_index)
        #     if _date_test in _exrates:
        #         if _date_test + timedelta(days=1) not in _exrates:
        #             _exrates[_date_test + timedelta(days=1)] = _exrates[_date_test]
        return _exrates
