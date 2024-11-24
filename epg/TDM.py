from loguru import logger
from .utils import (
    add_stop_time_to_info,
    convert_date_string,
    generate_formatted_date_range,
)

import requests


class UpdateFromTDM:
    def __init__(self):
        """Request API"""
        self.base_url = (
            "https://www.tdm.com.mo/api/v1.0/program-list/{date}?channelId={id}"
        )

        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.delta = 0

    def fetch_programs(self, id):
        programmes = []
        dates = generate_formatted_date_range(
            start_days_ago=7, end_days_in_future=7, fmt="%Y-%m-%d"
        )

        for date in dates:
            try:
                epg_json = requests.get(self.base_url.format(date=date, id=id)).json()
                if epg_json.get("message", "") != "OK":
                    logger.warning(f"Failed to fetch programs for channel {id}.")
                    return []

                epg_items = epg_json.get("data", [])

                programs_extracted = [
                    {
                        "start": convert_date_string(
                            item["date"], self.date_format, self.delta
                        ),
                        "title": item["title"],
                    }
                    for item in epg_items
                ]

                programmes.extend(programs_extracted)

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

            add_stop_time_to_info(programmes)
        else:
            logger.warning(f"No programme information was fetched for {id}.")
        return programmes


if __name__ == "__main__":
    updater = UpdateFromTDM()
    updater.fetch_programs("1")
