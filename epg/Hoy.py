from loguru import logger
from lxml import etree
from .utils import convert_date_string, generate_formatted_date

import requests


class UpdateFromHOY:
    def __init__(self):
        self.base_url = "https://epg-file.hoy.tv/hoy/OTT{id}{date}.xml"
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.delta = 0

    def fetch_programs(self, id):
        try:
            now, _ = generate_formatted_date(
                start_days_ago=0, end_days_in_future=0, fmt="%Y%m%d"
            )
            content = requests.get(
                self.base_url.format(id=id, date=now),
            ).content
        except requests.RequestException as e:
            logger.error(f"Request error for channel {id}: {e}")
            return []

        root = etree.fromstring(content)

        epg_items = root.xpath(".//EpgItem")
        programmes = [
            {
                "start": convert_date_string(
                    item.findtext("EpgStartDateTime"), self.date_format, self.delta
                ),
                "stop": convert_date_string(
                    item.findtext("EpgEndDateTime"), self.date_format, self.delta
                ),
                "title": (
                    f"{item.findtext('EpisodeInfo/EpisodeShortDescription')}#{item.findtext('EpisodeInfo/EpisodeIndex')}"
                    if item.findtext("EpisodeInfo/EpisodeIndex") != "0"
                    else item.findtext("EpisodeInfo/EpisodeShortDescription")
                ),
            }
            for item in epg_items
        ]

        if programmes:
            logger.info(
                f"Successfully fetched {len(programmes)} programs for channel {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromHOY()
    updater.fetch_programs("76")
