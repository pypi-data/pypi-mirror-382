import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
# parms_path = f'{Path(__file__).parent}/parms/'
from importlib import resources
import pandas as pd

import incentivedkutils as utils
import requests
import xmltodict
from dateutil import parser

from . import parms_entsoe


class Entsoe:
    @staticmethod
    def dayahead_prices(token, area, start_date, end_date):
        return transmission.dayahead_prices(token, area, start_date, end_date)

    @staticmethod
    def production_by_unit(token, area, start_date, end_date):
        return generation.production_by_unit(token, area, start_date, end_date)

    @staticmethod
    def production_by_type(token, area, start_date, end_date):
        return generation.production_by_type(token, area, start_date, end_date)

    @staticmethod
    def consumption(token, area, start_date, end_date):
        return load.consumption(token, area, start_date, end_date)

    @staticmethod
    def show_code_areas(data_type):
        return lib.show_code_areas(data_type)


class lib:
    _max_workers = 6
    _max_requests_per_minute = 200
    _batch_duration = 10
    _entsoe_table_parms = utils.load_csv((resources.files(parms_entsoe) / 'entsoe_table_parms.csv'))

    @staticmethod
    def show_code_areas(entsoe_data_type):
        entsoe_table = ''
        if entsoe_data_type.lower() in ['a73', 'production_by_unit']:
            entsoe_table = 'A73'
        elif entsoe_data_type.lower() in ['a75', 'production_by_type']:
            entsoe_table = 'A75'
        elif entsoe_data_type.lower() in ['a65', 'consumption']:
            entsoe_table = 'A65'
        elif entsoe_data_type.lower() in ['a44', 'dayahead_prices']:
            entsoe_table = 'A44'
        if entsoe_table:
            entsoe_codes = lib._load_csvfile(entsoe_table)
            areas = sorted(list(set([c['area'] for c in entsoe_codes])))
        else:
            areas = 'Function not implemented'
        return areas

    @staticmethod
    def _load_csvfile(file_name):
        csv_file = utils.load_csv((resources.files(parms_entsoe) / f'{file_name}.csv'))
        return csv_file

    @classmethod
    def _load_entsoe_table(cls, doc_url_base, segment):
        if segment['from_date']:
            segment_from_date = parser.parse(segment['from_date'])
        else:
            segment_from_date = datetime(1000, 1, 1)
        segment_from_date = max(segment_from_date, cls._start_date)
        if segment['to_date']:
            segment_to_date = parser.parse(segment['to_date'])
        else:
            segment_to_date = datetime(2999, 1, 1)
        segment_to_date = min(segment_to_date, cls._end_date)
        tasks = cls._create_tasks(doc_url_base, segment_from_date, segment_to_date)
        indata_xml = cls._load_tasks(tasks)
        indata_list = utils.flatten_list([cls._read_xml(obs) for obs in indata_xml])
        cls._delete_duplicates(indata_list)
        return indata_list

    @classmethod
    def _delete_duplicates(cls, data_list):
        data_list = list(set([tuple((k, v) for k, v in obs.items()) for obs in data_list]))
        data_list = [{t[0]: t[1] for t in obs} for obs in data_list]
        data_list = sorted(data_list, key=lambda d: d['ts'])
        return data_list

    @classmethod
    def _create_tasks(cls, doc_url_base, start_date, end_date):
        _entsoe_table = [obs for obs in cls._entsoe_table_parms if obs['entsoe_table'] == cls._entsoe_table][0]
        _request_max_days = int(_entsoe_table['request_max_days'])
        _tasks = []
        _base_url = f'https://web-api.tp.entsoe.eu/api?securityToken={cls._token}'
        if end_date > datetime.today() + timedelta(days=2):
            cls._end_date = datetime.today() + timedelta(days=2)
        for datestep in range(0, (end_date - start_date).days + 1, _request_max_days):
            step_start = start_date + timedelta(days=datestep)
            step_end = (min(step_start + timedelta(days=_request_max_days - 1), end_date) + timedelta(
                hours=(int(_entsoe_table['last_hour']))))
            _url_time = f'periodStart={step_start.strftime("%Y%m%d%H00")}&periodEnd={step_end.strftime("%Y%m%d%H00")}'
            _url = f'{_base_url}&{doc_url_base}&{_url_time}'
            _tasks.append(_url)
        # utils.prt(_tasks)
        return _tasks

    @classmethod
    def _load_tasks(cls, tasks):
        _indata_list = []
        _batches = len(tasks) // cls._max_requests_per_minute
        for batch in range(_batches + 1):
            st = datetime.today().timestamp()
            with ThreadPoolExecutor(max_workers=cls._max_workers) as executor:
                _indata_list += list(executor.map(cls._load_single_xml, tasks[batch * cls._max_requests_per_minute:(
                                                                                                                               batch + 1) * cls._max_requests_per_minute]))
            duration = datetime.today().timestamp() - st
            if duration < cls._batch_duration and batch < _batches:
                print(f'waiting for {cls._batch_duration - duration} after batch {batch} of {_batches}')
                time.sleep(cls._batch_duration - duration)
        return _indata_list

    @classmethod
    def _read_xml(cls, indata_xml):
        try:
            indata_json = json.dumps(xmltodict.parse(indata_xml))
            indata_dict = json.loads(indata_json)
        except:
            indata_dict = {}
        out_list = []
        if 'GL_MarketDocument' in indata_dict.keys():
            timeseries = indata_dict['GL_MarketDocument']['TimeSeries']
        elif 'Publication_MarketDocument' in indata_dict.keys():
            timeseries = indata_dict['Publication_MarketDocument']['TimeSeries']
        else:
            timeseries = []
        if timeseries:
            if type(timeseries) != list:
                timeseries = [timeseries]
            for obs in timeseries:
                day_list=[]
                resolution= obs['Period']['resolution']
                ts_start = parser.parse(obs['Period']['timeInterval']['start'])
                if 'outBiddingZone_Domain.mRID' in obs:
                    flow_direction = -1
                else:
                    flow_direction = 1
                data_points = obs['Period']['Point']
                if type(data_points) != list:
                    data_points = [data_points]
                for point in data_points:
                    obs_dict = cls._read_point(obs, point, ts_start, int(resolution[-3:-1]), flow_direction)
                    day_list.append(obs_dict)
                if resolution =='PT60M':
                    df=pd.DataFrame(day_list)
                    df = df.set_index('ts')
                    df.index = pd.to_datetime(df.index)
                    df = df.resample('15min').ffill()
                    df = df.reset_index()
                    day_list = df.to_dict('records')
                out_list += day_list
        return out_list

    @classmethod
    def _load_single_xml(cls, task):
        try:
            r = requests.get(task)
            r.encoding = r.apparent_encoding
            indata_xml = r.text
        except:
            indata_xml = ''
        return indata_xml


