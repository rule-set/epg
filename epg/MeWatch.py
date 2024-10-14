from loguru import logger
from .utils import convert_date_string, generate_formatted_date_range
import requests


class UpdateFromMeWatch:
    def __init__(self):
        self.base_url = "https://cdn.mewatch.sg/api/schedules?channels={id}&date={date}&duration=24&hour=0&lang=chn"
        self.date_format = "%Y-%m-%dT%H:%M:%SZ"
        self.delta = 8

    def fetch_programs(self, id):
        dates = generate_formatted_date_range(
            start_days_ago=7, end_days_in_future=7, fmt="%Y-%m-%d"
        )
        programmes = []

        for date in dates:
            try:
                response = requests.get(self.base_url.format(date=date, id=id)).json()
                programmes.extend(
                    [
                        {
                            "start": convert_date_string(
                                item["startDate"],
                                format=self.date_format,
                                delta=self.delta,
                            ),
                            "stop": convert_date_string(
                                item["endDate"],
                                format=self.date_format,
                                delta=self.delta,
                            ),
                            "title": item["item"].get(
                                "secondaryLanguageTitle", item["item"]["title"]
                            ),
                        }
                        for item in response[0]["schedules"]
                    ]
                )
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
    updater = UpdateFromMeWatch()
    updater.fetch_programs("242036")
