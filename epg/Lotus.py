from loguru import logger
from .utils import (
    add_stop_time_to_info,
    convert_timestamp,
    generate_ts_from_monday,
    time_to_seconds,
)
import re
import requests


class UpdateFromLotus:
    def __init__(self):
        self.base_url = "http://www.macaulotustv.cc/index.php/index/getdetail.html"

    def fetch_programs(self, program_id):
        programmes = []
        for ts in generate_ts_from_monday(end_days=7):
            try:
                response = requests.post(self.base_url, data={"d": ts})
                content = response.content.decode("unicode_escape")
                if len(content) == 4:
                    logger.warning(
                        f"Failed to fetch programs for {program_id} on {ts}."
                    )
                    continue
                start_times = re.findall(r"<em>(.*?)<\/em>", content)
                titles = re.findall(r"<span>(.*?)<\/span>", content)
                if start_times and titles:
                    programmes.extend(
                        [
                            {
                                "start": convert_timestamp(
                                    ts - 86400 + time_to_seconds(int(start_time))
                                    if i == 0
                                    and time_to_seconds(int(start_time)) > 43200
                                    else ts + time_to_seconds(int(start_time))
                                ),
                                "title": title,
                            }
                            for i, (start_time, title) in enumerate(
                                zip(start_times, titles)
                            )
                        ]
                    )
            except requests.RequestException as e:
                logger.error(f"Request failed for {program_id} on {ts}: {e}")
            except Exception as e:
                logger.error(f"Error for {program_id} on {ts}: {e}")
        if programmes:
            add_stop_time_to_info(programmes)
            logger.info(f"Fetched {len(programmes)} programs for {program_id}.")
        else:
            logger.warning(f"No programs fetched for {program_id}.")
        return programmes


if __name__ == "__main__":
    UpdateFromLotus().fetch_programs("Lotus")
