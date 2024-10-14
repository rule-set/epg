from loguru import logger
from .utils import convert_date_string, generate_formatted_date

import requests


class UpdateFromSCGD:
    def __init__(self):
        """Request API"""
        self.base_url = "http://epg.iqy.sc96655.com/v1/getPrograms?channel={id}&begin_time={begin_time}%2000%3A00%3A00&end_time={end_time}%2023%3A59%3A59"

        """ Request Header """
        self.headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI5ODQwODlhNjc1OGU0ZjJlOTViMjk4NWM4YjA1MDNmYiIsImNvbXBhbnkiOiJxaXlpIiwibmFtZSI6InRlcm1pbmFsIn0.1gDPpBcHJIE8dLiq7UekUlPWMtJOYymI8zoIYlsVgc4"
        }

        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.delta = 0

    def fetch_programs(self, id):
        try:
            start, end = generate_formatted_date(
                start_days_ago=7, end_days_in_future=7, fmt="%Y-%m-%d"
            )

            epg_json = requests.get(
                self.base_url.format(begin_time=start, end_time=end, id=id),
                headers=self.headers,
            ).json()

            epg_items = epg_json["ret_data"]

            programmes = [
                {
                    "start": convert_date_string(
                        item["begin_time"], format=self.date_format, delta=self.delta
                    ),
                    "stop": convert_date_string(
                        item["end_time"], format=self.date_format, delta=self.delta
                    ),
                    "title": item["name"],
                }
                for item in epg_items
            ]

        except requests.RequestException as e:
            logger.error(f"Network request failed for {id} on {date}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {id} on {date}: {e}")

        if programmes:
            logger.info(
                f"Successfully fetched and processed {len(programmes)} programs for {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromSCGD()
    updater.fetch_programs("3496")
