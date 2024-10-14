from loguru import logger
from .utils import add_stop_time_by_duration, convert_date_string

import requests


class UpdateFromAstro:
    def __init__(self):
        self.base_url = "https://contenthub-api.eco.astro.com.my/channel/{id}.json"
        self.date_format = "%Y-%m-%d %H:%M:%S.%f"
        self.delta = 8

    def fetch_programs(self, id):
        try:
            response = requests.get(self.base_url.format(id=id))
            response.raise_for_status()
            epg_json = response.json()

            if epg_json.get("responseCode") != 200:
                logger.warning(
                    f"Failed to fetch programs for channel {id}. Response code: {epg_json.get('responseCode')}"
                )
                return []

            programmes = [
                {
                    "start": convert_date_string(
                        item["datetimeInUtc"], self.date_format, self.delta
                    ),
                    "stop": item["duration"],
                    "title": item["title"],
                }
                for date_item in epg_json["response"]["schedule"].values()
                for item in date_item
            ]

            if programmes:
                add_stop_time_by_duration(programmes, "%H:%M:%S")

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
    updater = UpdateFromAstro()
    print(updater.fetch_programs("154"))
