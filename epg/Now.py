from loguru import logger
from .utils import (
    convert_timestamp,
)

import requests


class UpdateFromNow:
    def __init__(self):
        self.base_url = (
            "https://now.rule-set.workers.dev/?channel_id={id}&day={day}"
        )

        """Cookie (Chinese Version)"""
        self.headers = {
            "Cookie": "LANG=zh;",
        }

    def fetch_programs(self, id):
        programmes = []

        for day in range(0, 8):
            try:
                epg_json = requests.get(
                    self.base_url.format(id=id, day=day), headers=self.headers
                ).json()

                epg_items = epg_json[0]

                if len(epg_items) == 0:
                    logger.warning(f"Failed to fetch programs for channel {id}.")
                    return []

                programs_extracted = [
                    {
                        "start": convert_timestamp(item["start"] // 1000),
                        "stop": convert_timestamp(item["end"] // 1000),
                        "title": item["name"],
                    }
                    for item in epg_items
                ]

                programmes.extend(programs_extracted)

            except requests.RequestException as e:
                logger.error(f"Network request failed for {id} on {day}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error for {id} on {day}: {e}")
                continue

        if programmes:
            logger.info(
                f"Successfully fetched and processed {len(programmes)} programs for {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")
        return programmes


if __name__ == "__main__":
    updater = UpdateFromNow()
    print(updater.fetch_programs("096"))
