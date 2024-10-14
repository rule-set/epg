from loguru import logger
from .utils import convert_date_string, generate_formatted_date

import requests


class UpdateFromCtiTV:
    def __init__(self):
        self.base_url = "https://asia-east2-ctitv-237901.cloudfunctions.net/ctitv-API-program-list?chid={id}&start={start}&end={end}"

        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.delta = 0

    def fetch_programs(self, id):
        try:
            start, end = generate_formatted_date(
                start_days_ago=7, end_days_in_future=7, fmt="%Y-%m-%d"
            )
            epg_json = requests.get(
                self.base_url.format(start=start, end=end, id=id)
            ).json()

            if len(epg_json) == 0:
                logger.warning(f"Failed to fetch programs for channel {id}.")
                return []

            programmes = [
                {
                    "start": convert_date_string(
                        item["start"], self.date_format, self.delta
                    ),
                    "stop": convert_date_string(
                        item["end"], self.date_format, self.delta
                    ),
                    "title": item["title"],
                }
                for item in epg_json
            ]

        except requests.RequestException as e:
            logger.error(f"Network request failed for {id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {id}: {e}")

        if programmes:
            logger.info(
                f"Successfully fetched and processed {len(programmes)} programs for {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromCtiTV()
    updater.fetch_programs("52")
