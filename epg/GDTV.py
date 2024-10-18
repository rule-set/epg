from loguru import logger
from .utils import convert_timestamp, generate_formatted_date_range
import requests


class UpdateFromGDTV:
    def __init__(self):
        self.base_url = "https://gdtv.rule-set.workers.dev/?id={id}&date={date}"

    def fetch_programs(self, id):
        programmes = []
        dates = generate_formatted_date_range(
            start_days_ago=7, end_days_in_future=7, fmt="%Y-%m-%d"
        )

        for date in dates:
            try:
                rsp = requests.get(self.base_url.format(date=date, id=id))
                if rsp.status_code != 200:
                    logger.warning(
                        f"Failed to fetch programs for channel {id} @ {date}"
                    )
                    continue

                programmes.extend(
                    [
                        {
                            "start": convert_timestamp(item["startTime"]),
                            "stop": convert_timestamp(item["endTime"]),
                            "title": item["title"],
                        }
                        for item in rsp.json()
                    ]
                )
            except requests.RequestException as e:
                logger.error(f"Network request failed for {id} on {date}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error for {id} on {date}: {e}")

        if programmes:
            logger.info(
                f"Successfully fetched and processed {len(programmes)} programs for {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromGDTV()
    updater.fetch_programs("16")
