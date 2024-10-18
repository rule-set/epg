from loguru import logger
from .utils import (
    add_stop_time_to_info,
    convert_date_string,
    generate_dates_from_monday,
)

import requests


class UpdateFromTVMao:
    def __init__(self):
        self.base_url = "https://tvmao.rule-set.workers.dev/?id={id}&day={day}"
        self.date_format = "%Y%m%d %H:%M"
        self.delta = 0

    def fetch_programs(self, id):
        programmes = []

        dates = generate_dates_from_monday(end_days=14, fmt="%Y%m%d")
        for day, date in enumerate(dates):
            try:
                epg_json = requests.get(
                    self.base_url.format(id=id, day=day + 1)
                ).json()[2]["pro"]

                programmes.extend(
                    [
                        {
                            "start": convert_date_string(
                                f'{date} {item["time"]}',
                                format=self.date_format,
                                delta=self.delta,
                            ),
                            "title": item["name"],
                        }
                        for item in epg_json
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
    updater = UpdateFromTVMao()
    updater.fetch_programs("GDTV2")
