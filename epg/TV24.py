from loguru import logger
from lxml import html
from .utils import (
    add_stop_time_to_info,
    convert_date_with_tz,
    generate_formatted_date_range,
)

import requests


class UpdateFromTV24:
    def __init__(self):
        self.base_url = "https://tv24.co.uk/x/channel/{id}/0/{date}"
        self.date_format = "%Y-%m-%d %I:%M%p"
        self.tz = "Europe/London"

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

                epg_items = tree.xpath('//a[@class="program"]')

                programmes.extend(
                    [
                        {
                            "start": convert_date_with_tz(
                                "{} {}".format(
                                    date, item.xpath('.//span[@class="time"]/text()')[0]
                                ),
                                self.date_format,
                                self.tz,
                            ),
                            "title": item.xpath(".//h3/text()")[0],
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
    updater = UpdateFromTV24()
    print(updater.fetch_programs("nbc-news-now"))
