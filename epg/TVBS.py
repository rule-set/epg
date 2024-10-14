from loguru import logger
from .utils import (
    add_stop_time_to_info,
    convert_date_string,
    generate_formatted_date_range,
)
import requests


class UpdateFromTVBS:
    def __init__(self):
        """Request API"""
        self.base_url = "https://tvbsapp.tvbs.com.tw/pg_api/pg_list/{id}/{date}"
        self.date_format = "%Y-%m-%d %H:%M"
        self.delta = 0

    def fetch_programs(self, id):
        dates = generate_formatted_date_range(
            start_days_ago=0, end_days_in_future=7, fmt="%Y-%m-%d"
        )
        programmes = []

        for date in dates:
            try:
                epg_json = requests.get(self.base_url.format(date=date, id=id)).json()
                epg_data = epg_json["data"]
                programmes.extend(
                    [
                        {
                            "start": convert_date_string(
                                f'{date} {item["pg_hour"]}',
                                format=self.date_format,
                                delta=self.delta,
                            ),
                            "title": item["pg_name"],
                        }
                        for data in epg_data
                        if data["date"] == date and data["data"] != False
                        for item in data["data"]
                    ]
                )
            except requests.RequestException as e:
                logger.error(f"Network request failed for {id} on {date}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error for {id} on {date}: {e}")

        if programmes:
            add_stop_time_to_info(programmes)
            logger.info(
                f"Successfully fetched and processed {len(programmes)} programs for {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromTVBS()
    updater.fetch_programs("3")
