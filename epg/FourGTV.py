from loguru import logger
from .utils import (
    convert_date_string,
)
import cloudscraper


class UpdateFrom4GTV:
    def __init__(self):
        self.base_url = "https://www.4gtv.tv/proglist/{id}.txt"
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.delta = 0
        self.scraper = cloudscraper.create_scraper()

    def fetch_programs(self, id):
        try:
            rsp = self.scraper.get(self.base_url.format(id=id))
            rsp.encoding = "utf-8"

            epg_json = rsp.json()

            programmes = [
                {
                    "start": convert_date_string(
                        f'{item["sdate"]} {item["stime"]}',
                        format=self.date_format,
                        delta=self.delta,
                    ),
                    "stop": convert_date_string(
                        f'{item["edate"]} {item["etime"]}',
                        format=self.date_format,
                        delta=self.delta,
                    ),
                    "title": item["title"],
                }
                for item in epg_json
            ]
        except Exception as e:
            logger.error(f"Unexpected error for {id} on: {e}")
            programmes = []

        if programmes:
            logger.info(
                f"Successfully fetched and processed {len(programmes)} programs for {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFrom4GTV()
    updater.fetch_programs("litv-ftv13")
