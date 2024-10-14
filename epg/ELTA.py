from loguru import logger
from .utils import convert_timestamp, generate_formatted_date_range
import requests


class UpdateFromELTA:
    def __init__(self):
        self.base_url = "https://piceltaott-elta.cdn.hinet.net/production/json/program_list/program_list_{date}.json"
        self.request_all_channel()

    def request_all_channel(self):
        try:
            dates = generate_formatted_date_range(
                start_days_ago=7, end_days_in_future=7, fmt="%Y-%m-%d"
            )
            self.all_channel_data = [
                requests.get(self.base_url.format(date=date)).json() for date in dates
            ]
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")

    def fetch_programs(self, id):
        programmes = [
            {
                "start": convert_timestamp(epg["start_time"]),
                "stop": convert_timestamp(epg["end_time"]),
                "title": epg["program_desc"],
            }
            for data in self.all_channel_data
            for epg in data[id][1:]
        ]

        if programmes:
            logger.info(
                f"Successfully fetched {len(programmes)} programs for channel {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromELTA()
    updater.fetch_programs("104")
