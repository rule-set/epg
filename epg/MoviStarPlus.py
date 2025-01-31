from loguru import logger
from .utils import convert_date_string, generate_formatted_date_range
import requests


class UpdateFromMoviStarPlus:
    def __init__(self):
        self.base_url = "https://movistarplus.rule-set.workers.dev/?id={id}&date={date}"
        self.date_fmt = "%Y-%m-%dT%H:%M:%S%z"
        self.delta = 7

    def fetch_programs(self, id):
        programmes = []

        for date in generate_formatted_date_range(start_days_ago=7, end_days_in_future=6, fmt="%Y-%m-%d", tz="Europe/Madrid"):
            try:
                epg_json = requests.get(self.base_url.format(id=id, date=date), verify=False).json()
                item_list = next((item for item in epg_json if item.get("@type") == "ItemList"), None)
                if not item_list:
                    logger.warning(f"No ItemList found for channel {id} on date {date}.")
                    continue

                programmes.extend(
                    {
                        "start": convert_date_string(item["item"]["startDate"], self.date_fmt, self.delta),
                        "stop": convert_date_string(item["item"]["endDate"], self.date_fmt, self.delta),
                        "title": item["item"]["name"],
                    }
                    for item in item_list.get("itemListElement", [])
                    if all(key in item.get("item", {}) for key in ["startDate", "endDate", "name"])
                )

            except requests.RequestException as e:
                logger.error(f"Request error for channel {id}: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred for channel {id}: {e}")

        logger.info(f"Fetched {len(programmes)} programs for channel {id}." if programmes else f"No programmes fetched for {id}.")
        return programmes


if __name__ == "__main__":
    updater = UpdateFromMoviStarPlus()
    updater.fetch_programs("mvf1")
