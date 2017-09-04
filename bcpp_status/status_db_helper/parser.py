from arrow.arrow import Arrow
from datetime import datetime


def datetime_parser(json_dict):
    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    date_format2 = '%Y-%m-%d'
    for (key, value) in json_dict.items():
        if value:
            try:
                dt = datetime.strptime(value, date_format)
                json_dict[key] = Arrow.fromdatetime(dt).datetime
            except TypeError:
                pass
            except ValueError:
                try:
                    dt = datetime.strptime(value[:10], date_format2)
                    json_dict[key] = Arrow.fromdatetime(dt).date()
                except ValueError:
                    pass
    return json_dict
