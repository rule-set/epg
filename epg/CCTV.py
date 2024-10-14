from loguru import logger
from .utils import (
    convert_timestamp,
    generate_formatted_date_range,
)

import requests


class UpdateFromCCTV:
    def __init__(self):
        """Request API"""
        self.base_url = "https://api.cntv.cn/epg/getEpgInfoByChannelNew?c={id}&serviceId=tvcctv&d={date}"

    def fetch_programs(self, id):
        programmes = []
        dates = generate_formatted_date_range(
            start_days_ago=7, end_days_in_future=7, fmt="%Y%m%d"
        )

        for date in dates:
            try:
                epg_json = requests.get(self.base_url.format(date=date, id=id)).json()
                if epg_json.get("errcode", "") != "":
                    logger.warning(f"Failed to fetch programs for channel {id}.")
                    return []

                epg_items = epg_json["data"][id].get("list", [])

                programs_extracted = [
                    {
                        "start": convert_timestamp(item["startTime"]),
                        "stop": convert_timestamp(item["endTime"]),
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
        else:
            logger.warning(f"No programme information was fetched for {id}.")
        return programmes


if __name__ == "__main__":
    updater = UpdateFromCCTV()
    updater.fetch_programs("cctv1")
