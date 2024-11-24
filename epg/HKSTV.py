from loguru import logger
from lxml import html
from .utils import add_stop_time_to_info, convert_date_string

import cloudscraper
import json


class UpdateFromHKSTV:
    def __init__(self):
        self.base_url = "http://www.hkstv.tv/index/live.html"

        self.scraper = cloudscraper.create_scraper()

        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.delta = 0

    def fetch_programs(self, id):
        try:
            content = self.scraper.get(self.base_url.format(id=id)).content.decode(
                "utf-8"
            )
        except Exception as e:
            logger.error(f"Request error for channel {id}: {e}")
            return []

        tree = html.fromstring(content)
        epg = tree.xpath("//head/script/text()")
        epg = epg[0].replace("\n", "").replace("   // var epgdata = ", "")
        epg_json = json.loads(epg)
        dates = epg_json.keys()

        programmes = []

        for date in dates:
            epg_items = epg_json[date]
            programs_extracted = [
                {
                    "start": convert_date_string(
                        f'{item["program_date"]} {item["play_time"]}',
                        self.date_format,
                        self.delta,
                    ),
                    "title": item["title"],
                }
                for item in epg_items
            ]
            programmes.extend(programs_extracted)

        if programmes:
            logger.info(
                f"Successfully fetched and processed {len(programmes)} programs for {id}."
            )

            add_stop_time_to_info(programmes)
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromHKSTV()
    updater.fetch_programs("hkstv")
