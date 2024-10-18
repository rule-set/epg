from loguru import logger
from .utils import (
    convert_date_string,
    generate_formatted_date_range,
)

import json
import requests


class UpdateFromTBC:
    def __init__(self):
        self.base_url = "https://tbc.rule-set.workers.dev/?id={id}&date={date}"

        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.delta = 0

    def fetch_programs(self, id):
        dates = generate_formatted_date_range(
            start_days_ago=1, end_days_in_future=7, fmt="%Y%m%d"
        )
        programmes = []

        for date in dates:
            try:
                content = (
                    requests.get(self.base_url.format(date=date, id=id))
                    .content.decode("utf-8")[:-1]
                    .replace("result(", "")
                )

                epg_json = json.loads(content)
                epg_items = epg_json["data"]

                programmes.extend(
                    [
                        {
                            "start": convert_date_string(
                                item["starttime"],
                                format=self.date_format,
                                delta=self.delta,
                            ),
                            "stop": convert_date_string(
                                item["endtime"],
                                format=self.date_format,
                                delta=self.delta,
                            ),
                            "title": item["programname"],
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
            logger.info(
                f"Successfully fetched and processed {len(programmes)} programs for {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromTBC()
    print(updater.fetch_programs("240"))
