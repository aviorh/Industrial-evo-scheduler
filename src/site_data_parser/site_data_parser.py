import json
from src.site_data_parser.data_classes import SiteData


class SiteDataParser:
    @staticmethod
    def parse_file():
        with open('../../tests/files/site_data.json', 'r') as site_data_file:
            site_data_dict = json.load(site_data_file)


if __name__ == '__main__':
    SiteDataParser.parse_file()
