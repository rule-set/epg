from loguru import logger
from .utils import (
    add_stop_time_by_second,
    convert_date_string,
    generate_formatted_date_range,
)

import requests


class UpdateFromSingtel:
    def __init__(self):
        self.base_url = (
            "https://www.singtel.com/etc/singtel/public/tv/epg-parsed-data/{date}.json"
        )

        self.date_format = "%Y-%m-%dT%H:%M:%S"
        self.delta = 0

    def fetch_programs(self, id):
        programmes = []

        dates = generate_formatted_date_range(
            start_days_ago=1,
            end_days_in_future=7,
            fmt="%d%m%Y",
            tz="Asia/Singapore",
        )

        for date in dates:
            try:
                epg_json = requests.get(self.base_url.format(date=date)).json()
                epg_items = epg_json[id]
                programmes.extend(
                    [
                        {
                            "start": convert_date_string(
                                item["startDateTime"],
                                format=self.date_format,
                                delta=self.delta,
                            ),
                            "stop": item["duration"],
                            "title": item["program"]["title"],
                        }
                        for item in epg_items
                    ]
                )

            except requests.RequestException as e:
                logger.error(f"Network request failed for {id} on {date}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error for {id} on {date}: {e}")
                continue

        if programmes:
            add_stop_time_by_second(programmes)

            logger.info(
                f"Successfully fetched and processed {len(programmes)} programs for {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromSingtel()
    updater.fetch_programs("5502")
