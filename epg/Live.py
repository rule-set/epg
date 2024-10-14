from loguru import logger
from .utils import generate_formatted_date_range


class UpdateFromLive:
    def __init__(self):
        self.base_url = ""

    def fetch_programs(self, id):
        programmes = []
        dates = generate_formatted_date_range(
            start_days_ago=7, end_days_in_future=7, fmt="%Y%m%d"
        )

        programmes = [
            {
                "start": f"{date}000000",
                "stop": f"{date}235959",
                "title": "Live News",
            }
            for date in dates
        ]

        if programmes:
            logger.info(
                f"Successfully fetched and processed {len(programmes)} programs for {id}."
            )
        else:
            logger.warning(f"No programme information was fetched for {id}.")

        return programmes


if __name__ == "__main__":
    updater = UpdateFromLive()
    updater.fetch_programs("Fox Live")
