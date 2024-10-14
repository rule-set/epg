from loguru import logger
from lxml import html
from .utils import (
    add_stop_time_to_info,
    convert_date_with_tz,
    generate_formatted_date_range,
)

import requests


class UpdateFromTVPassport:
    def __init__(self):
        self.base_url = "https://www.tvpassport.com/tv-listings/stations/{id}/{date}"
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.tz = "America/New_York"

    def fetch_programs(self, id):
        programmes = []
        dates = generate_formatted_date_range(
            start_days_ago=7, end_days_in_future=7, fmt="%Y-%m-%d"
        )

        for date in dates:
            try:
                content = requests.get(
                    self.base_url.format(date=date, id=id)
                ).content.decode("utf-8")

                tree = html.fromstring(content)
                epg_items = tree.xpath('//div[@class="list-group-item"]')

                programmes.extend(
                    [
                        {
                            "start": convert_date_with_tz(
                                item.get("data-st"), self.date_format, self.tz
                            ),
                            "title": item.get("data-showname"),
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
            add_stop_time_to_info(programmes)
            logger.info(
                f"Successfully fetched and processed {len(programmes)} programs for {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromTVPassport()
    updater.fetch_programs("nbc-knbc-los-angeles-ca/2588")
