from loguru import logger
from lxml import html
from .utils import (
    add_stop_time_to_info,
    convert_date_string,
    generate_formatted_date_range,
)
import requests


class UpdateFromEntertainment:
    def __init__(self):
        self.url = "https://entertainment.ie/tv/{id}/date={date}"
        self.date_fmt = "%d-%m-%Y%H:%M"
        self.delta = 8

    def fetch_programs(self, id):
        programmes = []
        dates = generate_formatted_date_range(0, 7, "%d-%m-%Y")

        for date in dates:
            try:
                content = requests.get(self.url.format(id=id, date=date)).content
                tree = html.fromstring(content)
                titles = tree.xpath(
                    '//div[@class="text-holder"]/h3/a[@class="lightbox"]'
                )
                descs = tree.xpath('//a[@class="btn-share lightbox"]')
                times = tree.xpath('//span[@class="time"]')

                programmes.extend(
                    [
                        {
                            "start": convert_date_string(
                                f"{date}{time.text}", self.date_fmt, self.delta
                            ),
                            "title": f"{t.text.strip()} - {d.get('data-title')}",
                        }
                        for t, d, time in zip(titles, descs, times)
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
    updater = UpdateFromEntertainment()
    updater.fetch_programs("premier-sports-1")
