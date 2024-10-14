from loguru import logger
from .utils import (
    convert_date_string,
    generate_formatted_date_range,
)
import requests


class UpdateFromMoviStarPlus:
    def __init__(self):
        self.base_url = "https://movistarplus.masssoftzheng.workers.dev/?date={date}"

        self.date_fmt = "%Y-%m-%d %H:%M"
        self.delta = 6

    def fetch_programs(self, id):
        programmes = []

        dates = generate_formatted_date_range(
            start_days_ago=7, end_days_in_future=6, fmt="%Y-%m-%d", tz="Europe/Madrid"
        )
        for date in dates:
            try:
                epg_json = requests.get(
                    self.base_url.format(date=date), verify=False
                ).json()

                epg_item = epg_json["data"][id]["PROGRAMAS"]

                programmes.extend(
                    [
                        {
                            "start": convert_date_string(
                                f'{date} {item["HORA_INICIO"]}',
                                self.date_fmt,
                                self.delta,
                            ),
                            "stop": convert_date_string(
                                f'{date} {item["HORA_FIN"]}',
                                self.date_fmt,
                                self.delta,
                            ),
                            "title": item["TITULO"],
                        }
                        for item in epg_item
                    ]
                )
            except requests.RequestException as e:
                logger.error(f"Request error for channel {id}: {e}")
                continue
            except Exception as e:
                logger.error(f"An unexpected error occurred for channel {id}: {e}")
                continue

        if programmes:
            logger.info(
                f"Successfully fetched {len(programmes)} programs for channel {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromMoviStarPlus()
    updater.fetch_programs("MVF1-CODE")
