from loguru import logger
from lxml import html
from .utils import convert_date_string, generate_formatted_date_range
import requests


class UpdateFromRTHK:
    def __init__(self):
        self.base_url = "https://www.rthk.hk/timetable/{id}"
        self.start_date_format = "%Y%m%d %H:%M"
        self.end_date_format = "%Y%m%d %H:%M:%S"

    def fetch_programs(self, id):
        try:
            content = requests.get(self.base_url.format(id=id)).content.decode("utf-8")
        except requests.RequestException as e:
            logger.error(f"Request error for channel {id}: {e}")
            return []

        tree = html.fromstring(content)
        programmes = []
        dates = generate_formatted_date_range(7, 8, "%Y%m%d")

        for date in dates:
            time_xpath = f'//div[@date="{date}"]//div[contains(@class, "shdBlock") and (contains(@class, "clearfix") or contains(@class, "hiLite"))]//div[@class="shTimeBlock"]/p[@class="timeDis"]'
            name_xpath = f'//div[@date="{date}"]//div[contains(@class, "shdBlock") and (contains(@class, "clearfix") or contains(@class, "hiLite"))]//div[@class="shTitleBlock"]/div[@class="shTitle"]/a'

            time_array = tree.xpath(time_xpath)
            name_array = tree.xpath(name_xpath)

            for idx in range(len(time_array) // 2):
                start, stop = time_array[2 * idx].text, time_array[2 * idx + 1].text
                stop = "23:59:59" if stop == "00:00" else f"{stop}:00"
                name = name_array[idx].text.strip()

                programmes.append(
                    {
                        "start": convert_date_string(
                            f"{date} {start}", self.start_date_format, 0
                        ),
                        "stop": convert_date_string(
                            f"{date} {stop}", self.end_date_format, 0
                        ),
                        "title": name,
                    }
                )

        if programmes:
            logger.info(
                f"Successfully fetched and processed {len(programmes)} programs for {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromRTHK()
    updater.fetch_programs("tv34")
