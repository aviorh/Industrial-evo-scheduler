import json

from werkzeug.datastructures import FileStorage

from src.site_data_parser.data_classes import SiteData


class SiteDataParser:
    @staticmethod
    def parse_file(file: FileStorage, id: int):
        file.seek(0)
        content = file.read()
        data_dict = json.loads(content)
        data_dict['id'] = id
        site_data = SiteData.from_dict(data_dict)
        return site_data, data_dict


if __name__ == '__main__':
    SiteDataParser.parse_file()
