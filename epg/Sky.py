from loguru import logger
from .utils import convert_timestamp, generate_formatted_date_range

import requests


class UpdateFromSky:
    def __init__(self):
        self.base_url = "https://awk.epgsky.com/hawk/linear/schedule/{date}/{id}"

    def fetch_programs(self, id):
        programmes = []
        dates = generate_formatted_date_range(
            start_days_ago=1, end_days_in_future=7, fmt="%Y%m%d"
        )

        for date in dates:
            try:
                epg_json = requests.get(self.base_url.format(date=date, id=id)).json()
                epg_items = epg_json["schedule"][0]["events"]

                programmes.extend(
                    [
                        {
                            "start": convert_timestamp(item["st"]),
                            "stop": convert_timestamp(item["st"] + item["d"]),
                            "title": item["t"],
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
    updater = UpdateFromSky()
    updater.fetch_programs("1726")