class transmission(lib):
    @classmethod
    def dayahead_prices(cls, token, area, start_date, end_date=datetime(2030, 12, 31)):
        cls._token = token
        cls._entsoe_table = 'A44'
        cls._area = area
        cls._start_date = start_date
        cls._end_date = end_date
        in_list = cls._get_dayahead_prices()
        in_list = cls._delete_duplicates(in_list)
        return in_list

    @classmethod
    def _get_dayahead_prices(cls):
        if cls._area not in cls.show_code_areas(cls._entsoe_table):
            return 'Area not available'
        entsoe_codes = lib._load_csvfile(cls._entsoe_table)
        entsoe_codes = [c for c in entsoe_codes if c['area'] == cls._area]
        out_list = []
        for segment in entsoe_codes:
            doc_url_base = f'documentType={cls._entsoe_table}&processType=A16&in_Domain={segment["code"]}&out_Domain={segment["code"]}'
            indata_list = cls._load_entsoe_table(doc_url_base, segment)
            out_list += [dict(item, **{'area': cls._area, 'area_long': segment['area_long']}) for item in indata_list]
        return out_list

    @classmethod
    def _read_point(cls, obs, point, ts_start, time_resolution, flow_direction):
        obs_dict = {}
        if cls._entsoe_table == 'A44':
            obs_dict['ts'] = ts_start + timedelta(minutes=(int(point['position']) - 1) * time_resolution)
            obs_dict['value'] = float(point['price.amount'])
        return obs_dict


