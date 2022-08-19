import numpy as np
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

from src.database.models import SiteData


@dataclass
class SolutionBrick:
    product_id: int
    product_name: str
    start_time: datetime
    end_time: datetime

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "start_time": str(self.start_time),
            "end_time": str(self.end_time)
        }

    @classmethod
    def from_dict(cls, data_dict):
        """
        expects start_time/end_time to be in format Y-m-D H:M:S i.e 2022-09-20 19:30:00
        :param data_dict:
        :return:
        """
        res = cls(**data_dict)
        res.start_time = datetime.strptime(res.start_time, "%Y-%m-%d %H:%M:%S")
        res.end_time = datetime.strptime(res.end_time, "%Y-%m-%d %H:%M:%S")
        return res


@dataclass
class SolutionSchedule:
    start_date: date
    data: Dict[str, List[SolutionBrick]]

    @classmethod
    def create_from_raw(cls, raw: np.ndarray, site_data: SiteData):
        start_date = cls._get_start_date(site_data)
        data = cls._create_schedule(raw, start_date, site_data)
        return cls(start_date=start_date, data=data)

    def to_dict(self):
        return {
            "start_date": str(self.start_date),
            "data": {key: [l.to_dict() for l in lst] for key, lst in self.data.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str]):
        """
        able to receive json data and create the proper solution
        :param data:
        :return:
        """
        return cls(start_date=data["start_date"], data={key: [SolutionBrick.from_dict(l) for l in lst] for key, lst in data["data"].items()})

    @classmethod
    def _create_schedule(cls, raw, start_date, site_data) -> Dict[str, List[SolutionBrick]]:
        data = {str(prd_line['id']): [] for prd_line in site_data.json_data["production_lines"]}

        for prd_line in range(site_data.num_production_lines):
            for prd in range(site_data.num_products):
                for hr in range(site_data.total_working_hours):
                    if raw[prd_line][prd][hr] == 1:
                        prd_name = cls._get_product_name(site_data, prd)
                        day, hour_in_day = cls._get_day_and_hour_offsets(hr, site_data)
                        start_time = datetime.strptime(str(start_date), "%Y-%m-%d") + timedelta(days=day,
                                                                                                hours=hour_in_day)
                        end_time = datetime.strptime(str(start_time), "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)
                        (data[str(prd_line)]).append(
                            SolutionBrick(product_id=prd, product_name=prd_name, start_time=start_time,
                                          end_time=end_time))
        return data

    @classmethod
    def _get_day_and_hour_offsets(cls, hour_num: int, site_data: SiteData) -> (int, int):
        work_day_length = (site_data.json_data["num_shifts"] * site_data.json_data["shift_duration"])
        day = round(hour_num / work_day_length)
        hour_in_day = hour_num % work_day_length + site_data.json_data["usual_start_hour"]
        return day, hour_in_day

    @classmethod
    def _get_start_date(cls, site_data: SiteData) -> date:
        return site_data.schedule_start_date

    @classmethod
    def _get_product_name(cls, site_data: SiteData, product_id) -> Optional[str]:
        for prd in site_data.json_data["products"]:
            if prd["id"] == product_id:
                return prd["name"]

        return None