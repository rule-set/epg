from loguru import logger
from .utils import convert_timestamp, generate_timestamp_range

import requests


class UpdateFromBFGD:
    def __init__(self):
        self.base_url = "http://slave.bfgd.com.cn/media/event/get_list?chnlid={id}&pageidx=1&vcontrol=0&attachdesc=1&repeat=1&pagenum=2048&accesstoken=R621C86FCU319FA04BK783FB5EBIFA29A0DEP2BF4M340CAC5V0Z339C9W16D7E5AFCA1ADFD1&endtime={end_ts}&starttime={start_ts}&flagposter=0"

    def fetch_programs(self, id):
        try:
            start_ts, end_ts = generate_timestamp_range(
                start_days_ago=7, end_days_in_future=7
            )
            epg_json = requests.get(
                self.base_url.format(start_ts=start_ts, end_ts=end_ts, id=id)
            ).json()

            if epg_json.get("ret") != 0:
                logger.warning(f"Failed to fetch programs for channel {id}.")
                return []

            epg_items = epg_json["event_list"]
            programmes = [
                {
                    "start": convert_timestamp(item["start_time"]),
                    "stop": convert_timestamp(item["end_time"]),
                    "title": item["event_name"],
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
    updater = UpdateFromBFGD()
    updater.fetch_programs("4200000350")