class generation(lib):
    @classmethod
    def production_by_unit(cls, token, area, start_date, end_date=datetime(2030, 12, 31)):
        cls._token = token
        cls._entsoe_table = 'A73'
        cls._area = area
        cls._start_date = start_date
        cls._end_date = end_date
        in_list = cls._get_production_A73()
        return in_list

    @classmethod
    def production_by_type(cls, token, area, start_date, end_date=datetime(2030, 12, 31)):
        cls._entsoe_table = 'A75'
        cls._token = token
        cls._area = area
        cls._start_date = start_date
        cls._end_date = end_date
        in_list = cls._get_production_A75()
        return in_list

    @classmethod
    def _get_production_A73(cls):
        if cls._area not in lib.show_code_areas(cls._entsoe_table):
            return 'Area not available'
        entsoe_codes = lib._load_csvfile(cls._entsoe_table)
        entsoe_codes = [c for c in entsoe_codes if c['area'] == cls._area]
        out_list = []
        for segment in entsoe_codes:
            code = segment['code']
            doc_url_base = f'documentType={cls._entsoe_table}&processType=A16&in_Domain={code}'

            out_list += cls._load_entsoe_table(doc_url_base, segment)
        return out_list

    @classmethod
    def _get_production_A75(cls):
        if cls._area not in lib.show_code_areas(cls._entsoe_table):
            return 'Area not available'
        entsoe_codes = lib._load_csvfile(cls._entsoe_table)
        entsoe_codes = [c for c in entsoe_codes if c['area'] == cls._area]
        out_list = []
        psr_codes = {c['Code']: c['Type'] for c in lib._load_csvfile('psr_types')}
        for segment in entsoe_codes:
            code = segment['code']
            doc_url_base = f'documentType={cls._entsoe_table}&processType=A16&in_Domain={code}'
            indata_list = cls._load_entsoe_table(doc_url_base, segment)
            indata_list = [dict(item, **{'type': psr_codes[item['psr_type']].lower(), 'area': cls._area}) for item in
                           indata_list]
            out_list += [{k: v for k, v in obs.items() if k not in ['psr_type']} for obs in indata_list]
            return out_list

    @classmethod
    def _read_point(cls, obs, point, ts_start, time_resolution, flow_direction):
        obs_dict = {}
        if cls._entsoe_table == 'A73':
            obs_dict['unit_name'] = obs['MktPSRType']['PowerSystemResources']['name']
            obs_dict['ts'] = ts_start + timedelta(minutes=(int(point['position']) - 1) * time_resolution)
            obs_dict['value'] = float(point['quantity']) * flow_direction
        if cls._entsoe_table == 'A75':
            obs_dict['psr_type'] = obs['MktPSRType']['psrType']
            obs_dict['ts'] = ts_start + timedelta(minutes=(int(point['position']) - 1) * time_resolution)
            obs_dict['value'] = float(point['quantity']) * flow_direction
        return obs_dict


class load(lib):
    @classmethod
    def consumption(cls, token, area, start_date, end_date=datetime(2030, 12, 31)):
        in_list = []
        cls._token = token
        cls._area = area
        cls._start_date = start_date
        cls._end_date = end_date
        in_list += cls._get_consumption_A65()
        return in_list

    @classmethod
    def _get_consumption_A65(cls):
        cls._entsoe_table = 'A65'
        entsoe_codes = lib._load_csvfile(cls._entsoe_table)
        entsoe_codes = [c for c in entsoe_codes if c['area'] == cls._area]
        out_list = []
        for segment in entsoe_codes:
            code = segment['code']
            doc_url_base = f'documentType={cls._entsoe_table}&processType=A16&OutBiddingZone_Domain={code}'
            out_list += cls._load_entsoe_table(doc_url_base, segment)
        return out_list

    @classmethod
    def _read_point(cls, obs, point, ts_start, time_resolution, flow_direction):
        obs_dict = {}
        if cls._entsoe_table == 'A65':
            obs_dict['type'] = 'consumption'
            obs_dict['ts'] = ts_start + timedelta(minutes=(int(point['position']) - 1) * time_resolution)
            obs_dict['value'] = float(point['quantity']) * flow_direction
        return obs_dict
