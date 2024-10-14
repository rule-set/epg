from loguru import logger
from .utils import (
    convert_date_string,
    generate_formatted_date_range,
)

import requests


class UpdateFromVercel:
    def __init__(self):
        self.base_url = "https://tv-guide.vercel.app/api/stationAirings?stationId={id}&startDateTime={date}"

        self.date_format = "%Y-%m-%dT%H:%MZ"
        self.delta = 8

    def fetch_programs(self, id):
        programmes = []

        dates = generate_formatted_date_range(
            start_days_ago=7,
            end_days_in_future=7,
            fmt="%Y-%m-%d",
            tz="America/Los_Angeles",
        )

        for date in dates:
            try:
                epg_items = requests.get(self.base_url.format(date=date, id=id)).json()
                programmes.extend(
                    [
                        {
                            "start": convert_date_string(
                                item["startTime"],
                                format=self.date_format,
                                delta=self.delta,
                            ),
                            "stop": convert_date_string(
                                item["endTime"],
                                format=self.date_format,
                                delta=self.delta,
                            ),
                            "title": item["program"]["title"],
                        }
                        for item in epg_items
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
    updater = UpdateFromVercel()
    updater.fetch_programs("10240")
