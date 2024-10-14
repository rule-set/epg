from loguru import logger
from .utils import convert_date_string

import requests


class UpdateFromViuTV:
    def __init__(self):
        self.base_url = "https://olympics.viu.tv/prod/v1/epgs?startAt=20240715&endAt=20240815&channelId={id}"
        self.date_format = "%Y%m%d %H:%M"
        self.delta = 0

    def fetch_programs(self, id):
        try:
            response = requests.get(self.base_url.format(id=id))
            response.raise_for_status()
            epg_json = response.json()

            if type(epg_json) is not list:
                logger.warning(
                    f"Failed to fetch programs for channel {id}. Response code: {epg_json.get('error')}"
                )
                return []

            programmes = [
                {
                    "start": convert_date_string(
                        f'{item["date"]} {item["startTime"]}',
                        self.date_format,
                        self.delta,
                    ),
                    "stop": convert_date_string(
                        f'{item["date"]} {item["endTime"]}',
                        self.date_format,
                        self.delta,
                    ),
                    "title": item["title"][0],
                }
                for item in epg_json
            ]

            if programmes:
                logger.info(
                    f"Successfully fetched {len(programmes)} programs for channel {id}."
                )
            else:
                logger.warning(f"No programme information was fetched for {id}.")

            return programmes

        except requests.RequestException as e:
            logger.error(f"Request error for channel {id}: {e}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred for channel {id}: {e}")
            return []


if __name__ == "__main__":
    updater = UpdateFromViuTV()
    print(updater.fetch_programs("977"))
