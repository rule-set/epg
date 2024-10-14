from loguru import logger
from lxml import etree
from .utils import (
    convert_timestamp,
    generate_formatted_date_range,
)


import requests


class UpdateFromPlex:
    def __init__(self):
        self.base_url = "https://epg.provider.plex.tv/grid?date={date}&channelGridKey={id}&X-Plex-Language=zh-HK"
        self.headers = {
            "x-plex-provider-version": "5.1",
            "Host": "epg.provider.plex.tv",
        }

    def fetch_programs(self, id):
        programmes = []

        dates = generate_formatted_date_range(
            start_days_ago=1,
            end_days_in_future=7,
            fmt="%Y-%m-%d",
            tz="America/Los_Angeles",
        )

        for date in dates:
            try:
                content = requests.get(
                    self.base_url.format(date=date, id=id), headers=self.headers
                ).content.decode("utf-8")

                root = etree.fromstring(content)

                for video in root.findall(".//Video"):
                    title = f'{video.get("grandparentTitle")} - {video.get("title")}'
                    play = video.findall(".//Media")
                    programmes.extend(
                        [
                            {
                                "start": convert_timestamp(int(p.get("beginsAt"))),
                                "stop": convert_timestamp(int(p.get("endsAt"))),
                                "title": title,
                            }
                            for p in play
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
    updater = UpdateFromPlex()
    updater.fetch_programs("60a53634126de9002e694bc4")
