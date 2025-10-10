import requests


class Boliga():
    @staticmethod
    def huspriser(zip, from_year=2016):
        baseurl = f'https://api.boliga.dk/api/v2/sold/search/results?searchTab=1&sort=date-d&street=&propertyType=1&pageSize=100000&page=1'
        url = f'{baseurl}&zipcodeFrom={str(zip)}&zipcodeTo={str(zip)}&salesDateMin={str(from_year)}'
        return requests.get(url).json()['results']
