from loguru import logger
from .utils import convert_timestamp, generate_timestamp_range

import requests


class UpdateFromStarHub:
    def __init__(self):
        self.base_url = "https://waf-starhub-metadata-api-p001.ifs.vubiquity.com/v3.1/epg/schedules?locale=zh&locale_default=en_US&device=1&in_channel_id={id}&gt_end={start_ts}&lt_start={end_ts}&limit=1000&page=1"

    def fetch_programs(self, id):
        try:
            start_ts, end_ts = generate_timestamp_range(
                start_days_ago=7, end_days_in_future=14
            )
            epg_json = requests.get(
                self.base_url.format(start_ts=start_ts, end_ts=end_ts, id=id)
            ).json()

            if epg_json.get("resources", []) == []:
                logger.warning(f"Failed to fetch programs for channel {id}.")
                return []

            epg_items = epg_json["resources"]
            programmes = [
                {
                    "start": convert_timestamp(item["start"]),
                    "stop": convert_timestamp(item["end"]),
                    "title": f'{item.get("serie_title", "")} - {item.get("title", "")}'.strip(
                        " -"
                    ),
                }
                for item in epg_items
            ]

            if programmes:
                logger.info(
                    f"Successfully fetched and processed {len(programmes)} programs for {id}."
                )
            else:
                logger.warning(f"No programme information was fetched for {id}.")
            return programmes

        except requests.RequestException as e:
            logger.error(f"Request error for channel {id}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred for channel {id}: {e}")


if __name__ == "__main__":
    updater = UpdateFromStarHub()
    print(updater.fetch_programs("dc1af464-7877-46dd-95f0-f81ecd1e3677"))
