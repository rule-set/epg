from loguru import logger
from .utils import (
    add_stop_time_to_info,
    convert_date_string,
    generate_formatted_date_range,
)

import requests


class UpdateFromMyTVSuper:
    def __init__(self):
        self.base_url = (
            "https://content-api.mytvsuper.com/v1/epg?network_code={id}&from={date}"
        )
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.delta = 0

    def fetch_programs(self, id):
        programmes = []
        dates = generate_formatted_date_range(
            start_days_ago=7, end_days_in_future=7, fmt="%Y%m%d"
        )

        for date in dates:
            try:
                response = requests.get(self.base_url.format(id=id, date=date))
                response.raise_for_status()
                epg_json = response.json()[0]

                if epg_json.get("network_code") == "":
                    logger.warning(f"Failed to fetch programs for channel {id}.")
                    continue

                programs_extracted = [
                    {
                        "start": convert_date_string(
                            item["start_datetime"], self.date_format, self.delta
                        ),
                        "title": item["programme_title_tc"],
                    }
                    for data_item in epg_json["item"]
                    for item in data_item["epg"]
                ]

                programmes.extend(programs_extracted)

            except requests.RequestException as e:
                logger.error(f"Network request failed for {id} on {date}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error for {id} on {date}: {e}")
                continue

        if programmes:
            add_stop_time_to_info(programmes)
            logger.info(
                f"Successfully fetched and processed {len(programmes)} programs for {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromMyTVSuper()
    updater.fetch_programs("CJTV")
