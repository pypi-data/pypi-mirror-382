from datetime import datetime, timedelta

import requests


class Energidataservice:
    @staticmethod
    def gasprices_until_20221001(start_date=datetime(2010, 1, 1), end_date=datetime(2023, 10, 1)):
        import pandas as pd
        start_date_str = start_date.strftime("%Y-%m-%dT00:00")
        end_date_str = (end_date + timedelta(days=1)).strftime("%Y-%m-%dT00:00")
        base_url=f'https://api.energidataservice.dk/dataset/GasSystemBalanceUntil20221001?'
        url = f'{base_url}&start={start_date_str}&end={end_date_str}'
        indata_json = requests.get(url).json()['records']
        for d in indata_json:
            d.update((k, datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')) for k, v in d.items() if k in ['GasDay','Created'])
        indata_json=[obs for obs in indata_json if (obs['BalanceType']=='SCB' and obs['ProductCode'] == 'Valid ordinary')]
        indata_json = [obs for obs in indata_json if obs['ProductCode'] == 'Valid ordinary']
        df = pd.DataFrame(indata_json).sort_values(['GasDay', 'Created'])
        df = df.drop_duplicates(subset=['GasDay'], keep='first')
        indata_json=df.to_dict('records')
        return indata_json

    @staticmethod
    def gasprices(start_date=datetime(2020, 1, 1), end_date=datetime(2030, 12, 31)):
        start_date_str = start_date.strftime("%Y-%m-%dT00:00")
        end_date_str = (end_date + timedelta(days=1)).strftime("%Y-%m-%dT00:00")
        base_url = f"https://api.energidataservice.dk/dataset/GasDailyBalancingPrice?offset=0"
        url = f"{base_url}&start={start_date_str}&end={end_date_str}&"
        indata_json = requests.get(url).json()['records']
        for d in indata_json:
            d.update((k, datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')) for k, v in d.items() if k in ['GasDay'])
        indata_json = sorted(indata_json, key=lambda d: d['GasDay'])
        return indata_json

    @staticmethod
    def dayahead_prices(area, start_date=datetime(2020, 1, 1), end_date=datetime(2030, 12, 31)):
        filters = f'{{"PriceArea":"{area}"}}'
        start_date_str = start_date.strftime("%Y-%m-%dT00:00")
        end_date_str = (end_date + timedelta(days=1)).strftime("%Y-%m-%dT00:00")
        base_url = f"https://api.energidataservice.dk/dataset/Elspotprices?offset=0"
        url = f"{base_url}&start={start_date_str}&end={end_date_str}&filter={filters}&sort=HourUTC ASC"
        indata_json = requests.get(url, verify=True).json()['records']
        for d in indata_json:
            d.update((k, datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')) for k, v in d.items() if k in ['HourUTC', 'HourDK'])
        return indata_json

    @staticmethod
    def production_consumption(area, start_date=datetime(2020, 1, 1), end_date=datetime(2030, 12, 31)):
        filters = f'{{"PriceArea":"{area}"}}'
        start_date_str = start_date.strftime("%Y-%m-%dT00:00")
        end_date_str = (end_date + timedelta(days=1)).strftime("%Y-%m-%dT00:00")
        base_url = f"https://api.energidataservice.dk/dataset/ProductionConsumptionSettlement?offset=0"
        url = f"{base_url}&start={start_date_str}&end={end_date_str}&filter={filters}&sort=HourUTC ASC"
        indata_json = requests.get(url, verify=True).json()['records']
        for d in indata_json:
            d.update((k, datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')) for k, v in d.items() if k in ['HourUTC', 'HourDK'])
        return indata_json

    @staticmethod
    def transmission_lines(area, start_date=datetime(2020, 1, 1), end_date=datetime(2030, 12, 31)):
        start_date_str = start_date.strftime("%Y-%m-%dT00:00")
        end_date_str = (end_date + timedelta(days=1)).strftime("%Y-%m-%dT00:00")
        base_url = f"https://api.energidataservice.dk/dataset/Transmissionlines?offset=0&sort=HourUTC ASC"
        url = f"{base_url}&start={start_date_str}&end={end_date_str}"
        indata_json = requests.get(url, verify=True).json()['records']
        indata_json = [obs for obs in indata_json if obs['PriceArea'] == area]
        for d in indata_json:
            d.update((k, datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')) for k, v in d.items() if
                     (k in ['HourUTC', 'HourDK'] and v))
        return indata_json

    @staticmethod
    def forecasts(area, start_date=datetime(2020, 1, 1), end_date=datetime(2030, 12, 31)):
        start_date_str = start_date.strftime("%Y-%m-%dT00:00")
        end_date_str = (end_date + timedelta(days=1)).strftime("%Y-%m-%dT00:00")
        base_url = f"https://api.energidataservice.dk/dataset/Forecasts_Hour?offset=0"
        url = f"{base_url}&start={start_date_str}&end={end_date_str}"
        indata_json = requests.get(url, verify=True).json()['records']
        indata_json = [obs for obs in indata_json if obs['PriceArea'] == area]
        for d in indata_json:
            d.update((k, datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')) for k, v in d.items() if
                     (k in ['HourUTC', 'HourDK'] and v))
        return indata_json
